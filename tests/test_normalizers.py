from datetime import date, datetime

import pytest

from market_intelligence.ingestion.normalizers.balance_sheet import normalize_balance_sheet
from market_intelligence.ingestion.normalizers.cash_flow import normalize_cash_flow
from market_intelligence.ingestion.normalizers.employee_count import normalize_employee_count
from market_intelligence.ingestion.normalizers.financial_ratios import normalize_financial_ratios
from market_intelligence.ingestion.normalizers.historical_market_cap import normalize_historical_market_cap
from market_intelligence.ingestion.normalizers.income_growth import normalize_income_growth
from market_intelligence.ingestion.normalizers.income_statement import normalize_income_statement
from market_intelligence.ingestion.normalizers.key_metrics import normalize_key_metrics
from market_intelligence.ingestion.normalizers.stock_quote import normalize_stock_quote

TICKER_ID = 42

# Quarterly statements share the same envelope: date / period / fiscalYear.
QUARTERLY = {"date": "2025-06-30", "period": "Q2", "fiscalYear": "2025"}


def assert_quarterly_envelope(out: dict) -> None:
    assert out["ticker_id"] == TICKER_ID
    assert out["time"] == datetime(2025, 6, 30)
    assert out["period"] == "Q2"
    assert out["fiscal_year"] == 2025  # string from the API is coerced to int


def test_income_statement_maps_fields_and_keeps_raw():
    record = {**QUARTERLY, "revenue": 100, "grossProfit": 60, "netIncome": 20}
    out = normalize_income_statement(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert (out["revenue"], out["gross_profit"], out["net_income"]) == (100, 60, 20)
    assert out["raw"] is record


def test_balance_sheet_maps_fields():
    record = {
        **QUARTERLY,
        "cashAndShortTermInvestments": 5,
        "inventory": 6,
        "shortTermDebt": 7,
        "totalCurrentLiabilities": 8,
        "totalLiabilities": 9,
    }
    out = normalize_balance_sheet(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert out["cash_and_short_term"] == 5
    assert out["inventory"] == 6
    assert out["short_term_debt"] == 7
    assert out["total_current_liabilities"] == 8
    assert out["total_liabilities"] == 9


def test_cash_flow_maps_fields():
    record = {
        **QUARTERLY,
        "netIncome": 1,
        "accountsReceivables": 2,
        "operatingCashFlow": 3,
        "freeCashFlow": 4,
    }
    out = normalize_cash_flow(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert out["free_cash_flow"] == 4
    assert out["operating_cash_flow"] == 3


def test_key_metrics_maps_fields():
    record = {
        **QUARTERLY,
        "returnOnInvestedCapital": 0.21,
        "freeCashFlowYield": 0.04,
        "evToFreeCashFlow": 25.0,
        "incomeQuality": 1.1,
        "cashConversionCycle": -30,
    }
    out = normalize_key_metrics(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert out["return_on_invested_capital"] == 0.21
    assert out["cash_conversion_cycle"] == -30


def test_financial_ratios_maps_fields():
    record = {**QUARTERLY, "grossProfitMargin": 0.4, "netProfitMargin": 0.1, "inventoryTurnover": 7.5}
    out = normalize_financial_ratios(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert out["gross_profit_margin"] == 0.4
    assert out["inventory_turnover"] == 7.5


def test_income_growth_maps_fields():
    record = {**QUARTERLY, "growthRevenue": 0.1, "growthGrossProfit": 0.2, "growthNetIncome": 0.3}
    out = normalize_income_growth(record, TICKER_ID)
    assert_quarterly_envelope(out)
    assert out["growth_net_income"] == 0.3


@pytest.mark.parametrize(
    "normalizer, fields",
    [
        (normalize_income_statement, ["revenue", "gross_profit", "net_income"]),
        (normalize_balance_sheet, ["cash_and_short_term", "inventory", "short_term_debt"]),
        (normalize_cash_flow, ["net_income", "free_cash_flow"]),
        (normalize_key_metrics, ["return_on_invested_capital", "income_quality"]),
        (normalize_financial_ratios, ["gross_profit_margin", "net_profit_margin"]),
        (normalize_income_growth, ["growth_revenue", "growth_net_income"]),
    ],
)
def test_missing_optional_metrics_become_none(normalizer, fields):
    """The API omits metrics for some companies; those must become NULL, not errors."""
    out = normalizer(dict(QUARTERLY), TICKER_ID)
    for field in fields:
        assert out[field] is None


@pytest.mark.parametrize(
    "normalizer",
    [
        normalize_income_statement,
        normalize_balance_sheet,
        normalize_cash_flow,
        normalize_key_metrics,
        normalize_financial_ratios,
        normalize_income_growth,
    ],
)
def test_missing_required_key_fails_loudly(normalizer):
    """A record without a date or fiscal year is malformed and must not be stored."""
    with pytest.raises(KeyError):
        normalizer({"period": "Q2", "fiscalYear": "2025"}, TICKER_ID)
    with pytest.raises(KeyError):
        normalizer({"date": "2025-06-30", "period": "Q2"}, TICKER_ID)


def test_historical_market_cap():
    out = normalize_historical_market_cap({"date": "2025-06-30", "marketCap": 3_000_000_000_000}, TICKER_ID)
    assert out == {"ticker_id": TICKER_ID, "time": datetime(2025, 6, 30), "market_cap": 3_000_000_000_000}


def test_historical_market_cap_requires_market_cap():
    with pytest.raises(KeyError):
        normalize_historical_market_cap({"date": "2025-06-30"}, TICKER_ID)


def test_stock_quote_converts_epoch_timestamp():
    record = {"timestamp": 1_750_000_000, "price": 201.5, "marketCap": 3_000_000_000_000}
    out = normalize_stock_quote(record, TICKER_ID)
    assert out["time"] == datetime.fromtimestamp(1_750_000_000)
    assert out["price"] == 201.5
    assert out["market_cap"] == 3_000_000_000_000
    assert out["raw"] is record


def test_employee_count_parses_report_and_filing_dates():
    record = {"periodOfReport": "2024-09-28", "filingDate": "2024-11-01", "employeeCount": 164000}
    out = normalize_employee_count(record, TICKER_ID)
    assert out["time"] == datetime(2024, 9, 28)
    assert out["filing_date"] == date(2024, 11, 1)
    assert out["employee_count"] == 164000
