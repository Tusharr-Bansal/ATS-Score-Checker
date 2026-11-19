# Matching algorithm & scoring methodology

ATSScore combines an LLM with deterministic scoring. An LLM (Gemini) does what it is best at, turning messy documents
into structured data. The **score itself is deterministic and transparent**: it is computed from
explicit evidence (skills found, years counted, similarities measured), so every point can be
explained and the same inputs always give the same score.

```
JD text ─┐                       ┌─ required / preferred skills (+ alternatives, core flag)
         ├─ parse ─ extract ─────┤  min years, education, responsibilities
Resume ──┘  (PDF/DOCX)  (Gemini   └─ name, contact, skills, roles with dates, education, projects
                         or rules)
                │
                ▼
     normalise skills (taxonomy: aliases + implications)     embed passages (Gemini / MiniLM)
                │                                                       │
                └──────────────► 4 component scores ◄───────────────────┘
                                 skills · semantic · experience · education
                                          │
                              weighted sum → 0–100 + reasons
```

## 1. Extraction

| Step | Gemini path (`EXTRACTOR=gemini`) | Fallback (`EXTRACTOR=rules`, or if a Gemini call fails) |
|---|---|---|
| JD | JSON-mode call with a Pydantic schema (`JDData`): atomic skills, `alternatives` for "X or Y", `core` flag for role-defining skills, min years, education, responsibilities | Section headings (Requirements / Nice to have / Responsibilities), taxonomy skill scan, regex for years & degrees, "or" / "/" → alternatives |
| Resume | JSON-mode call (`ResumeData`): contact, skills from anywhere in the text, roles with `YYYY-MM` dates, education with level, projects, certifications | Section headings, regexes for email/phone/date ranges/degrees, taxonomy scan |

Both outputs go through the same post-processing:

* **Skill normalisation** (`app/skills.py`): ~170 canonical skills with aliases
  (`k8s → Kubernetes`, `Postgres → PostgreSQL`, `sklearn → scikit-learn`, `Java 17 → Java`) and
  *implications* (`Spring Boot ⇒ Java`, `PySpark ⇒ Spark + Python`, `Snowflake ⇒ Data Warehousing + SQL`,
  `Jenkins ⇒ CI/CD`, `FAISS ⇒ Vector Databases`). Unknown skills are kept as free text.
* The raw resume text is also scanned with the taxonomy, so skills mentioned only inside experience
  bullets are not lost.
* **Total experience** = union of all role date ranges (overlaps are merged, not double-counted).
* Skills named in the job title are always marked **core**.

## 2. Component scores (each in [0, 1])

### Skills (weight 0.40): LLM-led, verified

Every JD requirement gets a verdict for every candidate, from one of two matchers
(`SKILL_MATCHER`):

**`llm` (default when a Gemini key is set).** Gemini judges each requirement as `met`, `partial` or
`not_met` and must return a **verbatim quote from the resume** as evidence. The quote is then checked
in code (`app/llm_match.py`, `verify_quote`): if it cannot be found in the resume text, the claim is
discarded (scored as missing) and flagged in the explanation. The LLM can recognise equivalences no
list contains ("drew blood from arm veins" meets "Venipuncture"), but it cannot invent evidence.
Resumes are judged in batches (`MATCH_BATCH_SIZE`, default 10 per call) to fit free-tier quotas.

**`taxonomy` (offline mode, and the automatic fallback for any candidate the LLM could not judge).** Rules over `app/skills.py`:
listed skill or accepted alternative, implied skill (`Spring Boot ⇒ Java`), literal mention in the
resume text = 1.0; a semantically similar skill name (embedding cosine above a strict threshold, not a
known false friend such as Java/JavaScript) = 0.5; otherwise 0.

A third mode, `hybrid` (taxonomy first, LLM only for what it missed), was evaluated and removed: it
matched LLM-only recall on unseen domains (1.00) with slightly lower precision (0.88 vs 0.92), so it
added a second decision path without benefit.

| Verdict | Credit |
|---|---|
| met / matched | 1.0 |
| partial / related | 0.5 |
| not met, or LLM claim with an unverifiable quote | 0 |

`SkillScore = 0.8 × required coverage + 0.2 × preferred coverage`, where coverage is the credit-weighted
share of requirements and **core skills count double**, so generic overlap (Docker, Git, Excel) cannot
make a candidate from a different role look like a fit.

Why LLM-led: a hand-made taxonomy can promise that its entries are correct, but it can never promise
coverage, and every gap marks a good candidate as "missing" a skill they have. The held-out domains in
the evaluation (Phlebotomist, Pastry Chef, Paralegal, with vocabulary the taxonomy has never seen)
measure exactly this.

### Semantic similarity (weight 0.30)
Captures fit that keyword matching misses. The resume is split into passages: summary + skills, each
role, each individual bullet and each project. Two measures are averaged:

* **Overall similarity**: JD profile (title + responsibilities + required skills) vs the best
  whole-role passages: `0.6 × best + 0.4 × mean(top-3)`.
* **Responsibility coverage**: for each JD responsibility, the best-matching passage (bullets
  included); averaged. This also yields the "responsibility ↔ evidence" table in the UI.

Raw cosine similarities are mapped to [0, 1] with a calibrated linear ramp (`lo`→0, `hi`→1),
because each embedding model has its own similarity scale (`app/embeddings.py`).

### Relevant experience (weight 0.20)
Each role's months are weighted by how relevant the role is to this JD:

```
relevance = max( title_similarity(role title, JD title),
                 0.5 × description_similarity(role, JD) + 0.5 × required-skill overlap in that role )
relevant_years = Σ months × relevance × (0.5 if internship else 1) / 12      (capped at total years)
ExperienceScore = min(1, relevant_years / JD minimum years)
```

So a matching title alone is enough ("Junior Data Scientist" → "Data Scientist"), but otherwise the
role must both read like the JD *and* use the JD's skills. Ten years as a Data Engineer therefore
counts for little towards a Java backend role.

### Education (weight 0.10)
`0.75 × level + 0.25 × field`. Level: meets or exceeds the JD → 1.0; one level below → 0.7 if the
degree is preferred or 0.5 if it is required; further below → 0.2. Field: exact text match or
embedding similarity to the JD's fields. A JD with no degree requirement gives 1.0.

## 3. Final score and explanation

```
Score = 100 × (0.40·Skills + 0.30·Semantic + 0.20·Experience + 0.10·Education)
Fit:  ≥75 Strong · 60–75 Good · 40–60 Partial · <40 Weak
```

Weights are environment variables (`W_SKILLS` …). Every result stores the per-component points,
the evidence for each skill (listed / implied by X / mentioned / related / missing), every role with
its duration and relevance, and the responsibility-to-evidence mapping. The **reasons** shown to the
recruiter are generated from these numbers (not by an LLM), so they cannot contradict the score.

## 4. Why this design

* **LLM for extraction and evidence, not for the number.** An LLM asked to "rate this resume 0–100"
  is hard to explain, varies between runs, and is sensitive to wording. Here the LLM structures text
  and judges requirement by requirement with quoted evidence; the score is arithmetic over those
  verdicts, so every point traces to a quote or a rule.
* **Skill matching is LLM-led but verified.** Embeddings are poor at short skill names (Gemini:
  "Excel" vs "Docker" 0.82, "Java" vs "JavaScript" 0.89; MiniLM: "k8s" vs "Kubernetes" 0.47) and a
  taxonomy cannot cover every domain, so the LLM decides equivalences. Each "met" must be backed by a
  quote that code finds in the resume, which removes hallucinated matches. The taxonomy is the
  offline fallback; embeddings handle paraphrased experience and responsibilities.
* **Robustness.** Without an API key, or if Gemini fails or is rate-limited, extraction falls back
  to rules and embeddings to a local model, so the app keeps working.

## 5. Evaluation

`backend/eval/run_eval.py` ranks all 30 synthetic resumes against all 10 synthetic JDs. Several JDs
are close neighbours on purpose (Java vs Python backend; Data Scientist vs ML Engineer vs NLP
Engineer; Data Engineer vs Data Analyst; Frontend vs Full-stack; MLOps vs DevOps). See the README
for the latest numbers.
