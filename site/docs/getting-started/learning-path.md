---
sidebar_position: 3
title: '学习路径'
description: '根据你的经验水平和目标，选择适合你的 Hermes Agent 文档学习路径。'
---

# 学习路径 {#learning-path}

Hermes Agent 能做的很多——CLI 助手、Telegram/Discord 机器人、任务自动化、RL 训练，等等。这一页帮你根据自己的经验水平和想做的事，找到该从哪里开始、该读什么。

:::tip 从这里开始
如果你还没安装 Hermes Agent，先从[安装指南](/getting-started/installation)开始，然后跟着[快速入门](/getting-started/quickstart)走一遍。下面的内容都假设你已经安装好了。
:::

## 如何使用本页 {#how-to-use-this-page}

<a id="start-here"></a>
- **知道自己的水平？** 跳到[按经验水平](#by-experience-level)表格，跟着对应层级的阅读顺序走。
- **有明确的目标？** 直接看[按使用场景](#by-use-case)，找到匹配的场景。
- **随便看看？** 看看[核心功能一览](#key-features-at-a-glance)表格，快速了解 Hermes Agent 能做什么。

## 按经验水平 {#by-experience-level}

| 水平 | 目标 | 推荐阅读 | 预计时间 |
|---|---|---|---|
| **初学者** | 上手运行，进行基础对话，使用内置工具 | [安装](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI 使用](/user-guide/cli) → [配置](/user-guide/configuration) | ~1 小时 |
| **中级** | 搭建消息机器人，使用高级功能如记忆、定时任务、技能 | [会话](/user-guide/sessions) → [消息](/user-guide/messaging) → [工具](/user-guide/features/tools) → [技能](/user-guide/features/skills) → [记忆](/user-guide/features/memory) → [定时任务](/user-guide/features/cron) | ~2–3 小时 |
| **高级** | 构建自定义工具、创建技能、用 RL 训练模型、为项目做贡献 | [架构](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [RL 训练](/user-guide/features/rl-training) → [贡献指南](/developer-guide/contributing) | ~4–6 小时 |

## 按使用场景 {#by-use-case}

选择和你想做的事匹配的场景。每个场景都按阅读顺序链接到相关文档。

### "我想要一个 CLI 编程助手" {#i-want-a-cli-coding-assistant}

把 Hermes Agent 当作交互式终端助手，用来写代码、审代码、运行代码。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [CLI 使用](/user-guide/cli)
4. [代码执行](/user-guide/features/code-execution)
5. [上下文文件](/user-guide/features/context-files)
6. [技巧与窍门](/guides/tips)

:::tip
通过上下文文件直接把文件传入对话。Hermes Agent 可以读取、编辑和运行你项目里的代码。
:::

### "我想要一个 Telegram/Discord 机器人" {#i-want-a-telegram-discord-bot}

把 Hermes Agent 部署到你常用的消息平台上作为机器人。

1. [安装](/getting-started/installation)
2. [配置](/user-guide/configuration)
3. [消息功能概览](/user-guide/messaging)
4. [Telegram 设置](/user-guide/messaging/telegram)
5. [Discord 设置](/user-guide/messaging/discord)
6. [语音模式](/user-guide/features/voice-mode)
7. [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)
8. [安全](/user-guide/security)

完整的项目示例见：
- [每日简报机器人](/guides/daily-briefing-bot)
- [团队 Telegram 助手](/guides/team-telegram-assistant)

### "我想要自动化任务" {#i-want-to-automate-tasks}

安排周期性任务、运行批处理作业，或者把 Agent 的动作串联起来。

1. [快速入门](/getting-started/quickstart)
2. [定时任务调度](/user-guide/features/cron)
3. [批处理](/user-guide/features/batch-processing)
4. [委托](/user-guide/features/delegation)
5. [钩子](/user-guide/features/hooks)

:::tip
定时任务让 Hermes Agent 可以按计划运行任务——每日摘要、定期检查、自动生成报告——不需要你在场。
:::

### "我想要构建自定义工具/技能" {#i-want-to-build-custom-tools-skills}
用你自己的工具和可复用的技能包来扩展 Hermes Agent。

1. [Tools 概览](/user-guide/features/tools)
2. [Skills 概览](/user-guide/features/skills)
3. [MCP（Model Context Protocol）](/user-guide/features/mcp)
4. [架构](/developer-guide/architecture)
5. [添加 Tools](/developer-guide/adding-tools)
6. [创建 Skills](/developer-guide/creating-skills)

:::tip
Tool 是 Agent 可以调用的单个函数。Skill 是把 Tool、提示词和配置打包在一起的集合。先从 Tool 入手，再进阶到 Skill。
:::

### "我想训练模型" {#i-want-to-train-models}

使用强化学习来微调模型行为，Hermes Agent 内置了 RL 训练流水线。

1. [快速开始](/getting-started/quickstart)
2. [配置](/user-guide/configuration)
3. [RL 训练](/user-guide/features/rl-training)
4. [Provider 路由](/user-guide/features/provider-routing)
5. [架构](/developer-guide/architecture)

:::tip
RL 训练在你已经了解 Hermes Agent 如何处理对话和 Tool 调用的基础上效果最好。如果你是新手，建议先走完入门路径。
:::

### "我想把它当作 Python 库使用" {#i-want-to-use-it-as-a-python-library}

以编程方式将 Hermes Agent 集成到你自己的 Python 应用中。

1. [安装](/getting-started/installation)
2. [快速开始](/getting-started/quickstart)
3. [Python 库指南](/guides/python-library)
4. [架构](/developer-guide/architecture)
5. [Tools](/user-guide/features/tools)
6. [Sessions](/user-guide/sessions)

## 主要功能一览 {#key-features-at-a-glance}

不确定有哪些功能可用？以下是主要功能的快速目录：

| 功能 | 作用 | 链接 |
|---|---|---|
| **Tools** | Agent 可以调用的内置工具（文件 I/O、搜索、shell 等） | [Tools](/user-guide/features/tools) |
| **Skills** | 可安装的插件包，用于添加新能力 | [Skills](/user-guide/features/skills) |
| **Memory** | 跨 Session 的持久化记忆 | [Memory](/user-guide/features/memory) |
| **Context Files** | 将文件和目录输入到对话中 | [Context Files](/user-guide/features/context-files) |
| **MCP** | 通过 Model Context Protocol 连接外部工具服务器 | [MCP](/user-guide/features/mcp) |
| **Cron** | 调度周期性 Agent 任务 | [Cron](/user-guide/features/cron) |
| **Delegation** | 生成 sub-agent 以并行处理工作 | [Delegation](/user-guide/features/delegation) |
| **Code Execution** | 运行以编程方式调用 Hermes Tool 的 Python 脚本 | [Code Execution](/user-guide/features/code-execution) |
| **Browser** | 网页浏览和抓取 | [Browser](/user-guide/features/browser) |
| **Hooks** | 事件驱动的回调和中间件 | [Hooks](/user-guide/features/hooks) |
| **Batch Processing** | 批量处理多个输入 | [Batch Processing](/user-guide/features/batch-processing) |
| **RL Training** | 使用强化学习微调模型 | [RL Training](/user-guide/features/rl-training) |
| **Provider Routing** | 在多个 LLM Provider 之间路由请求 | [Provider Routing](/user-guide/features/provider-routing) |

## 接下来读什么 {#what-to-read-next}

根据你当前所处的阶段：

- **刚安装完？** → 前往 [Quickstart](/getting-started/quickstart) 运行你的第一次对话。
- **已完成 Quickstart？** → 阅读 [CLI 用法](/user-guide/cli) 和 [配置](/user-guide/configuration) 来自定义你的环境。
- **已熟悉基础操作？** → 探索 [Tools](/user-guide/features/tools)、[Skills](/user-guide/features/skills) 和 [Memory](/user-guide/features/memory)，解锁 Agent 的完整能力。
- **为团队搭建环境？** → 阅读 [Security](/user-guide/security) 和 [Sessions](/user-guide/sessions)，了解访问控制和对话管理。
- **准备开始开发？** → 跳入 [Developer Guide](/developer-guide/architecture)，了解内部原理并开始贡献。
- **想要实用示例？** → 查看 [Guides](/guides/tips)  section，获取实际项目和技巧。
:::tip
不需要全部读完。挑一条符合你目标的路径，按顺序跟着链接走，很快就能上手。随时都能回到这一页，继续下一步。
:::
