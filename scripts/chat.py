# scripts/chat.py
import asyncio
import os
import json
import asyncpg
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from market_intelligence.agents.sql_agent import SQLAgent
from market_intelligence.agents.synthesizer import Synthesizer

load_dotenv()


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def chat():
    pool       = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    sql_agent  = SQLAgent(pool=pool)
    synthesizer = Synthesizer(sql_agent=sql_agent)

    print("Market Intelligence — Chat")
    print("Type your question. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue
        if question.lower() == "exit":
            break

        # step 1 — SQL Agent generates and runs the initial query
        result = await sql_agent.query(question)

        if result["error"]:
            print(f"\nQuery error: {result['error']}\n")
            continue

        # step 2 — Synthesizer investigates and answers
        answer = await synthesizer.synthesize(
            question        = question,
            initial_sql     = result["sql"],
            initial_results = result["results"]
        )

        print(f"\n{answer}\n")

    await pool.close()


asyncio.run(chat())