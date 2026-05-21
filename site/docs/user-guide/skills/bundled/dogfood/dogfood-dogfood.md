---
title: "Dogfood — 探索式 Web 应用测试：发现 Bug、证据、报告"
sidebar_label: "Dogfood"
description: "探索式 Web 应用测试：发现 Bug、证据、报告"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="dogfood"></a>
# Dogfood

探索式 Web 应用测试：发现 Bug、证据、报告。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/dogfood` |
| 版本 | `1.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `qa`, `testing`, `browser`, `web`, `dogfood` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是该技能激活时 agent 看到的指令内容。
:::

<a id="dogfood-systematic-web-application-qa-testing"></a>
# Dogfood：系统化 Web 应用 QA 测试

<a id="overview"></a>
## 概述

本技能指导你使用浏览器工具集对 Web 应用进行系统化的探索式 QA 测试。你将浏览应用、与元素交互、捕获问题证据，并生成结构化的 Bug 报告。

<a id="prerequisites"></a>
## 前置条件

- 必须提供浏览器工具集（`browser_navigate`、`browser_snapshot`、`browser_click`、`browser_type`、`browser_vision`、`browser_console`、`browser_scroll`、`browser_back`、`browser_press`）
- 用户提供目标 URL 和测试范围

<a id="inputs"></a>
## 输入

用户提供以下内容：
1. **目标 URL** — 测试的入口点
2. **测试范围** — 要重点测试哪些区域/功能（或 “full site” 表示全面测试）
3. **输出目录**（可选）— 保存截图和报告的位置（默认：`./dogfood-output`）

<a id="workflow"></a>
## 工作流程

遵循以下 5 阶段系统化工作流程：

<a id="phase-1-plan"></a>
### 阶段 1：计划

1. 创建输出目录结构：
<!-- ascii-guard-ignore -->
   ```
   {output_dir}/
   ├── screenshots/       # 证据截图
   └── report.md          # 最终报告（在阶段 5 生成）
   ```
<!-- ascii-guard-ignore-end -->
2. 根据用户输入确定测试范围。
3. 通过规划要测试的页面和功能来构建粗略的站点地图：
   - 着陆页/首页
   - 导航链接（页眉、页脚、侧边栏）
   - 关键用户流程（注册、登录、搜索、结账等）
   - 表单和交互元素
   - 边界情况（空状态、错误页面、404 等）

<a id="phase-2-explore"></a>
### 阶段 2：探索

对于计划中的每个页面或功能：

1. **导航**到页面：
   ```
   browser_navigate(url="https://example.com/page")
   ```

2. **拍摄快照**以了解 DOM 结构：
   ```
   browser_snapshot()
   ```

3. **检查控制台**中的 JavaScript 错误：
   ```
   browser_console(clear=true)
   ```
   每次导航后以及每次重大交互后都执行此操作。静默的 JS 错误是高价值发现。

4. **拍摄带标注的截图**以直观评估页面并识别交互元素：
   ```
   browser_vision(question="描述页面布局，识别任何视觉问题、破损元素或可访问性问题", annotate=true)
   ```
   `annotate=true` 标志会在交互元素上覆盖带编号的 `[N]` 标签。每个 `[N]` 映射到 ref `@eN`，用于后续浏览器命令。
5. **系统性地测试交互元素**：
   - 点击按钮和链接：`browser_click(ref="@eN")`
   - 填写表单：`browser_type(ref="@eN", text="test input")`
   - 测试键盘导航：`browser_press(key="Tab")`、`browser_press(key="Enter")`
   - 滚动浏览内容：`browser_scroll(direction="down")`
   - 使用无效输入测试表单验证
   - 测试空提交

6. **每次交互后**，检查：
   - 控制台错误：`browser_console()`
   - 视觉变化：`browser_vision(question="交互后发生了什么变化？")`
   - 预期行为与实际行为

<a id="phase-3-collect-evidence"></a>
### 第三阶段：收集证据

针对发现的每个问题：

1. **截图**显示问题：
   ```
   browser_vision(question="捕获并描述此页面上可见的问题", annotate=false)
   ```
   保存响应中的 `screenshot_path`——你将在报告中引用它。

2. **记录详细信息**：
   - 问题出现的 URL
   - 复现步骤
   - 预期行为
   - 实际行为
   - 控制台错误（如有）
   - 截图路径

3. **对问题进行分类**，使用问题分类法（参见 `references/issue-taxonomy.md`）：
   - 严重程度：严重 / 高 / 中 / 低
   - 类别：功能 / 视觉 / 无障碍 / 控制台 / 用户体验 / 内容

<a id="phase-4-categorize"></a>
### 第四阶段：分类整理

1. 审查所有收集到的问题。
2. 去重——合并在不同位置表现相同的同一 bug。
3. 为每个问题分配最终的严重程度和类别。
4. 按严重程度排序（严重优先，然后是高、中、低）。
5. 按严重程度和类别统计问题数量，用于执行摘要。

<a id="phase-5-report"></a>
### 第五阶段：报告

使用 `templates/dogfood-report-template.md` 中的模板生成最终报告。

报告必须包含：
1. **执行摘要**，包括问题总数、按严重程度分类的明细以及测试范围
2. **每个问题的独立章节**，包含：
   - 问题编号和标题
   - 严重程度和类别标签
   - 观察到问题的 URL
   - 问题描述
   - 复现步骤
   - 预期行为与实际行为
   - 截图引用（使用 `MEDIA:&lt;screenshot_path&gt;` 作为内联图片）
   - 相关的控制台错误
3. **所有问题的汇总表**
4. **测试说明**——测试了哪些内容、未测试哪些内容、以及任何阻碍因素

将报告保存到 `{output_dir}/report.md`。

<a id="tools-reference"></a>
## 工具参考

| 工具 | 用途 |
|------|---------|
| `browser_navigate` | 跳转到 URL |
| `browser_snapshot` | 获取 DOM 文本快照（无障碍树） |
| `browser_click` | 通过引用（`@eN`）或文本点击元素 |
| `browser_type` | 在输入字段中输入文本 |
| `browser_scroll` | 在页面上向上/向下滚动 |
| `browser_back` | 在浏览器历史记录中后退 |
| `browser_press` | 按下键盘按键 |
| `browser_vision` | 截图 + AI 分析；使用 `annotate=true` 获取元素标签 |
| `browser_console` | 获取 JS 控制台输出和错误 |

<a id="tips"></a>
## 提示

- **在导航后和重要交互后，始终检查 `browser_console()`。** 静默的 JS 错误是最有价值的发现之一。
- **在需要推理交互元素位置或快照引用不清晰时，对 `browser_vision` 使用 `annotate=true`。**
- **同时使用有效和无效输入进行测试**——表单验证 bug 很常见。
- **滚动浏览长页面**——折叠区域以下的内容可能存在渲染问题。
- **测试导航流程**——端到端地点击完成多步骤流程。
- **通过注意截图中可见的任何布局问题，检查响应式行为。**
- **不要忘记边缘情况**：空状态、超长文本、特殊字符、快速点击。
- 在向用户报告截图时，请包含 `MEDIA:&lt;screenshot_path&gt;`，以便他们能内联查看证据。
