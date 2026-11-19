"""Turn uploaded PDF / DOCX / TXT files into clean plain text."""
from __future__ import annotations

import io
import re

import pdfplumber
from docx import Document

SUPPORTED = {".pdf", ".docx", ".txt"}


class ParseError(Exception):
    pass


def _clean(text: str) -> str:
    text = re.sub(r"\(cid:\d+\)", "•", text)          # unmapped PDF glyphs (usually bullets)
    text = text.replace(" ", " ").replace("​", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)        # de-hyphenate line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _pdf(data: bytes) -> str:
    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for p in pdf.pages:
            pages.append(p.extract_text(x_tolerance=1.5, y_tolerance=3) or "")
    return "\n".join(pages)


def _docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:  # many resume templates use tables for layout
        for row in table.rows:
            cells, seen = [], set()
            for c in row.cells:
                t = c.text.strip()
                if t and t not in seen:  # merged cells repeat their text
                    seen.add(t)
                    cells.append(t)
            if cells:
                lines.append(" | ".join(cells))
    return "\n".join(lines)


def extract_text(filename: str, data: bytes) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED:
        raise ParseError(f"Unsupported file type '{ext or filename}'. Use PDF, DOCX or TXT.")
    try:
        if ext == ".pdf":
            raw = _pdf(data)
        elif ext == ".docx":
            raw = _docx(data)
        else:
            raw = data.decode("utf-8", errors="ignore")
    except Exception as e:  # corrupted / encrypted files
        raise ParseError(f"Could not read {filename}: {e}") from e
    text = _clean(raw)
    if len(text) < 30:
        raise ParseError(f"No extractable text in {filename} (scanned image PDF?).")
    return text
