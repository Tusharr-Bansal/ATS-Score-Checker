"""Runtime configuration (environment variables, optionally from a .env file)."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:  # python-dotenv is optional
    pass


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./checkres.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    gemini_embed_model: str = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
    # "gemini" | "local" (sentence-transformers). Default: gemini when a key is present.
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "") or (
        "gemini" if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else "local")
    local_embed_model: str = os.getenv("LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    # "gemini" | "rules". Default: gemini when a key is present.
    extractor: str = os.getenv("EXTRACTOR", "") or (
        "gemini" if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else "rules")
    llm_concurrency: int = int(os.getenv("LLM_CONCURRENCY", 4))
    # Skill matching: "llm" (default with a key: Gemini judges each requirement with a verified resume
    # quote) or "taxonomy" (skills.py rules + embeddings). The taxonomy is also the automatic fallback
    # for any candidate the LLM could not judge (no key, API outage).
    skill_matcher: str = "taxonomy" if os.getenv("SKILL_MATCHER", "").lower() == "taxonomy" or not (
        os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else "llm"
    match_batch_size: int = int(os.getenv("MATCH_BATCH_SIZE", 10))
    llm_timeout_ms: int = int(os.getenv("LLM_TIMEOUT_MS", 120000))
    # client-side pacing (requests/min) to stay under the Gemini free-tier quota. 0 = unlimited (paid tier)
    llm_rpm: float = float(os.getenv("LLM_RPM", 10))
    # texts embedded per minute; Gemini embeddings free tier counts each text, limit 100/min. 0 = unlimited
    embed_per_min: float = float(os.getenv("EMBED_PER_MIN", 90))
    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
    max_upload_files: int = int(os.getenv("MAX_UPLOAD_FILES", 50))

    # Scoring weights (must sum to 1)
    w_skills: float = _f("W_SKILLS", 0.40)
    w_semantic: float = _f("W_SEMANTIC", 0.30)
    w_experience: float = _f("W_EXPERIENCE", 0.20)
    w_education: float = _f("W_EDUCATION", 0.10)


settings = Settings()
