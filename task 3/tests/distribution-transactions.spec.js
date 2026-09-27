const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const { test, expect } = require('@playwright/test');

const dbPath = path.resolve(__dirname, '..', '..', 'resources', 'distribution_qa (1).db');

function runQuery(sql, params = []) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (openErr) => {
            if (openErr) {
                reject(openErr);
            }
        });

        db.all(sql, params, (queryErr, rows) => {
            db.close((closeErr) => {
                if (queryErr) {
                    reject(queryErr);
                    return;
                }
                if (closeErr) {
                    reject(closeErr);
                    return;
                }
                resolve(rows);
            });
        });
    });
}

async function getDefaultPeriod() {
    const rows = await runQuery(`
    SELECT substr(transaction_date, 1, 7) AS period
    FROM Transactions
    WHERE transaction_date IS NOT NULL
      AND length(transaction_date) >= 7
    ORDER BY transaction_date DESC
    LIMIT 1
  `);

    if (!rows.length || !rows[0].period) {
        throw new Error('No transaction period found in Transactions table.');
    }

    return rows[0].period;
}

async function getDefaultDistributionPeriod() {
    const rows = await runQuery(`
        SELECT period
        FROM Distributions
        WHERE period IS NOT NULL
            AND length(period) >= 7
        ORDER BY period DESC
        LIMIT 1
    `);

    if (!rows.length || !rows[0].period) {
        throw new Error('No distribution period found in Distributions table.');
    }

    return rows[0].period;
}

function getPeriodOverride(name) {
    const value = process.env[name];
    if (value === undefined || value === null) {
        return undefined;
    }
    const trimmed = String(value).trim();
    return trimmed === '' ? undefined : trimmed;
}

function getNextMonthPeriod(period) {
    const match = /^(\d{4})-(\d{2})$/.exec(period);
    if (!match) {
        throw new Error(`Invalid period format: "${period}". Expected YYYY-MM.`);
    }

    const year = Number(match[1]);
    const month = Number(match[2]);
    if (month < 1 || month > 12) {
        throw new Error(`Invalid month in period: "${period}". Expected month between 01 and 12.`);
    }

    const date = new Date(Date.UTC(year, month - 1, 1));
    date.setUTCMonth(date.getUTCMonth() + 1);
    const nextYear = date.getUTCFullYear();
    const nextMonth = String(date.getUTCMonth() + 1).padStart(2, '0');

    return `${nextYear}-${nextMonth}`;
}

function formatAmount(value) {
    const amount = Number(value || 0);
    return amount.toFixed(2);
}

test.describe('Distribution and Transaction Validation by Period', () => {
    let distributionPeriod;
    let transactionPeriod;

    test.beforeAll(async () => {
        const forcedPeriod = getPeriodOverride('TEST_PERIOD');
        const distributionOverride = getPeriodOverride('DISTRIBUTION_PERIOD');
        const transactionOverride = getPeriodOverride('TRANSACTION_PERIOD');

        distributionPeriod = distributionOverride || forcedPeriod || (await getDefaultDistributionPeriod());

        if (transactionOverride) {
            transactionPeriod = transactionOverride;
        } else if (distributionOverride || forcedPeriod) {
            transactionPeriod = getNextMonthPeriod(distributionPeriod);
        } else {
            transactionPeriod = await getDefaultPeriod();
        }

        const distributionSummary = await runQuery(
            `
            SELECT COUNT(*) AS row_count, ROUND(COALESCE(SUM(distributed_amount), 0), 2) AS total_amount
            FROM Distributions
            WHERE period = ?
            `,
            [distributionPeriod]
        );

        const transactionSummary = await runQuery(
            `
            SELECT COUNT(*) AS row_count, ROUND(COALESCE(SUM(amount), 0), 2) AS total_amount
            FROM Transactions
            WHERE substr(transaction_date, 1, 7) = ?
            `,
            [transactionPeriod]
        );

        test.info().annotations.push({ type: 'distributionPeriod', description: distributionPeriod });
        test.info().annotations.push({ type: 'transactionPeriod', description: transactionPeriod });

        console.log('[period-selection] distributionPeriod:', distributionPeriod);
        console.log('[period-selection] transactionPeriod:', transactionPeriod);
        console.log(
            '[period-selection] distributionAmountTotal:',
            formatAmount(distributionSummary[0]?.total_amount),
            '| rows:',
            distributionSummary[0]?.row_count ?? 0
        );
        console.log(
            '[period-selection] transactionAmountTotal:',
            formatAmount(transactionSummary[0]?.total_amount),
            '| rows:',
            transactionSummary[0]?.row_count ?? 0
        );
    });

    test('Test 1: All distributions are COMPLETED for selected period', async () => {
        const incompleteRows = await runQuery(
            `
      SELECT distribution_id, client_id, status
      FROM Distributions
      WHERE period = ?
        AND UPPER(status) <> 'COMPLETED'
      ORDER BY distribution_id
      `,
            [distributionPeriod]
        );

        const periodRows = await runQuery(
            `
      SELECT COUNT(*) AS cnt
      FROM Distributions
      WHERE period = ?
      `,
            [distributionPeriod]
        );

        expect(
            periodRows[0].cnt,
            `No distributions found for period ${distributionPeriod}`
        ).toBeGreaterThan(0);
        expect(
            incompleteRows,
            `Found distributions not COMPLETED for period ${distributionPeriod}: ${JSON.stringify(incompleteRows)}`
        ).toHaveLength(0);
    });

    test('Test 2: All transactions are APPROVED for selected period (YYYY-MM from transaction_date)', async () => {
        const nonApprovedRows = await runQuery(
            `
      SELECT transaction_id, client_id, distribution_id, status, transaction_date
      FROM Transactions
      WHERE substr(transaction_date, 1, 7) = ?
        AND UPPER(status) <> 'APPROVED'
      ORDER BY transaction_id
      `,
            [transactionPeriod]
        );

        const periodRows = await runQuery(
            `
      SELECT COUNT(*) AS cnt
      FROM Transactions
      WHERE substr(transaction_date, 1, 7) = ?
      `,
            [transactionPeriod]
        );

        expect(
            periodRows[0].cnt,
            `No transactions found for period ${transactionPeriod}`
        ).toBeGreaterThan(0);
        expect(
            nonApprovedRows,
            `Found non-APPROVED transactions for period ${transactionPeriod}: ${JSON.stringify(nonApprovedRows)}`
        ).toHaveLength(0);
    });

    test('Test 3: No COMPLETED distribution exists without APPROVED transaction', async () => {
        const missingApprovedRows = await runQuery(
            `
      SELECT d.distribution_id, d.client_id, d.period, d.status AS distribution_status
      FROM Distributions d
      LEFT JOIN Transactions t
        ON t.distribution_id = d.distribution_id
       AND t.client_id = d.client_id
       AND UPPER(t.status) = 'APPROVED'
      WHERE d.period = ?
        AND UPPER(d.status) = 'COMPLETED'
        AND t.transaction_id IS NULL
      ORDER BY d.distribution_id
      `,
            [distributionPeriod]
        );

        expect(
            missingApprovedRows,
            `Found COMPLETED distributions without APPROVED transaction for ${distributionPeriod}: ${JSON.stringify(missingApprovedRows)}`
        ).toHaveLength(0);
    });

    test('Test 4: Client from distribution is present in transactions', async () => {
        const missingClientRows = await runQuery(
            `
      SELECT d.distribution_id, d.client_id, d.period
      FROM Distributions d
      LEFT JOIN Transactions t
        ON t.distribution_id = d.distribution_id
       AND t.client_id = d.client_id
      WHERE d.period = ?
        AND t.transaction_id IS NULL
      ORDER BY d.distribution_id
      `,
            [distributionPeriod]
        );

        expect(
            missingClientRows,
            `Found clients in Distributions but missing in Transactions for distribution period ${distributionPeriod}: ${JSON.stringify(missingClientRows)}`
        ).toHaveLength(0);
    });

    test('Test 5: No COMPLETED distribution has REJECTED transaction', async () => {
        const rejectedRows = await runQuery(
            `
      SELECT d.distribution_id, d.client_id, d.period, t.transaction_id, t.status
      FROM Distributions d
      JOIN Transactions t
        ON t.distribution_id = d.distribution_id
       AND t.client_id = d.client_id
      WHERE d.period = ?
        AND UPPER(d.status) = 'COMPLETED'
        AND UPPER(t.status) = 'REJECTED'
      ORDER BY t.transaction_id
      `,
            [distributionPeriod]
        );

        expect(
            rejectedRows,
            `Found COMPLETED distributions with REJECTED transactions for ${distributionPeriod}: ${JSON.stringify(rejectedRows)}`
        ).toHaveLength(0);
    });

    test('Test 6: No COMPLETED distribution has PENDING transaction', async () => {
        const pendingRows = await runQuery(
            `
      SELECT d.distribution_id, d.client_id, d.period, t.transaction_id, t.status
      FROM Distributions d
      JOIN Transactions t
        ON t.distribution_id = d.distribution_id
       AND t.client_id = d.client_id
      WHERE d.period = ?
        AND UPPER(d.status) = 'COMPLETED'
        AND UPPER(t.status) = 'PENDING'
      ORDER BY t.transaction_id
      `,
            [distributionPeriod]
        );

        expect(
            pendingRows,
            `Found COMPLETED distributions with PENDING transactions for ${distributionPeriod}: ${JSON.stringify(pendingRows)}`
        ).toHaveLength(0);
    });
});