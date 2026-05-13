from datetime import datetime


def normalize_income_statement(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":    ticker_id,
        "time":         datetime.fromisoformat(record["date"]),
        "period":       record.get("period"),
        "fiscal_year":  int(record["fiscalYear"]),
        "revenue":      record.get("revenue"),
        "gross_profit": record.get("grossProfit"),
        "net_income":   record.get("netIncome"),
        "raw":          record
    }