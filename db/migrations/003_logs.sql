CREATE TABLE IF NOT EXISTS sentinel_logs (
    id                  SERIAL PRIMARY KEY,
    run_date            DATE NOT NULL,
    market_baseline     NUMERIC,        -- market 30d performance
    flagged_sectors     JSONB,          -- structured outlier data
    notes               TEXT,           -- compressed markdown summary
    passed_to_analyst   BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_logs_run_date
    ON sentinel_logs(run_date DESC);


CREATE TABLE IF NOT EXISTS analyst_logs (
    id                  SERIAL PRIMARY KEY,
    sentinel_log_id     INTEGER REFERENCES sentinel_logs(id),
    run_date            DATE NOT NULL,
    sector              TEXT,
    sub_industry        TEXT,
    subsector_summary   TEXT,
    rankings            JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyst_logs_run_date
    ON analyst_logs(run_date DESC);

CREATE INDEX IF NOT EXISTS idx_analyst_logs_sentinel_id
    ON analyst_logs(sentinel_log_id);