"""Background processing of uploaded resume batches."""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from . import extraction, llm, llm_match
from .config import settings
from .db import Candidate, Job, SessionLocal
from .embeddings import get_embedder
from .matching import prepare_job, prewarm, score_candidate
from .schemas import JDData, ResumeData

log = logging.getLogger("checkres.services")


def _expected_extractor() -> str:
    return "gemini" if settings.extractor == "gemini" and llm.available() else "rules"


def _cached_extraction(db, content_hash: str, exclude_id: int):
    """Reuse a previous extraction of the identical file (saves Gemini calls on re-uploads), but only one made
    by the extractor in use now: a rules fallback from a Gemini outage is never reused when Gemini is on."""
    return db.scalar(select(Candidate).where(Candidate.content_hash == content_hash, Candidate.status == "done",
                                             Candidate.extractor == _expected_extractor(),
                                             Candidate.id != exclude_id).limit(1))


async def _extract_one(cid: int) -> None:
    with SessionLocal() as db:
        c = db.get(Candidate, cid)
        if c.data:  # already extracted before an interruption: don't spend another Gemini call
            c.status = "extracted"
            db.commit()
            return
        c.status = "processing"
        db.commit()
        prev = _cached_extraction(db, c.content_hash, c.id)
        if prev and prev.data:
            c.data, c.extractor, c.status = prev.data, prev.extractor, "extracted"
            db.commit()
            return
        text = c.raw_text
    try:
        data, src = await extraction.extract_resume(text)
        with SessionLocal() as db:
            c = db.get(Candidate, cid)
            c.data, c.extractor, c.status = data.model_dump(), src, "extracted"
            db.commit()
    except Exception as e:
        log.exception("extraction failed for candidate %s", cid)
        with SessionLocal() as db:
            c = db.get(Candidate, cid)
            c.status, c.error = "error", f"Extraction failed: {e}"
            db.commit()


def _score_all(job_id: int, cand_ids: list[int], verdicts: dict | None = None) -> None:
    emb = get_embedder()
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        ctx = prepare_job(JDData.model_validate(job.data), emb)
        cands = [db.get(Candidate, cid) for cid in cand_ids]
        try:
            prewarm(emb, [ResumeData.model_validate(c.data) for c in cands if c.data and c.status != "error"])
        except Exception:
            log.exception("batch embedding failed; falling back to per-candidate embedding")
        for cid in cand_ids:
            c = db.get(Candidate, cid)
            if c.status == "error" or not c.data:
                continue
            try:
                v = (verdicts or {}).get(str(cid))
                r = score_candidate(ctx, ResumeData.model_validate(c.data), c.raw_text, emb, verdicts=v)
                ai_on = settings.skill_matcher == "llm" and llm.available()
                r["ai"] = {
                    "extraction": c.extractor,                      # "gemini" or "rules"
                    "matching": "llm" if v else ("unavailable" if ai_on else "off"),
                    "fallback": ai_on and (not v or c.extractor != "gemini"),
                }
                if r["ai"]["fallback"]:
                    r["reasons"].insert(0, {"type": "negative", "text":
                        "AI analysis was unavailable for this resume (Gemini was overloaded, timed out or out of "
                        "quota), so it was scored with the rule-based fallback, which is less accurate. "
                        "Re-upload it later for a full AI analysis."})
                c.score, c.result, c.status = r["score"], r, "done"
            except Exception as e:
                log.exception("scoring failed for candidate %s", cid)
                c.status, c.error = "error", f"Scoring failed: {e}"
            db.commit()


async def _judge_skills(job_id: int, cand_ids: list[int]) -> dict:
    """LLM-led skill verdicts for the whole batch (a few Gemini calls, not one per candidate)."""
    if settings.skill_matcher != "llm" or not llm.available():
        return {}
    with SessionLocal() as db:
        jd = JDData.model_validate(db.get(Job, job_id).data)
        items = [(str(c.id), c.raw_text, ResumeData.model_validate(c.data))
                 for c in (db.get(Candidate, cid) for cid in cand_ids) if c.status != "error" and c.data]
    try:
        return await llm_match.match_batch(jd, items)
    except Exception:
        log.exception("LLM skill matching failed; scoring with the taxonomy matcher")
        return {}


async def process_batch(job_id: int, cand_ids: list[int]) -> None:
    # 1) LLM/rule extraction, concurrently (Gemini concurrency and pacing are handled in llm.py)
    await asyncio.gather(*(_extract_one(cid) for cid in cand_ids))
    # 2) LLM-led skill verdicts with verified quotes (falls back to taxonomy per candidate)
    with SessionLocal() as db:
        for cid in cand_ids:
            c = db.get(Candidate, cid)
            if c.status == "extracted":
                c.status = "matching"
        db.commit()
    verdicts = await _judge_skills(job_id, cand_ids)
    # 3) embeddings + scoring (CPU / sync API) off the event loop
    await asyncio.to_thread(_score_all, job_id, cand_ids, verdicts)


UNFINISHED = ("queued", "processing", "extracted", "matching")


async def resume_interrupted() -> None:
    """Background tasks die with the server (redeploy, crash, free-tier restart). On startup, pick up
    every resume that was left mid-way so nothing stays stuck in 'processing' forever."""
    from collections import defaultdict
    with SessionLocal() as db:
        rows = db.execute(select(Candidate.job_id, Candidate.id).where(Candidate.status.in_(UNFINISHED))).all()
    by_job = defaultdict(list)
    for job_id, cid in rows:
        by_job[job_id].append(cid)
    for job_id, ids in by_job.items():
        log.info("resuming %d interrupted resume(s) for job %s", len(ids), job_id)
        try:
            await process_batch(job_id, ids)
        except Exception:
            log.exception("could not resume job %s", job_id)
