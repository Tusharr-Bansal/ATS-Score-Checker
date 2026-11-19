"""Text embeddings with two interchangeable providers.

* gemini : Gemini embedding API (no local model; light deploy image)
* local  : sentence-transformers (all-MiniLM-L6-v2 by default; runs on CPU)

Cosine similarities from different models live on different scales, so each provider
carries its own calibration: raw cosine -> [0, 1] via a linear ramp between `lo` and `hi`
(values chosen from the sample-data evaluation, see README).
"""
from __future__ import annotations

import hashlib
import logging
import threading

import numpy as np

from .config import settings

log = logging.getLogger("checkres.embeddings")

CALIBRATION = {
    # doc_lo/doc_hi: passage-vs-passage similarity ramp
    # exp_lo/exp_hi:  stricter ramp for "is this past role relevant to the JD?"
    # title_lo/title_hi: past job title vs JD title
    # skill_related: minimum cosine for two different skill names to count as "related"
    "local": {"doc_lo": 0.25, "doc_hi": 0.55, "exp_lo": 0.30, "exp_hi": 0.50,
              "title_lo": 0.55, "title_hi": 0.85, "skill_related": 0.70},
    # gemini-embedding-001: very discriminative but compressed (own-role ~0.88, unrelated ~0.78);
    # skill names are near-useless for "related" (Excel~Docker 0.82, Java~JavaScript 0.89), so the
    # threshold only admits near-synonyms (Spark~PySpark 0.93). Fitted with eval/run_eval.py data.
    "gemini": {"doc_lo": 0.77, "doc_hi": 0.89, "exp_lo": 0.79, "exp_hi": 0.86,
               "title_lo": 0.88, "title_hi": 0.95, "skill_related": 0.92},
}


class Embedder:
    def __init__(self, provider: str):
        self.provider = provider
        self.cal = CALIBRATION[provider]
        self._cache: dict[str, np.ndarray] = {}
        self._lock = threading.Lock()
        self._model = None
        self._next_call = 0.0
        self.autosave_path = None  # if set, the cache is saved after every API batch (eval runs)

    # -------------------------------------------------------------- providers
    def _local(self, texts: list[str]) -> np.ndarray:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(settings.local_embed_model, device="cpu")
        return np.asarray(self._model.encode(texts, batch_size=32, normalize_embeddings=True,
                                             show_progress_bar=False), dtype=np.float32)

    def _gemini(self, texts: list[str]) -> np.ndarray:
        import time

        from google.genai import types

        from .llm import _retry_delay, client
        out = []
        size = max(1, min(100, int(settings.embed_per_min) or 100))  # API maximum: 100 texts per request
        for i in range(0, len(texts), size):
            batch = texts[i:i + size]
            if len(texts) > size:
                log.info("embedding texts %d-%d of %d", i + 1, i + len(batch), len(texts))
            for attempt in range(6):
                self._pace(len(batch))
                try:
                    r = client().models.embed_content(
                        model=settings.gemini_embed_model, contents=batch,
                        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY",
                                                        output_dimensionality=768))
                    out += [e.values for e in r.embeddings]
                    if self.autosave_path:  # keep finished batches even if a later one hits a quota
                        vb = np.asarray([x.values for x in r.embeddings], dtype=np.float32)
                        vb /= np.clip(np.linalg.norm(vb, axis=1, keepdims=True), 1e-9, None)
                        for t, vec in zip(batch, vb):
                            self._cache[hashlib.sha1(t.encode()).hexdigest()] = vec
                        self.save(self.autosave_path)
                    break
                except Exception as e:
                    msg = str(e)
                    if attempt == 5 or not any(k in msg for k in ("429", "RESOURCE_EXHAUSTED", "503", "500", "504", "DEADLINE_EXCEEDED")):
                        raise
                    wait = _retry_delay(msg, 2 ** (attempt + 2))
                    log.warning("Gemini embeddings %s, retry %d/5 in %.0fs [%s]",
                                "rate limited (429)" if "429" in msg else "unavailable", attempt + 1, wait,
                                msg[msg.find("Please retry"):][:60] or msg[:80])
                    time.sleep(wait)
        v = np.asarray(out, dtype=np.float32)
        return v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-9, None)

    def _pace(self, n: int) -> None:
        """Keep embedded texts under EMBED_PER_MIN. The free tier counts every text in a batch
        against its 100-per-minute quota, so pacing is by texts, not by API calls."""
        import time
        if settings.embed_per_min <= 0:
            return
        with self._lock:
            now = time.monotonic()
            if self._next_call > now:
                time.sleep(self._next_call - now)
            self._next_call = max(now, self._next_call) + 60.0 * n / settings.embed_per_min

    # -------------------------------------------------------------- API
    def embed(self, texts: list[str]) -> np.ndarray:
        """Unit-normalised embeddings, cached by text."""
        if not texts:
            return np.zeros((0, 1), dtype=np.float32)
        keys = [hashlib.sha1(t.encode()).hexdigest() for t in texts]
        missing = list({k: t for k, t in zip(keys, texts) if k not in self._cache}.items())
        if missing:
            vecs = (self._gemini if self.provider == "gemini" else self._local)([t for _, t in missing])
            for (k, _), v in zip(missing, vecs):
                self._cache[k] = v
        return np.stack([self._cache[k] for k in keys])

    # -------------------------------------------------------------- disk cache (used by the eval)
    def load(self, path) -> int:
        import os
        if not os.path.exists(path):
            return 0
        d = np.load(path, allow_pickle=False)
        self._cache.update(zip(d["keys"].tolist(), d["vecs"]))
        return len(d["keys"])

    def save(self, path) -> None:
        if self._cache:
            keys = list(self._cache)
            np.savez_compressed(path, keys=np.array(keys), vecs=np.stack([self._cache[k] for k in keys]))

    def calibrate(self, sim: float | np.ndarray, kind: str = "doc"):
        lo, hi = self.cal[f"{kind}_lo"], self.cal[f"{kind}_hi"]
        return np.clip((np.asarray(sim) - lo) / (hi - lo), 0.0, 1.0)


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(settings.embedding_provider)
    return _embedder
