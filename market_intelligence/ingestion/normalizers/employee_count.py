from datetime import datetime


def normalize_employee_count(record: dict, ticker_id: int) -> dict:
    return {
        "ticker_id":      ticker_id,
        "time":           datetime.fromisoformat(record["periodOfReport"]),
        "filing_date":    datetime.fromisoformat(record["filingDate"]).date(),
        "employee_count": record.get("employeeCount"),
    }
