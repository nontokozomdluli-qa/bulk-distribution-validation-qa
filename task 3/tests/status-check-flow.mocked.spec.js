const { test, expect } = require('@playwright/test');

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class NotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = 'NotFoundError';
    }
}

function createStatusCheckFlow(records) {
    return {
        getDistributionStatus(clientId, period) {
            if (!clientId || String(clientId).trim() === '') {
                throw new ValidationError('clientId is required');
            }
            if (!period || String(period).trim() === '') {
                throw new ValidationError('period is required in YYYY-MM format');
            }

            const normalizedClientId = String(clientId).trim().toUpperCase();
            const normalizedPeriod = String(period).trim();
            if (!/^[A-Z]\d+$/.test(normalizedClientId)) {
                throw new ValidationError('clientId must follow Letter+Number format (e.g., C101)');
            }
            const row = records.find(
                (record) =>
                    record.clientId.toUpperCase() === normalizedClientId &&
                    record.period === normalizedPeriod
            );

            if (!row) {
                throw new NotFoundError(
                    `No distribution found for clientId=${normalizedClientId}, period=${normalizedPeriod}`
                );
            }

            return {
                clientId: normalizedClientId,
                period: normalizedPeriod,
                status: row.status,
                distributedAmount: row.distributedAmount,
            };
        },
    };
}

const mockedRecords = [
    { clientId: 'C101', period: '2026-06', status: 'COMPLETED', distributedAmount: 3250.4 },
    { clientId: 'C108', period: '2026-06', status: 'PENDING', distributedAmount: 0 },
    { clientId: 'C109', period: '2026-06', status: 'FAILED', distributedAmount: 0 },
];

test.describe('Status-check flow (fully mocked, local-only)', () => {
    let flow;

    test.beforeEach(() => {
        // Isolated in-memory fixture makes the flow deterministic and CI-friendly.
        flow = createStatusCheckFlow(mockedRecords);
    });

    test('test 1: returns COMPLETED status and distributed amount for a valid client/period', async () => {
        const response = flow.getDistributionStatus('C101', '2026-06');

        expect(response).toEqual({
            clientId: 'C101',
            period: '2026-06',
            status: 'COMPLETED',
            distributedAmount: 3250.4,
        });
    });

    test('test 2: returns PENDING status for a distribution that is still in progress', async () => {
        const response = flow.getDistributionStatus('C108', '2026-06');

        expect(response.status).toBe('PENDING');
        expect(response.distributedAmount).toBe(0);
    });

    test('test 3: returns FAILED status for a distribution that did not process', async () => {
        const response = flow.getDistributionStatus('C109', '2026-06');

        expect(response.status).toBe('FAILED');
        expect(response.distributedAmount).toBe(0);
    });

    test('test 4: throws NotFoundError for an unknown but valid-format client ID', async () => {
        expect(() => flow.getDistributionStatus('C999', '2026-06')).toThrow(NotFoundError);
        expect(() => flow.getDistributionStatus('C999', '2026-06')).toThrow(
            'No distribution found for clientId=C999, period=2026-06'
        );
    });

    test('test 5: throws ValidationError when period is missing', async () => {
        expect(() => flow.getDistributionStatus('C101', '')).toThrow(ValidationError);
        expect(() => flow.getDistributionStatus('C101', '')).toThrow(
            'period is required in YYYY-MM format'
        );
    });

    test('test 6: throws NotFoundError when distribution period is missing for an existing client', async () => {
        expect(() => flow.getDistributionStatus('C101', '2026-07')).toThrow(NotFoundError);
        expect(() => flow.getDistributionStatus('C101', '2026-07')).toThrow(
            'No distribution found for clientId=C101, period=2026-07'
        );
    });

    test('test 7: throws ValidationError when client ID format is invalid', async () => {
        expect(() => flow.getDistributionStatus('101', '2026-06')).toThrow(ValidationError);
        expect(() => flow.getDistributionStatus('101', '2026-06')).toThrow(
            'clientId must follow Letter+Number format (e.g., C101)'
        );
    });
});
