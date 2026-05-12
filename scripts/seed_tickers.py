import asyncio
import os
import argparse
import asyncpg
from dotenv import load_dotenv
from market_intelligence.ingestion.stock_source.csv_source import seed_from_csv
from market_intelligence.ingestion.stock_source.json_source import seed_from_json
from market_intelligence.storage.gics_repository import GICSRepository
from market_intelligence.storage.ticker_repository import TickerRepository

load_dotenv()

async def main(file_path: str):
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))

    async with pool.acquire() as conn:
        gics_repo   = GICSRepository(conn)
        ticker_repo = TickerRepository(conn)

        if file_path.endswith('.csv'):
            succeeded, failed = await seed_from_csv(file_path, gics_repo, ticker_repo)
        elif file_path.endswith('.json'):
            succeeded, failed = await seed_from_json(file_path, gics_repo, ticker_repo)
        else:
            raise ValueError(f"Unsupported file type: {file_path}. Use .csv or .json")

    await pool.close()

    print(f"\nDone: {succeeded} succeeded, {len(failed)} failed")
    if failed:
        for symbol, reason in failed:
            print(f"  ✗ {symbol}: {reason}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed tickers from a CSV or JSON file")
    parser.add_argument("file_path", help="Path to .csv or .json file")
    args = parser.parse_args()
    asyncio.run(main(args.file_path))