FROM python:3.11-slim
WORKDIR /app
# Set to true to bake in offline sentence-transformers embeddings (bigger image).
ARG WITH_LOCAL_EMBEDDINGS=false
COPY requirements.txt requirements-local.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && if [ "$WITH_LOCAL_EMBEDDINGS" = "true" ]; then \
      pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
      && pip install --no-cache-dir sentence-transformers \
      && python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"; \
    fi
COPY app ./app
COPY eval ./eval
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
