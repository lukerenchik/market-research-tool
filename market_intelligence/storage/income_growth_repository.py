import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class IncomeGrowthRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:          int,
        time:               datetime,
        period:             str,
        fiscal_year:        int,
        growth_revenue:     float | None,
        growth_gross_profit: float | None,
        growth_net_income:  float | None,
        raw:                dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO income_growth
                (time, ticker_id, period, fiscal_year,
                 growth_revenue, growth_gross_profit,
                 growth_net_income, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year         = EXCLUDED.fiscal_year,
                growth_revenue      = EXCLUDED.growth_revenue,
                growth_gross_profit = EXCLUDED.growth_gross_profit,
                growth_net_income   = EXCLUDED.growth_net_income,
                raw                 = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            growth_revenue, growth_gross_profit,
            growth_net_income,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM income_growth
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM income_growth
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )