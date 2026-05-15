from subprocess import call
from typing import Any
import httpx
import asyncio
import time

FMP_BASE_URL = "https://financialmodelingprep.com/stable/"

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_call_time
            wait = self.min_interval - elapsed
            if wait > 0:
                await asyncio.sleep(wait)
            self.last_call_time = time.monotonic()

class FMPProvider():
    def __init__(self, api_key: str, calls_per_minute: int = 300):
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=FMP_BASE_URL, timeout=30.0)
        self.rate_limiter = RateLimiter(calls_per_minute)

    async def _get(self, endpoint: str, params: dict = None) -> Any:
        await self.rate_limiter.acquire()
        params = params or {}
        params["apikey"] = self.api_key
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()


    async def get_company_profile(self, ticker: str) -> dict:
        return await self._get(f"profile", params={"symbol": ticker})

    async def get_company_employee_count(self, ticker: str) -> dict:
        return await self._get(f"employee-count", params={"symbol": ticker})

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

    async def get_sp500_constituents(self) -> list[dict]:
        return await self._get("/v3/sp500_constituent")

    async def close(self):
        await self.client.aclose()

