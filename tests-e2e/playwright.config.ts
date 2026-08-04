import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'npm run preview --prefix ../frontend-web -- --port 5173',
      url: 'http://localhost:5173',
      reuseExistingServer: false,
      timeout: 120 * 1000,
    },
    {
      command: 'npm run preview --prefix ../frontend-client -- --port 5174',
      url: 'http://localhost:5174',
      reuseExistingServer: false,
      timeout: 120 * 1000,
    }
  ],
});
