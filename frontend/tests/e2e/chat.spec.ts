/**
 * Chat E2E Tests - With real test user
 */
import { test, expect } from '@playwright/test';

// Real test user credentials (created by setup_e2e_user.py)
const TEST_USER = {
  account: 'e2etest@example.com',
  password: 'Test123456!'
};

test.describe('Login Flow', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('http://localhost:5174/login');

    // Verify login form exists
    await expect(page.locator('input[type="email"], input[type="text"]').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("登录")').first()).toBeVisible();
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('http://localhost:5174/modules/ai-tools');

    await page.waitForURL(/\/login/, { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:5174/login');

    // Fill login form
    await page.fill('input[type="email"], input[type="text"]', TEST_USER.account);
    await page.fill('input[type="password"]', TEST_USER.password);

    // Submit login
    await page.click('button[type="submit"], button:has-text("登录")');

    // Should redirect to tools page
    await page.waitForURL(/\/modules\/ai-tools/, { timeout: 10000 });
    expect(page.url()).toContain('/modules/ai-tools');
  });
});

test.describe('Tool Selection (requires login)', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:5174/login');
    await page.fill('input[type="email"], input[type="text"]', TEST_USER.account);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"], button:has-text("登录")');
    await page.waitForURL(/\/modules\/ai-tools/, { timeout: 10000 });
  });

  test('should display tool list', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Wait a bit for dynamic content
    await page.waitForTimeout(2000);

    // Try to find tool list or sidebar
    const toolSelectors = [
      '.tool-list',
      '.tool-selector',
      '.sidebar',
      '.tool-category',
      '.tool-card'
    ];

    let found = false;
    for (const selector of toolSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 3000 })) {
          console.log(`✅ Found element with selector: ${selector}`);
          found = true;
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!found) {
      // Take screenshot for debugging
      await page.screenshot({ path: 'test-results/debug-tool-list.png', fullPage: true });

      // Check what's actually on the page
      const bodyText = await page.locator('body').textContent();
      console.log('Page content preview:', bodyText?.substring(0, 200));

      throw new Error('Tool list not found. Screenshot saved to test-results/debug-tool-list.png');
    }

    expect(found).toBeTruthy();
  });

  test('should select first tool', async ({ page }) => {
    // Wait for content to load
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Find and click first tool card
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();

    await expect(toolCard).toBeVisible({ timeout: 5000 });
    await toolCard.click();
    console.log('✅ Clicked first tool card');

    // Wait for Vue to process the click
    await page.waitForTimeout(1500);

    // Verify we stayed on the same page (URL didn't change unexpectedly)
    expect(page.url()).toContain('/modules/ai-tools');

    // Verify sidebar is still visible (meaning we didn't navigate away)
    const sidebar = page.locator('.sidebar, .tool-selector').first();
    await expect(sidebar).toBeVisible({ timeout: 3000 });
  });

  test('should display collapse button', async ({ page }) => {
    // Wait for content
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Look for collapse button
    const collapseButton = page.locator('.collapse-button, [class*="collapse"], button:has([class*="chevron"])').first();

    try {
      await expect(collapseButton).toBeVisible({ timeout: 5000 });
      console.log('✅ Found collapse button');
    } catch (e) {
      await page.screenshot({ path: 'test-results/debug-collapse-button.png', fullPage: true });
      throw new Error('Collapse button not found. Screenshot saved.');
    }
  });
});

test.describe('Basic UI (no login required)', () => {
  test('should load frontend', async ({ page }) => {
    await page.goto('http://localhost:5174/');

    // Should show app container
    await expect(page.locator('#app')).toBeVisible({ timeout: 5000 });
  });

  test('should have Vue loaded', async ({ page }) => {
    await page.goto('http://localhost:5174/');

    // Check Vue is loaded by looking for the app
    const appExists = await page.locator('#app').count();
    expect(appExists).toBeGreaterThan(0);
  });
});

test.describe('Real Chat Flow (End-to-End)', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:5174/login');
    await page.fill('input[type="email"], input[type="text"]', TEST_USER.account);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"], button:has-text("登录")');
    await page.waitForURL(/\/modules\/ai-tools/, { timeout: 10000 });
  });

  test('complete chat flow with real AI response', async ({ page }) => {
    console.log('Starting real E2E chat test...');

    // 1. Wait for tools
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });
    console.log('Step 1: Tools loaded');

    // 2. Select tool
    await toolCard.click();
    await page.waitForTimeout(1500);
    console.log('Step 2: Tool selected');

    // 3. Find input
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    console.log('Step 3: Chat input found');

    // 4. Type message
    const testMessage = 'Hello, please introduce yourself briefly';
    await chatInput.fill(testMessage);
    console.log('Step 4: Message typed');

    // 5. Send message
    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();
    console.log('Step 5: Message sent');

    // 6. Wait for user message to appear
    const userMessage = page.locator('[data-testid="message-item"]').first();
    await expect(userMessage).toBeVisible({ timeout: 5000 });
    console.log('Step 6: User message displayed');

    // 7. Wait for AI response (this may take 30-60 seconds)
    console.log('Step 7: Waiting for AI response (up to 60 seconds)...');

    const aiMessage = page.locator('[data-testid="message-item"]').nth(1);

    try {
      await expect(aiMessage).toBeVisible({ timeout: 60000 });
      console.log('Step 7: AI response received');

      const aiMessageContent = await aiMessage.textContent();
      console.log(`AI response length: ${aiMessageContent?.length || 0} characters`);
      console.log(`AI response content: "${aiMessageContent?.trim()}"`);

      // Verify response is not empty
      expect(aiMessageContent?.trim().length).toBeGreaterThan(0);
      console.log('Step 8: AI response validated');

      console.log('✅ Real E2E chat test PASSED!');
    } catch (e) {
      console.log('❌ AI response timeout (60 seconds)');
      console.log('Possible reasons:');
      console.log('  - AI API not configured or invalid key');
      console.log('  - Network issues');
      console.log('  - Backend service errors');

      await page.screenshot({
        path: 'test-results/failed-ai-response.png',
        fullPage: true
      });

      throw new Error('AI response timeout - check backend logs and API configuration');
    }
  });

  test('Shift+Enter for newline', async ({ page }) => {
    // Select tool
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await toolCard.click();
    await page.waitForTimeout(1500);

    // Find input and test Shift+Enter
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });

    await chatInput.fill('Line 1');
    await chatInput.press('Shift+Enter');
    await chatInput.type('Line 2');

    const inputValue = await chatInput.inputValue();
    expect(inputValue).toContain('Line 1\nLine 2');

    // Verify message not sent
    const messages = await page.locator('[data-testid="message-item"]').count();
    expect(messages).toBe(0);
  });
});
