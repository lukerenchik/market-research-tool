from datetime import datetime


def normalize_financial_ratios(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":            ticker_id,
        "time":                 datetime.fromisoformat(record["date"]),
        "period":               record.get("period"),
        "fiscal_year":          int(record["fiscalYear"]),
        "gross_profit_margin":  record.get("grossProfitMargin"),
        "net_profit_margin":    record.get("netProfitMargin"),
        "inventory_turnover":   record.get("inventoryTurnover"),
        "raw":                  record
    }
