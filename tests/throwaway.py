# tests/throwaway.py
import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from market_intelligence.agents.sql_agent import SQLAgent

load_dotenv()

async def test():
    pool  = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    agent = SQLAgent(pool=pool)

    print("\n=== HOMEBUILDING ===")
    result = await agent.query(
        "Show me all tickers in the Homebuilding sub-industry with their "
        "most recent key metrics including ROIC, free cash flow yield, "
        "income quality, and cash conversion cycle. Include company name "
        "and sector."
    )
    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        for row in result["results"]:
            print(row)

    print("\n=== IT CONSULTING & OTHER SERVICES ===")
    result = await agent.query(
        "Show me all tickers in the IT Consulting & Other Services "
        "sub-industry with their most recent key metrics including ROIC, "
        "free cash flow yield, income quality, and cash conversion cycle. "
        "Include company name and sector."
    )
    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        for row in result["results"]:
            print(row)

    await pool.close()

asyncio.run(test())