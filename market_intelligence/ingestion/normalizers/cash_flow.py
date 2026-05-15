from datetime import datetime


def normalize_cash_flow(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":            ticker_id,
        "time":                 datetime.fromisoformat(record["date"]),
        "period":               record.get("period"),
        "fiscal_year":          int(record["fiscalYear"]),
        "net_income":           record.get("netIncome"),
        "accounts_receivables": record.get("accountsReceivables"),
        "operating_cash_flow":  record.get("operatingCashFlow"),
        "free_cash_flow":       record.get("freeCashFlow"),
        "raw":                  record
    }
