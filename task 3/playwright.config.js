// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 30_000,
    expect: {
        timeout: 5_000,
    },
    reporter: [['list'], ['html', { open: 'never' }]],
    use: {
        trace: 'retain-on-failure',
    },
});