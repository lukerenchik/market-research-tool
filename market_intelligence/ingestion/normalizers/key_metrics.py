from datetime import datetime


def normalize_key_metrics(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":                    ticker_id,
        "time":                         datetime.fromisoformat(record["date"]),
        "period":                       record.get("period"),
        "fiscal_year":                  int(record["fiscalYear"]),
        "return_on_invested_capital":   record.get("returnOnInvestedCapital"),
        "free_cash_flow_yield":         record.get("freeCashFlowYield"),
        "ev_to_free_cash_flow":         record.get("evToFreeCashFlow"),
        "income_quality":               record.get("incomeQuality"),
        "cash_conversion_cycle":        record.get("cashConversionCycle"),
        "raw":                          record
    }
