import asyncpg
from .base import BaseRepository

class GICSRepository(BaseRepository):

    async def get_sector_id(self, name: str) -> int | None:
        row = await self.conn.fetchrow(
            "SELECT id FROM gics_sectors WHERE name = $1",
            name
        )
        return row['id'] if row else None

    async def get_industry_group_id(self, name: str) -> int | None:
        row = await self.conn.fetchrow(
            "SELECT id FROM gics_industry_groups WHERE name = $1",
            name
        )
        return row['id'] if row else None

    async def get_industry_id(self, name: str) -> int | None:
        row = await self.conn.fetchrow(
            "SELECT id FROM gics_industries WHERE name = $1",
            name
        )
        return row['id'] if row else None

    async def get_sub_industry_id(self, name: str) -> int | None:
        row = await self.conn.fetchrow(
            "SELECT id FROM gics_sub_industries WHERE name = $1",
            name
        )
        return row['id'] if row else None



