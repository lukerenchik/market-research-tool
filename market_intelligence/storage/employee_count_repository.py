import json
from datetime import datetime, date
import asyncpg
from .base import BaseRepository


class EmployeeCountRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:      int,
        time:           datetime,
        filing_date:    date | None,
        employee_count: int | None,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO employee_count_history
                (time, ticker_id, filing_date, employee_count)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (ticker_id, time) DO UPDATE SET
                filing_date    = EXCLUDED.filing_date,
                employee_count = EXCLUDED.employee_count
            """,
            time, ticker_id, filing_date, employee_count
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM employee_count_history
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 10) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM employee_count_history
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )