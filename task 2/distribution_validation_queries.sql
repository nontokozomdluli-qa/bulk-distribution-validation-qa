-- Task 2: single SQL script
-- 1) Clients in distribution output with no corresponding approved transaction
SELECT
    c.client_id,
    c.client_name,
    d.distribution_id,
    d.period,
    d.distributed_amount
FROM Distributions d
JOIN Clients c
    ON c.client_id = d.client_id
LEFT JOIN Transactions t
    ON t.distribution_id = d.distribution_id
   AND t.client_id = d.client_id
   AND t.status = 'APPROVED'
WHERE t.transaction_id IS NULL
ORDER BY d.period, c.client_id;

-- 2) Total distributed amount per month
SELECT
    period,
    ROUND(SUM(distributed_amount), 2) AS total_distributed_amount
FROM Distributions
GROUP BY period
ORDER BY period;

-- 3) Clients whose distributed amount differs from calculated source amount by more than $0.01
SELECT
    c.client_id,
    c.client_name,
    s.period,
    s.source_amount,
    s.fee_pct,
    ROUND(s.source_amount * (1 - s.fee_pct), 2) AS calculated_source_amount,
    d.distributed_amount,
    ROUND(ABS(d.distributed_amount - (s.source_amount * (1 - s.fee_pct))), 4) AS difference
FROM SourceCalculations s
JOIN Distributions d
    ON d.client_id = s.client_id
   AND d.period = s.period
JOIN Clients c
    ON c.client_id = s.client_id
WHERE ABS(d.distributed_amount - (s.source_amount * (1 - s.fee_pct))) > 0.01
ORDER BY s.period, c.client_id;
