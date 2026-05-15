import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from market_intelligence.ingestion.providers.fmp import FMPProvider
from market_intelligence.ingestion.normalizers.stock_quote import normalize_stock_quote
from market_intelligence.ingestion.normalizers.historical_market_cap import normalize_historical_market_cap
from market_intelligence.ingestion.normalizers.income_statement import normalize_income_statement
from market_intelligence.storage.stock_quote_repository import StockQuoteRepository
from market_intelligence.storage.historical_market_cap_repository import HistoricalMarketCapRepository
from market_intelligence.storage.income_statement_repository import IncomeStatementRepository

load_dotenv()

SECTOR = "Information Technology"


async def ingest_ticker(
    ticker_id:      int,
    symbol:         str,
    provider:       FMPProvider,
    conn:           asyncpg.Connection,
    call_counter:   list
) -> tuple[int, list]:
    succeeded = 0
    errors = []

    quote_repo      = StockQuoteRepository(conn)
    market_cap_repo = HistoricalMarketCapRepository(conn)
    income_repo     = IncomeStatementRepository(conn)

    # --- Stock Quote ---
    try:
        raw_quotes = await provider.get_stock_quote(ticker=symbol)
        call_counter[0] += 1
        for record in raw_quotes:
            normalized = normalize_stock_quote(record, ticker_id)
            await quote_repo.upsert(**normalized)
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} stock_quote: {e}")

    # --- Historical Market Cap ---
    try:
        raw_market_caps = await provider.get_company_historical_market_cap(ticker=symbol)
        call_counter[0] += 1
        for record in raw_market_caps:
            normalized = normalize_historical_market_cap(record, ticker_id)
            await market_cap_repo.upsert(**normalized)
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} historical_market_cap: {e}")

    # --- Income Statement ---
    try:
        raw_income = await provider.get_income_statement(ticker=symbol)
        call_counter[0] += 1
        for record in raw_income:
            normalized = normalize_income_statement(record, ticker_id)
            await income_repo.upsert(**normalized)
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} income_statement: {e}")

    return succeeded, errors


async def ingest_technology():
    pool     = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    provider = FMPProvider(api_key=os.getenv("FMP_API_KEY"))

    # single shared counter so we can track total API calls
    call_counter = [0]

    async with pool.acquire() as conn:
        tickers = await conn.fetch(
            """
            SELECT t.id, t.symbol
            FROM tickers t
            JOIN gics_sectors s ON t.sector_id = s.id
            WHERE s.name = $1
            AND t.is_active = TRUE
            ORDER BY t.symbol
            """,
            SECTOR
        )

        print(f"Found {len(tickers)} tickers in {SECTOR}\n")

        total_succeeded = 0
        total_errors    = []

        for row in tickers:
            ticker_id = row["id"]
            symbol    = row["symbol"]

            if await already_ingested(ticker_id, conn):
                print(f"Skipping {symbol} — already ingested")
                continue

            print(f"Ingesting {symbol} (API calls so far: {call_counter[0]})...")
            succeeded, errors = await ingest_ticker(
                ticker_id, symbol, provider, conn, call_counter
            )
            total_succeeded += succeeded
            total_errors.extend(errors)

    await provider.close()
    await pool.close()

    print(f"\n--- Done ---")
    print(f"API calls used:  {call_counter[0]} / 250")
    print(f"Endpoints saved: {total_succeeded}")
    if total_errors:
        print(f"\nErrors ({len(total_errors)}):")
        for err in total_errors:
            print(f"  ✗ {err}")

async def already_ingested(ticker_id: int, conn: asyncpg.Connection) -> bool:
    row = await conn.fetchrow(
        "SELECT 1 FROM stock_quotes WHERE ticker_id = $1 LIMIT 1",
        ticker_id
    )
    return row is not None


asyncio.run(ingest_technology())