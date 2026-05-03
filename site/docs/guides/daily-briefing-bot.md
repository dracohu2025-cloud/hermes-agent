---
sidebar_position: 3
title: "教程：每日简报机器人"
description: "构建一个自动化的每日简报机器人，每天早晨研究你关注的话题、总结发现，并发送到 Telegram 或 Discord"
---

# 教程：构建一个每日简报机器人 {#tutorial-build-a-daily-briefing-bot}

在本教程中，你将构建一个个人简报机器人，它每天早晨自动醒来，研究你关心的话题，总结发现，并将一份简洁的简报直接发送到你的 Telegram 或 Discord。

学完本教程，你将拥有一个完全自动化的工作流，它结合了 **网页搜索**、**定时调度**、**任务委派** 和 **消息投递** —— 全程无需编写代码。

## 我们要构建什么 {#what-we-re-building}

流程如下：

1. **早上 8:00** —— 定时调度器触发你的任务
2. **Hermes 启动** 一个全新的 Agent 会话，并加载你的提示词
3. **网页搜索** 拉取你关注话题的最新新闻
4. **摘要生成** 将内容提炼成清晰的简报格式
5. **消息投递** 将简报发送到你的 Telegram 或 Discord

整个过程全自动运行。你只需在喝早咖啡时阅读简报即可。

## 前置条件 {#prerequisites}

开始之前，请确保你已准备好：

- **已安装 Hermes Agent** —— 参见[安装指南](/getting-started/installation)
- **Gateway 正在运行** —— gateway 守护进程负责执行定时任务：
  ```bash
  hermes gateway install   # 安装为用户服务
  sudo hermes gateway install --system   # Linux 服务器：开机自启系统服务
  # 或者
  hermes gateway           # 在前台运行
  ```
- **Firecrawl API 密钥** —— 在环境变量中设置 `FIRECRAWL_API_KEY` 以启用网页搜索
- **已配置消息服务**（可选但推荐）—— 设置好 [Telegram](/user-guide/messaging/telegram) 或 Discord 并指定一个家庭频道

:::tip 没有消息服务？没关系
<a id="no-messaging-no-problem"></a>
你仍然可以按照本教程操作，使用 `deliver: "local"`。简报会保存到 `~/.hermes/cron/output/` 目录下，你可以随时阅读。
:::

## 第一步：手动测试工作流 {#step-1-test-the-workflow-manually}

在自动化之前，先确保简报功能正常。启动一个聊天会话：

```bash
hermes
```

然后输入以下提示词：

```
搜索关于 AI Agent 和开源大语言模型的最新新闻。
用简洁的简报格式总结前 3 条新闻，并附上链接。
```

Hermes 会搜索网页、阅读结果，并生成类似下面的内容：

```
☀️ 你的 AI 简报 — 2026 年 3 月 8 日

1. Qwen 3 发布，拥有 235B 参数
   阿里巴巴最新的开放权重模型在多项基准测试中与 GPT-4.5 持平，
   同时保持完全开源。
   → https://qwenlm.github.io/blog/qwen3/

2. LangChain 推出 Agent 协议标准
   一项用于 Agent 间通信的新开放标准，在发布第一周内就获得了
   15 个主流框架的采用。
   → https://blog.langchain.dev/agent-protocol/

3. 欧盟 AI 法案对通用模型开始执法
   首批合规截止日期到来，开源模型在 1000 万参数阈值以下获得豁免。
   → https://artificialintelligenceact.eu/updates/

---
3 条新闻 • 搜索来源数：8 • 由 Hermes Agent 生成
```

如果这一步成功了，你就可以开始自动化了。

<a id="iterate-on-the-format"></a>
:::tip 反复调整格式
尝试不同的提示词，直到你得到满意的输出。可以添加类似“使用 emoji 标题”或“每条摘要不超过两句话”的指令。最终确定的格式将用于定时任务。
:::
## 第二步：创建定时任务 {#step-2-create-the-cron-job}

现在我们来安排它每天早上自动运行。你可以通过两种方式实现。

在创建定时任务之前，请确保 Hermes 已全局配置了默认模型和提供商。如果你希望某个特定任务使用不同的值，可以在创建时设置显式的逐任务模型/提供商覆盖。

### 选项 A：自然语言（在聊天中） {#option-a-natural-language-in-chat}

直接告诉 Hermes 你想要什么：

```
每天早上8点，搜索关于 AI Agent 和开源大语言模型的最新新闻。
用简洁的简报形式总结前3条最重要的故事，并附上链接。
语气要友好、专业。发送到 Telegram。
```

Hermes 会使用统一的 `cronjob` 工具为你创建定时任务。

### 选项 B：CLI 斜杠命令 {#option-b-cli-slash-command}

使用 `/cron` 命令可以获得更多控制：

```
/cron add "0 8 * * *" "搜索关于 AI Agent 和开源大语言模型的最新新闻。找到至少5篇过去24小时内的最新文章。用简洁的每日简报格式总结前3条最重要的故事。每条故事包括：清晰的标题、两句话的摘要和来源 URL。语气要友好、专业。用 emoji 项目符号格式化，最后附上故事总数。"
```

### 黄金法则：自包含提示 {#the-golden-rule-self-contained-prompts}

:::warning 关键概念
定时任务在**完全全新的会话**中运行——没有之前对话的记忆，也没有你“之前设置过什么”的上下文。你的提示必须包含 Agent 完成任务所需的**一切**。
:::
<a id="critical-concept"></a>

**糟糕的提示：**
```
执行我平时的早间简报。
```

**好的提示：**
```
搜索关于 AI Agent 和开源大语言模型的最新新闻。
找到至少5篇过去24小时内的最新文章。用简洁的每日简报格式总结
前3条最重要的故事。每条故事包括：清晰的标题、两句话的摘要和来源 URL。
语气要友好、专业。用 emoji 项目符号格式化。
```

好的提示明确说明了**搜索什么**、**多少篇文章**、**什么格式**以及**什么语气**。它一次性包含了 Agent 所需的一切。

## 第三步：自定义简报 {#step-3-customize-the-briefing}

一旦基础简报能正常工作，你就可以发挥创意了。

### 多主题简报 {#multi-topic-briefings}

在一份简报中覆盖多个领域：

```
/cron add "0 8 * * *" "创建一份涵盖三个主题的早间简报。对于每个主题，搜索过去24小时内的最新新闻，并总结前2条故事，附上链接。

主题：
1. AI 和机器学习——重点关注开源模型和 Agent 框架
2. 加密货币——重点关注比特币、以太坊和监管新闻
3. 太空探索——重点关注 SpaceX、NASA 和商业航天

格式化为一份干净的简报，包含章节标题和 emoji。最后附上今天的日期和一句励志名言。"
```

### 使用委派进行并行研究 {#using-delegation-for-parallel-research}

为了更快的简报，告诉 Hermes 将每个主题委派给子 Agent：

```
/cron add "0 8 * * *" "通过将研究委派给子 Agent 来创建一份早间简报。委派三个并行任务：

1. 委派：搜索过去24小时内前2条 AI/ML 新闻故事，附上链接
2. 委派：搜索过去24小时内前2条加密货币新闻故事，附上链接
3. 委派：搜索过去24小时内前2条太空探索新闻故事，附上链接

收集所有结果，将它们合并成一份干净的简报，包含章节标题、emoji 格式和来源链接。将今天的日期作为标题。"
```
每个子 Agent 独立并行搜索，然后主 Agent 将所有结果整合成一份精炼的简报。更多细节请参阅[委托文档](/user-guide/features/delegation)。

### 仅工作日运行 {#weekday-only-schedule}

周末不需要简报？使用针对周一至周五的 cron 表达式：

```
/cron add "0 8 * * 1-5" "搜索最新的 AI 和技术新闻..."
```

### 每日两次简报 {#twice-daily-briefings}

获取早间概览和晚间回顾：

```
/cron add "0 8 * * *" "早间简报：搜索过去 12 小时的 AI 新闻..."
/cron add "0 18 * * *" "晚间回顾：搜索过去 12 小时的 AI 新闻..."
```

### 通过记忆添加个人上下文 {#adding-personal-context-with-memory}

如果你启用了[记忆](/user-guide/features/memory)，可以存储跨会话持久化的偏好。但请记住——cron 任务在全新会话中运行，没有对话记忆。要添加个人上下文，请直接将其嵌入提示词中：

```
/cron add "0 8 * * *" "你正在为一位资深机器学习工程师创建简报，他关注：PyTorch 生态、Transformer 架构、开放权重模型以及欧盟 AI 监管。除非涉及开源，否则跳过产品发布或融资轮次的故事。

搜索这些主题的最新新闻。总结前 3 条故事并附上链接。内容要简洁且技术性强——这位读者不需要基础解释。"
```

<a id="tailor-the-persona"></a>
:::tip 定制角色
在简报中说明*为谁*制作，能显著提升相关性。告诉 Agent 你的角色、兴趣以及要跳过什么。
:::

## 第 4 步：管理你的任务 {#step-4-manage-your-jobs}

### 列出所有已调度任务 {#list-all-scheduled-jobs}

在聊天中：
```
/cron list
```

或者从终端：
```bash
hermes cron list
```

你会看到类似如下的输出：

```
ID          | Name              | Schedule    | Next Run           | Deliver
------------|-------------------|-------------|--------------------|--------
a1b2c3d4    | Morning Briefing  | 0 8 * * *   | 2026-03-09 08:00   | telegram
e5f6g7h8    | Evening Recap     | 0 18 * * *  | 2026-03-08 18:00   | telegram
```

### 删除任务 {#remove-a-job}

在聊天中：
```
/cron remove a1b2c3d4
```

或者用对话方式：
```
删除我的早间简报 cron 任务。
```

Hermes 会使用 `cronjob(action="list")` 找到它，再用 `cronjob(action="remove")` 删除它。

### 检查网关状态 {#check-gateway-status}

确保调度器确实在运行：

```bash
hermes cron status
```

如果网关未运行，你的任务将不会执行。为了可靠性，将其安装为后台服务：

```bash
hermes gateway install
# 或者在 Linux 服务器上
sudo hermes gateway install --system
```

## 更进一步 {#going-further}

你已经构建了一个可用的每日简报机器人。以下是一些可以继续探索的方向：

- **[定时任务 (Cron)](/user-guide/features/cron)** — 关于调度格式、重复限制和投递选项的完整参考
- **[委托](/user-guide/features/delegation)** — 深入探讨并行子 Agent 工作流
- **[消息平台](/user-guide/messaging)** — 设置 Telegram、Discord 或其他投递目标
- **[记忆](/user-guide/features/memory)** — 跨会话的持久化上下文
- **[技巧与最佳实践](/guides/tips)** — 更多提示词工程建议
<a id="what-else-can-you-schedule"></a>
:::tip 你还能安排什么？
简报机器人模式适用于任何场景：竞争对手监控、GitHub 仓库摘要、天气预报、投资组合跟踪、服务器健康检查，甚至每日笑话。只要你能用提示词描述出来，就能安排它。
:::
