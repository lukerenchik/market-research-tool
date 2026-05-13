import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class KeyMetricsRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:                      int,
        time:                           datetime,
        period:                         str,
        fiscal_year:                    int,
        return_on_invested_capital:     float | None,
        free_cash_flow_yield:           float | None,
        ev_to_free_cash_flow:           float | None,
        income_quality:                 float | None,
        cash_conversion_cycle:          float | None,
        raw:                            dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO key_metrics
                (time, ticker_id, period, fiscal_year,
                 return_on_invested_capital, free_cash_flow_yield,
                 ev_to_free_cash_flow, income_quality,
                 cash_conversion_cycle, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year                 = EXCLUDED.fiscal_year,
                return_on_invested_capital  = EXCLUDED.return_on_invested_capital,
                free_cash_flow_yield        = EXCLUDED.free_cash_flow_yield,
                ev_to_free_cash_flow        = EXCLUDED.ev_to_free_cash_flow,
                income_quality              = EXCLUDED.income_quality,
                cash_conversion_cycle       = EXCLUDED.cash_conversion_cycle,
                raw                         = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            return_on_invested_capital, free_cash_flow_yield,
            ev_to_free_cash_flow, income_quality,
            cash_conversion_cycle,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM key_metrics
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM key_metrics
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )