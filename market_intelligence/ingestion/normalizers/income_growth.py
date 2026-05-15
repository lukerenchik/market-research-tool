from datetime import datetime


def normalize_income_growth(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":            ticker_id,
        "time":                 datetime.fromisoformat(record["date"]),
        "period":               record.get("period"),
        "fiscal_year":          int(record["fiscalYear"]),
        "growth_revenue":       record.get("growthRevenue"),
        "growth_gross_profit":  record.get("growthGrossProfit"),
        "growth_net_income":    record.get("growthNetIncome"),
        "raw":                  record
    }
