/**
 * AI 内容保存功能 E2E 测试
 * 测试用户保存 AI 回复到知识库和党建活动的功能
 */
import { test, expect } from '@playwright/test';

// Real test user credentials (created by setup_e2e_user.py)
const TEST_USER = {
  account: 'e2etest@example.com',
  password: 'Test123456!'
};

test.describe('AI 内容保存功能', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5174/login');
    await page.fill('input[type="email"], input[type="text"]', TEST_USER.account);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"], button:has-text("登录")');
    await page.waitForURL(/\/modules\/ai-tools/, { timeout: 10000 });
  });

  test('应该显示 AI 回复的保存按钮', async ({ page }) => {
    // 等待工具加载
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });

    // 选择第一个工具
    await toolCard.click();
    await page.waitForTimeout(1500);

    // 发送消息
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill('写一个简单的测试函数');

    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();

    // 等待 AI 回复（可能需要较长时间）
    console.log('等待 AI 回复...');
    const assistantMessage = page.locator('[data-testid="message-item"][data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible({ timeout: 60000 });
    console.log('AI 回复已接收');

    // 将鼠标悬停在 AI 回复上以显示工具栏
    await assistantMessage.hover();
    await page.waitForTimeout(500); // 等待工具栏动画完成

    // 验证保存按钮存在（应该是 2 个：保存到知识库、保存到党建活动）
    const saveButtons = assistantMessage.locator('.save-button');
    const count = await saveButtons.count();
    console.log(`找到 ${count} 个保存按钮`);

    expect(count).toBe(2);

    // 验证按钮标题属性
    const firstButton = saveButtons.first();
    await expect(firstButton).toHaveAttribute('title', '保存到知识库');

    const secondButton = saveButtons.nth(1);
    await expect(secondButton).toHaveAttribute('title', '保存到党建活动');
  });

  test('应该能够打开保存到知识库对话框', async ({ page }) => {
    // 等待工具加载
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });

    // 选择第一个工具
    await toolCard.click();
    await page.waitForTimeout(1500);

    // 发送消息
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill('写一段测试文本');

    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();

    // 等待 AI 回复
    console.log('等待 AI 回复...');
    const assistantMessage = page.locator('[data-testid="message-item"][data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible({ timeout: 60000 });
    console.log('AI 回复已接收');

    // 将鼠标悬停在 AI 回复上
    await assistantMessage.hover();
    await page.waitForTimeout(500);

    // 点击第一个保存按钮（保存到知识库）
    const firstSaveButton = assistantMessage.locator('.save-button').first();
    await firstSaveButton.click();

    // 验证保存对话框打开
    const dialog = page.locator('.el-dialog');
    await expect(dialog).toBeVisible({ timeout: 3000 });

    // 验证对话框标题
    const dialogTitle = dialog.locator('.el-dialog__title');
    await expect(dialogTitle).toContainText('保存到知识库');

    // 验证表单元素存在
    const cascader = dialog.locator('.el-cascader');
    await expect(cascader).toBeVisible();

    const filenameInput = dialog.locator('input[placeholder*="文件名"], input.el-input__inner');
    await expect(filenameInput).toBeVisible();

    // 验证保存按钮存在
    const saveButton = dialog.locator('button:has-text("保存"), button.el-button--primary');
    await expect(saveButton).toBeVisible();

    // 关闭对话框（因为可能没有目录数据）
    const cancelButton = dialog.locator('button:has-text("取消")');
    await cancelButton.click();
    await expect(dialog).not.toBeVisible({ timeout: 2000 });
  });

  test('应该能够打开保存到党建活动对话框', async ({ page }) => {
    // 等待工具加载
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });

    // 选择第一个工具
    await toolCard.click();
    await page.waitForTimeout(1500);

    // 发送消息
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill('写一段党建相关的内容');

    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();

    // 等待 AI 回复
    console.log('等待 AI 回复...');
    const assistantMessage = page.locator('[data-testid="message-item"][data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible({ timeout: 60000 });
    console.log('AI 回复已接收');

    // 将鼠标悬停在 AI 回复上
    await assistantMessage.hover();
    await page.waitForTimeout(500);

    // 点击第二个保存按钮（保存到党建活动）
    const secondSaveButton = assistantMessage.locator('.save-button').nth(1);
    await secondSaveButton.click();

    // 验证保存对话框打开
    const dialog = page.locator('.el-dialog');
    await expect(dialog).toBeVisible({ timeout: 3000 });

    // 验证对话框标题
    const dialogTitle = dialog.locator('.el-dialog__title');
    await expect(dialogTitle).toContainText('保存到党建活动');

    // 关闭对话框
    const cancelButton = dialog.locator('button:has-text("取消")');
    await cancelButton.click();
    await expect(dialog).not.toBeVisible({ timeout: 2000 });
  });

  test('工具栏应该在鼠标悬停时显示', async ({ page }) => {
    // 等待工具加载
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });

    // 选择第一个工具
    await toolCard.click();
    await page.waitForTimeout(1500);

    // 发送消息
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill('你好');

    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();

    // 等待 AI 回复
    console.log('等待 AI 回复...');
    const assistantMessage = page.locator('[data-testid="message-item"][data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible({ timeout: 60000 });
    console.log('AI 回复已接收');

    // 工具栏默认应该是隐藏的（opacity: 0）
    const toolbar = assistantMessage.locator('.message-toolbar');
    await expect(toolbar).toBeVisible(); // 元素存在但可能透明

    // 鼠标移开
    await page.mouse.move(0, 0);
    await page.waitForTimeout(300);

    // 检查工具栏的 opacity（悬停前应该透明）
    const opacityBefore = await toolbar.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacityBefore)).toBeLessThan(0.5);

    // 鼠标悬停
    await assistantMessage.hover();
    await page.waitForTimeout(300);

    // 检查工具栏的 opacity（悬停后应该不透明）
    const opacityAfter = await toolbar.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacityAfter)).toBeGreaterThan(0.5);
  });

  test('代码块应该正确渲染', async ({ page }) => {
    // 等待工具加载
    await page.waitForTimeout(2000);
    const toolCard = page.locator('.tool-card, .tool-item, [class*="tool"]').first();
    await expect(toolCard).toBeVisible({ timeout: 5000 });

    // 选择第一个工具
    await toolCard.click();
    await page.waitForTimeout(1500);

    // 发送消息要求生成代码
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill('写一个 JavaScript 函数，计算数组的和');

    const sendButton = page.locator('button:has-text("发送"), button[type="submit"], [class*="send"]').first();
    await expect(sendButton).toBeVisible({ timeout: 3000 });
    await sendButton.click();

    // 等待 AI 回复
    console.log('等待 AI 回复...');
    const assistantMessage = page.locator('[data-testid="message-item"][data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible({ timeout: 60000 });
    console.log('AI 回复已接收');

    // 查找代码块（markdown 渲染后的代码块）
    const codeBlock = assistantMessage.locator('pre code, .code-block-wrapper').first();
    await expect(codeBlock).toBeVisible({ timeout: 5000 });
  });
});
