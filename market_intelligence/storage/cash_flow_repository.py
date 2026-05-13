import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class CashFlowRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:            int,
        time:                 datetime,
        period:               str,
        fiscal_year:          int,
        net_income:           float | None,
        accounts_receivables: float | None,
        operating_cash_flow:  float | None,
        free_cash_flow:       float | None,
        raw:                  dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO cash_flow_statements
                (time, ticker_id, period, fiscal_year,
                 net_income, accounts_receivables,
                 operating_cash_flow, free_cash_flow, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year          = EXCLUDED.fiscal_year,
                net_income           = EXCLUDED.net_income,
                accounts_receivables = EXCLUDED.accounts_receivables,
                operating_cash_flow  = EXCLUDED.operating_cash_flow,
                free_cash_flow       = EXCLUDED.free_cash_flow,
                raw                  = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            net_income, accounts_receivables,
            operating_cash_flow, free_cash_flow,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM cash_flow_statements
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM cash_flow_statements
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )