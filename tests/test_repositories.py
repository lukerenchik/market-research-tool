"""Integration tests: repositories against a real PostgreSQL/TimescaleDB.

Skipped unless TEST_DATABASE_URL is set (see conftest.py). Each test runs in a
transaction that is rolled back, so the database is left untouched.
"""
import json
from datetime import datetime, timezone

import asyncpg
import pytest

from market_intelligence.storage import KeyMetricsRepository, StockQuoteRepository

pytestmark = pytest.mark.integration

Q2 = datetime(2025, 6, 30, tzinfo=timezone.utc)


def key_metrics_kwargs(ticker_id: int, **overrides) -> dict:
    kwargs = dict(
        ticker_id=ticker_id,
        time=Q2,
        period="Q2",
        fiscal_year=2025,
        return_on_invested_capital=0.20,
        free_cash_flow_yield=0.04,
        ev_to_free_cash_flow=25.0,
        income_quality=1.1,
        cash_conversion_cycle=-30.0,
        raw={"source": "test"},
    )
    kwargs.update(overrides)
    return kwargs


async def test_upsert_inserts_a_row(conn, ticker_id):
    await KeyMetricsRepository(conn).upsert(**key_metrics_kwargs(ticker_id))

    row = await KeyMetricsRepository(conn).get_latest(ticker_id)
    assert row["period"] == "Q2"
    assert float(row["return_on_invested_capital"]) == pytest.approx(0.20)
    assert json.loads(row["raw"]) == {"source": "test"}


async def test_upsert_is_idempotent_and_updates_in_place(conn, ticker_id):
    repo = KeyMetricsRepository(conn)
    await repo.upsert(**key_metrics_kwargs(ticker_id))
    await repo.upsert(**key_metrics_kwargs(ticker_id))  # rerun of the same job
    await repo.upsert(**key_metrics_kwargs(ticker_id, return_on_invested_capital=0.35))  # restated value

    assert await conn.fetchval("SELECT COUNT(*) FROM key_metrics WHERE ticker_id = $1", ticker_id) == 1
    row = await repo.get_latest(ticker_id)
    assert float(row["return_on_invested_capital"]) == pytest.approx(0.35)


async def test_history_is_newest_first_and_respects_limit(conn, ticker_id):
    repo = KeyMetricsRepository(conn)
    for month, period in [(3, "Q1"), (6, "Q2"), (9, "Q3")]:
        await repo.upsert(
            **key_metrics_kwargs(ticker_id, time=datetime(2025, month, 28, tzinfo=timezone.utc), period=period)
        )

    history = await repo.get_history(ticker_id, limit=2)
    assert [r["period"] for r in history] == ["Q3", "Q2"]


async def test_stock_quote_upsert_is_idempotent(conn, ticker_id):
    repo = StockQuoteRepository(conn)
    day = datetime(2025, 6, 30, tzinfo=timezone.utc)
    await repo.upsert(ticker_id=ticker_id, time=day, price=100.0, market_cap=None, raw={"v": 1})
    await repo.upsert(ticker_id=ticker_id, time=day, price=101.5, market_cap=None, raw={"v": 2})

    rows = await conn.fetch("SELECT price FROM stock_quotes WHERE ticker_id = $1", ticker_id)
    assert [float(r["price"]) for r in rows] == [101.5]


async def test_unique_constraint_blocks_duplicate_rows(conn, ticker_id):
    """Migration 002: raw INSERTs (bypassing the upsert) cannot create duplicates."""
    insert = "INSERT INTO historical_market_cap (time, ticker_id, market_cap) VALUES ($1, $2, $3)"
    await conn.execute(insert, Q2, ticker_id, 1_000)
    with pytest.raises(asyncpg.UniqueViolationError):
        await conn.execute(insert, Q2, ticker_id, 2_000)
