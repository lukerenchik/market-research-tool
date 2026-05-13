import pandas as pd
from market_intelligence.ingestion.normalizers.ticker_import import normalize_ticker_row
from market_intelligence.storage.gics_repository import GICSRepository
from market_intelligence.storage.ticker_repository import TickerRepository

async def seed_from_csv(
    csv_path: str,
    gics_repo: GICSRepository,
    ticker_repo: TickerRepository
) -> tuple[int, list]:
    df = pd.read_csv(csv_path)

    succeeded = 0
    failed = []

    for _, row in df.iterrows():
        normalized = await normalize_ticker_row(
            symbol            = row['Symbol'],
            company_name      = row['Security'],
            sector_name       = row['GICS Sector'],
            sub_industry_name = row['GICS Sub-Industry'],
            gics_repo         = gics_repo
        )

        if not normalized:
            failed.append((row['Symbol'], f"sector not found: {row['GICS Sector']}"))
            continue

        await ticker_repo.upsert(**normalized)
        succeeded += 1
        symbol = row['Symbol']
        sector = row['GICS Sector']
        print(f"{symbol} - {sector}")

    return succeeded, failed
