"""JD-to-resume matching and scoring.

Final score (0-100) = 100 * ( w_skills     * SkillScore
                            + w_semantic   * SemanticScore
                            + w_experience * ExperienceScore
                            + w_education  * EducationScore )

Every component is in [0, 1] and is computed from evidence that is returned alongside
the score, so the UI can show exactly why a candidate got their number.
See README.md / docs/ALGORITHM.md for the full description.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from . import skills as sk
from .config import settings
from .dates import months_between
from .embeddings import Embedder
from .schemas import EDU_RANK, JDData, ResumeData, SkillReq

INTERN_WEIGHT = 0.5  # internship months count half towards relevant experience


@dataclass
class JobContext:
    jd: JDData
    profile_vec: np.ndarray                      # title + responsibilities + required skills
    title_vec: np.ndarray
    resp_texts: list[str]
    resp_vecs: np.ndarray
    skill_vecs: dict[str, np.ndarray] = field(default_factory=dict)
    field_vecs: np.ndarray | None = None


def _jd_profile_text(jd: JDData) -> str:
    req = ", ".join(r.name for r in jd.required_skills)
    resp = " ".join(jd.responsibilities[:6]) or jd.summary
    return f"{jd.title}. {resp} Required skills: {req}."


def prepare_job(jd: JDData, emb: Embedder) -> JobContext:
    resp = jd.responsibilities[:12]
    names = sorted({n for r in jd.required_skills + jd.preferred_skills for n in [r.name, *r.alternatives]})
    vecs = emb.embed([_jd_profile_text(jd), jd.title or "job"] + resp + names + jd.education_fields)
    i = 2
    ctx = JobContext(jd=jd, profile_vec=vecs[0], title_vec=vecs[1], resp_texts=resp,
                     resp_vecs=vecs[i:i + len(resp)])
    i += len(resp)
    ctx.skill_vecs = {n: vecs[i + k] for k, n in enumerate(names)}
    i += len(names)
    ctx.field_vecs = vecs[i:] if jd.education_fields else None
    return ctx


# ----------------------------------------------------------------------------- chunks
def resume_chunks(res: ResumeData) -> list[dict]:
    """Passages used for semantic comparison, each with a human-readable label."""
    chunks = []
    head = " ".join(filter(None, [res.summary, "Skills: " + ", ".join(res.skills[:40]) if res.skills else ""]))
    if head.strip():
        chunks.append({"label": "Summary & skills", "text": head})
    for e in res.experience:
        label = f"{e.title} @ {e.company}".strip(" @")
        t = f"{e.title} at {e.company}. {e.description}".strip()
        if len(t) > 10:
            chunks.append({"label": label, "text": t, "exp": e})
        # individual bullets: finer-grained evidence for responsibility coverage
        bullets = [b.strip(" •-") for b in re.split(r"\n|(?<=[.;])\s+(?=[A-Z])", e.description or "")]
        bullets = [b for b in bullets if len(b) > 25]
        if len(bullets) > 1:
            for b in bullets:
                chunks.append({"label": f"{label}: “{b[:70]}{'…' if len(b) > 70 else ''}”",
                               "text": f"{e.title}: {b}", "bullet": True})
    for p in res.projects:
        chunks.append({"label": f"Project: {p.name}", "text": f"{p.name}: {p.description}"})
    return chunks or [{"label": "Resume", "text": res.summary or "empty"}]


def resume_embedding_texts(res: ResumeData) -> list[str]:
    """Every text score_candidate() will embed for this resume. Embedding them for a whole batch
    in one go (see prewarm) turns hundreds of tiny API calls into a few 100-text requests."""
    texts = [c["text"] for c in resume_chunks(res)]
    if settings.skill_matcher == "taxonomy":  # skill names are only embedded by the taxonomy matcher
        texts += list(res.skills)
    texts += [e.title or "role" for e in res.experience]
    texts += [f"{e.degree} {e.field}".strip() for e in res.education]
    return texts


def prewarm(emb: Embedder, resumes: list[ResumeData]) -> None:
    texts = list(dict.fromkeys(t for r in resumes for t in resume_embedding_texts(r)))
    if texts:
        emb.embed(texts)


# ----------------------------------------------------------------------------- skills
def _skill_index(res: ResumeData) -> tuple[set[str], dict[str, str]]:
    explicit = {s.lower() for s in res.skills}
    implied_by: dict[str, str] = {}
    for s in res.skills:
        for imp in sk.implied(sk.normalize(s)):
            if imp.lower() not in explicit:
                implied_by.setdefault(imp.lower(), s)
    return explicit, implied_by


def _match_requirement(req: SkillReq, explicit, implied_by, text: str, cand_names: list[str],
                       cand_vecs: np.ndarray, ctx: JobContext, emb: Embedder) -> dict:
    options = [req.name, *req.alternatives]
    label = req.name + (f" (or {', '.join(req.alternatives)})" if req.alternatives else "")
    for opt in options:
        if opt.lower() in explicit:
            return {"skill": label, "status": "matched", "credit": 1.0, "via": opt,
                    "evidence": f"Listed: {opt}" if opt == req.name else f"Has alternative {opt}"}
    for opt in options:
        if opt.lower() in implied_by:
            return {"skill": label, "status": "matched", "credit": 1.0, "via": opt,
                    "evidence": f"Implied by {implied_by[opt.lower()]}"}
    for opt in options:
        if sk.mentions(text, opt):
            return {"skill": label, "status": "matched", "credit": 1.0, "via": opt,
                    "evidence": f"Mentioned in resume text: {opt}"}
    # semantic fallback: closest candidate skill by embedding
    best, best_name = 0.0, None
    if len(cand_names):
        for opt in options:
            v = ctx.skill_vecs.get(opt)
            if v is None:
                continue
            sims = cand_vecs @ v
            for j in np.argsort(-sims)[:3]:
                if not sk.are_false_friends(opt, cand_names[j]) and sims[j] > best:
                    best, best_name = float(sims[j]), cand_names[j]
                    break
    if best_name and best >= emb.cal["skill_related"]:
        return {"skill": label, "status": "related", "credit": 0.5, "via": best_name,
                "evidence": f"Related skill: {best_name} (similarity {best:.2f})"}
    return {"skill": label, "status": "missing", "credit": 0.0, "via": None, "evidence": "Not found"}


def _from_verdict(req: SkillReq, v: dict) -> dict:
    """Turn a verified LLM verdict (llm_match.py) into a skill detail row."""
    label = req.name + (f" (or {', '.join(req.alternatives)})" if req.alternatives else "")
    quote = f"“{v['evidence']}”" if v.get("evidence") else ""
    status, credit = {"met": ("matched", 1.0), "partial": ("partial", 0.5), "not_met": ("missing", 0.0)}[v["status"]]
    text = " — ".join(x for x in (quote, v.get("reason", "")) if x) or "Not found"
    return {"skill": label, "status": status, "credit": credit, "via": v.get("evidence") or None,
            "source": "llm", "evidence": text}


def score_skills(ctx, res, text, emb, verdicts: dict | None = None, mode: str | None = None):
    """mode 'llm': verified LLM verdicts (llm_match.py); 'taxonomy': rules + embeddings (skills.py).
    In llm mode the taxonomy runs only for requirements without a verdict (no key / API outage)."""
    mode = mode or settings.skill_matcher
    explicit, implied_by = _skill_index(res)
    cand_names = res.skills
    _vecs = []

    def cand_vecs():  # candidate skill-name embeddings, computed only if the taxonomy matcher runs
        if not _vecs:
            _vecs.append(emb.embed(cand_names) if cand_names else np.zeros((0, 1)))
        return _vecs[0]

    details = []
    i = 0
    for kind, reqs in (("required", ctx.jd.required_skills), ("preferred", ctx.jd.preferred_skills)):
        for r in reqs:
            i += 1
            v = (verdicts or {}).get(f"R{i}") if mode == "llm" else None
            if v is not None and v.get("verified", True):
                d = _from_verdict(r, v)
            else:
                # no LLM verdict (taxonomy mode / outage), or the LLM's quote was not found in the resume:
                # use the rule-based matcher for this requirement instead of scoring it zero
                d = _match_requirement(r, explicit, implied_by, text, cand_names, cand_vecs(), ctx, emb)
                d["source"] = "taxonomy"
                if v is not None:
                    d["source"] = "llm_rejected"
                    d["evidence"] = (f"{d['evidence']}. (LLM said '{v['claimed']}' quoting "
                                     f"“{v.get('evidence', '')[:80]}”, which is not in the resume, so rules decided)")
            d["kind"] = kind
            d["core"] = bool(getattr(r, "core", False)) and kind == "required"
            details.append(d)

    def cov(kind):
        # core (role-defining) skills count double
        xs = [(d["credit"], 2.0 if d.get("core") else 1.0) for d in details if d["kind"] == kind]
        return (sum(c * w for c, w in xs) / sum(w for _, w in xs)) if xs else None

    req_cov, pref_cov = cov("required"), cov("preferred")
    if req_cov is None and pref_cov is None:
        score = None
    elif pref_cov is None:
        score = req_cov
    elif req_cov is None:
        score = pref_cov
    else:
        score = 0.8 * req_cov + 0.2 * pref_cov
    return score, req_cov, pref_cov, details


# ----------------------------------------------------------------------------- semantic
def score_semantic(ctx, chunks, chunk_vecs, emb):
    whole = np.array([not c.get("bullet") for c in chunks])
    prof_sims = chunk_vecs[whole] @ ctx.profile_vec  # overall fit: whole roles/projects, not bullets
    top = np.sort(prof_sims)[::-1][:3]
    overall = float(emb.calibrate(0.6 * top[0] + 0.4 * top.mean()))
    coverage, cov_details = None, []
    if len(ctx.resp_texts):
        sims = ctx.resp_vecs @ chunk_vecs.T          # (n_resp, n_chunks)
        best_idx = sims.argmax(axis=1)
        best = sims.max(axis=1)
        cal = emb.calibrate(best)
        coverage = float(cal.mean())
        for r, j, s, c in zip(ctx.resp_texts, best_idx, best, cal):
            cov_details.append({"responsibility": r, "evidence": chunks[j]["label"],
                                "similarity": round(float(s), 3), "strength": round(float(c), 2)})
    score = overall if coverage is None else 0.5 * overall + 0.5 * coverage
    return score, overall, coverage, cov_details


# ----------------------------------------------------------------------------- experience
def score_experience(ctx, res, chunks, chunk_vecs, emb, req_options: list[tuple[list[str], float]]):
    entries, rel_months = [], 0.0
    exp_chunks = [(c, v) for c, v in zip(chunks, chunk_vecs) if c.get("exp") is not None]
    title_vecs = emb.embed([c["exp"].title or "role" for c, _ in exp_chunks]) if exp_chunks else []
    for (c, v), tv in zip(exp_chunks, title_vecs):
        e = c["exp"]
        months = months_between(e.start, e.end) if e.start else 0
        # three signals, take the strongest: role description vs JD, job title vs JD title, skill overlap
        sem = float(emb.calibrate(float(v @ ctx.profile_vec), "exp"))
        title = float(emb.calibrate(float(tv @ ctx.title_vec), "title"))
        # skill overlap: core-weighted share of required skills evidenced in this role's own text
        # (explicit mentions plus implied ones, e.g. "Spring Boot" => Java)
        role_skills = {s.lower() for s in sk.scan_text(c["text"])}
        role_skills |= {i.lower() for s in list(role_skills) for i in sk.implied(sk.normalize(s))}
        hits = sum(w for opts, w in req_options if any(o.lower() in role_skills for o in opts))
        overlap = hits / sum(w for _, w in req_options) if req_options else 0.0
        # a matching job title is enough on its own; otherwise description AND skills must agree
        relevance = max(title, 0.5 * sem + 0.5 * overlap)
        intern = "intern" in e.title.lower()
        weight = relevance * (INTERN_WEIGHT if intern else 1.0)
        rel_months += months * weight
        entries.append({"title": e.title, "company": e.company, "start": e.start, "end": e.end,
                        "months": months, "relevance": round(relevance, 2), "internship": intern})
    total_years = res.total_years
    relevant_years = round(min(rel_months / 12, total_years if total_years else rel_months / 12), 1)
    req = ctx.jd.min_years
    if req and req > 0:
        score = min(1.0, relevant_years / req)
    else:
        score = 1.0 if relevant_years >= 1 else 0.5 + 0.5 * relevant_years
    return score, {"required_years": req, "total_years": total_years, "relevant_years": relevant_years,
                   "entries": entries}


# ----------------------------------------------------------------------------- education
def score_education(ctx, res, emb):
    jd = ctx.jd
    best = max(res.education, key=lambda e: EDU_RANK.get(e.level, 0), default=None)
    cand_level = best.level if best else "none"
    info = {"required_level": jd.education_level, "required": jd.education_required,
            "candidate_level": cand_level,
            "candidate_degree": f"{best.degree}{', ' + best.institution if best and best.institution else ''}"
            if best else "", "field_match": None}
    if jd.education_level == "none":
        return 1.0, info
    need, have = EDU_RANK[jd.education_level], EDU_RANK.get(cand_level, 0)
    if have >= need:
        level = 1.0
    elif have == need - 1:
        level = 0.5 if jd.education_required else 0.7
    else:
        level = 0.2
    field_score = 1.0
    if ctx.field_vecs is not None and len(ctx.field_vecs) and res.education:
        texts = [f"{e.degree} {e.field}".strip() for e in res.education]
        sims = emb.embed(texts) @ ctx.field_vecs.T
        lexical = any(f.lower() in t.lower() for f in jd.education_fields for t in texts)
        field_score = 1.0 if lexical else float(emb.calibrate(sims.max()))
        info["field_match"] = round(field_score, 2)
    return 0.75 * level + 0.25 * field_score, info


# ----------------------------------------------------------------------------- main
def fit_label(score: float) -> str:
    return "Strong fit" if score >= 75 else "Good fit" if score >= 60 else "Partial fit" if score >= 40 else "Weak fit"


def score_candidate(ctx: JobContext, res: ResumeData, text: str, emb: Embedder,
                    verdicts: dict | None = None, mode: str | None = None) -> dict:
    chunks = resume_chunks(res)
    chunk_vecs = emb.embed([c["text"] for c in chunks])

    s_skill, req_cov, pref_cov, skill_details = score_skills(ctx, res, text, emb, verdicts, mode)
    s_sem, sem_overall, sem_cov, resp_details = score_semantic(ctx, chunks, chunk_vecs, emb)
    req_options = [([r.name, *r.alternatives], 2.0 if r.core else 1.0) for r in ctx.jd.required_skills]
    s_exp, exp_info = score_experience(ctx, res, chunks, chunk_vecs, emb, req_options)
    s_edu, edu_info = score_education(ctx, res, emb)

    w = {"skills": settings.w_skills, "semantic": settings.w_semantic,
         "experience": settings.w_experience, "education": settings.w_education}
    comps = {"skills": s_skill, "semantic": s_sem, "experience": s_exp, "education": s_edu}
    if comps["skills"] is None:  # JD without any recognisable skills: redistribute weight
        w["semantic"] += w.pop("skills")
        comps.pop("skills")
    wsum = sum(w.values())
    total = 100 * sum(w[k] * comps[k] for k in comps) / wsum

    breakdown = {k: {"score": round(comps[k], 3), "weight": round(w[k] / wsum, 3),
                     "points": round(100 * w[k] * comps[k] / wsum, 1), "max_points": round(100 * w[k] / wsum, 1)}
                 for k in comps}
    breakdown.setdefault("skills", {})
    breakdown["skills"].update({"required_coverage": req_cov, "preferred_coverage": pref_cov})
    breakdown["semantic"].update({"overall_similarity": round(sem_overall, 3),
                                  "responsibility_coverage": None if sem_cov is None else round(sem_cov, 3)})

    result = {
        "score": round(total, 1),
        "fit": fit_label(total),
        "breakdown": breakdown,
        "skill_details": skill_details,
        "matched_skills": [d["skill"] for d in skill_details if d["status"] == "matched"],
        "related_skills": [d for d in skill_details if d["status"] in ("related", "partial")],
        "missing_skills": [d["skill"] for d in skill_details if d["status"] == "missing" and d["kind"] == "required"],
        "missing_preferred": [d["skill"] for d in skill_details
                              if d["status"] == "missing" and d["kind"] == "preferred"],
        "experience": exp_info,
        "education": edu_info,
        "responsibility_coverage": resp_details,
    }
    result["reasons"] = build_reasons(ctx, result)
    return result


def build_reasons(ctx: JobContext, r: dict) -> list[dict]:
    """Plain-language, evidence-backed reasons for the score."""
    out = []
    b = r["breakdown"]
    req = [d for d in r["skill_details"] if d["kind"] == "required"]
    if req:
        m = sum(d["status"] == "matched" for d in req)
        rel = sum(d["status"] in ("related", "partial") for d in req)
        txt = f"Has {m} of {len(req)} required skills"
        if rel:
            txt += f" (+{rel} partial/related)"
        if r["missing_skills"]:
            txt += f"; missing {', '.join(r['missing_skills'][:5])}"
        out.append({"type": "positive" if m / len(req) >= 0.75 else "negative" if m / len(req) < 0.5 else "neutral",
                    "text": txt + f" → {b['skills']['points']}/{b['skills']['max_points']} pts."})
    pref = [d for d in r["skill_details"] if d["kind"] == "preferred"]
    if pref:
        m = sum(d["status"] == "matched" for d in pref)
        out.append({"type": "positive" if m else "neutral",
                    "text": f"Has {m} of {len(pref)} nice-to-have skills"
                            + (f" ({', '.join(d['skill'] for d in pref if d['status'] == 'matched')})" if m else "") + "."})
    implied = [d for d in r["skill_details"] if d["status"] == "matched" and d["evidence"].startswith(("Implied", "Mentioned"))]
    if implied:
        out.append({"type": "neutral", "text": "Inferred skills (not listed explicitly): "
                    + "; ".join(f"{d['skill']} ← {d['evidence']}" for d in implied[:4]) + "."})

    discarded = [d for d in r["skill_details"] if d.get("source") == "llm_rejected"]
    if discarded:
        out.append({"type": "neutral", "text": f"{len(discarded)} LLM skill claim(s) had a quote that is not in the "
                    "resume, so the rule-based matcher decided them instead: "
                    + ", ".join(d["skill"] for d in discarded[:4]) + "."})
    llm_rows = [d for d in r["skill_details"] if d.get("source") == "llm"]
    if llm_rows:
        out.append({"type": "neutral", "text": f"Skill verdicts: {len(llm_rows)} judged by the LLM with verified "
                    f"resume quotes, {len(r['skill_details']) - len(llm_rows)} by the rule-based taxonomy."})

    e = r["experience"]
    if e["required_years"]:
        ok = e["relevant_years"] >= e["required_years"]
        out.append({"type": "positive" if ok else "negative",
                    "text": f"{e['relevant_years']} years of relevant experience ({e['total_years']} total) vs "
                            f"{e['required_years']:g}+ required → {b['experience']['points']}/{b['experience']['max_points']} pts."})
    else:
        out.append({"type": "neutral", "text": f"{e['relevant_years']} years of relevant experience "
                                                f"({e['total_years']} total); JD states no minimum."})
    weak_roles = [x for x in e["entries"] if x["relevance"] < 0.4 and x["months"] >= 6]
    if weak_roles:
        out.append({"type": "neutral", "text": "Experience counted only partially (less related to this role): "
                    + ", ".join(f"{x['title']} @ {x['company']}" for x in weak_roles[:3]) + "."})

    cov = r["responsibility_coverage"]
    if cov:
        strong = sorted(cov, key=lambda c: -c["strength"])
        top = strong[0]
        out.append({"type": "positive" if top["strength"] >= 0.6 else "neutral",
                    "text": f"Closest work to the JD: “{top['evidence']}” ↔ “{top['responsibility'][:90]}”."})
        weak = [c for c in cov if c["strength"] < 0.3]
        if weak:
            out.append({"type": "negative", "text": f"{len(weak)} of {len(cov)} responsibilities have little "
                        f"supporting evidence, e.g. “{weak[0]['responsibility'][:90]}”."})
    out.append({"type": "neutral", "text": f"Semantic similarity to the JD → {b['semantic']['points']}/"
                                            f"{b['semantic']['max_points']} pts."})

    ed = r["education"]
    if ed["required_level"] != "none":
        ok = EDU_RANK.get(ed["candidate_level"], 0) >= EDU_RANK[ed["required_level"]]
        out.append({"type": "positive" if ok else "negative",
                    "text": f"Education: {ed['candidate_degree'] or 'not found'} "
                            f"({ed['candidate_level']}) vs {ed['required_level']} "
                            f"{'required' if ed['required'] else 'preferred'}."})
    return out
