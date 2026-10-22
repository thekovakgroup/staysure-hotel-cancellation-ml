FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

COPY requirements-api.txt ./

RUN python -m pip install --no-cache-dir -r requirements-api.txt

COPY app ./app
COPY scripts/verify_artifacts.py ./scripts/verify_artifacts.py
COPY models/preprocessing_pipeline.joblib ./models/preprocessing_pipeline.joblib
COPY models/random_forest_tuned_bundle.joblib ./models/random_forest_tuned_bundle.joblib
COPY models/artifact_manifest.csv ./models/artifact_manifest.csv

RUN python scripts/verify_artifacts.py \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]