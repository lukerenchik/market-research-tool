from datetime import datetime


def normalize_stock_quote(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":  ticker_id,
        "time":       datetime.fromtimestamp(record["timestamp"]),
        "price":      record.get("price"),
        "market_cap": record.get("marketCap"),
        "raw":        record
    }