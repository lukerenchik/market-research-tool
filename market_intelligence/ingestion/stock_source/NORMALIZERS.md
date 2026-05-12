# Ticker Normalizer

The normalizer converts any source format (CSV, JSON, API response) into a
standard shape before writing to the database. New ingestion sources should
always go through the normalizer — never write directly to the repository.

---

## What It Does

Takes four string fields from any source, resolves them to GICS database IDs,
and returns a dict ready to pass to `TickerRepository.upsert()`.

---

## Required Inputs

| Parameter          | Type   | Description                                      | Example                                      |
|--------------------|--------|--------------------------------------------------|----------------------------------------------|
| `symbol`           | `str`  | Stock ticker symbol                              | `"AAPL"`                                     |
| `company_name`     | `str`  | Full company name                                | `"Apple Inc."`                               |
| `sector_name`      | `str`  | GICS sector name — must match `gics_sectors`     | `"Information Technology"`                   |
| `sub_industry_name`| `str`  | GICS sub-industry — must match `gics_sub_industries` | `"Technology Hardware, Storage & Peripherals"` |
| `gics_repo`        | `GICSRepository` | Active repository instance for DB lookups | see usage below                    |

> **Note:** `sector_name` and `sub_industry_name` must exactly match the values
> in your database. If a sector is not found, the ticker will be skipped.
> Industry and industry group are derived automatically from sub-industry.

---

## How to Call It

```python
from market_intelligence.ingestion.normalizers.ticker import normalize_ticker_row
from market_intelligence.storage.gics_repository import GICSRepository
from market_intelligence.storage.ticker_repository import TickerRepository

async with pool.acquire() as conn:
    gics_repo   = GICSRepository(conn)
    ticker_repo = TickerRepository(conn)

    normalized = await normalize_ticker_row(
        symbol           = "AAPL",
        company_name     = "Apple Inc.",
        sector_name      = "Information Technology",
        sub_industry_name= "Technology Hardware, Storage & Peripherals",
        gics_repo        = gics_repo
    )

    if normalized:
        await ticker_repo.upsert(**normalized)
```

`normalize_ticker_row` returns `None` if the sector name is not found in the
database. Always check for `None` before calling `upsert`.

---

## Adding a New Ingestion Source

1. Create a new script in `scripts/` — e.g. `scripts/seed_from_json.py`
2. Load your data (CSV, JSON, API response — whatever the source is)
3. Map your source fields to the four required inputs
4. Call `normalize_ticker_row` and then `ticker_repo.upsert`

**Example for a JSON source:**

```python
import asyncio, asyncpg, json, os
from dotenv import load_dotenv
from market_intelligence.ingestion.normalizers.ticker import normalize_ticker_row
from market_intelligence.storage.gics_repository import GICSRepository
from market_intelligence.storage.ticker_repository import TickerRepository

load_dotenv()

async def seed():
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))

    with open("db/seeds/my_tickers.json") as f:
        tickers = json.load(f)

    async with pool.acquire() as conn:
        gics_repo   = GICSRepository(conn)
        ticker_repo = TickerRepository(conn)

        for item in tickers:
            normalized = await normalize_ticker_row(
                symbol            = item["ticker"],        # map your field names here
                company_name      = item["name"],
                sector_name       = item["sector"],
                sub_industry_name = item["sub_industry"],
                gics_repo         = gics_repo
            )
            if normalized:
                await ticker_repo.upsert(**normalized)

    await pool.close()

asyncio.run(seed())
```

The only thing that changes between sources is the field mapping on lines
inside the loop. The normalizer and repository calls are always identical.

---

## What the Normalizer Returns

```python
{
    "symbol":             "AAPL",
    "company_name":       "Apple Inc.",
    "sector_id":          4,       # resolved from gics_sectors
    "industry_group_id":  9,       # derived from sub_industry
    "industry_id":        22,      # derived from sub_industry
    "sub_industry_id":    87,      # resolved from gics_sub_industries
}
```

Returns `None` if `sector_name` does not match any row in `gics_sectors`.

---

## File Location

```
market_intelligence/
└── ingestion/
    └── normalizers/
        ├── __init__.py
        └── ticker.py    ← normalizer lives here
```
