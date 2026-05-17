# scripts/backfill_historical_prices.py
import asyncio
import os
import asyncpg
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from market_intelligence.storage.stock_quote_repository import StockQuoteRepository

load_dotenv()

EXCLUDED_SYMBOLS = {"BRK.B", "BRK.A", "BF.B", "BF.A"}


async def backfill():
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))

    async with pool.acquire() as conn:
        tickers = await conn.fetch(
            """
            SELECT id, symbol FROM tickers
            WHERE is_active = TRUE
            ORDER BY symbol
            """
        )

    succeeded   = 0
    failed      = []
    total       = len(tickers)

    print(f"Backfilling {total} tickers — 5 years of daily prices\n")

    for i, row in enumerate(tickers):
        ticker_id = row["id"]
        symbol    = row["symbol"]

        if symbol in EXCLUDED_SYMBOLS:
            print(f"[{i+1}/{total}] Skipping {symbol} — excluded")
            continue

        try:
            # fetch 5 years of daily history
            yf_ticker = yf.Ticker(symbol)
            hist      = yf_ticker.history(period="5y")

            if hist.empty:
                failed.append((symbol, "no data returned"))
                print(f"[{i+1}/{total}] {symbol} — no data")
                continue

            # write each day to stock_quotes
            async with pool.acquire() as conn:
                repo = StockQuoteRepository(conn)
                for ts, row_data in hist.iterrows():
                    # normalize timezone — yfinance returns tz-aware timestamps
                    time = ts.to_pydatetime().astimezone(timezone.utc)
                    await repo.upsert(
                        ticker_id  = ticker_id,
                        time       = time,
                        price      = float(row_data["Close"]),
                        market_cap = None,   # not available from yfinance
                        raw        = {
                            "source": "yfinance",
                            "open":   float(row_data["Open"]),
                            "high":   float(row_data["High"]),
                            "low":    float(row_data["Low"]),
                            "close":  float(row_data["Close"]),
                            "volume": int(row_data["Volume"])
                        }
                    )

            succeeded += 1
            print(f"[{i+1}/{total}] {symbol} — {len(hist)} days loaded")

        except Exception as e:
            failed.append((symbol, str(e)))
            print(f"[{i+1}/{total}] {symbol} — ERROR: {e}")

    await pool.close()

    print(f"\n{'='*40}")
    print(f"Done: {succeeded} succeeded, {len(failed)} failed")
    if failed:
        print(f"\nFailed tickers:")
        for symbol, reason in failed:
            print(f"  ✗ {symbol}: {reason}")


asyncio.run(backfill())