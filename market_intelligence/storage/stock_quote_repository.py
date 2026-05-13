import json
from datetime import datetime
import asyncpg
from .base import BaseRepository


class StockQuoteRepository(BaseRepository):

    async def upsert(
        self,
        ticker_id:  int,
        time:       datetime,
        price:      float | None,
        market_cap: int | None,
        raw:        dict
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO stock_quotes (time, ticker_id, price, market_cap, raw)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (ticker_id, time) DO UPDATE SET
                price      = EXCLUDED.price,
                market_cap = EXCLUDED.market_cap,
                raw        = EXCLUDED.raw
            """,
            time, ticker_id, price, market_cap, json.dumps(raw)
        )

    async def get_latest(self, ticker_id: int) -> asyncpg.Record | None:
        return await self.conn.fetchrow(
            """
            SELECT * FROM stock_quotes
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT 1
            """,
            ticker_id
        )

    async def get_history(self, ticker_id: int, limit: int = 252) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            """
            SELECT * FROM stock_quotes
            WHERE ticker_id = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            ticker_id, limit
        )