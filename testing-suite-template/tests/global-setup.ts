import { chromium, firefox, webkit } from '@playwright/test';

/**
 * Global setup for all tests
 * Runs once before all test files
 */
async function globalSetup() {
  console.log('🚀 Starting Universal Testing Suite...');

  // Pre-install browsers if needed
  if (process.env.INSTALL_BROWSERS) {
    console.log('📦 Installing browsers...');
    await chromium.install();
    await firefox.install();
    await webkit.install();
  }

  // Set up test database or external services
  if (process.env.SETUP_TEST_DB) {
    console.log('🗄️ Setting up test database...');
    // Add your database setup logic here
  }

  // Set up test data
  if (process.env.SETUP_TEST_DATA) {
    console.log('📊 Setting up test data...');
    // Add your test data setup logic here
  }

  console.log('✅ Global setup complete');
}

export default globalSetup;