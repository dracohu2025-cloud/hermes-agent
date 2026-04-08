---
sidebar_position: 11
title: "使用 Cron 自动化一切"
description: "使用 Hermes cron 的真实自动化模式 —— 监控、报告、流水线和多 Skill 工作流"
---

# 使用 Cron 自动化一切

[每日简报机器人教程](/guides/daily-briefing-bot) 介绍了基础知识。本指南将更进一步 —— 提供五个你可以直接套用到自己工作流中的真实自动化模式。

有关完整的功能参考，请参阅 [定时任务 (Cron)](/user-guide/features/cron)。

:::info 核心概念
Cron 任务在全新的 Agent 会话中运行，不会继承你当前聊天的记忆。Prompt 必须是**完全自包含的** —— 包含 Agent 需要知道的所有信息。
:::

---

## 模式 1：网站变更监控

监控某个 URL 的变化，仅在内容发生变化时接收通知。

这里的 `script` 参数是秘密武器。在每次执行前都会运行一个 Python 脚本，其标准输出（stdout）将成为 Agent 的上下文。脚本负责机械性工作（抓取、对比差异）；Agent 负责推理（这个变化是否有意义？）。

创建监控脚本：

```bash
mkdir -p ~/.hermes/scripts
```

```python title="~/.hermes/scripts/watch-site.py"
import hashlib, json, os, urllib.request

URL = "https://example.com/pricing"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watch-site-state.json")

# 获取当前内容
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-Monitor/1.0"})
content = urllib.request.urlopen(req, timeout=30).read().decode()
current_hash = hashlib.sha256(content.encode()).hexdigest()

# 加载之前的状态
prev_hash = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev_hash = json.load(f).get("hash")

# 保存当前状态
with open(STATE_FILE, "w") as f:
    json.dump({"hash": current_hash, "url": URL}, f)

# 输出给 Agent 的内容
if prev_hash and prev_hash != current_hash:
    print(f"CHANGE DETECTED on {URL}")
    print(f"Previous hash: {prev_hash}")
    print(f"Current hash: {current_hash}")
    print(f"\nCurrent content (first 2000 chars):\n{content[:2000]}")
else:
    print("NO_CHANGE")
```

设置 cron 任务：

```bash
/cron add "every 1h" "If the script output says CHANGE DETECTED, summarize what changed on the page and why it might matter. If it says NO_CHANGE, respond with just [SILENT]." --script ~/.hermes/scripts/watch-site.py --name "Pricing monitor" --deliver telegram
```

:::tip [SILENT] 技巧
当 Agent 的最终回复包含 `[SILENT]` 时，消息推送会被抑制。这意味着只有在真正发生变化时你才会收到通知 —— 不会在安静时段收到垃圾信息。
:::

---

## 模式 2：每周报告

从多个来源汇总信息并生成格式化的摘要。该任务每周运行一次并发送到你的主频道。

```bash
/cron add "0 9 * * 1" "Generate a weekly report covering:

1. Search the web for the top 5 AI news stories from the past week
2. Search GitHub for trending repositories in the 'machine-learning' topic
3. Check Hacker News for the most discussed AI/ML posts

Format as a clean summary with sections for each source. Include links.
Keep it under 500 words — highlight only what matters." --name "Weekly AI digest" --deliver telegram
```

通过 CLI 操作：

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly report covering the top AI news, trending ML GitHub repos, and most-discussed HN posts. Format with sections, include links, keep under 500 words." \
  --name "Weekly AI digest" \
  --deliver telegram
```

`0 9 * * 1` 是标准的 cron 表达式：每周一上午 9:00。

---

## 模式 3：GitHub 仓库监控器

监控仓库中的新 issue、PR 或 release。

```bash
/cron add "every 6h" "Check the GitHub repository NousResearch/hermes-agent for:
- New issues opened in the last 6 hours
- New PRs opened or merged in the last 6 hours
- Any new releases

Use the terminal to run gh commands:
  gh issue list --repo NousResearch/hermes-agent --state open --json number,title,author,createdAt --limit 10
  gh pr list --repo NousResearch/hermes-agent --state all --json number,title,author,createdAt,mergedAt --limit 10

Filter to only items from the last 6 hours. If nothing new, respond with [SILENT].
Otherwise, provide a concise summary of the activity." --name "Repo watcher" --deliver discord
```

:::warning 自包含 Prompt
注意 Prompt 是如何包含精确的 `gh` 命令的。Cron Agent 没有关于之前运行或你偏好的记忆 —— 请务必交代清楚所有细节。
:::

---

## 模式 4：数据采集流水线

定期抓取数据，保存到文件，并检测随时间变化的趋势。此模式结合了脚本（用于采集）和 Agent（用于分析）。

```python title="~/.hermes/scripts/collect-prices.py"
import json, os, urllib.request
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.hermes/data/prices")
os.makedirs(DATA_DIR, exist_ok=True)

# 获取当前数据（例如：加密货币价格）
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
data = json.loads(urllib.request.urlopen(url, timeout=30).read())

# 追加到历史文件
entry = {"timestamp": datetime.now().isoformat(), "prices": data}
history_file = os.path.join(DATA_DIR, "history.jsonl")
with open(history_file, "a") as f:
    f.write(json.dumps(entry) + "\n")

# 加载最近的历史记录用于分析
lines = open(history_file).readlines()
recent = [json.loads(l) for l in lines[-24:]]  # 最近 24 个数据点

# 输出给 Agent 的内容
print(f"Current: BTC=${data['bitcoin']['usd']}, ETH=${data['ethereum']['usd']}")
print(f"Data points collected: {len(lines)} total, showing last {len(recent)}")
print(f"\nRecent history:")
for r in recent[-6:]:
    print(f"  {r['timestamp']}: BTC=${r['prices']['bitcoin']['usd']}, ETH=${r['prices']['ethereum']['usd']}")
```

```bash
/cron add "every 1h" "Analyze the price data from the script output. Report:
1. Current prices
2. Trend direction over the last 6 data points (up/down/flat)
3. Any notable movements (>5% change)

If prices are flat and nothing notable, respond with [SILENT].
If there's a significant move, explain what happened." \
  --script ~/.hermes/scripts/collect-prices.py \
  --name "Price tracker" \
  --deliver telegram
```

脚本负责机械的数据采集；Agent 则增加了推理层。

---

## 模式 5：多 Skill 工作流

将多个 Skill 串联起来执行复杂的定时任务。Skill 会在 Prompt 执行前按顺序加载。

```bash
# 使用 arxiv skill 查找论文，然后使用 obsidian skill 保存笔记
/cron add "0 8 * * *" "Search arXiv for the 3 most interesting papers on 'language model reasoning' from the past day. For each paper, create an Obsidian note with the title, authors, abstract summary, and key contribution." \
  --skill arxiv \
  --skill obsidian \
  --name "Paper digest"
```

直接通过工具调用：

```python
cronjob(
    action="create",
    skills=["arxiv", "obsidian"],
    prompt="Search arXiv for papers on 'language model reasoning' from the past day. Save the top 3 as Obsidian notes.",
    schedule="0 8 * * *",
    name="Paper digest",
    deliver="local"
)
```

Skill 按顺序加载 —— 先加载 `arxiv`（教 Agent 如何搜索论文），然后加载 `obsidian`（教 Agent 如何写笔记）。Prompt 将它们联系在一起。

---

## 管理你的任务

```bash
# 列出所有活动任务
/cron list

# 立即触发任务（用于测试）
/cron run <job_id>

# 暂停任务而不删除它
/cron pause <job_id>

# 编辑运行中任务的计划或 Prompt
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Updated task description"

# 为现有任务添加或移除 Skill
/cron edit <job_id> --skill arxiv --skill obsidian
/cron edit <job_id> --clear-skills

# 永久移除任务
/cron remove <job_id>
```

---

## 投递目标 (Delivery Targets)

`--deliver` 标志控制结果发送到哪里：

| 目标 | 示例 | 使用场景 |
|--------|---------|----------|
| `origin` | `--deliver origin` | 创建该任务的同一个聊天窗口（默认） |
| `local` | `--deliver local` | 仅保存到本地文件 |
| `telegram` | `--deliver telegram` | 你的 Telegram 主频道 |
| `discord` | `--deliver discord` | 你的 Discord 主频道 |
| `slack` | `--deliver slack` | 你的 Slack 主频道 |
| 特定聊天 | `--deliver telegram:-1001234567890` | 特定的 Telegram 群组 |
| 线程内 | `--deliver telegram:-1001234567890:17585` | 特定的 Telegram 话题线程 |
---

## 小技巧

**让 Prompt 保持独立完整。** Cron 任务中的 Agent 没有对话记忆。请直接在 Prompt 中包含 URL、仓库名称、格式偏好以及交付指令。

**大方使用 `[SILENT]`。** 对于监控类任务，务必包含类似“如果没有变化，请回复 `[SILENT]`”的指令。这能有效防止通知噪音。

**使用脚本进行数据采集。** `script` 参数允许 Python 脚本处理枯燥的部分（HTTP 请求、文件 I/O、状态跟踪）。Agent 只需查看脚本的标准输出（stdout）并对其进行推理。这比让 Agent 亲自去抓取数据更便宜、更可靠。

**使用 `/cron run` 进行测试。** 在等待定时触发之前，可以使用 `/cron run <job_id>` 立即执行任务，以验证输出是否符合预期。

**调度表达式。** 像 `every 2h`、`30m` 和 `daily at 9am` 这种易于理解的格式，与标准的 cron 表达式（如 `0 9 * * *`）同样有效。

---

*如需查看完整的 cron 参考指南（包括所有参数、边缘情况和内部原理），请参阅 [定时任务 (Cron)](/user-guide/features/cron)。*
