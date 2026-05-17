# tests/test_sql_agent.py
import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from market_intelligence.agents.sql_agent import SQLAgent

load_dotenv()

QUESTIONS = [
    "Which sector has the highest average ROIC right now?",
    "Show me the 10 companies with the best free cash flow yield",
    "How many tickers are in each sector?",
]

async def test():
    pool  = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    agent = SQLAgent(pool=pool)

    for question in QUESTIONS:
        print(f"\nQuestion: {question}")
        result = await agent.query(question)

        print(f"SQL:\n{result['sql']}\n")

        if result['error']:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Results ({len(result['results'])} rows):")
            for row in result['results'][:5]:
                print(f"  {row}")

    await pool.close()

asyncio.run(test())