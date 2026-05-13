import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class BalanceSheetRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:                  int,
        time:                       datetime,
        period:                     str,
        fiscal_year:                int,
        cash_and_short_term:        float | None,
        inventory:                  float | None,
        short_term_debt:            float | None,
        total_current_liabilities:  float | None,
        total_liabilities:          float | None,
        raw:                        dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO balance_sheets
                (time, ticker_id, period, fiscal_year,
                 cash_and_short_term, inventory, short_term_debt,
                 total_current_liabilities, total_liabilities, raw)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (ticker_id, time, period) DO UPDATE SET
                fiscal_year               = EXCLUDED.fiscal_year,
                cash_and_short_term       = EXCLUDED.cash_and_short_term,
                inventory                 = EXCLUDED.inventory,
                short_term_debt           = EXCLUDED.short_term_debt,
                total_current_liabilities = EXCLUDED.total_current_liabilities,
                total_liabilities         = EXCLUDED.total_liabilities,
                raw                       = EXCLUDED.raw
            """,
            time, ticker_id, period, fiscal_year,
            cash_and_short_term, inventory, short_term_debt,
            total_current_liabilities, total_liabilities,
            json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM balance_sheets
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 20) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM balance_sheets
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )