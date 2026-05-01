from typing import Any
import httpx

FMP_BASE_URL = "https://financialmodelingprep.com/stable/"

class FMPProvider():
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=FMP_BASE_URL, timeout=30.0)

    async def _get(self, endpoint: str, params: dict = None) -> Any:
        params = params or {}
        params["apikey"] = self.api_key
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()


    async def get_company_profile(self, ticker: str) -> dict:
        return await self._get(f"profile", params={"symbol": ticker})

    async def get_company_employee_count(self, ticker: str) -> dict:
        return await self._get(f"employee-count", params={"symbol": ticker})

    async def get_stock_peer_comparison(self, ticker: str) -> dict:
        return await self._get(f"stock-peers", params={"symbol": ticker})

    async def get_company_historical_employee_count(self, ticker: str) -> dict:
        return await self._get(f"historical-employee-count", params={"symbol": ticker})

    async def get_company_historical_market_cap(self, ticker: str) -> dict:
        return await self._get(f"historical-market-capitalization", params={"symbol": ticker})

    async def get_income_statement(self, ticker: str) -> dict:
        return await self._get(f"income-statement", params={"symbol": ticker})

    async def get_balance_sheet_statement(self, ticker: str) -> dict:
        return await self._get(f"balance-sheet-statement", params={"symbol": ticker})

    async def get_cash_flow_statement(self, ticker: str) -> dict:
        return await self._get(f"cash-flow-statement", params={"symbol": ticker})
        
    async def get_key_metrics(self, ticker: str) -> dict:
        return await self._get(f"key-metrics", params={"symbol": ticker})

    async def get_financial_ratios(self, ticker: str) -> dict:
        return await self._get(f"ratios", params={"symbol": ticker})

    async def get_income_statement_growth(self, ticker: str) -> dict:
        return await self._get(f"income-statement-growth", params={"symbol": ticker})

    async def get_stock_quote(self, ticker: str) -> dict:
        return await self._get(f"quote", params={"symbol": ticker})


 #List of interesting endpoints:

'''
Company and Reference Data:
- Company Profile Data - DONE
- Company Employee Count - Untested
- Stock Peer Comparison - Untested
- Company Historical Employee Count - Untested
- Company Historical Market Cap - Untested


Fundamentals:
- Financial Statements:
-- Income Statement
-- Balance Sheet Statement
-- cash Flow Statement
-- Key Metrics
-- Financial Ratios
-- Income Statement Growth

Quote:
- Stock Quote


'''