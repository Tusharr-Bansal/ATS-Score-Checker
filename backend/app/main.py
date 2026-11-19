"""CheckRes API.

  POST /api/jobs                       Module 1  paste or upload a JD -> extracted requirements
  GET  /api/jobs | /api/jobs/{id}
  POST /api/jobs/{id}/resumes          Module 2  batch upload (PDF/DOCX), processed in background
  GET  /api/jobs/{id}/candidates       Module 3/4 ranking table (poll while status != done)
  GET  /api/candidates/{id}            Module 5  full candidate analysis
"""
from __future__ import annotations

import hashlib
import logging

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from . import extraction, llm
from .config import settings
from .db import Candidate, Job, SessionLocal, init_db
from .parsing import ParseError, extract_text
from .services import process_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app = FastAPI(title="CheckRes — AI Resume Matching & Ranking", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "extractor": settings.extractor if llm.available() or settings.extractor == "rules"
            else "rules", "llm_model": settings.gemini_model if llm.available() else None,
            "embedding_provider": settings.embedding_provider,
            "weights": {"skills": settings.w_skills, "semantic": settings.w_semantic,
                        "experience": settings.w_experience, "education": settings.w_education}}


def _job_out(job: Job, n: int | None = None) -> dict:
    return {"id": job.id, "title": job.title, "data": job.data, "extractor": job.extractor,
            "raw_text": job.raw_text, "created_at": job.created_at, "candidate_count": n}


# ------------------------------------------------------------------ Module 1: JD
@app.post("/api/jobs")
async def create_job(text: str = Form(""), file: UploadFile | None = File(None)):
    if file is not None and file.filename:
        try:
            text = extract_text(file.filename, await file.read())
        except ParseError as e:
            raise HTTPException(400, str(e))
    if len(text.strip()) < 50:
        raise HTTPException(400, "Please paste or upload a job description (at least a few lines).")
    data, src = await extraction.extract_jd(text)
    with SessionLocal() as db:
        job = Job(title=data.title or text.strip().splitlines()[0][:200], raw_text=text,
                  data=data.model_dump(), extractor=src)
        db.add(job)
        db.commit()
        return _job_out(job, 0)


@app.get("/api/jobs")
def list_jobs():
    with SessionLocal() as db:
        rows = db.execute(select(Job, func.count(Candidate.id)).outerjoin(Candidate)
                          .group_by(Job.id).order_by(Job.created_at.desc())).all()
        return [{**_job_out(j, n), "raw_text": None} for j, n in rows]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(404, "Job not found")
        return _job_out(job, len(job.candidates))


# ------------------------------------------------------------------ Module 2: resumes
@app.post("/api/jobs/{job_id}/resumes")
async def upload_resumes(job_id: int, background: BackgroundTasks, files: list[UploadFile] = File(...)):
    if len(files) > settings.max_upload_files:
        raise HTTPException(400, f"Upload at most {settings.max_upload_files} files per batch.")
    created, rejected = [], []
    with SessionLocal() as db:
        if not db.get(Job, job_id):
            raise HTTPException(404, "Job not found")
        for f in files:
            data = await f.read()
            if not f.filename.lower().endswith((".pdf", ".docx")):
                rejected.append({"filename": f.filename, "error": "Only PDF and DOCX resumes are supported."})
                continue
            c = Candidate(job_id=job_id, filename=f.filename, content_hash=hashlib.sha256(data).hexdigest())
            try:
                c.raw_text = extract_text(f.filename, data)
            except ParseError as e:
                c.status, c.error = "error", str(e)
            db.add(c)
            db.flush()
            created.append(c.id)
        db.commit()
        todo = [cid for cid in created if db.get(Candidate, cid).status != "error"]
    if todo:
        background.add_task(process_batch, job_id, todo)
    return {"accepted": len(created), "queued": len(todo), "rejected": rejected, "candidate_ids": created}


# ------------------------------------------------------------------ Module 4: ranking
@app.get("/api/jobs/{job_id}/candidates")
def ranking(job_id: int):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(404, "Job not found")
        out = []
        for c in job.candidates:
            d, r = c.data or {}, c.result or {}
            out.append({
                "id": c.id, "filename": c.filename, "status": c.status, "error": c.error,
                "name": d.get("name") or c.filename, "score": c.score, "fit": r.get("fit"),
                "total_years": d.get("total_years"),
                "relevant_years": (r.get("experience") or {}).get("relevant_years"),
                "matched_skills": r.get("matched_skills", []), "missing_skills": r.get("missing_skills", []),
            })
        out.sort(key=lambda x: (x["score"] is None, -(x["score"] or 0)))
        for i, row in enumerate(out, 1):
            row["rank"] = i if row["score"] is not None else None
        return {"job_id": job_id, "pending": sum(x["status"] in ("queued", "processing") for x in out),
                "candidates": out}


# ------------------------------------------------------------------ Module 5: candidate detail
@app.get("/api/candidates/{cand_id}")
def candidate_detail(cand_id: int):
    with SessionLocal() as db:
        c = db.get(Candidate, cand_id)
        if not c:
            raise HTTPException(404, "Candidate not found")
        return {"id": c.id, "job_id": c.job_id, "job_title": c.job.title, "filename": c.filename,
                "status": c.status, "error": c.error, "extractor": c.extractor,
                "profile": c.data, "score": c.score, "result": c.result}
