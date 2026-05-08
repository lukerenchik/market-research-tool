import asyncpg
from .base import BaseRepository

class TickerRepository(BaseRepository):

    async def upsert(
        self,
        symbol: str,
        company_name: str,
        sector_id: int | None = None,
        industry_group_id: int | None = None,
        industry_id: int | None = None,
        sub_industry_id: int | None = None,
        raw: dict | None = None
    ) -> int:
        row = await self.conn.fetchrow(
        """
        INSERT INTO tickers (
        symbol,
        company_name,
        sector_id,
        industry_group_id,
        industry_id,
        sub_industry_id,
        raw
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (symbol) DO UPDATE SET
            company_name        = EXCLUDED.company_name,
            sector_id           = EXCLUDED.sector_id,
            industry_group_id   = EXCLUDED.industry_group_id,
            industry_id         = EXCLUDED.industry_id,
            sub_industry_id     = EXCLUDED.sub_industry_id,
            raw                 = EXCLUDED.raw,
            updated_at          = NOW()
        RETURNING id
        """,
        symbol,
        company_name,
        sector_id,
        industry_group_id,
        industry_id,
        sub_industry_id,
        raw
        )

    async def get_all_active(self) -> list[asyncpg.Record]:
        return await self.conn.fetch(
            "SELECT * FROM tickers WHERE is_active = TRUE ORDER BY symbol"
        )