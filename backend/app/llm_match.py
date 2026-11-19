"""LLM-led skill matching with deterministic verification.

For each JD requirement and each candidate, Gemini returns a verdict (met / partial / not_met)
and a VERBATIM quote from the resume as evidence. The quote is then checked in code against the
resume text: a "met" or "partial" whose quote cannot be found is downgraded to not_met and flagged
as unverified. The LLM therefore decides *whether* a requirement is evidenced, but cannot invent
evidence; the final score is still plain arithmetic over these verdicts (see matching.py).

Candidates are judged in batches (MATCH_BATCH_SIZE per call) to stay within free-tier quotas.
"""
from __future__ import annotations

import asyncio
import logging
import re
from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel, Field

from . import llm
from .config import settings
from .schemas import JDData, SkillReq

log = logging.getLogger("checkres.llm_match")
PROMPT_VERSION = "v2"  # v2: also rates relevance of each role and project


class ReqVerdict(BaseModel):
    requirement_id: str = Field(description="Requirement id, e.g. 'R3'")
    status: Literal["met", "partial", "not_met"]
    evidence: str = Field("", description="Shortest EXACT phrase copied from this candidate's resume (max 20 "
                                          "words) proving the requirement; empty for not_met")
    reason: str = Field("", description="Max 12 words")


class ItemRating(BaseModel):
    item_id: str = Field(description="Role or project id from the list, e.g. 'E1' or 'P2'")
    relevance: float = Field(description="0 = unrelated, 0.5 = related or transferable, 1 = the same kind of work")
    reason: str = Field("", description="Max 12 words")


class CandidateVerdicts(BaseModel):
    candidate_id: str = Field(description="Candidate id, e.g. 'C2'")
    verdicts: list[ReqVerdict]
    ratings: list[ItemRating] = Field(default_factory=list)


class BatchVerdicts(BaseModel):
    candidates: list[CandidateVerdicts]


PROMPT = """You are a meticulous recruiter checking whether candidates meet the requirements of a job.
Judge every requirement for every candidate, using ONLY what each candidate's resume says.

Status rules:
- met: the resume clearly shows the requirement, the same skill under another name, or a more specific
  form of it. Examples: "PostgreSQL" meets "SQL"; "drew blood from arm veins" meets "Venipuncture";
  "Tally Prime" meets "Accounting software". A listed alternative also counts as met.
- partial: closely related but not the same, or only weak/indirect evidence (coursework, assisting
  someone else, an adjacent tool).
- not_met: no evidence. Do not infer skills from job titles or employer names alone. Similar-sounding
  is not the same: Java is not JavaScript, React is not React Native.

evidence: copy the shortest exact phrase from that candidate's resume (max 20 words) that proves the
verdict, character for character. Never paraphrase. Use "" for not_met.

Also rate how relevant each listed role (E1, E2, ...) and project (P1, P2, ...) is to THIS job, judging the
work actually described in the resume rather than the job title: 1 = the same kind of work,
0.5 = related or transferable work, 0 = unrelated.

REQUIREMENTS
{requirements}

CANDIDATES
{candidates}
"""


def requirement_list(jd: JDData) -> list[tuple[str, str, SkillReq]]:
    """[(id, kind, req)] in a fixed order: required first, then preferred."""
    out = [(f"R{i + 1}", "required", r) for i, r in enumerate(jd.required_skills)]
    n = len(out)
    out += [(f"R{n + i + 1}", "preferred", r) for i, r in enumerate(jd.preferred_skills)]
    return out


def _req_line(rid: str, kind: str, r: SkillReq) -> str:
    alt = f" (alternatives: {', '.join(r.alternatives)})" if r.alternatives else ""
    return f"{rid} [{kind}] {r.name}{alt}"


# ----------------------------------------------------------------------------- verification
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%+#&]+", " ", s.lower()).strip()


def verify_quote(quote: str, resume_text: str) -> bool:
    """True if the quote really appears in the resume (tolerant to case, punctuation, line breaks)."""
    q, t = _norm(quote), _norm(resume_text)
    if len(q) < 3:
        return False
    if q in t:
        return True
    # tolerate small differences (e.g. a dropped word): a long contiguous overlap is required
    m = SequenceMatcher(None, q, t, autojunk=False).find_longest_match(0, len(q), 0, len(t))
    return m.size >= max(12, 0.8 * len(q))


# ----------------------------------------------------------------------------- batching
def _items_line(res) -> str:
    if res is None:
        return ""
    items = [f"E{i + 1} = {e.title} at {e.company} ({e.start or '?'} to {e.end or '?'})" for i, e in enumerate(res.experience)]
    items += [f"P{i + 1} = project: {p.name}" for i, p in enumerate(res.projects)]
    return ("ROLES AND PROJECTS TO RATE: " + "; ".join(items) + "\n") if items else ""


async def _judge_chunk(jd: JDData, chunk: list[tuple]) -> dict[str, dict]:
    reqs = requirement_list(jd)
    cands = "\n\n".join(f"=== C{i + 1} ===\n{_items_line(item[2] if len(item) > 2 else None)}RESUME:\n{item[1][:7000]}"
                          for i, item in enumerate(chunk))
    prompt = PROMPT.format(requirements="\n".join(_req_line(*r) for r in reqs), candidates=cands)
    res: BatchVerdicts = await llm._generate(prompt, BatchVerdicts)
    valid_ids = {rid for rid, _, _ in reqs}
    out: dict[str, dict[str, dict]] = {}
    for cv in res.candidates:
        m = re.fullmatch(r"C(\d+)", cv.candidate_id.strip())
        if not m or not (1 <= int(m.group(1)) <= len(chunk)):
            continue
        key, text = chunk[int(m.group(1)) - 1][:2]
        verdicts = {}
        for v in cv.verdicts:
            if v.requirement_id not in valid_ids:
                continue
            verified = v.status == "not_met" or verify_quote(v.evidence, text)
            verdicts[v.requirement_id] = {
                "status": v.status if verified else "not_met",
                "claimed": v.status,
                "evidence": v.evidence.strip(),
                "reason": v.reason.strip(),
                "verified": verified,
            }
        ratings = {r.item_id.strip(): {"relevance": max(0.0, min(1.0, float(r.relevance))), "reason": r.reason.strip()}
                   for r in cv.ratings if re.fullmatch(r"[EP]\d+", r.item_id.strip())}
        out[key] = {"reqs": verdicts, "ratings": ratings}
    return out


async def match_batch(jd: JDData, items: list[tuple], on_chunk=None) -> dict[str, dict]:
    """items: [(key, resume_text, ResumeData | None)] ->
    {key: {"reqs": {requirement_id: verdict}, "ratings": {"E1"/"P1": {relevance, reason}}}}.
    Failed chunks are omitted (callers fall back to the rule-based path for those candidates)."""
    if not items or not requirement_list(jd):
        return {}
    size = max(1, settings.match_batch_size)
    chunks = [items[i:i + size] for i in range(0, len(items), size)]

    async def run(chunk):
        try:
            r = await _judge_chunk(jd, chunk)
        except Exception as e:
            log.error("LLM skill matching failed for %d candidates (%s); using taxonomy for them", len(chunk),
                      str(e)[:160])
            return {}
        if on_chunk:
            on_chunk(r)
        return r

    results = await asyncio.gather(*(run(c) for c in chunks))
    merged: dict[str, dict[str, dict]] = {}
    for r in results:
        merged.update(r)
    return merged
