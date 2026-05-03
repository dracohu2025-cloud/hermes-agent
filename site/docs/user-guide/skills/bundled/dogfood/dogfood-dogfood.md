---
title: "Dogfood — Web 应用的探索性质量保证：发现 Bug、证据、报告"
sidebar_label: "Dogfood"
description: "Web 应用的探索性质量保证：发现 Bug、证据、报告"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Dogfood {#dogfood}

Web 应用的探索性质量保证：发现 Bug、证据、报告。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/dogfood` |
| 版本 | `1.0.0` |
| 标签 | `qa`, `testing`, `browser`, `web`, `dogfood` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Dogfood：系统性 Web 应用 QA 测试 {#dogfood-systematic-web-application-qa-testing}

## 概述 {#overview}

本技能指导你使用浏览器工具集对 Web 应用进行系统性的探索性 QA 测试。你将浏览应用、与元素交互、捕获问题证据，并生成结构化的 Bug 报告。

## 前置条件 {#prerequisites}

- 浏览器工具集必须可用（`browser_navigate`、`browser_snapshot`、`browser_click`、`browser_type`、`browser_vision`、`browser_console`、`browser_scroll`、`browser_back`、`browser_press`）
- 用户提供目标 URL 和测试范围

## 输入 {#inputs}

用户提供：
1. **目标 URL** — 测试的入口点
2. **范围** — 要重点测试的领域/功能（或“全站”进行全面测试）
3. **输出目录**（可选）— 保存截图和报告的位置（默认：`./dogfood-output`）

## 工作流程 {#workflow}

遵循以下 5 阶段系统化工作流程：

### 阶段 1：计划 {#phase-1-plan}

1. 创建输出目录结构：
<!-- ascii-guard-ignore -->
   ```
   {output_dir}/
   ├── screenshots/       # 证据截图
   └── report.md          # 最终报告（在阶段 5 生成）
   ```
<!-- ascii-guard-ignore-end -->
2. 根据用户输入确定测试范围。
3. 通过规划要测试的页面和功能，构建粗略的站点地图：
   - 着陆页/首页
   - 导航链接（页眉、页脚、侧边栏）
   - 关键用户流程（注册、登录、搜索、结账等）
   - 表单和交互元素
   - 边界情况（空状态、错误页面、404）

### 阶段 2：探索 {#phase-2-explore}

对于计划中的每个页面或功能：

1. **导航**到该页面：
   ```
   browser_navigate(url="https://example.com/page")
   ```

2. **拍摄快照**以了解 DOM 结构：
   ```
   browser_snapshot()
   ```

3. **检查控制台**是否有 JavaScript 错误：
   ```
   browser_console(clear=true)
   ```
   每次导航后以及每次重要交互后都要执行此操作。静默的 JS 错误是高价值发现。

4. **拍摄带注释的截图**以直观评估页面并识别交互元素：
   ```
   browser_vision(question="描述页面布局，识别任何视觉问题、损坏的元素或可访问性问题", annotate=true)
   ```
   `annotate=true` 标志会在交互元素上叠加编号的 `[N]` 标签。每个 `[N]` 对应后续浏览器命令中的引用 `@eN`。

5. **系统性地测试交互元素**：
   - 点击按钮和链接：`browser_click(ref="@eN")`
   - 填写表单：`browser_type(ref="@eN", text="测试输入")`
   - 测试键盘导航：`browser_press(key="Tab")`、`browser_press(key="Enter")`
   - 滚动内容：`browser_scroll(direction="down")`
   - 使用无效输入测试表单验证
   - 测试空提交
6. **每次交互后**，检查以下内容：
   - 控制台错误：`browser_console()`
   - 视觉变化：`browser_vision(question="交互后发生了什么变化？")`
   - 预期行为与实际行为

### 阶段 3：收集证据 {#phase-3-collect-evidence}

针对发现的每个问题：

1. **截取屏幕截图**，展示问题所在：
   ```
   browser_vision(question="捕获并描述此页面上可见的问题", annotate=false)
   ```
   从响应中保存 `screenshot_path` —— 你将在报告中引用它。

2. **记录详细信息**：
   - 问题出现的 URL
   - 复现步骤
   - 预期行为
   - 实际行为
   - 控制台错误（如有）
   - 截图路径

3. **使用问题分类法**（参见 `references/issue-taxonomy.md`）对问题进行分类：
   - 严重程度：严重 / 高 / 中 / 低
   - 类别：功能 / 视觉 / 无障碍 / 控制台 / 用户体验 / 内容

### 阶段 4：分类 {#phase-4-categorize}

1. 审查所有收集到的问题。
2. 去重 —— 合并在不同位置表现为同一 Bug 的问题。
3. 为每个问题分配最终的严重程度和类别。
4. 按严重程度排序（严重优先，然后是高、中、低）。
5. 按严重程度和类别统计问题数量，用于执行摘要。

### 阶段 5：报告 {#phase-5-report}

使用 `templates/dogfood-report-template.md` 中的模板生成最终报告。

报告必须包含：
1. **执行摘要**，包括问题总数、按严重程度分类的统计以及测试范围
2. **每个问题的章节**，包含：
   - 问题编号和标题
   - 严重程度和类别徽章
   - 观察到的 URL
   - 问题描述
   - 复现步骤
   - 预期行为与实际行为
   - 截图引用（使用 `MEDIA:&lt;screenshot_path&gt;` 作为内联图片）
   - 相关的控制台错误
3. **所有问题的汇总表**
4. **测试说明** —— 测试了什么、未测试什么、任何阻塞项

将报告保存到 `{output_dir}/report.md`。

## 工具参考 {#tools-reference}

| 工具 | 用途 |
|------|------|
| `browser_navigate` | 跳转到某个 URL |
| `browser_snapshot` | 获取 DOM 文本快照（无障碍树） |
| `browser_click` | 通过引用（`@eN`）或文本点击元素 |
| `browser_type` | 在输入框中输入内容 |
| `browser_scroll` | 在页面上向上/向下滚动 |
| `browser_back` | 在浏览器历史中后退 |
| `browser_press` | 按下键盘按键 |
| `browser_vision` | 截图 + AI 分析；使用 `annotate=true` 获取元素标签 |
| `browser_console` | 获取 JS 控制台输出和错误 |

## 提示 {#tips}

- **在导航后以及重要交互后，始终检查 `browser_console()`。** 静默的 JS 错误是最有价值的发现之一。
- **当需要推理交互元素的位置或快照引用不清晰时，对 `browser_vision` 使用 `annotate=true`。**
- **同时使用有效和无效输入进行测试** —— 表单验证 Bug 很常见。
- **滚动浏览长页面** —— 折叠区域以下的内容可能存在渲染问题。
- **测试导航流程** —— 端到端地点击多步骤流程。
- **通过注意截图中可见的任何布局问题，检查响应式行为。**
- **不要忘记边界情况**：空状态、超长文本、特殊字符、快速点击。
- 向用户报告截图时，请包含 `MEDIA:&lt;screenshot_path&gt;`，以便他们能内联查看证据。
