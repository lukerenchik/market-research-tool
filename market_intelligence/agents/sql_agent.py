import os
import asyncpg
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCHEMA_CONTEXT = (Path(__file__).parent / "sql_agent.md").read_text()

class SQLAgent:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _generate_sql(self, question: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{
                "role" : "user",
                "content":(
                    f"{SCHEMA_CONTEXT}\n\n"
                    f"Question: {question}\n\n"
                    f"Write a single PostgreSQL query to answer this. "
                    f"Return only the SQL, nothing else." 
                )
            }]
        )
        sql = response.content[0].text.strip()

        if sql.startswith("```"):
            lines = sql.split("\n")
            sql   = "\n".join(lines[1:-1]).strip()

        return sql

    async def _execute(self, sql: str) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [dict(row) for row in rows]

    async def query (self, question: str) -> dict:
        sql = self._generate_sql(question)

        try:
            results = await self._execute(sql)
            return {
                "question": question,
                "sql":      sql,
                "results":  results,
                "error":    None
            }
        except Exception as e:
            return {
                "question": question,
                "sql":      sql,
                "results":  [],
                "error":    str(e)
            }