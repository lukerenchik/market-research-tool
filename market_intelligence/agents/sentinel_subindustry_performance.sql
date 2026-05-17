WITH latest_prices AS (
    SELECT DISTINCT ON (ticker_id)
        ticker_id, price, time
    FROM stock_quotes
    ORDER BY ticker_id, time DESC
),
prior_prices AS (
    SELECT DISTINCT ON (ticker_id)
        ticker_id, price
    FROM stock_quotes
    WHERE time <= NOW() - INTERVAL '30 days'
    ORDER BY ticker_id, time DESC
)
SELECT
    gs.name                                          AS sector_name,
    gsi.name                                         AS sub_industry_name,
    COUNT(DISTINCT lp.ticker_id)                     AS ticker_count,
    ROUND(
        AVG(
            (lp.price - pp.price) / NULLIF(pp.price, 0) * 100
        )::numeric, 4
    )                                                AS avg_change_pct_30d
FROM latest_prices lp
JOIN prior_prices pp         ON pp.ticker_id = lp.ticker_id
JOIN tickers t               ON t.id = lp.ticker_id
JOIN gics_sectors gs         ON gs.id = t.sector_id
JOIN gics_sub_industries gsi ON gsi.id = t.sub_industry_id
WHERE t.is_active = TRUE
GROUP BY gs.name, gsi.name
HAVING COUNT(DISTINCT lp.ticker_id) >= 2
ORDER BY avg_change_pct_30d ASC;