from datetime import datetime


def normalize_balance_sheet(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":                ticker_id,
        "time":                     datetime.fromisoformat(record["date"]),
        "period":                   record.get("period"),
        "fiscal_year":              int(record["fiscalYear"]),
        "cash_and_short_term":      record.get("cashAndShortTermInvestments"),
        "inventory":                record.get("inventory"),
        "short_term_debt":          record.get("shortTermDebt"),
        "total_current_liabilities": record.get("totalCurrentLiabilities"),
        "total_liabilities":        record.get("totalLiabilities"),
        "raw":                      record
    }
