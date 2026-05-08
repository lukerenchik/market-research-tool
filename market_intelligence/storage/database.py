import asyncpg
import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager

async def get_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size = 2,
        max_size = 10
    )

@asynccontextmanager
async def get_connection(pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    async with pool.acquire() as conn:
        yield conn

