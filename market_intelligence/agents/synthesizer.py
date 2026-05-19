# market_intelligence/agents/synthesizer.py
import os
import json
import anthropic
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from market_intelligence.agents.sql_agent import SQLAgent

load_dotenv()

PROMPT = (Path(__file__).parent / "synthesizer.md").read_text()


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class Synthesizer:

    def __init__(self, sql_agent: SQLAgent, max_follow_ups: int = 3):
        self.sql_agent    = sql_agent
        self.max_follow_ups = max_follow_ups
        self.client       = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def _call(self, messages: list[dict]) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=PROMPT,
            messages=messages
        )
        return response.content[0].text.strip()

    async def synthesize(
        self,
        question:        str,
        initial_sql:     str,
        initial_results: list[dict]
    ) -> str:
        # conversation history — grows with each follow-up round
        messages = [
            {
                "role": "user",
                "content": (
                    f"User question: {question}\n\n"
                    f"Initial SQL query run:\n{initial_sql}\n\n"
                    f"Initial results:\n"
                    f"{json.dumps(initial_results, indent=2, default=_serialize)}\n\n"
                    f"You have up to {self.max_follow_ups} follow-up queries available. "
                    f"Do you need to investigate further before answering? "
                    f"If yes, respond with exactly:\n"
                    f"QUERY: <your SQL query>\n"
                    f"REASON: <one line — what you expect to learn>\n\n"
                    f"If you have enough to answer, respond with:\n"
                    f"ANSWER: <your full answer>"
                )
            }
        ]

        follow_ups_used = 0

        while follow_ups_used < self.max_follow_ups:
            response = self._call(messages)

            # LLM wants to run a follow-up query
            if response.startswith("QUERY:"):
                lines     = response.strip().split("\n")
                sql_line  = next((l for l in lines if l.startswith("QUERY:")), "")
                sql       = sql_line.replace("QUERY:", "").strip()

                result    = await self.sql_agent.query(sql)
                follow_ups_used += 1
                remaining = self.max_follow_ups - follow_ups_used

                # add LLM response and query result to conversation
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Query result:\n"
                        f"{json.dumps(result['results'], indent=2, default=_serialize)}\n\n"
                        + (
                            f"You have {remaining} follow-up "
                            f"{'query' if remaining == 1 else 'queries'} remaining. "
                            f"Do you need to investigate further?\n"
                            f"QUERY: <sql> / REASON: <reason>  OR  ANSWER: <answer>"
                            if remaining > 0
                            else
                            f"No more follow-up queries available. "
                            f"Please provide your final answer now.\n"
                            f"ANSWER: <your full answer>"
                        )
                    )
                })

            # LLM is ready to answer
            elif response.startswith("ANSWER:"):
                return response.replace("ANSWER:", "").strip()

            # unexpected response — ask it to comply
            else:
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": (
                        "Please respond with either:\n"
                        "QUERY: <sql>\nREASON: <reason>\n\n"
                        "or\n\nANSWER: <your answer>"
                    )
                })

        # follow-up limit reached — force a final answer
        messages.append({
            "role": "user",
            "content": "Follow-up limit reached. Provide your final answer now.\nANSWER: <your answer>"
        })
        final = self._call(messages)
        return final.replace("ANSWER:", "").strip()