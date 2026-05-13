import json
from market_intelligence.ingestion.normalizers.ticker_import import normalize_ticker_row
from market_intelligence.storage.gics_repository import GICSRepository
from market_intelligence.storage.ticker_repository import TickerRepository

async def seed_from_json(
    json_path: str,
    gics_repo: GICSRepository,
    ticker_repo: TickerRepository
) -> tuple[int, list]:
    with open(json_path) as f:
        tickers = json.load(f)

        succeeded = 0
        failed = []

        for item in tickers:
            normalized = await normalize_ticker_row(
                symbol            = item['symbol'],
                company_name      = item['company_name'],
                sector_name       = item['sector'],
                sub_industry_name = item['sub_industry'],
                gics_repo         = gics_repo
            )

            if not normalized:
                failed.append((item['symbol'], f"sector not found: {item['sector']}"))
                continue

        await ticker_repo.upsert(**normalized)
        succeeded += 1
        print(f"{item['symbol']} - {item['sector']}")

    return succeeded, failed