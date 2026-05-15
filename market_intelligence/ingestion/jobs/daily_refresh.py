# market_intelligence/ingestion/jobs/daily_refresh.py
import asyncio
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv
from market_intelligence.ingestion.providers.fmp import FMPProvider
from market_intelligence.ingestion.normalizers.stock_quote import normalize_stock_quote
from market_intelligence.ingestion.normalizers.historical_market_cap import normalize_historical_market_cap
from market_intelligence.storage.stock_quote_repository import StockQuoteRepository
from market_intelligence.storage.historical_market_cap_repository import HistoricalMarketCapRepository

load_dotenv()

EXCLUDED_SYMBOLS = {"BRK.B", "BRK.A", "BF.B", "BF.A"}


def is_weekday() -> bool:
    return datetime.today().weekday() < 5  # 0=Monday, 4=Friday


async def refresh_ticker(
    ticker_id:    int,
    symbol:       str,
    provider:     FMPProvider,
    conn:         asyncpg.Connection,
    call_counter: list
) -> tuple[int, list]:
    succeeded = 0
    errors    = []

    quote_repo      = StockQuoteRepository(conn)
    market_cap_repo = HistoricalMarketCapRepository(conn)

    # --- Stock Quote ---
    try:
        raw = await provider.get_stock_quote(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await quote_repo.upsert(**normalize_stock_quote(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} stock_quote: {e}")

    # --- Historical Market Cap ---
    try:
        raw = await provider.get_company_historical_market_cap(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await market_cap_repo.upsert(**normalize_historical_market_cap(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} historical_market_cap: {e}")

    return succeeded, errors


async def daily_refresh():
    if not is_weekday():
        print("Today is a weekend — skipping refresh.")
        return

    print(f"Starting daily refresh — {datetime.today().strftime('%A %Y-%m-%d')}\n")

    pool     = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    provider = FMPProvider(api_key=os.getenv("FMP_API_KEY"))

    call_counter    = [0]
    total_succeeded = 0
    total_errors    = []

    async with pool.acquire() as conn:
        tickers = await conn.fetch(
            """
            SELECT t.id, t.symbol
            FROM tickers t
            WHERE t.is_active = TRUE
            ORDER BY t.symbol
            """
        )

        print(f"Refreshing {len(tickers)} tickers...\n")

        for row in tickers:
            ticker_id = row["id"]
            symbol    = row["symbol"]

            if symbol in EXCLUDED_SYMBOLS:
                print(f"  Skipping {symbol} — excluded")
                continue

            print(f"  Refreshing {symbol} (API calls so far: {call_counter[0]})...")
            succeeded, errors = await refresh_ticker(
                ticker_id, symbol, provider, conn, call_counter
            )
            total_succeeded += succeeded
            total_errors.extend(errors)

    await provider.close()
    await pool.close()

    print(f"\n{'='*40}")
    print(f"Completed:       {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print(f"API calls used:  {call_counter[0]}")
    print(f"Records updated: {total_succeeded}")
    if total_errors:
        print(f"\nErrors ({len(total_errors)}):")
        for err in total_errors:
            print(f"  ✗ {err}")
    else:
        print("No errors.")


asyncio.run(daily_refresh())