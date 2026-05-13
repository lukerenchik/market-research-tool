import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class IncomeStatementRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:    int,
        time:         datetime,
        period:       str,
        fiscal_year:  int,
        revenue:      float | None,
        gross_profit: float | None,
        net_income:   float | None,
        raw:          dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO income_statements
                (time, ticker_id, period, fiscal_year,
                 revenue, gross_profit, net_income, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year  = EXCLUDED.fiscal_year,
                revenue      = EXCLUDED.revenue,
                gross_profit = EXCLUDED.gross_profit,
                net_income   = EXCLUDED.net_income,
                raw          = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            revenue, gross_profit, net_income,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM income_statements
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM income_statements
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )