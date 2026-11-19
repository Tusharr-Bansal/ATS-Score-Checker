"""Gemini-based structured extraction (JSON mode with a Pydantic response schema)."""
from __future__ import annotations

import asyncio
import logging
import random
import re
import time

from pydantic import BaseModel

from .config import settings
from .schemas import JDData, ResumeData

log = logging.getLogger("checkres.llm")
_client = None
_sem: asyncio.Semaphore | None = None


def available() -> bool:
    return bool(settings.gemini_api_key)


def client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        # per-request timeout (ms) so a hung call is retried instead of blocking forever
        # SDK-internal retries are disabled (attempts=1): retries and pacing are handled below,
        # otherwise the SDK silently retries 429s and requests pile up against the quota.
        _client = genai.Client(api_key=settings.gemini_api_key,
                               http_options=types.HttpOptions(timeout=settings.llm_timeout_ms,
                                                              retry_options=types.HttpRetryOptions(attempts=1)))
    return _client


class _RateLimiter:
    """Spaces request starts at least 60/rpm seconds apart (Gemini free tier: ~5 requests/min/model)."""

    def __init__(self, rpm: float):
        self.interval = 60.0 / rpm if rpm > 0 else 0.0
        self._next = 0.0
        self._lock: asyncio.Lock | None = None

    async def wait(self) -> None:
        if not self.interval:
            return
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            now = time.monotonic()
            if self._next > now:
                await asyncio.sleep(self._next - now)
            self._next = max(now, self._next) + self.interval


_limiter = _RateLimiter(settings.llm_rpm)


def _retry_delay(msg: str, fallback: float) -> float:
    """Server-suggested wait ('Please retry in 31.5s', '...in 750ms', retryDelay: '31s'), else fallback.
    Waits over 5 minutes mean a daily quota is exhausted: raise instead of sleeping for hours."""
    m = re.search(r"retry in (\d+(?:\.\d+)?)\s*(ms|s)\b", msg) or \
        re.search(r"retryDelay'?\"?:\s*'?\"?(\d+(?:\.\d+)?)(ms|s)", msg)
    if not m:
        return fallback
    secs = float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)
    if secs > 300:
        raise RuntimeError(f"Gemini quota exhausted (server asks to wait {secs / 3600:.1f} h): {msg[:300]}")
    return secs + 1.0


def _semaphore() -> asyncio.Semaphore:
    global _sem
    if _sem is None:
        _sem = asyncio.Semaphore(settings.llm_concurrency)
    return _sem


JD_PROMPT = """You are an expert technical recruiter. Extract the hiring requirements from the job description below.

Rules:
- required_skills: only must-have skills from the requirements. preferred_skills: nice-to-have / preferred / bonus items.
- Each skill must be atomic: split "Docker and Kubernetes" into two items. Use standard names
  (e.g. "PostgreSQL", "Kubernetes", "CI/CD", "REST APIs", "Machine Learning", "Statistics").
- When the JD offers alternatives ("PostgreSQL or MySQL", "Power BI or Tableau", "FastAPI or Django",
  "Snowflake, BigQuery or Redshift"), output ONE item: name = the first option, alternatives = the others.
- Broad competencies that are explicitly required (e.g. "Microservices", "ETL", "Data Warehousing",
  "Statistics", "Model Deployment") are skills too.
- core = true for the 2-4 required skills that define the role (the ones in the job title or that the
  whole JD revolves around, e.g. "Java" + "Spring Boot" for a Java backend role); false for generic ones
  like Git, Docker or REST APIs unless the role is about them.
- Do not invent anything that is not in the text.
- min_years: the minimum years of experience required (number), null if not stated.
- education_level: minimum degree mentioned; education_required = false if it says preferred / or equivalent experience.
- responsibilities: the key duties, one short sentence each.

JOB DESCRIPTION:
\"\"\"
{text}
\"\"\""""

RESUME_PROMPT = """You are an expert resume parser. Extract the candidate's information from the resume below.

Rules:
- skills: EVERY technical skill, language, framework, tool, platform and method mentioned anywhere
  (skills section, experience bullets, projects, certifications). Atomic items, standard names, no duplicates.
- experience: one item per role (include internships). Dates as "YYYY-MM" ("YYYY-01" if only the year
  is given); end = "present" for a current role. description = the role's bullet points, one per line (newline-separated).
- education: level mapping: B.Tech/B.E./B.Sc./BCA/BBA/B.Com/B.A. -> bachelor; M.Tech/M.Sc./M.E./MS/MBA/MCA -> master;
  PhD -> phd; Diploma -> diploma. field = subject (e.g. "Computer Science").
- Copy facts only; never guess missing values (leave them empty).

RESUME:
\"\"\"
{text}
\"\"\""""


async def _generate(prompt: str, schema: type[BaseModel]) -> BaseModel:
    from google.genai import types

    cfg = types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema,
                                      temperature=0.0)
    delay = 4.0
    attempts = 6
    for attempt in range(attempts):
        try:
            async with _semaphore():
                await _limiter.wait()
                resp = await client().aio.models.generate_content(
                    model=settings.gemini_model, contents=prompt, config=cfg)
            return schema.model_validate_json(resp.text)
        except Exception as e:  # rate limits (429), 5xx, occasional invalid JSON
            msg = str(e)
            retryable = any(k in msg for k in ("429", "RESOURCE_EXHAUSTED", "500", "503", "504", "UNAVAILABLE",
                                               "DEADLINE_EXCEEDED", "INTERNAL",
                                               "overloaded", "validation error", "Invalid JSON",
                                               "timed out", "Timeout", "timeout"))
            if attempt == attempts - 1 or not retryable:
                raise
            wait = _retry_delay(msg, delay)
            kind = ("rate limited (429)" if "429" in msg else "unavailable (503)" if "503" in msg
                    else "timed out (504)" if "504" in msg else msg[:80])
            log.warning("Gemini %s, retry %d/%d in %.0fs", kind, attempt + 1, attempts - 1, wait)
            await asyncio.sleep(wait + random.random())
            delay = min(delay * 2, 60)
    raise RuntimeError("unreachable")


async def extract_jd(text: str) -> JDData:
    return await _generate(JD_PROMPT.format(text=text[:20000]), JDData)


async def extract_resume(text: str) -> ResumeData:
    return await _generate(RESUME_PROMPT.format(text=text[:20000]), ResumeData)
