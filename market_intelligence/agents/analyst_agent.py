import os
import asyncpg
import anthropic
from dotenv import load_dotenv

load_dotenv()

class AnalystAgent:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


    def _generate_sql(self, question: str) -> str:
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens =1000,
            messages=[{
                f"{SCHEMA_CONTEXT}\n\n"
                    f"Question: {question}\n\n"
                    f"Write a single SQL query to answer this question. "
                    f"Return only the SQL, nothing else."
            }]
        )
        return response.content[0].text.strip()

    async def _execute_query(self, sql:str) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [dict(row) for row in rows]

    def _synthesize_answer(
        self,
        question: str,
        sql: str,
        results: list[dict]
    ) -> str:
        response = self.client.messages.create(
            model ="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content" : (
                    f"A user asked this financial question:\n{question}\n\n"
                    f"This SQL query was run:\n{sql}\n\n"
                    f"These are the results:\n{results}\n\n"
                    f"Write a clear, concise answer in plain English. "
                    f"Be specific — include actual numbers, company names, "
                    f"and sector names from the results. "
                    f"Format numbers readably (e.g. $1.2T, 15.3%, -42 days)."
                )
            }]
        )
        return response.content[0].text.strip()

    async def ask(self, question: str) -> dict:
        sql = self._generate_sql(question)

        try:
            results = await self._execute_query(sql)
        except Exception as e:
            return {
                "question": question,
                "sql":      sql,
                "results":  [],
                "answer":   f"The generated query failed to execute: {e}",
                "error":    str(e)
            }

        answer =self._synthesize_answer(question, sql, results)

        return {
            "question": question,
            "sql": sql,
            "results": results,
            "answer": answer
        }