"""Shared fixtures.

Unit tests need nothing. Integration tests (marked ``integration``) need a
PostgreSQL/TimescaleDB instance and are skipped unless TEST_DATABASE_URL is set,
e.g. the docker-compose database:

    TEST_DATABASE_URL=postgresql://postgres:password@localhost:6543/postgres pytest
"""
import asyncio
import os
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "db" / "migrations"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


def pytest_collection_modifyitems(config, items):
    if TEST_DATABASE_URL:
        return
    skip = pytest.mark.skip(reason="TEST_DATABASE_URL not set")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


async def _apply_schema_if_missing() -> None:
    conn = await asyncpg.connect(TEST_DATABASE_URL)
    try:
        exists = await conn.fetchval("SELECT to_regclass('public.tickers') IS NOT NULL")
        if exists:
            return
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            await conn.execute(path.read_text())
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def schema():
    """Create the schema from db/migrations once per test session."""
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL not set")
    asyncio.run(_apply_schema_if_missing())


@pytest_asyncio.fixture
async def conn(schema):
    """A connection inside a transaction that is rolled back after each test."""
    connection = await asyncpg.connect(TEST_DATABASE_URL)
    tx = connection.transaction()
    await tx.start()
    try:
        yield connection
    finally:
        await tx.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def ticker_id(conn) -> int:
    return await conn.fetchval(
        "INSERT INTO tickers (symbol, company_name) VALUES ('TEST', 'Test Corp') RETURNING id"
    )
