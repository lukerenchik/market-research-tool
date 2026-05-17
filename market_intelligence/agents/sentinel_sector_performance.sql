WITH timeframes AS (
    SELECT unnest(ARRAY[7, 30, 90, 365, 1825]) AS window_days
),
latest_prices AS (
    SELECT DISTINCT ON (ticker_id)
        ticker_id, price, time
    FROM stock_quotes
    ORDER BY ticker_id, time DESC
),
sector_perf AS (
    SELECT
        gs.name AS sector_name,
        tf.window_days,
        AVG(
            (lp.price - hp.price) / NULLIF(hp.price, 0) * 100
        ) AS avg_change_pct,
        COUNT(DISTINCT lp.ticker_id) AS ticker_count
    FROM timeframes tf
    CROSS JOIN latest_prices lp
    JOIN tickers t ON t.id = lp.ticker_id
    JOIN gics_sectors gs ON gs.id = t.sector_id
    JOIN LATERAL (
        SELECT DISTINCT ON (ticker_id)
            price
        FROM stock_quotes
        WHERE ticker_id = lp.ticker_id
          AND time <= NOW() - (tf.window_days || ' days')::INTERVAL
        ORDER BY ticker_id, time DESC
    ) hp ON true
    WHERE t.is_active = TRUE
    GROUP BY gs.name, tf.window_days
)
SELECT
    sector_name,
    window_days,
    ROUND(avg_change_pct::numeric, 4) AS avg_change_pct,
    ticker_count
FROM sector_perf
ORDER BY window_days, avg_change_pct DESC;