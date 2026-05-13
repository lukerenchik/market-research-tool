-- Daily time-series (unique per ticker per day)
ALTER TABLE stock_quotes
    ADD CONSTRAINT uq_stock_quotes
    UNIQUE (ticker_id, time);

ALTER TABLE historical_market_cap
    ADD CONSTRAINT uq_historical_market_cap
    UNIQUE (ticker_id, time);

-- Quarterly financials (unique per ticker per period per year)
ALTER TABLE income_statements
    ADD CONSTRAINT uq_income_statements
    UNIQUE (ticker_id, time, period);

ALTER TABLE balance_sheets
    ADD CONSTRAINT uq_balance_sheets
    UNIQUE (ticker_id, time, period);

ALTER TABLE cash_flow_statements
    ADD CONSTRAINT uq_cash_flow_statements
    UNIQUE (ticker_id, time, period);

ALTER TABLE key_metrics
    ADD CONSTRAINT uq_key_metrics
    UNIQUE (ticker_id, time, period);

ALTER TABLE financial_ratios
    ADD CONSTRAINT uq_financial_ratios
    UNIQUE (ticker_id, time, period);

ALTER TABLE income_growth
    ADD CONSTRAINT uq_income_growth
    UNIQUE (ticker_id, time, period);

-- Employee count (unique per ticker per filing)
ALTER TABLE employee_count_history
    ADD CONSTRAINT uq_employee_count_history
    UNIQUE (ticker_id, time);