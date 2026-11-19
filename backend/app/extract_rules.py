"""Rule-based extraction: works offline with no API key, and is the fallback if Gemini fails.

Heuristics: section headings, regexes for contact details, dates and degrees, and the
skill taxonomy for skill detection.
"""
from __future__ import annotations

import re

from . import skills as sk
from .dates import DATE_RANGE, parse_point, to_iso
from .schemas import Education, Experience, JDData, Project, ResumeData, SkillReq

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)\d{3,5}[\s-]?\d{3,5}")
YEARS = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)", re.I)

RESUME_HEADINGS = {
    "summary": ["summary", "profile", "professional summary", "about me", "objective", "career objective"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "technologies", "tech stack",
               "skills & tools", "competencies"],
    "experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "internships", "experience & internships"],
    "education": ["education", "academic background", "academics", "qualifications", "educational qualifications"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications", "courses"],
}
JD_HEADINGS = {
    "responsibilities": ["responsibilities", "what you will do", "what you'll do", "key responsibilities",
                         "the role", "about the role", "duties", "your role", "role overview"],
    "required": ["requirements", "what we need", "must have", "must-have", "required skills",
                 "qualifications", "what you need", "what you'll need", "minimum qualifications",
                 "who you are", "required"],
    "preferred": ["nice to have", "good to have", "preferred", "bonus", "preferred qualifications",
                  "nice-to-have", "plus", "desirable"],
}

DEGREES = [
    ("phd", r"\b(ph\.?\s?d|doctor(?:ate)?)(?!\w)"),
    ("master", r"\b(m\.?\s?tech|m\.?\s?sc|m\.e\.|m\.s\.|ms|master'?s?|mba|mca|m\.?\s?com|m\.a\.)(?!\w)"),
    ("bachelor", r"\b(b\.?\s?tech|b\.e\.?|be|b\.?\s?sc|b\.s\.|bachelor'?s?|bca|bba|b\.?\s?com|b\.a\.)(?!\w)"),
    ("diploma", r"\b(diploma)(?!\w)"),
]


def degree_level(text: str) -> str:
    t = text.lower()
    for level, pat in DEGREES:
        if re.search(pat, t):
            return level
    return "none"


def _sections(text: str, headings: dict[str, list[str]]) -> dict[str, list[str]]:
    lookup = {h: key for key, hs in headings.items() for h in hs}
    out: dict[str, list[str]] = {"_header": []}
    cur = "_header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = re.sub(r"[^a-z&' -]", "", line.lower()).strip()
        if len(line) <= 40 and key in lookup:
            cur = lookup[key]
            out.setdefault(cur, [])
            continue
        out.setdefault(cur, []).append(line)
    return out


def split_top_level(s: str, seps: str = r",|;|\band\b|\|") -> list[str]:
    """Split on separators that are not inside parentheses."""
    out, buf, depth = [], "", 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if depth == 0:
            m = re.match(seps, s[i:])
            if m and m.group(0):
                out.append(buf)
                buf = ""
                i += len(m.group(0))
                continue
        buf += ch
        i += 1
    out.append(buf)
    return [p.strip() for p in out if p.strip()]


def _strip_bullet(line: str) -> str:
    return re.sub(r"^[\-•*·▪◦●–]\s*", "", line).strip()


# ----------------------------------------------------------------------------- resume
def extract_resume(text: str) -> ResumeData:
    secs = _sections(text, RESUME_HEADINGS)
    header = secs.get("_header", [])
    email = (EMAIL.search(text) or [None])[0] if EMAIL.search(text) else ""
    phone_m = PHONE.search("\n".join(header[:5])) or PHONE.search(text)
    phone = phone_m.group(0).strip() if phone_m else ""

    name = ""
    for line in header[:4]:
        if not EMAIL.search(line) and not re.search(r"\d{3}", line) and 1 <= len(line.split()) <= 5:
            name = line.strip()
            break
    location = ""
    for line in header[:5]:
        for part in re.split(r"\s*[|•]\s*", line):
            if part and not EMAIL.search(part) and not PHONE.fullmatch(part.strip()) and part != name \
                    and not re.search(r"\d{4,}", part) and len(part) < 40:
                location = part.strip()
        if location:
            break

    # skills: explicit section + anything the taxonomy finds anywhere in the text
    listed = []
    for line in secs.get("skills", []):
        listed += split_top_level(_strip_bullet(line), r",|;|\||•")
    skills = sk.normalize_list(listed + sk.scan_text(text))

    # experience: a line containing a date range starts a new entry
    exps: list[Experience] = []
    for line in secs.get("experience", []):
        m = DATE_RANGE.search(line)
        if m:
            head = (line[:m.start()] + line[m.end():]).strip(" ()|,–—-")
            head = re.sub(r"\(\s*\)", "", head).strip(" ()|,")
            parts = re.split(r"\s+[—–|@]\s+|\s+-\s+|\s+at\s+|,\s+", head, maxsplit=1)
            title = parts[0].strip(" ()") if parts else head
            company = parts[1].strip(" ()") if len(parts) > 1 else ""
            exps.append(Experience(title=title, company=company,
                                   start=to_iso(parse_point(m.group("start"))),
                                   end="present" if m.group("end").lower() in
                                       {"present", "current", "now", "till date", "to date", "ongoing"}
                                   else to_iso(parse_point(m.group("end"))),
                                   description=""))
        elif exps:
            exps[-1].description = (exps[-1].description + "\n" + _strip_bullet(line)).strip()

    edus: list[Education] = []
    for line in secs.get("education", []):
        level = degree_level(line)
        if level == "none":
            continue
        yrs = re.findall(r"(?:19|20)\d{2}", line)
        parts = [p.strip() for p in re.split(r",\s*|\s+[—–|]\s+", re.sub(r"\(.*?\)", "", line)) if p.strip()]
        degree = parts[0] if parts else line
        field = degree.split(" in ", 1)[1] if " in " in degree else ""
        edus.append(Education(degree=degree, field=field, institution=", ".join(parts[1:]),
                              end_year=int(yrs[-1]) if yrs else None, level=level))

    projects = []
    for line in secs.get("projects", []):
        l = _strip_bullet(line)
        if ":" in l:
            n, d = l.split(":", 1)
            projects.append(Project(name=n.strip(), description=d.strip()))
        elif projects:
            projects[-1].description += " " + l
        else:
            projects.append(Project(name=l[:60], description=l))

    return ResumeData(
        name=name, email=email or "", phone=phone, location=location,
        summary=" ".join(secs.get("summary", []))[:600],
        skills=skills, experience=exps, education=edus, projects=projects,
        certifications=[_strip_bullet(l) for l in secs.get("certifications", [])],
    )


# ----------------------------------------------------------------------------- JD
def _skill_reqs(lines: list[str]) -> list[SkillReq]:
    reqs: list[SkillReq] = []
    seen: set[str] = set()
    for line in lines:
        # "Python and SQL" -> two requirements; "Snowflake, BigQuery or Redshift" inside one
        # segment, or "PostgreSQL or MySQL" -> one requirement with alternatives.
        for seg in split_top_level(_strip_bullet(line)):
            found = [s for s in sk.scan_text(seg) if s.lower() not in seen]
            if not found:
                continue
            if len(found) >= 2 and re.search(r"\bor\b|/|\(", seg):
                found.sort(key=lambda s: _first_pos(seg, s))
                reqs.append(SkillReq(name=found[0], alternatives=found[1:]))
            else:
                reqs += [SkillReq(name=f) for f in found]
            seen |= {f.lower() for f in found}
    return reqs


def _first_pos(line: str, canon: str) -> int:
    best = len(line)
    for term in [canon] + sk.TAXONOMY.get(canon, ([], []))[0]:
        i = line.lower().find(term.lower())
        if i >= 0:
            best = min(best, i)
    return best


def extract_jd(text: str) -> JDData:
    secs = _sections(text, JD_HEADINGS)
    lines = [l for l in text.splitlines() if l.strip()]
    title = lines[0].strip() if lines else ""

    req_lines = secs.get("required") or [l for k, v in secs.items() if k != "preferred" for l in v]
    pref_lines = secs.get("preferred", [])
    required = _skill_reqs(req_lines)
    req_names = {n.lower() for r in required for n in [r.name, *r.alternatives]}
    preferred = [p for p in _skill_reqs(pref_lines) if p.name.lower() not in req_names]

    min_years = None
    for l in req_lines + lines:
        m = YEARS.search(l)
        if m:
            min_years = float(m.group(1))
            break

    edu_level, edu_required, fields = "none", False, []
    for l in req_lines + pref_lines:
        lvl = degree_level(l)
        if lvl != "none" and ("degree" in l.lower() or lvl in {"bachelor", "master", "phd"}):
            edu_level = lvl
            edu_required = l in req_lines and "prefer" not in l.lower() and "equivalent" not in l.lower()
            m = re.search(r"\bin\s+(.+)", l)
            if m:
                fields = [f.strip(" .()") for f in re.split(r",|\bor\b|/|\(", m.group(1))
                          if f.strip(" .") and "related" not in f and "equivalent" not in f
                          and "another" not in f]
            break

    resp = [_strip_bullet(l) for l in secs.get("responsibilities", []) if len(l) > 15]
    # if no explicit section, take bullet-looking lines outside requirement sections
    if not resp:
        resp = [_strip_bullet(l) for l in secs.get("_header", []) if l.lstrip().startswith(("-", "•", "*"))]
    summary = " ".join(l for l in secs.get("_header", [])[1:4] if not l.lstrip().startswith(("-", "•")))
    return JDData(title=title, summary=summary[:400], required_skills=required, preferred_skills=preferred,
                  min_years=min_years, education_level=edu_level, education_required=edu_required,
                  education_fields=fields, responsibilities=resp)
