import asyncio
import os
from dotenv import load_dotenv
from market_intelligence.storage import get_pool, GICSRepository

load_dotenv()

async def test():
    pool = await get_pool()
    async with pool.acquire() as conn:
        repo = GICSRepository(conn)
        sector_id = await repo.get_sector_id('Energy')
        print(f"Energy sector_id: {sector_id}")
    await pool.close()

asyncio.run(test())