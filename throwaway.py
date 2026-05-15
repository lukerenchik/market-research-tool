# tests/throwaway.py
import asyncio
import os
import json
from dotenv import load_dotenv
from market_intelligence.ingestion.providers.fmp import FMPProvider

load_dotenv()

async def test():
    provider = FMPProvider(api_key=os.getenv("FMP_API_KEY"))

    print("\n--- Key Metrics ---")
    key_metrics = await provider.get_key_metrics(ticker="AAPL")
    print(json.dumps(key_metrics[:1], indent=2, default=str))

    print("\n--- Balance Sheet ---")
    balance_sheet = await provider.get_balance_sheet_statement(ticker="AAPL")
    print(json.dumps(balance_sheet[:1], indent=2, default=str))

    print("\n--- Cash Flow ---")
    cash_flow = await provider.get_cash_flow_statement(ticker="AAPL")
    print(json.dumps(cash_flow[:1], indent=2, default=str))

    print("\n--- Financial Ratios ---")
    financial_ratios = await provider.get_financial_ratios(ticker="AAPL")
    print(json.dumps(financial_ratios[:1], indent=2, default=str))

    print("\n--- Income Growth ---")
    income_growth = await provider.get_income_statement_growth(ticker="AAPL")
    print(json.dumps(income_growth[:1], indent=2, default=str))

    print("\n--- Employee Count ---")
    employee_count = await provider.get_company_historical_employee_count(ticker="AAPL")
    print(json.dumps(employee_count[:2], indent=2, default=str))

    await provider.close()

asyncio.run(test())