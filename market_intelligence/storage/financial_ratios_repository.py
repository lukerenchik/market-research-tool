import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class FinancialRatiosRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:          int,
        time:               datetime,
        period:             str,
        fiscal_year:        int,
        gross_profit_margin: float | None,
        net_profit_margin:  float | None,
        inventory_turnover: float | None,
        raw:                dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO financial_ratios
                (time, ticker_id, period, fiscal_year,
                 gross_profit_margin, net_profit_margin,
                 inventory_turnover, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year         = EXCLUDED.fiscal_year,
                gross_profit_margin = EXCLUDED.gross_profit_margin,
                net_profit_margin   = EXCLUDED.net_profit_margin,
                inventory_turnover  = EXCLUDED.inventory_turnover,
                raw                 = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            gross_profit_margin, net_profit_margin,
            inventory_turnover,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM financial_ratios
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM financial_ratios
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )