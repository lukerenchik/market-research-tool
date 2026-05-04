-- ============================================================
-- ENABLE EXTENSION
-- ============================================================
CREATE EXTENSION IF NOT EXISTS timescaledb;


-- ============================================================
-- GICS TAXONOMY (Reference tables, slow-changing)
-- ============================================================

-- Approved, Now the question becomes, how do I populate these?

CREATE TABLE gics_sectors (
    id          SERIAL PRIMARY KEY,
    code        CHAR(2) NOT NULL UNIQUE,    -- e.g. '10'
    name        VARCHAR(100) NOT NULL UNIQUE -- e.g. 'Energy'
);

CREATE TABLE gics_industry_groups (
    id          SERIAL PRIMARY KEY,
    code        CHAR(4) NOT NULL UNIQUE,    -- e.g. '1010'
    name        VARCHAR(100) NOT NULL,
    sector_id   INTEGER NOT NULL REFERENCES gics_sectors(id)
);

CREATE TABLE gics_industries (
    id              SERIAL PRIMARY KEY,
    code            CHAR(6) NOT NULL UNIQUE, -- e.g. '101010'
    name            VARCHAR(100) NOT NULL,
    industry_group_id INTEGER NOT NULL REFERENCES gics_industry_groups(id)
);

CREATE TABLE gics_sub_industries (
    id              SERIAL PRIMARY KEY,
    code            CHAR(8) NOT NULL UNIQUE, -- e.g. '10101010'
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    industry_id     INTEGER NOT NULL REFERENCES gics_industries(id)
);


-- ============================================================
-- TICKERS (Reference, slow-changing)
-- ============================================================

CREATE TABLE tickers (
    id                  SERIAL PRIMARY KEY,
    symbol              VARCHAR(10) NOT NULL UNIQUE,
    company_name        VARCHAR(255),
    -- Do I need to know what exchange they are listed on? Seems like its completely trivial information. (Remove)
    exchange            VARCHAR(50),
    -- Description doesn't provide anything meaningful, if a company is interesting research will be necessary. (Remove)
    description         TEXT,

    -- GICS classification (explicit at every level for query simplicity)
    sector_id           INTEGER REFERENCES gics_sectors(id),
    industry_group_id   INTEGER REFERENCES gics_industry_groups(id),
    industry_id         INTEGER REFERENCES gics_industries(id),
    sub_industry_id     INTEGER REFERENCES gics_sub_industries(id),

    is_active           BOOLEAN DEFAULT TRUE,
    -- I think this is here so that I can retire a stock in the future, not immediately useful. (Keep)
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Index for sector-level queries (your primary analysis lens)
CREATE INDEX idx_tickers_sector ON tickers(sector_id);
CREATE INDEX idx_tickers_industry ON tickers(industry_id);


-- ============================================================
-- COMPANY SNAPSHOTS (Slow-changing, re-fetch periodically)
-- ============================================================

CREATE TABLE company_profiles (
    id              SERIAL PRIMARY KEY,
    ticker_id       INTEGER NOT NULL REFERENCES tickers(id),
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    price           NUMERIC,
    market_cap      BIGINT,
    price_range     VARCHAR(50),    -- FMP returns this as a string e.g. "142.53-198.23"
    employee_count  INTEGER,

    raw             JSONB           -- full FMP profile payload
);

CREATE INDEX idx_company_profiles_ticker ON company_profiles(ticker_id);


-- ============================================================
-- EMPLOYEE COUNT HISTORY (Event-driven, from filings)
-- ============================================================

CREATE TABLE employee_count_history (
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


-- ============================================================
-- DAILY MARKET DATA (High-frequency time-series)
-- ============================================================

CREATE TABLE stock_quotes (
    time                TIMESTAMPTZ NOT NULL,
    ticker_id           INTEGER NOT NULL REFERENCES tickers(id),

    price               NUMERIC,
    change_percentage   NUMERIC,
    year_high           NUMERIC,
    year_low            NUMERIC,
    market_cap          BIGINT,
    price_avg_200       NUMERIC,

    raw                 JSONB
);

SELECT create_hypertable(
    'stock_quotes',
    'time',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX idx_stock_quotes_ticker ON stock_quotes(ticker_id, time DESC);


CREATE TABLE historical_market_cap (
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

CREATE INDEX idx_historical_market_cap_ticker ON historical_market_cap(ticker_id, time DESC);


-- ============================================================
-- QUARTERLY FINANCIALS (Periodic time-series)
-- ============================================================

CREATE TABLE income_statements (
    time            TIMESTAMPTZ NOT NULL,   -- period end date
    ticker_id       INTEGER NOT NULL REFERENCES tickers(id),
    period          VARCHAR(10),            -- 'Q1', 'Q2', 'Q3', 'Q4', 'FY'
    fiscal_year     SMALLINT,

    revenue         NUMERIC,
    gross_profit    NUMERIC,
    ebitda          NUMERIC,
    net_income      NUMERIC,

    raw             JSONB
);

SELECT create_hypertable(
    'income_statements',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX idx_income_statements_ticker ON income_statements(ticker_id, time DESC);


CREATE TABLE balance_sheets (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      VARCHAR(10),
    fiscal_year                 SMALLINT,

    cash_and_short_term         NUMERIC,
    inventory                   NUMERIC,
    short_term_debt             NUMERIC,
    total_current_liabilities   NUMERIC,
    long_term_debt              NUMERIC,
    total_liabilities           NUMERIC,
    retained_earnings           NUMERIC,
    net_debt                    NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'balance_sheets',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX idx_balance_sheets_ticker ON balance_sheets(ticker_id, time DESC);


CREATE TABLE cash_flow_statements (
    time                    TIMESTAMPTZ NOT NULL,
    ticker_id               INTEGER NOT NULL REFERENCES tickers(id),
    period                  VARCHAR(10),
    fiscal_year             SMALLINT,

    net_income              NUMERIC,
    accounts_receivables    NUMERIC,
    net_change_in_cash      NUMERIC,
    cash_at_end_of_period   NUMERIC,
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

CREATE INDEX idx_cash_flow_ticker ON cash_flow_statements(ticker_id, time DESC);


-- ============================================================
-- DERIVED METRICS & RATIOS (Quarterly)
-- ============================================================

CREATE TABLE key_metrics (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      VARCHAR(10),
    fiscal_year                 SMALLINT,

    -- S tier
    return_on_invested_capital  NUMERIC,
    free_cash_flow_yield        NUMERIC,
    ev_to_free_cash_flow        NUMERIC,
    income_quality              NUMERIC,
    cash_conversion_cycle       NUMERIC,

    -- A tier
    return_on_assets            NUMERIC,
    net_debt_to_ebitda          NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'key_metrics',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX idx_key_metrics_ticker ON key_metrics(ticker_id, time DESC);


CREATE TABLE financial_ratios (
    time                    TIMESTAMPTZ NOT NULL,
    ticker_id               INTEGER NOT NULL REFERENCES tickers(id),
    period                  VARCHAR(10),
    fiscal_year             SMALLINT,

    gross_profit_margin     NUMERIC,
    ebitda_margin           NUMERIC,
    net_profit_margin       NUMERIC,
    inventory_turnover      NUMERIC,
    price_to_earnings       NUMERIC,
    debt_to_assets          NUMERIC,

    raw                     JSONB
);

SELECT create_hypertable(
    'financial_ratios',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX idx_financial_ratios_ticker ON financial_ratios(ticker_id, time DESC);


CREATE TABLE income_growth (
    time                        TIMESTAMPTZ NOT NULL,
    ticker_id                   INTEGER NOT NULL REFERENCES tickers(id),
    period                      VARCHAR(10),
    fiscal_year                 SMALLINT,

    growth_revenue              NUMERIC,
    growth_cost_of_revenue      NUMERIC,
    growth_gross_profit         NUMERIC,
    growth_gross_profit_ratio   NUMERIC,
    growth_ebitda               NUMERIC,
    growth_net_income           NUMERIC,

    raw                         JSONB
);

SELECT create_hypertable(
    'income_growth',
    'time',
    chunk_time_interval => INTERVAL '1 year',
    if_not_exists => TRUE
);

CREATE INDEX idx_income_growth_ticker ON income_growth(ticker_id, time DESC);