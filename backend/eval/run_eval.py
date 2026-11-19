"""Generalisation test: rank all 70 sample resumes against each of the 20 sample JDs
(J01-J10 tech, J11-J20 non-tech; both sets built as near-neighbour pairs).

Ground truth (sample_data/labels.json): each resume was written for one JD (relevance 2);
resumes written for neighbouring roles get relevance 1; everything else 0. Ten resumes are
off-domain distractors (role "NONE": nurse, chef, lawyer, ...) and should score Weak (<40) everywhere.

Metrics per JD
  P@3     share of the top-3 that are the JD's own resumes (3 exist per JD)
  MRR     1 / rank of the first own resume
  nDCG@10 graded ranking quality (own = 2, adjacent = 1)
  Order   share of (strong > mid > junior) pairs ordered correctly among own resumes
  P@2     share of the top-2 that are the JD's own strong/mid resumes
  Sep0    lowest own-resume score minus highest UNRELATED (relevance 0) score; > 0 means no
          unrelated resume outranks any of the JD's own resumes (juniors included)
  Margin  lowest own-resume score minus highest other-resume score incl. neighbouring roles
  Dist    highest score of any off-domain distractor for this JD (should be < 40 = Weak)

Usage (from backend/):
  python -m eval.run_eval                  # uses EXTRACTOR / EMBEDDING_PROVIDER from env / .env
  python -m eval.run_eval --show 5         # also print the top-5 table per JD
  python -m eval.run_eval --refresh        # ignore cached extractions
Extractions are cached in eval/.cache/<extractor>/ so Gemini is called only once per file.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app import extraction  # noqa: E402
from app.config import settings  # noqa: E402
from app.embeddings import get_embedder  # noqa: E402
from app import llm_match
from app.matching import prepare_job, prewarm, score_candidate  # noqa: E402
from app.parsing import extract_text  # noqa: E402
from app.schemas import JDData, ResumeData  # noqa: E402

DATA = ROOT / "sample_data"
LEVEL_RANK = {"strong": 3, "mid": 2, "junior": 1}


async def load_all(refresh: bool):
    labels = json.loads((DATA / "labels.json").read_text())
    # one cache folder per extractor+model, so results from different models never mix
    tag = f"gemini-{settings.gemini_model}" if settings.extractor == "gemini" else settings.extractor
    cache = Path(__file__).parent / ".cache" / tag
    cache.mkdir(parents=True, exist_ok=True)
    total, done, t0 = len(labels["jobs"]) + len(labels["resumes"]), 0, time.time()

    async def get(kind, name, path):
        nonlocal done
        cf = cache / f"{name}.json"
        text = extract_text(path.name, path.read_bytes())
        if cf.exists() and not refresh:
            d = json.loads(cf.read_text())
            if d["source"] == settings.extractor:  # ignore fallback results cached by an earlier failed run
                done += 1
                return text, (JDData if kind == "jd" else ResumeData).model_validate(d["data"]), d["source"]
        t = time.time()
        if kind == "jd":
            data, src = await extraction.extract_jd(text)
        else:
            data, src = await extraction.extract_resume(text)
        if src == settings.extractor:  # only cache real results, never rule-based fallbacks
            cf.write_text(json.dumps({"source": src, "data": data.model_dump()}, indent=1))
        done += 1
        print(f"  [{done}/{total}] {name:16} via {src:6} {time.time() - t:5.1f}s  (elapsed {time.time() - t0:.0f}s)",
              flush=True)
        return text, data, src

    print(f"Extracting {total} documents with {settings.extractor} (cached ones are skipped)...", flush=True)
    if settings.extractor == "gemini" and settings.llm_rpm:
        print(f"  pacing: {settings.llm_rpm:g} requests/min (LLM_RPM) -> about "
              f"{total / settings.llm_rpm:.0f} min for an empty cache", flush=True)
    jd_items = list(labels["jobs"].items())
    jd_out = await asyncio.gather(*(get("jd", jid, DATA / "jds" / j["file"]) for jid, j in jd_items))
    jobs = {jid: r for (jid, _), r in zip(jd_items, jd_out)}
    res_items = list(labels["resumes"].items())
    res_out = await asyncio.gather(*(get("res", f, DATA / "resumes" / f) for f, _ in res_items))
    resumes = {f: r for (f, _), r in zip(res_items, res_out)}
    return labels, jobs, resumes


def ndcg(gains: list[int], k: int = 10) -> float:
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains[:k]))
    ideal = sorted(gains, reverse=True)
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal[:k]))
    return dcg / idcg if idcg else 0.0


async def load_verdicts(jobs, resumes) -> dict:
    """LLM skill verdicts for every (JD, resume) pair, cached on disk per JD (one Gemini call judges
    MATCH_BATCH_SIZE resumes). Returns {jid: {filename: {requirement_id: verdict}}}."""
    cache = Path(__file__).parent / ".cache" / f"match-{settings.gemini_model}-{llm_match.PROMPT_VERSION}"
    cache.mkdir(parents=True, exist_ok=True)
    out, todo = {}, []
    for jid, (_, jd, _) in jobs.items():
        cf = cache / f"{jid}.json"
        out[jid] = json.loads(cf.read_text()) if cf.exists() else {}
        missing = [(f, rtext) for f, (rtext, _, _) in resumes.items() if f not in out[jid]]
        if missing:
            todo.append((jid, jd, missing, cf))
    if not todo:
        return out
    n_calls = sum(-(-len(m) // settings.match_batch_size) for _, _, m, _ in todo)
    print(f"LLM skill matching: {sum(len(m) for _, _, m, _ in todo)} (JD, resume) pairs in ~{n_calls} calls "
          f"(cached in {cache.name}/)...", flush=True)
    t0, done = time.time(), 0

    async def one(jid, jd, missing, cf):
        nonlocal done

        def save(chunk_result):
            nonlocal done
            out[jid].update(chunk_result)
            cf.write_text(json.dumps(out[jid], indent=1))
            done += 1
            print(f"  [{done}/{n_calls}] {jid}: judged {len(chunk_result)} resumes (elapsed {time.time() - t0:.0f}s)",
                  flush=True)
        await llm_match.match_batch(jd, missing, on_chunk=save)

    await asyncio.gather(*(one(*t) for t in todo))
    left = sum(1 for jid, (_, _, _) in jobs.items() for f in resumes if f not in out[jid])
    if left:
        print(f"  NOTE: {left} pairs could not be judged by the LLM and are scored with the taxonomy matcher;"
              f" rerun to retry only those.", flush=True)
    return out


def skill_level_eval(all_scores, held, show_errors: bool) -> None:
    """Precision / recall of skill matching against hand labels (sample_data/skill_labels.json)."""
    p = DATA / "skill_labels.json"
    if not p.exists():
        return
    labels = json.loads(p.read_text())["labels"]
    results = {(jid, s[1]): s[4] for jid, scored in all_scores.items() for s in scored}
    stats = {"known": [0, 0, 0, 0], "held-out": [0, 0, 0, 0]}  # tp, fp, fn, tn
    errors, unmapped = [], 0
    for lab in labels:
        r = results.get((lab["jd"], lab["resume"]))
        keys = [k.strip().lower() for k in lab["requirement"].split("|")]
        row = next((d for d in (r or {}).get("skill_details", []) if any(k in d["skill"].lower() for k in keys)), None)
        if row is None:
            unmapped += 1
            continue
        pred = row["credit"] >= 0.5
        st = stats["held-out" if lab["jd"] in held else "known"]
        st[0 if pred and lab["met"] else 1 if pred else 2 if lab["met"] else 3] += 1
        if pred != lab["met"]:
            errors.append(f"  {'FALSE MATCH' if pred else 'MISSED':11} {lab['jd']} {lab['resume']:16} "
                          f"{row['skill'][:34]:34} [{row.get('source', '?')}] {row['evidence'][:90]}")
    print("\nSkill-level matching vs hand labels (credit >= 0.5 counts as matched):")
    for name, (tp, fp, fn, tn) in stats.items():
        n = tp + fp + fn + tn
        if n:
            prec = tp / (tp + fp) if tp + fp else float("nan")
            rec = tp / (tp + fn) if tp + fn else float("nan")
            print(f"  {name:9} n={n:3}  precision {prec:.2f}  recall {rec:.2f}  accuracy {(tp + tn) / n:.2f}"
                  f"   (false matches {fp}, missed {fn})")
    if unmapped:
        print(f"  ({unmapped} labels could not be mapped to an extracted requirement)")
    if errors and show_errors:
        print("\n".join(errors))
    elif errors:
        print(f"  {len(errors)} errors; run with --errors to list them")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--show", type=int, default=0, help="print top-N per JD")
    ap.add_argument("--errors", action="store_true", help="list every skill-level matching error")
    args = ap.parse_args()
    logging.basicConfig(level=logging.WARNING, format="  %(levelname)s %(name)s: %(message)s")
    logging.getLogger("atsscore.embeddings").setLevel(logging.INFO)

    t0 = time.time()
    labels, jobs, resumes = asyncio.run(load_all(args.refresh))
    srcs = {s for *_, s in list(jobs.values()) + list(resumes.values())}
    emb = get_embedder()
    print(f"extractor={settings.extractor} (used: {','.join(sorted(srcs))})  embeddings={emb.provider}  "
          f"skill_matcher={settings.skill_matcher}  "
          f"weights=S{settings.w_skills}/Sem{settings.w_semantic}/E{settings.w_experience}/Ed{settings.w_education}")

    model = settings.gemini_embed_model if emb.provider == "gemini" else settings.local_embed_model
    emb_cache = Path(__file__).parent / ".cache" / f"emb-{emb.provider}-{model.replace('/', '_')}.npz"
    n = emb.load(emb_cache)
    emb.autosave_path = emb_cache
    print(f"Embedding resumes in batches ({n} embeddings cached on disk)...", flush=True)
    prewarm(emb, [rd for _, rd, _ in resumes.values()])
    emb.save(emb_cache)
    verdicts = asyncio.run(load_verdicts(jobs, resumes)) if settings.skill_matcher == "llm" else {}
    rows, all_scores = [], {}
    for jid, (jtext, jd, _) in jobs.items():
        print(f"  scoring {jid}", flush=True)
        ctx = prepare_job(jd, emb)
        scored = []
        for f, (rtext, rd, _) in resumes.items():
            r = score_candidate(ctx, rd, rtext, emb, verdicts=verdicts.get(jid, {}).get(f))
            lab = labels["resumes"][f]
            rel = 2 if lab["role"] == jid else 1 if (lab["role"] in labels["adjacent"][jid]
                                                      or jid in lab.get("adjacent", [])) else 0
            scored.append((r["score"], f, lab, rel, r))
        scored.sort(key=lambda x: -x[0])
        all_scores[jid] = scored
        gains = [s[3] for s in scored]
        own = [s for s in scored if s[3] == 2]
        p3 = sum(1 for s in scored[:3] if s[3] == 2) / min(3, len(own))
        first = next(i for i, s in enumerate(scored) if s[3] == 2) + 1
        pairs = [(a, b) for a in own for b in own if LEVEL_RANK[a[2]["level"]] > LEVEL_RANK[b[2]["level"]]]
        order = sum(a[0] > b[0] for a, b in pairs) / len(pairs) if pairs else 1.0
        margin = min(s[0] for s in own) - max(s[0] for s in scored if s[3] != 2)
        sep0 = min(s[0] for s in own) - max(s[0] for s in scored if s[3] == 0)
        p2 = sum(1 for s in scored[:2] if s[3] == 2 and s[2]["level"] != "junior") / 2
        dist = [s[0] for s in scored if s[2]["role"] == "NONE" and s[3] == 0]
        rows.append((jid, labels["jobs"][jid]["title"], p3, 1 / first, ndcg(gains), order, margin,
                     [s[0] for s in own], p2, sep0, max(dist) if dist else float("nan"), dist))

    emb.save(emb_cache)
    print(f"\n{'JD':4} {'Title':36} {'P@2':>5} {'P@3':>5} {'MRR':>5} {'nDCG':>5} {'Order':>5} {'Sep0':>6} {'Margin':>7} {'Dist':>5}  own (strong/mid/junior)")
    for jid, title, p3, mrr, nd, order, margin, own, p2, sep0, dmax, _ in rows:
        print(f"{jid:4} {title[:36]:36} {p2:5.2f} {p3:5.2f} {mrr:5.2f} {nd:5.2f} {order:5.2f} {sep0:6.1f} {margin:7.1f} {dmax:5.1f}  "
              + " / ".join(f"{x:.0f}" for x in own))

    def summary(label, rs):
        n = len(rs)
        if not n:
            return
        mean = lambda i: sum(r[i] for r in rs) / n
        print(f"{label:41} {mean(8):5.2f} {mean(2):5.2f} {mean(3):5.2f} {mean(4):5.2f} {mean(5):5.2f} {mean(9):6.1f} "
              f"{mean(6):7.1f} {max(r[10] for r in rs):5.1f}")
    held = {j for j, x in labels["jobs"].items() if x.get("heldout")}
    summary("MEAN tech (J01-J10)", [r for r in rows if int(r[0][1:]) <= 10])
    summary("MEAN non-tech (J11-J20)", [r for r in rows if 10 < int(r[0][1:]) and r[0] not in held])
    summary("MEAN held-out domains", [r for r in rows if r[0] in held])
    summary("MEAN all", rows)
    n = len(rows)
    print(f"JDs where no unrelated resume beats an own resume: {sum(r[9] > 0 for r in rows)}/{n}")
    dists = [d for r in rows for d in r[11]]
    if dists:
        print(f"Distractors scored Weak (<40): {sum(d < 40 for d in dists)}/{len(dists)} distractor x JD pairs "
              f"(max {max(dists):.1f}, median {sorted(dists)[len(dists) // 2]:.1f})")
    top1 = sum(1 for jid in all_scores if all_scores[jid][0][3] == 2)
    print(f"Top-1 correct: {top1}/{n}   time: {time.time()-t0:.1f}s")
    skill_level_eval(all_scores, held, args.errors)

    if args.show:
        for jid, scored in all_scores.items():
            print(f"\n== {jid} {labels['jobs'][jid]['title']}")
            for sc, f, lab, rel, r in scored[:args.show]:
                tag = "OWN" if rel == 2 else "adj" if rel == 1 else "---"
                b = r["breakdown"]
                print(f"  {sc:5.1f} {tag} {f:16} {lab['role']}-{lab['level']:6} {lab['name']:18} "
                      f"skills={b['skills']['score']:.2f} sem={b['semantic']['score']:.2f} "
                      f"exp={b['experience']['score']:.2f} edu={b['education']['score']:.2f}")


if __name__ == "__main__":
    main()
