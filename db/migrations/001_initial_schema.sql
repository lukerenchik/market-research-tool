-- ============================================================
-- ENABLE EXTENSION
-- ============================================================
CREATE EXTENSION IF NOT EXISTS timescaledb;


-- ============================================================
-- GICS TAXONOMY (Reference tables, slow-changing)
-- ============================================================

-- Approved, Now the question becomes, how do I populate these?

CREATE TABLE IF NOT EXISTS gics_sectors (
    id          SERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,    -- e.g. '10'
    name        TEXT NOT NULL UNIQUE -- e.g. 'Energy'
);

CREATE TABLE IF NOT EXISTS gics_industry_groups (
    id          SERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,    -- e.g. '1010'
    name        TEXT NOT NULL,
    sector_id   INTEGER NOT NULL REFERENCES gics_sectors(id)
);

CREATE TABLE IF NOT EXISTS gics_industries (
    id              SERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE, -- e.g. '101010'
    name            TEXT NOT NULL,
    industry_group_id INTEGER NOT NULL REFERENCES gics_industry_groups(id)
);

CREATE TABLE IF NOT EXISTS gics_sub_industries (
    id              SERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE, -- e.g. '10101010'
    name            TEXT NOT NULL,
    description     TEXT,
    industry_id     INTEGER NOT NULL REFERENCES gics_industries(id)
);


-- ============================================================
-- TICKERS (Reference, slow-changing)
-- ============================================================

CREATE TABLE IF NOT EXISTS tickers (
    id                  SERIAL PRIMARY KEY,
    symbol              TEXT NOT NULL UNIQUE,
    company_name        TEXT,

    -- GICS classification (explicit at every level for query simplicity)
    sector_id           INTEGER REFERENCES gics_sectors(id),
    industry_group_id   INTEGER REFERENCES gics_industry_groups(id),
    industry_id         INTEGER REFERENCES gics_industries(id),
    sub_industry_id     INTEGER REFERENCES gics_sub_industries(id),

    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    raw                 JSONB
);

-- Index for sector-level queries (your primary analysis lens)
CREATE INDEX IF NOT EXISTS idx_tickers_sector ON tickers(sector_id);
CREATE INDEX IF NOT EXISTS idx_tickers_industry ON tickers(industry_id);


-- ============================================================
-- COMPANY SNAPSHOTS (Slow-changing, re-fetch periodically)
-- ============================================================

-- This seems like most of this data is going to be found elsewhere, lets keep a tab on it and see
-- If this data fetch is really necessary.


-- ============================================================
-- EMPLOYEE COUNT HISTORY (Event-driven, from filings)
-- ============================================================

CREATE TABLE IF NOT EXISTS employee_count_history (
    time            TIMESTAMPTZ NOT NULL,
    ticker_id       INTEGER NOT NULL REFERENCES tickers(id),
    filing_date     DATE,
    employee_count  INTEGER,

    PRIMARY KEY (ticker_id, time)
);

SELECT create_hypertable(
    'employee_count_history',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

-- TODO: prices are currently unadjusted
-- corporate actions (splits, mergers) not yet handled
-- revisit
-- ============================================================
-- DAILY MARKET DATA (High-frequency time-series)
-- ============================================================

CREATE TABLE IF NOT EXISTS stock_quotes (
    time                TIMESTAMPTZ NOT NULL,
    ticker_id           INTEGER NOT NULL REFERENCES tickers(id),

    price               NUMERIC,
    market_cap          BIGINT,

    raw                 JSONB
);

SELECT create_hypertable(
    'stock_quotes',
    'time',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_stock_quotes_ticker ON stock_quotes(ticker_id, time DESC);


CREATE TABLE IF NOT EXISTS historical_market_cap (
    time        TIMESTAMPTZ NOT NULL,
    ticker_id   INTEGER NOT NULL REFERENCES tickers(id),
    market_cap  BIGINT NOT NULL
);

SELECT create_hypertable(
    'historical_market_cap',
    'time',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_historical_market_cap_ticker ON historical_market_cap(ticker_id, time DESC);


-- ============================================================
-- QUARTERLY FINANCIALS (Periodic time-series)
-- ============================================================

CREATE TABLE IF NOT EXISTS income_statements (
    time            TIMESTAMPTZ NOT NULL,   -- period end date
    ticker_id       INTEGER NOT NULL REFERENCES tickers(id),
    period          TEXT,            -- 'Q1', 'Q2', 'Q3', 'Q4', 'FY'
    fiscal_year     SMALLINT,

    revenue         NUMERIC,
    gross_profit    NUMERIC,
    net_income      NUMERIC,

    raw             JSONB
);

SELECT create_hypertable(
    'income_statements',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_income_statements_ticker ON income_statements(ticker_id, time DESC);


CREATE TABLE IF NOT EXISTS balance_sheets (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      TEXT,
    fiscal_year                 SMALLINT,

    cash_and_short_term         NUMERIC,
    inventory                   NUMERIC,
    short_term_debt             NUMERIC,
    total_current_liabilities   NUMERIC,
    total_liabilities           NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'balance_sheets',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_balance_sheets_ticker ON balance_sheets(ticker_id, time DESC);


CREATE TABLE IF NOT EXISTS cash_flow_statements (
    time                    TIMESTAMPTZ NOT NULL,
    ticker_id               INTEGER NOT NULL REFERENCES tickers(id),
    period                  TEXT,
    fiscal_year             SMALLINT,

    net_income              NUMERIC,
    accounts_receivables    NUMERIC,
    operating_cash_flow     NUMERIC,
    free_cash_flow          NUMERIC,

    raw                     JSONB
);

SELECT create_hypertable(
    'cash_flow_statements',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_cash_flow_ticker ON cash_flow_statements(ticker_id, time DESC);


-- ============================================================
-- DERIVED METRICS & RATIOS (Quarterly)
-- ============================================================

CREATE TABLE IF NOT EXISTS key_metrics (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      TEXT,
    fiscal_year                 SMALLINT,

    return_on_invested_capital  NUMERIC,
    free_cash_flow_yield        NUMERIC,
    ev_to_free_cash_flow        NUMERIC,
    income_quality              NUMERIC,
    cash_conversion_cycle       NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'key_metrics',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_key_metrics_ticker ON key_metrics(ticker_id, time DESC);


CREATE TABLE IF NOT EXISTS financial_ratios (
    time                    TIMESTAMPTZ NOT NULL,
    ticker_id               INTEGER NOT NULL REFERENCES tickers(id),
    period                  TEXT,
    fiscal_year             SMALLINT,

    gross_profit_margin     NUMERIC,
    net_profit_margin       NUMERIC,
    inventory_turnover      NUMERIC,

    raw                     JSONB
);

SELECT create_hypertable(
    'financial_ratios',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_financial_ratios_ticker ON financial_ratios(ticker_id, time DESC);


CREATE TABLE IF NOT EXISTS income_growth (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      TEXT,
    fiscal_year                 SMALLINT,

    growth_revenue              NUMERIC,
    growth_gross_profit         NUMERIC,
    growth_net_income           NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'income_growth',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_income_growth_ticker ON income_growth(ticker_id, time DESC);