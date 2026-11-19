# ATSScore: AI resume matching & candidate ranking

Upload a job description and a batch of resumes (PDF/DOCX). ATSScore extracts structured
requirements and candidate profiles, scores each candidate 0–100 against the JD, ranks them, and
explains every score: matched, related and missing skills, relevant vs required experience,
education, and which parts of the resume support which JD responsibilities.

**Stack:** React (Vite) · FastAPI · PostgreSQL · Gemini Flash-Lite (structured extraction,
evidence-backed skill verdicts) · Gemini embeddings · sentence-transformers (offline fallback) ·
pdfplumber / python-docx

## Features (mapped to the assignment)

| Module | Implementation |
|---|---|
| 1. JD input | Paste text or upload PDF/DOCX/TXT → required skills (with "X or Y" alternatives and ★ core skills), nice-to-haves, min years, education, responsibilities |
| 2. Resume upload | Drag-and-drop batch upload (10+ files; default limit 50), PDF + DOCX, processed in the background with live status; duplicate files reuse earlier extractions |
| 3. AI matching | Score from four parts: skills (LLM verdict per requirement, each backed by a resume quote that code verifies) · semantic similarity (embeddings over roles, bullets, projects) · relevance-weighted experience · education |
| 4. Ranking dashboard | Table: rank, candidate, relevant/total experience, match %, fit label, matched and missing skills |
| 5. Candidate analysis | Score breakdown, plain-language reasons, per-skill evidence with the quoted resume line and who judged it (LLM or rules), experience comparison with per-role relevance, responsibility ↔ evidence table, all extracted info |

The full scoring method is described in **[docs/ALGORITHM.md](docs/ALGORITHM.md)**.

## Architecture

```
frontend/ (React + Vite)             backend/ (FastAPI)
  JobForm ─ POST /api/jobs ──────────► parsing.py      PDF/DOCX/TXT → text
  ResumeUpload ─ POST /jobs/{id}/resumes   extraction.py   Gemini (llm.py) or rules (extract_rules.py)
                                           llm_match.py    LLM skill verdicts + quote verification
  RankingTable ─ GET /jobs/{id}/candidates skills.py       taxonomy (offline / fallback matcher)
  CandidatePanel ─ GET /candidates/{id}    embeddings.py   Gemini or sentence-transformers + calibration
                                           matching.py     4 component scores, reasons
                                           services.py     background batch processing
                                           db.py ──────────► PostgreSQL (jobs, candidates; JSONB)
sample_data/  23 JDs, 76 resumes, labels          backend/eval/run_eval.py  ranking + skill metrics
```

## Running locally

### Option A: Docker (PostgreSQL + API + UI)
```bash
cp backend/.env.example backend/.env      # add GEMINI_API_KEY
docker compose up --build                 # UI http://localhost:3000 · API http://localhost:8000/docs
```
Without a Gemini key, build with offline embeddings: `WITH_LOCAL_EMBEDDINGS=true docker compose up --build`.

### Option B: dev mode
```bash
# backend
cd backend
python -m venv .venv && .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt                          # + requirements-local.txt for offline embeddings
cp .env.example .env                                     # add GEMINI_API_KEY; SQLite is the default DB
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm run dev                                              # http://localhost:5173 (proxies /api → :8000)
```

### Modes
| `GEMINI_API_KEY` | Extraction | Skill matching | Embeddings |
|---|---|---|---|
| set | Gemini (`GEMINI_MODEL`, default `gemini-3.5-flash-lite`) | LLM verdicts + verified quotes | Gemini (`gemini-embedding-001`) |
| not set | rule-based | taxonomy (`skills.py`) | local `all-MiniLM-L6-v2` (needs `requirements-local.txt`) |

Overrides: `EXTRACTOR=gemini|rules`, `SKILL_MATCHER=llm|taxonomy`, `EMBEDDING_PROVIDER=gemini|local`.
Any document or candidate the LLM cannot handle (outage, retries exhausted) falls back to the rule-based
path automatically, and the explanation says so.

### Free-tier quotas
The Gemini free tier has per-minute and per-day limits per Google Cloud project. ATSScore paces its
own requests so it stays within them instead of retrying into 429 errors:

| Setting | Default | Why |
|---|---|---|
| `LLM_RPM` | 10 | Flash-Lite requests per minute (Flash allows ~5/min and ~20/day, too few for batches) |
| `EMBED_PER_MIN` | 90 | The embeddings quota counts each text, not each request (100/min, 1,000/day) |
| `MATCH_BATCH_SIZE` | 10 | Resumes judged per LLM call |

An upload of 10 resumes costs about 11 Flash-Lite calls (10 extractions + 1 matching call) and
about 90 embedded texts (≈7 per resume + ≈15 for the JD). Set `LLM_RPM=0` and `EMBED_PER_MIN=0` on a paid tier.

## Sample data & evaluation

`sample_data/` holds **synthetic** data only (fictional people, companies and contacts):

* **23 JDs**, in three groups. Most come in near-neighbour pairs, so the ranking has to separate
  similar roles, not just different fields:
  * 10 tech: Java vs Python backend; Data Scientist vs ML Engineer vs NLP Engineer; Data Engineer vs
    Data Analyst; Frontend vs MERN; MLOps vs DevOps
  * 10 non-tech: Digital vs Content Marketing; B2B Sales vs Business Development; HR Generalist vs
    Talent Acquisition; Operations vs Project Manager; Accountant vs Financial Analyst
  * 3 **held-out domains** (Phlebotomist, Pastry Chef, Paralegal): no vocabulary from these fields was
    added anywhere in the code, and their resumes are worded differently from the JDs
    ("drew blood from arm veins" vs "Venipuncture")
* **76 resumes**, mixed PDF and DOCX: strong / mid / junior candidates per JD, plus 10 **off-domain
  decoys** (nurse, chef, lawyer, architect, …) that should score Weak against the JDs they don't fit
* `labels.json`: which JD each resume was written for, and which roles are neighbours
* `skill_labels.json`: 67 hand-labelled requirement × resume pairs (does this resume really meet this
  requirement?), including deliberate traps ("puff pastry" is a laminated dough but not viennoiserie;
  "typed affidavits drafted by the advocate" is not drafting)

Regenerate with `python sample_data/generate.py` (needs `reportlab`, `python-docx`).

```bash
cd backend
python -m eval.run_eval                 # ranking + skill-level metrics, all 23 JDs × 76 resumes
python -m eval.run_eval --show 5        # plus the top 5 per JD with component scores
python -m eval.run_eval --errors        # plus every skill-level mistake with its evidence
```
Extractions, embeddings and LLM verdicts are cached in `backend/eval/.cache/`, so only the first run
calls Gemini.

### Results (Gemini Flash-Lite extraction + LLM skill matching + Gemini embeddings)

| Ranking metric | Tech (10 JDs) | Non-tech (10) | Held-out (3) | All (23) |
|---|---|---|---|---|
| Top-1 is the JD's own strongest candidate | 10/10 | 10/10 | 3/3 | **23/23** |
| P@2 (strong + mid are the top 2) | 1.00 | 1.00 | 0.67 | 0.96 |
| P@3 | 0.73 | 0.87 | 1.00 | 0.83 |
| nDCG@10 | 0.88 | 0.93 | 0.97 | **0.91** |
| Strong > mid > junior ordering | 1.00 | 1.00 | 1.00 | 1.00 |

* **Absolute scores make sense:** all **227/227** decoy × JD pairs score Weak (< 40; max 34.8,
  median 8.5). Strong candidates score 90–99, mid candidates 46–91, juniors 21–61.
* **P@3 misses are juniors** (6–18 months of experience) ranked just below an experienced candidate
  from the neighbouring role, e.g. a 6-year data scientist above a 6-month MIS intern for a Data
  Analyst job. A recruiter would plausibly rank them the same way.
* Held-out P@2 of 0.67: in two held-out JDs the second place goes to a neighbouring professional
  (an experienced lawyer for Paralegal, a chef de partie for Pastry Chef) rather than the weaker
  in-field candidate.

### Skill matching: LLM vs taxonomy (same data, `SKILL_MATCHER=llm|taxonomy`)

| | Taxonomy (`skills.py`) | **LLM + verified quotes** |
|---|---|---|
| Known domains: precision / recall | 1.00 / 0.92 | 1.00 / 0.92 |
| **Unseen domains: precision / recall** | 0.88 / **0.65** | 0.92 / **1.00** |
| Unseen domains: strong candidate's score (Phlebotomist / Pastry / Paralegal) | 66 / 76 / 78 | **93 / 96 / 96** |
| Ranking nDCG@10, all JDs | 0.92 | 0.91 |

The taxonomy is precise on vocabulary it knows, but missed 35% of the skills candidates actually had
in fields it had never seen. Each of those misses tells a recruiter that a good candidate lacks a skill
they have. The LLM closes that gap. Ranking order is almost the same either way, because semantic
similarity and experience already carry it; the improvement is in the individual scores and the
"missing skills" explanations, which are what a recruiter reads. A third mode (taxonomy first, LLM
only for misses) was also tested and dropped: same recall, slightly lower precision, more complexity.

## API

Interactive docs: `http://localhost:8000/docs`

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | active extractor / embedding provider / weights |
| POST | `/api/jobs` | form field `text` or `file` → job with extracted requirements |
| GET | `/api/jobs`, `/api/jobs/{id}` | list / get jobs |
| POST | `/api/jobs/{id}/resumes` | multipart `files` (PDF/DOCX) → queued for processing |
| GET | `/api/jobs/{id}/candidates` | ranking (+ `pending` count while processing) |
| GET | `/api/candidates/{id}` | full analysis for one candidate |

## Deployment notes
* **Backend**: `backend/Dockerfile` (respects `$PORT`). Set `GEMINI_API_KEY` and `DATABASE_URL`
  (`postgres://` and `postgresql://` URLs are both accepted). With Gemini embeddings the image needs
  no PyTorch, so it fits small instances.
* **Frontend**: `frontend/Dockerfile`, or any static host (`npm run build` → `dist/`). Set
  `VITE_API_URL` to the backend URL at build time, and `CORS_ORIGINS` on the backend.
* Resume batches are processed in a FastAPI background task, so uploads return immediately; the
  UI polls until scoring is complete.

## Known limitations
* **Quote verification catches invented evidence, not misread evidence.** In testing, a fake LLM that
  made up 1,375 quotes got none of them through. But a genuine quote can still be misinterpreted:
  "Type and format affidavits drafted by the advocate" was credited as "Drafting affidavits"
  (1 of 44 held-out labels). The mitigation is transparency: every verdict shows its quote in the
  UI, so a recruiter can spot it at a glance. A prompt rule targeting this case was considered but
  not applied, since it would have been tuned on the same labels used to measure it.
* **Partial credit is a judgement call:** "assisted with dessert garnishing" earned half credit for
  "Plated desserts", which a strict reviewer might mark as not met.
* **Free-tier throughput:** roughly 120 resumes a day on one free Gemini project (the 1,000/day
  embedding quota is the bottleneck).
* **The test set is small and synthetic** (76 resumes written for this project); real resumes are
  messier.
* Scanned (image-only) PDFs are rejected; there is no OCR.
* Embedding calibration constants (`app/embeddings.py`) are fitted to `gemini-embedding-001` and
  MiniLM; recheck them with `eval/run_eval.py` when changing the embedding model.
* Background tasks run in-process. A production system would use a job queue (Celery/RQ) and
  authentication.
