import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class HistoricalMarketCapRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:  int,
        time:       datetime,
        market_cap: int,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO historical_market_cap (time, ticker_id, market_cap)
            VALUES ($1, $2, $3)
            ON CONFLICT (ticker_id, time) DO UPDATE SET
                market_cap = EXCLUDED.market_cap
            """,
            time, ticker_id, market_cap
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM historical_market_cap
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 252) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM historical_market_cap
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )