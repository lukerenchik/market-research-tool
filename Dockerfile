FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY pyproject.toml README.md ./
COPY market_intelligence ./market_intelligence
RUN pip install --no-cache-dir .

COPY scripts ./scripts
COPY db ./db

RUN useradd --create-home appuser
USER appuser

# Default job: refresh daily quotes and market caps for all active tickers.
# Override the command to run other jobs, e.g.
#   docker compose run --rm ingest python -m market_intelligence.ingestion.jobs.ingest_all
CMD ["python", "-m", "market_intelligence.ingestion.jobs.daily_refresh"]
