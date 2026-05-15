import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from market_intelligence.ingestion.providers.fmp import FMPProvider

# Normalizers
from market_intelligence.ingestion.normalizers.stock_quote import normalize_stock_quote
from market_intelligence.ingestion.normalizers.historical_market_cap import normalize_historical_market_cap
from market_intelligence.ingestion.normalizers.income_statement import normalize_income_statement
from market_intelligence.ingestion.normalizers.key_metrics import normalize_key_metrics
from market_intelligence.ingestion.normalizers.balance_sheet import normalize_balance_sheet
from market_intelligence.ingestion.normalizers.cash_flow import normalize_cash_flow
from market_intelligence.ingestion.normalizers.financial_ratios import normalize_financial_ratios
from market_intelligence.ingestion.normalizers.income_growth import normalize_income_growth
from market_intelligence.ingestion.normalizers.employee_count import normalize_employee_count

# Repositories
from market_intelligence.storage.stock_quote_repository import StockQuoteRepository
from market_intelligence.storage.historical_market_cap_repository import HistoricalMarketCapRepository
from market_intelligence.storage.income_statement_repository import IncomeStatementRepository
from market_intelligence.storage.key_metrics_repository import KeyMetricsRepository
from market_intelligence.storage.balance_sheet_repository import BalanceSheetRepository
from market_intelligence.storage.cash_flow_repository import CashFlowRepository
from market_intelligence.storage.financial_ratios_repository import FinancialRatiosRepository
from market_intelligence.storage.income_growth_repository import IncomeGrowthRepository
from market_intelligence.storage.employee_count_repository import EmployeeCountRepository

load_dotenv()
# Tickers to exclude from ingestion
EXCLUDED_SYMBOLS = {"BRK.B", "BRK.A", "BF.B", "BF.A"}

async def already_ingested(ticker_id: int, conn: asyncpg.Connection) -> bool:
    row = await conn.fetchrow(
        "SELECT 1 FROM stock_quotes WHERE ticker_id = $1 LIMIT 1",
        ticker_id
    )
    return row is not None


async def ingest_ticker(
    ticker_id:    int,
    symbol:       str,
    provider:     FMPProvider,
    conn:         asyncpg.Connection,
    call_counter: list
) -> tuple[int, list]:
    succeeded = 0
    errors    = []

    quote_repo      = StockQuoteRepository(conn)
    market_cap_repo = HistoricalMarketCapRepository(conn)
    income_repo     = IncomeStatementRepository(conn)
    key_metrics_repo = KeyMetricsRepository(conn)
    balance_repo    = BalanceSheetRepository(conn)
    cash_flow_repo  = CashFlowRepository(conn)
    ratios_repo     = FinancialRatiosRepository(conn)
    growth_repo     = IncomeGrowthRepository(conn)
    employee_repo   = EmployeeCountRepository(conn)

    # --- Stock Quote ---
    try:
        raw = await provider.get_stock_quote(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await quote_repo.upsert(**normalize_stock_quote(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} stock_quote: {e}")

    # --- Historical Market Cap ---
    try:
        raw = await provider.get_company_historical_market_cap(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await market_cap_repo.upsert(**normalize_historical_market_cap(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} historical_market_cap: {e}")

    # --- Income Statement ---
    try:
        raw = await provider.get_income_statement(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await income_repo.upsert(**normalize_income_statement(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} income_statement: {e}")

    # --- Key Metrics ---
    try:
        raw = await provider.get_key_metrics(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await key_metrics_repo.upsert(**normalize_key_metrics(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} key_metrics: {e}")

    # --- Balance Sheet ---
    try:
        raw = await provider.get_balance_sheet_statement(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await balance_repo.upsert(**normalize_balance_sheet(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} balance_sheet: {e}")

    # --- Cash Flow ---
    try:
        raw = await provider.get_cash_flow_statement(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await cash_flow_repo.upsert(**normalize_cash_flow(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} cash_flow: {e}")

    # --- Financial Ratios ---
    try:
        raw = await provider.get_financial_ratios(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await ratios_repo.upsert(**normalize_financial_ratios(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} financial_ratios: {e}")

    # --- Income Growth ---
    try:
        raw = await provider.get_income_statement_growth(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await growth_repo.upsert(**normalize_income_growth(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} income_growth: {e}")

    # --- Employee Count ---
    try:
        raw = await provider.get_company_historical_employee_count(ticker=symbol)
        call_counter[0] += 1
        for record in raw:
            await employee_repo.upsert(**normalize_employee_count(record, ticker_id))
        succeeded += 1
    except Exception as e:
        errors.append(f"{symbol} employee_count: {e}")

    return succeeded, errors


async def ingest_all():
    pool     = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    provider = FMPProvider(api_key=os.getenv("FMP_API_KEY"))

    call_counter    = [0]
    total_succeeded = 0
    total_errors    = []

    async with pool.acquire() as conn:
        tickers = await conn.fetch(
            """
            SELECT t.id, t.symbol, s.name AS sector
            FROM tickers t
            JOIN gics_sectors s ON t.sector_id = s.id
            WHERE t.is_active = TRUE
            ORDER BY s.name, t.symbol
            """,
        )

        print(f"Found {len(tickers)} active tickers\n")

        current_sector = None
        for row in tickers:
            ticker_id = row["id"]
            symbol    = row["symbol"]
            sector    = row["sector"]

            if sector != current_sector:
                current_sector = sector
                
            if symbol in EXCLUDED_SYMBOLS:
                print(f"  Skipping {symbol} — excluded")
                continue

            if await already_ingested(ticker_id, conn):
                print(f"  Skipping {symbol} — already ingested")
                continue

            print(f"  Ingesting {symbol} (API calls so far: {call_counter[0]})...")
            succeeded, errors = await ingest_ticker(
                ticker_id, symbol, provider, conn, call_counter
            )
            total_succeeded += succeeded
            total_errors.extend(errors)

    await provider.close()
    await pool.close()

    print(f"\n{'='*40}")
    print(f"API calls used:  {call_counter[0]}")
    print(f"Endpoints saved: {total_succeeded}")
    if total_errors:
        print(f"\nErrors ({len(total_errors)}):")
        for err in total_errors:
            print(f"  ✗ {err}")
    else:
        print("No errors.")


asyncio.run(ingest_all())
