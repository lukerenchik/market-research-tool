WITH timeframes AS (
    SELECT unnest(ARRAY[7, 30, 90, 365, 1825]) AS window_days
),
latest_prices AS (
    SELECT DISTINCT ON (ticker_id)
        ticker_id, price, time
    FROM stock_quotes
    ORDER BY ticker_id, time DESC
),
baseline AS (
    SELECT
        tf.window_days,
        AVG(
            (lp.price - hp.price) / NULLIF(hp.price, 0) * 100
        ) AS avg_change_pct
    FROM timeframes tf
    CROSS JOIN latest_prices lp
    JOIN LATERAL (
        SELECT DISTINCT ON (ticker_id)
            price
        FROM stock_quotes
        WHERE ticker_id = lp.ticker_id
          AND time <= NOW() - (tf.window_days || ' days')::INTERVAL
        ORDER BY ticker_id, time DESC
    ) hp ON true
    GROUP BY tf.window_days
)
SELECT window_days, ROUND(avg_change_pct::numeric, 4) AS avg_change_pct
FROM baseline
ORDER BY window_days;