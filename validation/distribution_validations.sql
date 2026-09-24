-- SQLite-ready validation script for bulk distribution QA
-- Run from the project root:
-- sqlite3 bulk_distribution_validation.db ".read validation/distribution_validations.sql"

.mode csv
.headers on
.nullvalue NULL

DROP TABLE IF EXISTS source_calculations;
DROP TABLE IF EXISTS distribution_output;

CREATE TABLE source_calculations (
    client_id TEXT,
    client_name TEXT,
    source_amount REAL,
    fee_pct REAL,
    expected_net_amount REAL
);

CREATE TABLE distribution_output (
    client_id TEXT,
    client_name TEXT,
    distributed_amount REAL,
    status TEXT
);

.import --skip 1 resources/source_calculations.csv source_calculations
.import --skip 1 resources/distribution_output.csv distribution_output

-- 1) Record count validation
-- Source calculations is the source of truth.
SELECT
    src.record_count AS source_record_count,
    dist.record_count AS distribution_record_count,
    src.record_count - dist.record_count AS record_count_difference
FROM (
    SELECT COUNT(*) AS record_count FROM source_calculations
) src
CROSS JOIN (
    SELECT COUNT(*) AS record_count FROM distribution_output
) dist
WHERE src.record_count <> dist.record_count;

-- 2) Missing records: source present but not in distribution, and distribution present but not in source.
SELECT
    s.client_id,
    s.client_name,
    s.source_amount,
    'MISSING_IN_DISTRIBUTION' AS validation_issue
FROM source_calculations s
LEFT JOIN distribution_output d
    ON s.client_id = d.client_id
WHERE d.client_id IS NULL

UNION ALL

SELECT
    d.client_id,
    d.client_name,
    NULL AS source_amount,
    'MISSING_IN_SOURCE' AS validation_issue
FROM distribution_output d
LEFT JOIN source_calculations s
    ON d.client_id = s.client_id
WHERE s.client_id IS NULL;

-- 3) Duplicate records
-- 3a) Duplicate by ClientID only
SELECT
    'source_calculations' AS table_name,
    client_id,
    client_name,
    source_amount,
    COUNT(*) AS duplicate_count
FROM source_calculations
GROUP BY client_id, client_name, source_amount
HAVING COUNT(*) > 1;

SELECT
    'distribution_output' AS table_name,
    client_id,
    client_name,
    distributed_amount AS source_amount,
    COUNT(*) AS duplicate_count
FROM distribution_output
GROUP BY client_id, client_name, distributed_amount
HAVING COUNT(*) > 1;

-- 3b) Duplicate by ClientID only (strict check)
SELECT
    'source_calculations' AS table_name,
    client_id,
    MIN(client_name) AS client_name,
    MIN(source_amount) AS source_amount,
    COUNT(*) AS duplicate_count
FROM source_calculations
GROUP BY client_id
HAVING COUNT(*) > 1;

SELECT
    'distribution_output' AS table_name,
    client_id,
    MIN(client_name) AS client_name,
    MIN(distributed_amount) AS source_amount,
    COUNT(*) AS duplicate_count
FROM distribution_output
GROUP BY client_id
HAVING COUNT(*) > 1;

-- 4) Calculation errors
-- Correct net amount = source_amount - (source_amount * fee_pct / 100)
SELECT
    s.client_id,
    s.source_amount,
    s.expected_net_amount,
    (s.source_amount - (s.source_amount * s.fee_pct / 100.0)) AS correct_net_amount
FROM source_calculations s
WHERE ABS(s.expected_net_amount - (s.source_amount - (s.source_amount * s.fee_pct / 100.0))) > 0.01;

-- 5) Negative source amounts
SELECT
    client_id,
    source_amount
FROM source_calculations
WHERE source_amount < 0;

-- 6) Zero distribution amounts
SELECT
    client_id,
    client_name,
    distributed_amount,
    status
FROM distribution_output
WHERE distributed_amount = 0;

-- 7) Rounding off discrepancies
SELECT
    s.client_id,
    s.expected_net_amount,
    d.distributed_amount,
    d.distributed_amount - s.expected_net_amount AS difference
FROM source_calculations s
INNER JOIN distribution_output d
    ON s.client_id = d.client_id
WHERE ABS(d.distributed_amount - s.expected_net_amount) > 0.01;
