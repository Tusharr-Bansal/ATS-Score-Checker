"""Extraction orchestrator: Gemini first (if configured), rule-based fallback, then normalisation.

Normalisation is identical for both extractors, so matching sees one consistent format.
"""
from __future__ import annotations

import logging

from . import extract_rules, llm
from . import skills as sk
from .config import settings
from .dates import merged_months
from .schemas import JDData, ResumeData, SkillReq

log = logging.getLogger("atsscore.extraction")


def _norm_reqs(reqs: list[SkillReq], exclude: set[str] = frozenset()) -> list[SkillReq]:
    out, seen = [], set(exclude)
    for r in reqs:
        names = sk.normalize_list([r.name])
        if not names:
            continue
        alts = [a for a in sk.normalize_list(names[1:] + list(r.alternatives)) if a.lower() != names[0].lower()]
        key = names[0].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(SkillReq(name=names[0], alternatives=alts, core=r.core))
    return out


def _mark_core(jd: JDData, text: str) -> None:
    """Skills named in the job title are always core. If the extractor marked none (rule-based
    path), also mark required skills mentioned 3+ times across the JD."""
    title = jd.title or (text.strip().splitlines() or [""])[0]
    had_core = any(r.core for r in jd.required_skills)
    for r in jd.required_skills:
        opts = [r.name, *r.alternatives]
        if any(sk.mentions(title, o) for o in opts):
            r.core = True
        elif not had_core:
            count = max(len(sk.mention_spans(text, o)) for o in opts)
            r.core = count >= 3


def postprocess_jd(jd: JDData, text: str = "") -> JDData:
    jd.required_skills = _norm_reqs(jd.required_skills)
    _mark_core(jd, text)
    jd.preferred_skills = _norm_reqs(jd.preferred_skills, {r.name.lower() for r in jd.required_skills})
    jd.responsibilities = [r.strip() for r in jd.responsibilities if r and r.strip()]
    return jd


def postprocess_resume(res: ResumeData, text: str) -> ResumeData:
    # union of extracted skills and taxonomy hits in the raw text (catches skills the LLM skipped)
    res.skills = sk.normalize_list(list(res.skills) + sk.scan_text(text))
    for e in res.education:
        if e.level == "none":
            e.level = extract_rules.degree_level(e.degree)
    for x in res.experience:
        if x.end and x.end.lower() in {"current", "now", "till date", "ongoing"}:
            x.end = "present"
    months = merged_months([(x.start, x.end) for x in res.experience])
    res.total_years = round(months / 12, 1)
    return res


async def extract_jd(text: str) -> tuple[JDData, str]:
    if settings.extractor == "gemini" and llm.available():
        try:
            return postprocess_jd(await llm.extract_jd(text), text), "gemini"
        except Exception as e:
            log.exception("Gemini JD extraction failed, using rules: %s", e)
    return postprocess_jd(extract_rules.extract_jd(text), text), "rules"


async def extract_resume(text: str) -> tuple[ResumeData, str]:
    if settings.extractor == "gemini" and llm.available():
        try:
            return postprocess_resume(await llm.extract_resume(text), text), "gemini"
        except Exception as e:
            log.exception("Gemini resume extraction failed, using rules: %s", e)
    return postprocess_resume(extract_rules.extract_resume(text), text), "rules"
