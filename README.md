# Market Intelligence Pipeline

An async Python ETL pipeline that loads S&P 500 fundamentals and prices into
PostgreSQL/TimescaleDB, plus a small set of LLM agents that query that data and
write analyst-style summaries.

[![CI](https://github.com/lukerenchik/fusa-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/lukerenchik/fusa-tool/actions/workflows/ci.yml)

## What it does

- **Ingests** nine datasets per ticker (quotes, historical market cap, income
  statement, balance sheet, cash flow, key metrics, ratios, income growth,
  employee count) for ~500 S&P 500 companies from the
  [Financial Modeling Prep](https://site.financialmodelingprep.com/) API.
- **Normalizes** each API payload into a typed record, then **upserts** it
  through a repository layer. Unique constraints plus `ON CONFLICT DO UPDATE`
  make every job safe to re-run and let restated figures overwrite old ones.
- **Stores** data in TimescaleDB: nine time-series hypertables plus a full GICS
  taxonomy (sector → industry group → industry → sub-industry).
- **Analyzes** the data with LLM agents (Claude) that use deterministic SQL and
  Python wherever possible and only call the model for judgment and narrative.

## Architecture

```
 Financial Modeling Prep API
            │  httpx (async) + RateLimiter
            ▼
   ┌──────────────────┐   ┌──────────────┐   ┌──────────────────────────┐
   │ providers/fmp.py │──▶│ normalizers/ │──▶│ storage/ *_repository.py │
   └──────────────────┘   └──────────────┘   │ asyncpg, idempotent      │
            ▲                                │ upserts                  │
            │ jobs/ingest_all.py             └────────────┬─────────────┘
            │ jobs/daily_refresh.py                       ▼
                                          ┌──────────────────────────────┐
                                          │ PostgreSQL + TimescaleDB     │
                                          │ 9 hypertables, GICS taxonomy │
                                          └──────────────┬───────────────┘
                                                         │
              ┌──────────────────────────────────────────┼───────────────┐
              ▼                                          ▼               │
   Sentinel agent                                  SQL agent ─▶ Synthesizer
   hardcoded SQL → outlier detection (Python)      question → SQL → results →
   → Claude writes notes → sentinel_logs           up to 3 follow-up queries → answer
```

### Design notes

- **Idempotent writes.** Migration `002` adds a unique key per ticker/period
  (or ticker/day) to every time-series table; every repository upserts on it.
- **Per-endpoint error isolation.** One failing endpoint for one ticker is
  recorded and reported at the end of the run; it doesn't abort the job.
- **Rate limiting.** A shared async `RateLimiter` spaces API calls to the
  provider's per-minute quota.
- **Cheap LLM use.** The Sentinel's data gathering and outlier detection are
  plain SQL and Python. Claude is only called to write the summary, and not at
  all when nothing is flagged.
- **Resumable backfill.** `ingest_all` skips tickers that already have data.
- **Raw payloads kept.** Most tables store the original API record in a `JSONB`
  `raw` column so new fields can be promoted to columns later without re-fetching.

## Quickstart

Requires Python 3.10+, Docker, and the `psql` client.

```bash
cp .env.example .env              # add FMP_API_KEY and ANTHROPIC_API_KEY
docker compose up -d timescaledb  # TimescaleDB on localhost:6543

pip install -e ".[dev]"
set -a; source .env; set +a       # load DATABASE_URL etc. into the shell

./scripts/setup_db.sh             # run migrations + load GICS taxonomy
python scripts/seed_tickers.py db/seeds/sp500_tickers.csv

python -m market_intelligence.ingestion.jobs.ingest_all      # full load (many API calls)
python -m market_intelligence.ingestion.jobs.daily_refresh   # quotes + market cap, weekdays
```

Optional:

```bash
pip install -e ".[backfill]"
python scripts/backfill_historical_prices.py   # 5 years of daily prices via yfinance

python scripts/chat.py                         # ask questions in plain English
python scripts/smoke/check_sentinel.py         # run the Sentinel and print its report
```

Run the daily job in a container instead:

```bash
docker compose --profile jobs run --rm ingest
```

## Tests

```bash
pytest                                   # unit tests, no services needed
TEST_DATABASE_URL=postgresql://postgres:password@localhost:6543/postgres pytest
```

With `TEST_DATABASE_URL` set, the integration tests also run against a real
database (the schema is created from `db/migrations/` if missing, and each test
rolls back its changes). GitHub Actions runs the migrations, the full test
suite, and a Docker build on every push and pull request.

| Area | What is covered |
|---|---|
| Normalizers | Field mapping, type coercion, missing optional metrics → `NULL`, malformed records raise |
| FMP provider | Request URL/params/API key (mocked transport), HTTP errors surface, rate-limit spacing |
| Sentinel agent | Outlier threshold, direction, acceleration, driver sub-industry, sorting, data shaping, no LLM call when nothing is flagged |
| Repositories (DB) | Upsert idempotency, restated values overwrite, history ordering, unique constraints |

`scripts/smoke/` holds manual scripts that call the live LLM and a populated
database; they are not part of the automated suite.

## Project layout

```
market_intelligence/
  ingestion/
    providers/fmp.py          async API client + RateLimiter
    normalizers/              API record → DB record, one module per dataset
    stock_source/             ticker list loaders (CSV / JSON)
    jobs/                     ingest_all.py, daily_refresh.py
  storage/                    asyncpg pool + one repository per table
  agents/                     Sentinel, SQL agent, Synthesizer (+ their prompts and SQL)
  api/                        FastAPI app (stub)
db/
  migrations/                 001 schema, 002 unique constraints, 003 agent logs
  seeds/                      GICS taxonomy, S&P 500 constituents
scripts/                      setup_db.sh, seeding, backfill, chat CLI, smoke/
tests/                        pytest suite
```

## Status and known gaps

- The **Analyst agent** (`agents/analyst_agent.py`) and the **HTTP API** are
  unfinished.
- API calls are not yet retried with backoff; failures are logged and the run
  continues.
- Prices are unadjusted; splits and other corporate actions are not handled.
- The SQL agent executes model-generated SQL. Point `DATABASE_URL` at a
  **read-only** database role if you expose it to anyone but yourself.
