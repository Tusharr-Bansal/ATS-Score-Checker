"""Date parsing and experience-duration arithmetic."""
from __future__ import annotations

import re
from datetime import date

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
PRESENT = {"present", "current", "now", "till date", "to date", "ongoing", "today"}

_MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
_POINT = rf"(?:{_MON}\s*'?\d{{2,4}}|\d{{1,2}}[/.-]\d{{4}}|\d{{4}}[/.-]\d{{1,2}}|\d{{4}})"
DATE_RANGE = re.compile(
    rf"(?P<start>{_POINT})\s*(?:-|–|—|to|until)\s*(?P<end>{_POINT}|present|current|now|till date|to date|ongoing)",
    re.I)


def today_ym() -> tuple[int, int]:
    t = date.today()
    return t.year, t.month


def parse_point(s: str | None) -> tuple[int, int] | None:
    """'Mar 2021' | '03/2021' | '2021-03' | '2021' | 'present' -> (year, month)."""
    if not s:
        return None
    s = s.strip().lower()
    if s in PRESENT:
        return today_ym()
    m = re.match(rf"^({_MON})\s*'?(\d{{2,4}})$", s)
    if m:
        mon = MONTHS.get(m.group(1)[:3])
        yr = int(m.group(2))
        yr = yr + 2000 if yr < 100 else yr
        return (yr, mon) if mon else None
    m = re.match(r"^(\d{1,2})[/.-](\d{4})$", s)
    if m:
        return int(m.group(2)), max(1, min(12, int(m.group(1))))
    m = re.match(r"^(\d{4})[/.-](\d{1,2})$", s)
    if m:
        return int(m.group(1)), max(1, min(12, int(m.group(2))))
    m = re.match(r"^(\d{4})$", s)
    if m:
        return int(m.group(1)), 1
    return None


def to_iso(p: tuple[int, int] | None) -> str | None:
    return f"{p[0]:04d}-{p[1]:02d}" if p else None


def months_between(start: str | None, end: str | None) -> int:
    a = parse_point(start)
    b = parse_point(end) if end else today_ym()
    if not a or not b:
        return 0
    return max(0, (b[0] - a[0]) * 12 + (b[1] - a[1]) + 1)


def merged_months(ranges: list[tuple[str | None, str | None]]) -> int:
    """Total months covered by possibly-overlapping (start, end) ranges."""
    iv = []
    for s, e in ranges:
        a = parse_point(s)
        b = parse_point(e) if e else today_ym()
        if a and b:
            x, y = a[0] * 12 + a[1], b[0] * 12 + b[1]
            if y >= x:
                iv.append((x, y))
    iv.sort()
    total, cur = 0, None
    for x, y in iv:
        if cur and x <= cur[1] + 1:
            cur = (cur[0], max(cur[1], y))
        else:
            if cur:
                total += cur[1] - cur[0] + 1
            cur = (x, y)
    if cur:
        total += cur[1] - cur[0] + 1
    return total
