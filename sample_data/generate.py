"""Render the synthetic JDs and resumes to files and write ground-truth labels.

Usage:  python sample_data/generate.py
Needs:  reportlab, python-docx
"""
import json
from pathlib import Path

from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from jds_spec import ADJACENT, JDS
from resumes_spec import RESUMES

HERE = Path(__file__).parent
JD_DIR, RES_DIR = HERE / "jds", HERE / "resumes"


def resume_sections(r):
    """Return list of (heading, [lines]) for a resume spec."""
    secs = [("", [r["name"], f'{r["email"]} | {r["phone"]} | {r["location"]}']),
            ("Summary", [r["summary"]])]
    if r["skills"]:
        secs.append(("Skills", [", ".join(r["skills"])]))
    exp = []
    for title, company, dates, bullets in r["experience"]:
        exp.append(f"<b>{title}</b> — {company} ({dates})")
        exp += [f"- {b}" for b in bullets]
    secs.append(("Experience", exp))
    if r["projects"]:
        secs.append(("Projects", [f"<b>{n}</b>: {d}" for n, d in r["projects"]]))
    secs.append(("Education", [f"{d}, {inst} ({yrs})" for d, inst, yrs in r["education"]]))
    if r["certs"]:
        secs.append(("Certifications", r["certs"]))
    return secs


def write_pdf(path, sections):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    story = []
    for head, lines in sections:
        if head:
            story += [Spacer(1, 6), Paragraph(head.upper(), styles["Heading3"])]
            story += [Paragraph(l, styles["BodyText"]) for l in lines]
        else:  # header block
            story.append(Paragraph(lines[0], styles["Title"]))
            story += [Paragraph(l, styles["BodyText"]) for l in lines[1:]]
    doc.build(story)


def write_docx(path, sections):
    doc = Document()
    doc.styles["Normal"].font.size = Pt(10.5)
    for head, lines in sections:
        if head:
            doc.add_heading(head.upper(), level=2)
        else:
            doc.add_heading(lines[0], level=0)
            lines = lines[1:]
        for l in lines:
            p = doc.add_paragraph()
            # minimal <b>…</b> support
            parts = l.replace("</b>", "<b>").split("<b>")
            for i, part in enumerate(parts):
                if part:
                    p.add_run(part).bold = (i % 2 == 1)
    doc.save(str(path))


def main():
    JD_DIR.mkdir(exist_ok=True)
    RES_DIR.mkdir(exist_ok=True)

    jobs = {}
    for jid, jd in JDS.items():
        (JD_DIR / jd["file"]).write_text(jd["text"], encoding="utf-8")
        jobs[jid] = {"file": jd["file"], "title": jd["text"].splitlines()[0], "heldout": jd.get("heldout", False)}
    # Two JDs also as documents, to demo JD file upload.
    write_pdf(JD_DIR / "J03_data_scientist.pdf",
              [("", [JDS["J03"]["text"].splitlines()[0]])] +
              [("Description", [l for l in JDS["J03"]["text"].splitlines()[1:] if l.strip()])])
    write_docx(JD_DIR / "J07_fullstack_mern_developer.docx",
               [("", [JDS["J07"]["text"].splitlines()[0]])] +
               [("Description", [l for l in JDS["J07"]["text"].splitlines()[1:] if l.strip()])])

    labels = {}
    for i, r in enumerate(RESUMES, 1):
        fname = f"resume_{i:02d}.{r['fmt']}"
        secs = resume_sections(r)
        (write_pdf if r["fmt"] == "pdf" else write_docx)(RES_DIR / fname, secs)
        labels[fname] = {"id": r["id"], "role": r["role"], "level": r["level"], "name": r["name"],
                         "adjacent": r.get("adjacent", [])}

    (HERE / "labels.json").write_text(json.dumps(
        {"jobs": jobs, "adjacent": ADJACENT, "resumes": labels}, indent=2), encoding="utf-8")
    print(f"Wrote {len(jobs)} JDs and {len(labels)} resumes")


if __name__ == "__main__":
    main()
