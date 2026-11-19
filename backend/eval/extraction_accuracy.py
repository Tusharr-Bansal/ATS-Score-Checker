"""Resume-parsing accuracy: compares cached extractions against the ground truth the
synthetic resumes were generated from (sample_data/resumes_spec.py). No API calls; it
reads the caches written by run_eval (eval/.cache/<extractor>/), so run that first.

Fields checked per resume
  name, email, phone   exact match (case-insensitive; phone compared by digits)
  roles                same number of roles as the source resume
  role dates           a role whose start AND end month both match the source (per role)
  total years          |extracted - true| <= 0.1 years, both computed from the dates today
  degree level         highest level (diploma/bachelor/master/phd) matches
  institutions         each source institution found among the extracted ones
  skills recall        share of the resume's listed skills that appear in the stored skill
                       list (only resumes with a Skills section), two ways:
                       as written - the specific name survives ("Darwinbox", "CloudWatch")
                       canonical  - after the alias table, which maps tools to their category
                                    ("Darwinbox" -> "HRMS"); this is the form the app stores.
                       The LLM matcher reads the raw resume text, so the collapse does not hide
                       evidence from it; the stored list feeds the skill chips, the summary
                       embedding and the taxonomy fallback.

Caveat: the synthetic resumes share one clean layout, so these numbers are an upper bound.
Real resumes (two columns, right-aligned dates, tables) are harder, mostly for the rules parser.

Usage (from backend/):  python -m eval.extraction_accuracy [--errors]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "sample_data"))

from app.dates import merged_months, parse_point  # noqa: E402  (pure date arithmetic, no API)
from resumes_spec import RESUMES  # noqa: E402
from app.skills import normalize as canon  # noqa: E402  (alias table, e.g. "k8s" -> "Kubernetes")

CACHE = Path(__file__).parent / ".cache"
LEVEL = {"none": 0, "diploma": 1, "bachelor": 2, "master": 3, "phd": 4}


def true_level(degree: str) -> str:
    d = degree.lower()
    if d.startswith(("ph.d", "phd", "doctor")):
        return "phd"
    if d.startswith(("m.", "mba", "pgdm", "master")):
        return "master"
    if d.startswith(("diploma", "dmlt")):
        return "diploma"
    return "bachelor"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9+#]", "", (s or "").lower())


def ym(s: str | None):
    p = parse_point(s) if s else None
    if s and s.strip().lower() == "present":
        return "present"
    return p


def true_dates(rng: str):
    a, b = [x.strip() for x in rng.split(" - ")]
    return ym(a), ym(b)


def skill_found(skill: str, extracted: list[str], use_alias: bool) -> bool:
    # "Hibernate/JPA" counts if any part is found; matching is loose (substring either way).
    # use_alias: both sides go through the app's alias table, so "Amazon Web Services" == "AWS"
    # but also "Darwinbox" == "HRMS" (the table maps specific tools to their category).
    raw = [skill] + re.split(r"[/(),&]", skill)
    f = (lambda x: (x, canon(x.strip()))) if use_alias else (lambda x: (x,))
    parts = {norm(y) for p in raw if p.strip() for y in f(p)} - {""}
    ex = {norm(y) for e in extracted for y in f(e)} - {""}
    return any(p == e or (len(p) > 2 and (p in e or e in p)) for p in parts for e in ex)


def evaluate(tag: str, show_errors: bool):
    folder = CACHE / tag
    if not folder.exists():
        return None
    by_id = {r["id"]: r for r in RESUMES}
    labels = json.loads((ROOT / "sample_data" / "labels.json").read_text())["resumes"]
    hits = {k: [0, 0] for k in ["name", "email", "phone", "roles", "role dates", "total years",
                                "degree level", "institutions", "skills (as written)",
                                "skills (canonical)"]}
    errors = []

    def add(field, ok, n=1, rid="", detail=""):
        hits[field][0] += ok
        hits[field][1] += n
        if ok < n and detail:
            errors.append(f"{rid} {field}: {detail}")

    for fname, lab in labels.items():
        cf = folder / f"{fname}.json"
        if not cf.exists():
            continue
        t, d = by_id[lab["id"]], json.loads(cf.read_text())["data"]
        rid = t["id"]
        add("name", norm(d["name"]) == norm(t["name"]), rid=rid, detail=f"{d['name']!r} vs {t['name']!r}")
        add("email", d["email"].strip().lower() == t["email"], rid=rid, detail=f"{d['email']!r}")
        add("phone", re.sub(r"\D", "", d["phone"]) == re.sub(r"\D", "", t["phone"]), rid=rid,
            detail=f"{d['phone']!r}")
        add("roles", len(d["experience"]) == len(t["experience"]), rid=rid,
            detail=f"{len(d['experience'])} extracted vs {len(t['experience'])}")
        got = {(ym(x["start"]), ym(x["end"] or "present")) for x in d["experience"]}
        want = [true_dates(e[2]) for e in t["experience"]]
        ok = sum(w in got for w in want)
        add("role dates", ok, len(want), rid=rid, detail=f"{ok}/{len(want)} roles have both dates right")
        true_yrs = merged_months([tuple(x.strip() for x in e[2].replace("Present", "present").split(" - "))
                                  for e in t["experience"]]) / 12
        ext_yrs = merged_months([(x["start"], x["end"]) for x in d["experience"]]) / 12
        add("total years", abs(ext_yrs - true_yrs) <= 0.1, rid=rid,
            detail=f"{ext_yrs:.1f} vs {true_yrs:.1f}")
        tl = max((true_level(e[0]) for e in t["education"]), key=LEVEL.get)
        el = max((x.get("level") or "none" for x in d["education"]), key=LEVEL.get, default="none")
        add("degree level", el == tl, rid=rid, detail=f"{el} vs {tl}")
        insts = [norm(x.get("institution")) for x in d["education"]]
        ok = sum(any(norm(e[1]) and (norm(e[1]) in i or (i and i in norm(e[1]))) for i in insts)
                 for e in t["education"])
        add("institutions", ok, len(t["education"]), rid=rid, detail=f"{ok}/{len(t['education'])}")
        if t["skills"]:
            for field, alias in (("skills (as written)", False), ("skills (canonical)", True)):
                missed = [s for s in t["skills"] if not skill_found(s, d["skills"], alias)]
                add(field, len(t["skills"]) - len(missed), len(t["skills"]), rid=rid,
                    detail=f"missed {missed}")
    if show_errors:
        for e in errors:
            print(f"    {e}")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--errors", action="store_true", help="list every field that was wrong")
    args = ap.parse_args()
    tags = sorted(p.name for p in CACHE.iterdir() if p.is_dir() and (p.name == "rules" or p.name.startswith("gemini-")))
    results = {}
    for tag in tags:
        if args.errors:
            print(f"\n  errors for {tag}:")
        h = evaluate(tag, args.errors)
        if h and h["name"][1]:
            results[tag] = h
    if not results:
        print("No cached extractions found; run `python -m eval.run_eval` first.")
        return
    fields = list(next(iter(results.values())))
    print(f"\nResume parsing accuracy vs ground truth ({len(RESUMES)} synthetic resumes)")
    print(f"{'Field':20}" + "".join(f"{t:>32}" for t in results))
    for f in fields:
        print(f"{f:20}" + "".join(
            f"{(f'{h[f][0] / h[f][1]:.1%} ({h[f][0]}/{h[f][1]})' if h[f][1] else '-'):>32}"
            for h in results.values()))


if __name__ == "__main__":
    main()
