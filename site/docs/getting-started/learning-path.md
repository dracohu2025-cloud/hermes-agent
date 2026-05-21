---
sidebar_position: 3
title: '学习路径'
description: '根据您的经验水平和目标，选择通过 Hermes Agent 文档学习的最佳路径。'
---

<a id="learning-path"></a>
# 学习路径

Hermes Agent 功能强大——可以是 CLI 助手、Telegram/Discord 机器人、任务自动化、强化学习训练等等。本页将帮助您根据自己的经验水平和目标，确定从哪里开始、阅读哪些内容。

:::tip 从这里开始
如果您尚未安装 Hermes Agent，请先阅读[安装指南](/getting-started/installation)，然后完成[快速入门](/getting-started/quickstart)。以下内容均假设您已成功安装。
:::

<a id="how-to-use-this-page"></a>
<a id="start-here"></a>
## 如何使用本页

- **了解自己的水平？** 跳转到[按经验水平](#by-experience-level)表格，按照对应级别的阅读顺序学习。
- **有具体目标？** 跳转到[按使用场景](#by-use-case)，找到匹配的场景。
- **只是随意浏览？** 查看[关键功能一览](#key-features-at-a-glance)表格，快速了解 Hermes Agent 能做什么。

<a id="by-experience-level"></a>
## 按经验水平

| 级别 | 目标 | 推荐阅读 | 预计时间 |
|---|---|---|---|
| **初学者** | 上手运行、进行基本对话、使用内置工具 | [安装](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI 使用方法](/user-guide/cli) → [配置](/user-guide/configuration) | ~1 小时 |
| **中级** | 设置消息机器人、使用进阶功能如记忆、定时任务和技能 | [会话](/user-guide/sessions) → [消息](/user-guide/messaging) → [工具](/user-guide/features/tools) → [技能](/user-guide/features/skills) → [记忆](/user-guide/features/memory) → [定时任务](/user-guide/features/cron) | ~2–3 小时 |
| **高级** | 构建自定义工具、创建技能、理解模型训练相关能力、为项目做贡献 | [架构](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [贡献](/developer-guide/contributing) | ~4–6 小时 |

<a id="by-use-case"></a>
## 按使用场景

选择与您想要做的事情相匹配的场景。每个场景都按推荐阅读顺序链接了相关文档。

<a id="i-want-a-cli-coding-assistant"></a>
### “我想要一个 CLI 编码助手”

将 Hermes Agent 用作交互式终端助手，用于编写、审查和运行代码。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [CLI 使用方法](/user-guide/cli)
4. [代码执行](/user-guide/features/code-execution)
5. [上下文文件](/user-guide/features/context-files)
6. [技巧与提示](/guides/tips)

:::tip
通过上下文文件将文件直接传入对话。Hermes Agent 可以读取、编辑和运行您项目中的代码。
:::

<a id="i-want-a-telegram-discord-bot"></a>
### “我想要一个 Telegram/Discord 机器人”

将 Hermes Agent 部署为您最喜爱的消息平台上的机器人。

1. [安装](/getting-started/installation)
2. [配置](/user-guide/configuration)
3. [消息概览](/user-guide/messaging)
4. [Telegram 设置](/user-guide/messaging/telegram)
5. [Discord 设置](/user-guide/messaging/discord)
6. [语音模式](/user-guide/features/voice-mode)
7. [将语音模式与 Hermes 配合使用](/guides/use-voice-mode-with-hermes)
8. [安全](/user-guide/security)
完整项目示例请参见：
- [每日简报机器人](/guides/daily-briefing-bot)
- [团队 Telegram 助手](/guides/team-telegram-assistant)

<a id="i-want-to-automate-tasks"></a>
### “我想自动化任务”

安排重复性任务、运行批处理作业，或者将多个 Agent 动作串联起来。

1. [快速入门](/getting-started/quickstart)
2. [Cron 调度](/user-guide/features/cron)
3. [批处理](/user-guide/features/batch-processing)
4. [委派](/user-guide/features/delegation)
5. [钩子](/user-guide/features/hooks)

:::tip
Cron 作业让 Hermes Agent 可以按计划自动运行任务——每日汇总、定期检查、自动报告——无需你亲自在场。
:::

<a id="i-want-to-build-custom-tools-skills"></a>
### “我想构建自定义工具/技能”

用你自己的工具和可复用的技能包扩展 Hermes Agent。

1. [插件](/user-guide/features/plugins)
2. [构建 Hermes 插件](/guides/build-a-hermes-plugin)
3. [工具概览](/user-guide/features/tools)
4. [技能概览](/user-guide/features/skills)
5. [MCP（模型上下文协议）](/user-guide/features/mcp)
6. [架构](/developer-guide/architecture)
7. [添加工具](/developer-guide/adding-tools)
8. [创建技能](/developer-guide/creating-skills)

:::tip
对于大多数自定义工具创建，建议从插件开始。[添加工具](/developer-guide/adding-tools)页面针对的是 Hermes 核心的内置开发，而非通常的用户/自定义工具路径。
:::

<a id="i-want-to-train-models"></a>
### “我想训练模型”

使用强化学习，通过 Hermes Agent 内置的 RL 训练管道微调模型行为。

1. [快速入门](/getting-started/quickstart)
2. [配置](/user-guide/configuration)
3. 关注官方最新的训练与评估相关文档
4. [提供者路由](/user-guide/features/provider-routing)
5. [架构](/developer-guide/architecture)

:::tip
当你已经了解 Hermes Agent 如何处理对话和工具调用的基础知识后，RL 训练效果最好。如果你是新手，请先走一遍初学者路径。
:::

<a id="i-want-to-use-it-as-a-python-library"></a>
### “我想把它作为 Python 库使用”

通过编程方式将 Hermes Agent 集成到你自己的 Python 应用程序中。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [Python 库指南](/guides/python-library)
4. [架构](/developer-guide/architecture)
5. [工具](/user-guide/features/tools)
6. [会话](/user-guide/sessions)

<a id="key-features-at-a-glance"></a>
## 核心功能速览

不确定有哪些可用功能？以下是主要功能的快速目录：

| 功能 | 作用 | 链接 |
|---|---|---|
| **工具** | Agent 可调用的内置工具（文件 I/O、搜索、Shell 等） | [工具](/user-guide/features/tools) |
| **技能** | 可安装的插件包，用于添加新能力 | [技能](/user-guide/features/skills) |
| **记忆** | 跨会话持久化记忆 | [记忆](/user-guide/features/memory) |
| **上下文文件** | 将文件和目录送入对话 | [上下文文件](/user-guide/features/context-files) |
| **MCP** | 通过模型上下文协议连接到外部工具服务器 | [MCP](/user-guide/features/mcp) |
| **Cron** | 安排重复的 Agent 任务 | [Cron](/user-guide/features/cron) |
| **委派** | 生成子 Agent 进行并行工作 | [委派](/user-guide/features/delegation) |
| **代码执行** | 运行 Python 脚本，以编程方式调用 Hermes 工具 | [代码执行](/user-guide/features/code-execution) |
| **浏览器** | 网页浏览与抓取 | [浏览器](/user-guide/features/browser) |
| **钩子** | 事件驱动的回调与中间件 | [钩子](/user-guide/features/hooks) |
| **批处理** | 批量处理多个输入 | [批处理](/user-guide/features/batch-processing) |
| **训练与评估** | 关注模型训练、评估和轨迹数据相关能力 | 参考最新开发者文档与发布说明 |
| **提供者路由** | 跨多个 LLM 提供者路由请求 | [提供者路由](/user-guide/features/provider-routing) |
<a id="what-to-read-next"></a>
## 接下来读什么

根据你当前所处的位置：

- **刚完成安装？** → 前往[快速开始](/getting-started/quickstart)运行你的第一个对话。
- **已完成快速开始？** → 阅读[CLI 用法](/user-guide/cli)和[配置](/user-guide/configuration)来自定义你的设置。
- **对基础操作已熟悉？** → 探索[工具](/user-guide/features/tools)、[技能](/user-guide/features/skills)和[记忆](/user-guide/features/memory)以解锁 Agent 的全部能力。
- **正在为团队搭建环境？** → 阅读[安全](/user-guide/security)和[会话](/user-guide/sessions)以了解访问控制和对话管理。
- **准备好开始构建？** → 跳转到[开发者指南](/developer-guide/architecture)了解内部机制并开始贡献。
- **想要实际示例？** → 查看[指南](/guides/tips)一节，获取真实项目与技巧。

:::tip
你不需要读完所有内容。选择符合你目标的路径，按顺序阅读链接，就能快速上手。以后随时可以回到本页找到下一步。
:::
