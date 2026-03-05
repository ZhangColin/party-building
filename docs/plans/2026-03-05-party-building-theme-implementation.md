# 党建主题样式统一化实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 将党建主题样式（中国红 + 金色）统一应用到所有导航/布局组件和自定义业务组件

**架构:** 混合方案 - 全局 CSS 类提供通用样式，组件级样式处理特殊场景

**技术栈:** Vue 3, Tailwind CSS, TypeScript, Element Plus

---

## 前置准备

### Task 0: 确认工作目录

**Step 1: 验证当前目录**

运行: `pwd`
预期: `/Users/zhangcolin/workspace/party-building`

**Step 2: 确认前端目录结构**

运行: `ls -la frontend/src/`
预期: 显示 components/, layouts/, views/, styles/ 等目录

**Step 3: 检查现有主题文件**

运行: `cat frontend/src/styles/party-theme.css`
预期: 显示已定义的 CSS 变量（--el-color-primary: #C8102E 等）

---

## 阶段一：全局样式基础设施

### Task 1: 扩展 Tailwind 配置添加党建色板

**Files:**
- Modify: `frontend/tailwind.config.js:10-88`

**Step 1: 打开 Tailwind 配置文件**

运行: `code frontend/tailwind.config.js`

**Step 2: 在 colors 对象中添加党建色系**

找到 `colors` 定义（约第 10 行），在 `info` 对象后添加：

```javascript
// 党建色彩系统
party: {
  red: {
    DEFAULT: '#C8102E',  // 中国红
    light: '#E84D56',    // 浅红
    dark: '#8B0000',     // 深红
    50: '#FEF2F2',
    100: '#FEE2E2',
    200: '#FECACA',
    300: '#FCA5A5',
    400: '#F87171',
    500: '#C8102E',
    600: '#A80D27',
    700: '#8B0000',
    800: '#6B0000',
    900: '#4B0000',
  },
  gold: {
    DEFAULT: '#FFD700',  // 五星金
    light: '#FFE55C',    // 浅金
    dark: '#CCB800',     // 深金
    50: '#FFFEF5',
    100: '#FFFECC',
    200: '#FFFDA6',
    300: '#FFF966',
    400: '#FFEF00',
    500: '#FFD700',
    600: '#CCB800',
    700: '#A69400',
    800: '#807000',
    900: '#594C00',
  },
  deepRed: '#8B0000',  // 党建深红
},
```

**Step 3: 保存并验证语法**

运行: `cd frontend && npm run build -- --mode development 2>&1 | head -20`
预期: 无 Tailwind 配置错误

**Step 4: 提交**

```bash
git add frontend/tailwind.config.js
git commit -m "feat(style): 扩展Tailwind配置添加党建色板

- 添加party.red色系（中国红渐变）
- 添加party.gold色系（金色装饰）
- 添加party.deepRed深红色

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: 在 party-theme.css 中添加全局 CSS 类

**Files:**
- Modify: `frontend/src/styles/party-theme.css:54-74`

**Step 1: 打开主题样式文件**

运行: `code frontend/src/styles/party-theme.css`

**Step 2: 在文件末尾添加全局 CSS 类**

在 `.party-emblem-icon` 样式后添加：

```css
/* ============================================
   党建主题全局样式类
   ============================================ */

/* 容器类 */
.party-card {
  background: white;
  border-left: 3px solid var(--party-color-gold);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.08);
  padding: 16px;
}

.party-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #EEEEEE;
  border-top: 3px solid var(--party-color-gold);
}

/* 标题装饰类 */
.party-title-underline {
  border-bottom: 2px solid var(--party-color-gold);
  padding-bottom: 8px;
  margin-bottom: 16px;
}

.party-title-bar {
  border-left: 4px solid var(--party-color-gold);
  padding-left: 12px;
  font-weight: 600;
}

/* 按钮类 */
.party-btn-primary {
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  border: none;
  color: white;
  border-radius: 4px;
  font-weight: 500;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.party-btn-primary:hover {
  background: linear-gradient(135deg, #D81030 0%, #A80D27 100%);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
}

.party-btn-secondary {
  background: white;
  border: 1px solid var(--party-color-gold);
  color: #8B0000;
  border-radius: 4px;
  font-weight: 500;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.party-btn-secondary:hover {
  background: #FFE55C;
  border-color: #FFD700;
}

/* 徽章/标签类 */
.party-badge {
  background: linear-gradient(135deg, #FFD700, #CCB800);
  color: #8B0000;
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.party-tag {
  background: linear-gradient(135deg, #C8102E, #E84D56);
  color: white;
  padding: 4px 12px;
  border-radius: 2px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

/* 分割线类 */
.party-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #FFD700, transparent);
  margin: 16px 0;
  border: none;
}

.party-divider-red {
  height: 2px;
  background: linear-gradient(90deg, transparent, #C8102E, transparent);
  margin: 16px 0;
  border: none;
}

/* 强调文字类 */
.party-text-gold {
  color: #CCB800;
  font-weight: 600;
}

.party-text-red {
  color: #C8102E;
  font-weight: 600;
}

/* 列表项激活态（用于菜单） */
.party-menu-item-active {
  background: linear-gradient(135deg, rgba(200, 16, 46, 0.1), rgba(139, 0, 0, 0.1));
  border-left: 3px solid #FFD700;
  color: #C8102E;
}
```

**Step 3: 保存并验证**

运行: `cd frontend && npm run build -- --mode development 2>&1 | grep -i "css\|error" | head -10`
预期: CSS 编译成功，无错误

**Step 4: 提交**

```bash
git add frontend/src/styles/party-theme.css
git commit -m "feat(style): 添加党建主题全局CSS类

- 添加容器类（party-card, party-section）
- 添加标题装饰类（party-title-underline, party-title-bar）
- 添加按钮类（party-btn-primary, party-btn-secondary）
- 添加徽章/标签类（party-badge, party-tag）
- 添加分割线类（party-divider, party-divider-red）
- 添加强调文字类（party-text-gold, party-text-red）
- 添加菜单激活态（party-menu-item-active）

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 阶段二：导航/布局组件改造

### Task 3: 改造 ModuleSwitcher 组件

**Files:**
- Modify: `frontend/src/components/ModuleSwitcher.vue:72-99`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/ModuleSwitcher.vue`

**Step 2: 修改激活状态样式**

找到 `.module-button.active` 样式块（约第 93 行），替换为：

```css
.module-button.active {
  @apply font-semibold;
  /* 党建主题：激活状态使用红色渐变背景 + 白色文字 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.4), 0 2px 4px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
}
```

**Step 3: 保存**

**Step 4: 本地测试**

运行: `cd frontend && npm run dev`
访问: `http://localhost:5173`
操作: 点击模块切换按钮
预期: 激活模块显示红色渐变背景 + 白色文字 + 金色边框

**Step 5: 提交**

```bash
git add frontend/src/components/ModuleSwitcher.vue
git commit -m "feat(style): ModuleSwitcher激活状态使用党建红色渐变

- 激活按钮使用红色渐变背景
- 添加金色边框装饰
- 增强阴影效果

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: 改造 SidebarMenu 组件

**Files:**
- Modify: `frontend/src/components/SidebarMenu.vue:56-85`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/SidebarMenu.vue`

**Step 2: 修改容器样式**

找到 `.sidebar-menu` 样式块（约第 57 行），修改为：

```css
.sidebar-menu {
  height: 100%;
  position: relative;
  transition: width 0.3s;
  /* 党建主题：淡红色背景 */
  background: linear-gradient(180deg, rgba(200, 16, 46, 0.03) 0%, rgba(139, 0, 0, 0.05) 100%);
  border-right: 1px solid rgba(200, 16, 46, 0.1);
}
```

**Step 3: 修改折叠按钮样式**

找到 `.collapse-button` 样式块（约第 75 行），修改为：

```css
.collapse-button {
  @apply absolute top-3 -right-4 w-8 h-8 rounded-full cursor-pointer flex items-center justify-center z-10 transition-all duration-200;
  /* 党建主题：白色背景 + 金色边框 */
  background: white;
  border: 1px solid #FFD700;
  color: #C8102E;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.15);
}

.collapse-button:hover {
  background: #FFF5E6;
  border-color: #C8102E;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.25);
}
```

**Step 4: 保存**

**Step 5: 本地测试**

运行: 保持 `npm run dev` 运行
访问: 任意有侧边栏的页面
预期: 侧边栏显示淡红色背景，折叠按钮有金色边框

**Step 6: 提交**

```bash
git add frontend/src/components/SidebarMenu.vue
git commit -m "feat(style): SidebarMenu应用党建主题

- 添加淡红色渐变背景
- 折叠按钮使用金色边框
- 优化阴影效果使用红色调

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: 改造 MenuItem 组件

**Files:**
- Modify: `frontend/src/components/MenuItem.vue`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/MenuItem.vue`

**Step 2: 读取当前样式**

先查看文件内容，确定需要修改的样式块

**Step 3: 应用党建主题样式**

根据当前样式结构，修改：
- 菜单项悬停态：淡红色背景
- 激活态：使用 `.party-menu-item-active` 类或内联样式
- 文字颜色：红色系

示例修改（具体根据实际文件内容调整）：

```css
/* 悬停态 */
.menu-item:hover {
  background: rgba(200, 16, 46, 0.08);
  color: #C8102E;
}

/* 激活态 */
.menu-item.active {
  background: linear-gradient(135deg, rgba(200, 16, 46, 0.1), rgba(139, 0, 0, 0.1));
  border-left: 3px solid #FFD700;
  color: #C8102E;
  font-weight: 600;
}
```

**Step 4: 保存**

**Step 5: 本地测试**

访问: 有侧边栏菜单的页面
操作: 点击菜单项
预期: 激活项显示金色左边框 + 红色文字

**Step 6: 提交**

```bash
git add frontend/src/components/MenuItem.vue
git commit -m "feat(style): MenuItem应用党建主题

- 激活项使用金色左边框
- 悬停态使用淡红色背景
- 调整文字颜色为红色系

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 阶段三：自定义业务组件改造

### Task 6: 改造 AgentList 卡片组件

**Files:**
- Modify: `frontend/src/components/AgentList.vue`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/AgentList.vue`

**Step 2: 为卡片容器添加 party-card 类**

找到卡片容器的 class 或 div，添加 `party-card` 类：

```vue
<div class="agent-list">
  <div
    v-for="agent in agents"
    :key="agent.id"
    class="agent-card party-card"
    @click="selectAgent(agent)"
  >
    <!-- 原有内容 -->
  </div>
</div>
```

**Step 3: 移除或调整原有样式**

在 `<style>` 中，移除与 `.party-card` 冲突的样式（如 border-left, background 等）

**Step 4: 保存**

**Step 5: 本地测试**

访问: AI工具页面
预期: Agent 卡片显示金色左边框

**Step 6: 提交**

```bash
git add frontend/src/components/AgentList.vue
git commit -m "feat(style): AgentList应用党建卡片样式

- 使用party-card类
- 显示金色左边框装饰

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: 改造 ConversationList 组件

**Files:**
- Modify: `frontend/src/components/ConversationList.vue`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/ConversationList.vue`

**Step 2: 应用党建主题样式**

类似 Task 6，为会话列表项添加 `party-card` 或 `party-menu-item-active` 类

**Step 3: 保存并测试**

**Step 4: 提交**

```bash
git add frontend/src/components/ConversationList.vue
git commit -m "feat(style): ConversationList应用党建主题

- 会话项使用党建卡片样式
- 激活会话金色左边框

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 8: 改造 ChatInput 发送按钮

**Files:**
- Modify: `frontend/src/components/ChatInput.vue`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/ChatInput.vue`

**Step 2: 修改发送按钮样式**

找到发送按钮，添加 `party-btn-primary` 类或修改样式：

```vue
<button
  class="send-button party-btn-primary"
  :disabled="!message.trim()"
  @click="sendMessage"
>
  发送
</button>
```

**Step 3: 保存并测试**

**Step 4: 提交**

```bash
git add frontend/src/components/ChatInput.vue
git commit -m "feat(style): ChatInput发送按钮使用党建样式

- 发送按钮使用红色渐变背景

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 9: 改造 PreviewPanel 工具栏

**Files:**
- Modify: `frontend/src/components/PreviewPanel.vue`

**Step 1: 打开组件文件**

运行: `code frontend/src/components/PreviewPanel.vue`

**Step 2: 添加金色分割线**

在工具栏区域添加 `.party-divider` 类：

```vue
<div class="preview-toolbar">
  <div class="toolbar-content">
    <!-- 工具栏内容 -->
  </div>
  <div class="party-divider"></div>
</div>
```

**Step 3: 保存并测试**

**Step 4: 提交**

```bash
git add frontend/src/components/PreviewPanel.vue
git commit -m "feat(style): PreviewPanel添加金色装饰分割线

- 工具栏底部添加金色渐变分割线

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 阶段四：批量改造剩余组件

### Task 10-15: 批量应用全局样式类

对以下组件重复应用相应的全局 CSS 类：

**Task 10: AIToolSelector**
- 使用 `.party-card` 类

**Task 11: UserInfo**
- 菜单项使用 `.party-menu-item-active` 激活态

**Task 12: WelcomeMessage**
- 标题使用 `.party-title-underline`

**Task 13: ToastNotification**
- 使用 `.party-tag` 样式

**Task 14: MediaChatInterface**
- 消息气泡应用红色主题

**Task 15: PreviewToolbar**
- 按钮使用 `.party-btn-primary`

每个任务遵循相同模式：
1. 打开文件
2. 添加对应的全局 CSS 类
3. 移除冲突样式
4. 本地测试
5. 提交

---

## 阶段五：验证与优化

### Task 16: 视觉一致性检查

**Step 1: 启动开发服务器**

运行: `cd frontend && npm run dev`

**Step 2: 逐页检查清单**

访问以下页面，验证党建样式一致性：

- [ ] 登录页 (`/login`) - 按钮红色渐变
- [ ] AI工具首页 (`/modules/ai-tools`) - 模块切换器激活态
- [ ] 聊天界面 - 发送按钮、消息气泡
- [ ] 侧边栏 - 菜单激活态金色边框
- [ ] 卡片组件 - 金色左边框
- [ ] 管理页面 - 统一党建主题

**Step 3: 使用浏览器开发工具**

运行: 打开 Chrome DevTools
操作: 检查元素，验证颜色值
检查点:
- 红色: `#C8102E` 或 `rgb(200, 16, 46)`
- 金色: `#FFD700` 或 `rgb(255, 215, 0)`

**Step 4: 响应式测试**

操作: 调整浏览器窗口大小
检查点:
- 移动端（<768px）
- 平板端（768px - 1023px）
- 桌面端（>1023px）

**Step 5: 控制台检查**

运行: 打开浏览器控制台
预期: 无 CSS 相关警告或错误

**Step 6: 提交验证结果**

创建验证报告文件：

```bash
cat > frontend/THEME_VERIFICATION.md << 'EOF'
# 党建主题样式验证报告

**日期:** 2026-03-05
**验证者:** Claude

## 验收结果

- [x] 视觉一致性 - 所有红色使用中国红系
- [x] 装饰统一 - 所有金色使用五星金
- [x] 功能完整性 - 所有组件功能正常
- [x] 响应式 - 移动/平板/桌面端无破坏
- [x] 无控制台错误

## 浏览器兼容性

- [x] Chrome/Edge
- [x] Safari
- [x] Firefox

## 已知问题

无

## 截图附件

（此处可添加截图）
EOF
```

提交:

```bash
git add frontend/THEME_VERIFICATION.md
git commit -m "test: 添加党建主题样式验证报告

- 确认视觉一致性
- 确认功能完整性
- 确认响应式兼容

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 17: 性能优化检查

**Step 1: 检查 CSS 文件大小**

运行: `cd frontend && npm run build`
操作: 查看 `dist/assets/*.css` 文件大小
预期: CSS 文件增长 < 50KB

**Step 2: 运行 Lighthouse 性能测试**

运行: 打开 Chrome Lighthouse
操作: 对主要页面运行审计
关注: Performance, Accessibility 颜色对比度

**Step 3: 提交优化建议（如有）**

如果发现性能问题，创建优化任务

---

## 阶段六：文档与收尾

### Task 18: 更新项目文档

**Step 1: 更新 CLAUDE.md**

在 `CLAUDE.md` 中添加样式规范说明：

```markdown
## 样式规范

### 党建主题色彩

项目使用党建主题色彩系统，定义在 `frontend/src/styles/party-theme.css`：

- **主红色:** `#C8102E`（中国红）
- **金色:** `#FFD700`（五星金）
- **深红色:** `#8B0000`

### 使用全局 CSS 类

优先使用预定义的全局类：
- `.party-card`: 卡片容器（金色左边框）
- `.party-btn-primary`: 主按钮（红色渐变）
- `.party-title-underline`: 标题装饰（金色底线）

详细类列表参见 `party-theme.css`。
```

**Step 2: 提交文档更新**

```bash
git add CLAUDE.md
git commit -m "docs: 添加党建主题样式规范说明

- 记录色彩系统
- 记录全局CSS类使用方法

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 19: 最终验证与发布准备

**Step 1: 运行完整测试套件**

运行: `cd frontend && npm run test`
预期: 所有单元测试通过

**Step 2: 构建生产版本**

运行: `cd frontend && npm run build`
预期: 构建成功，无错误

**Step 3: 检查构建产物**

运行: `ls -lh frontend/dist/`
预期: 输出文件结构正常

**Step 4: 创建发布标签（可选）**

```bash
git tag -a v1.0.0-party-theme -m "党建主题样式统一化完成"
git push origin v1.0.0-party-theme
```

**Step 5: 最终提交**

```bash
git add -A
git commit -m "chore: 完成党建主题样式统一化实施

- 全局CSS类定义完成
- 导航/布局组件改造完成
- 自定义业务组件改造完成
- 视觉一致性验证通过
- 文档更新完成

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 附录：故障排查

### 问题 1: 样式不生效

**症状:** 添加类名后样式未应用

**排查步骤:**
1. 检查 `party-theme.css` 是否在 `style.css` 中导入
2. 检查类名拼写是否正确
3. 使用 DevTools 检查样式优先级

**解决方案:**
```css
/* 确保样式权重足够 */
.party-card.party-card {
  /* 重复类名增加权重 */
}
```

---

### 问题 2: 颜色显示不正确

**症状:** 颜色与设计不符

**排查步骤:**
1. 使用 DevTools 检查计算后的颜色值
2. 检查是否有其他样式覆盖

**解决方案:**
```css
/* 使用 !important 作为最后手段 */
.party-btn-primary {
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%) !important;
}
```

---

### 问题 3: 响应式布局破坏

**症状:** 移动端样式错乱

**排查步骤:**
1. 检查媒体查询是否正确
2. 检查固定宽度值

**解决方案:**
```css
/* 使用相对单位 */
.party-card {
  padding: clamp(12px, 2vw, 16px);
}
```

---

## 完成标准

本实施计划完成后，应达到以下标准：

1. **视觉一致性:** 所有组件使用统一的党建色彩系统
2. **代码质量:** 遵循 DRY 原则，全局类复用率 > 80%
3. **用户体验:** 无视觉干扰，交互反馈清晰
4. **可维护性:** 新组件可快速应用党建主题
5. **性能:** CSS 增长 < 50KB，无性能退化

---

**实施估计时间:** 3-4 小时
**预计提交数:** ~20 个 commits
**建议实施顺序:** 按任务编号顺序执行
