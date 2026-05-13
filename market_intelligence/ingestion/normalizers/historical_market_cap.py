from datetime import datetime


def normalize_historical_market_cap(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":  ticker_id,
        "time":       datetime.fromisoformat(record["date"]),
        "market_cap": record["marketCap"],
    }