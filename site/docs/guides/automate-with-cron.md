---
sidebar_position: 11
title: "用 Cron 自动化一切"
description: "使用 Hermes cron 的真实自动化模式——监控、报告、流水线以及多技能工作流"
---

<a id="automate-anything-with-cron"></a>
# 用 Cron 自动化一切

[每日简报机器人教程](/guides/daily-briefing-bot)涵盖了基础知识。本指南更进一步——五个你可以根据自己的工作流调整的真实自动化模式。

完整的特性参考，请参见[定时任务（Cron）](/user-guide/features/cron)。

<a id="key-concept"></a>
:::info 核心理念
Cron 任务会在全新的 Agent 会话中运行，不保留当前聊天的记忆。提示词必须**完全自包含**——包含 Agent 需要知道的一切。
:::

<a id="don-t-need-the-llm-you-have-two-zero-token-options"></a>
:::tip 不需要 LLM？你有两个零 Token 的选择。
- **周期性看门狗**，脚本已经生成确切的输出消息（内存警报、磁盘警报、心跳）：使用[纯脚本 cron 任务](/guides/cron-script-only)。同样的调度器，无需 LLM。你可以在聊天中让 Hermes 为你设置一个——`cronjob` 工具知道何时选择 `no_agent=True`，并且会为你编写脚本。
- **从已在运行的脚本一次性发送**（CI 步骤、提交后钩子、部署脚本、外部调度的监控）：使用 [`hermes send`](/guides/pipe-script-output) 将 stdout 或文件直接通过管道发送到 Telegram / Discord / Slack 等，无需设置 cron 条目。
:::
<a id="pattern-1-website-change-monitor"></a>
## 模式 1：网站变化监控

监控一个 URL 的变化，只有在内容发生改变时才收到通知。

这里的 `script` 参数是秘密武器。一个 Python 脚本会在每次执行前运行，其标准输出会作为 Agent 的上下文。脚本负责机械工作（抓取、差异对比）；Agent 负责推理（这个变化有意思吗？）。

创建监控脚本：

```bash
mkdir -p ~/.hermes/scripts
```

```python title="~/.hermes/scripts/watch-site.py"
import hashlib, json, os, urllib.request

URL = "https://example.com/pricing"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watch-site-state.json")

# Fetch current content
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-Monitor/1.0"})
content = urllib.request.urlopen(req, timeout=30).read().decode()
current_hash = hashlib.sha256(content.encode()).hexdigest()

# Load previous state
prev_hash = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev_hash = json.load(f).get("hash")

# Save current state
with open(STATE_FILE, "w") as f:
    json.dump({"hash": current_hash, "url": URL}, f)

# Output for the agent
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
/cron add "every 1h" "如果脚本输出显示 CHANGE DETECTED，总结页面上发生了什么变化以及为什么可能重要。如果是 NO_CHANGE，仅回复 [SILENT]。" --script ~/.hermes/scripts/watch-site.py --name "价格监控" --deliver telegram
```

:::tip [SILENT] 技巧
<a id="the-silent-trick"></a>
当 Agent 的最终响应包含 `[SILENT]` 时，投递会被抑制。这意味着只有当真的有事情发生时你才会收到通知——安静时段不会收到垃圾消息。
:::

---

<a id="pattern-2-weekly-report"></a>
## 模式 2：周报

从多个来源汇总信息，生成格式整齐的摘要。每周运行一次，投递到你的首页频道。

```bash
/cron add "0 9 * * 1" "生成一份周报，涵盖以下内容：

1. 搜索过去一周内排名前五的 AI 新闻。
2. 在 GitHub 上搜索 'machine-learning' 主题下的热门仓库。
3. 查看 Hacker News 上讨论最多的 AI/ML 帖子。

以整洁摘要的形式呈现，每个来源单独一个小节。包含链接。
篇幅控制在 500 字以内——只强调重要内容。" --name "每周 AI 摘要" --deliver telegram
```
从 CLI 执行：

```bash
hermes cron create "0 9 * * 1" \
  "生成一份每周报告，涵盖顶级 AI 新闻、热门的 ML GitHub 仓库以及讨论最多的 HN 帖子。按章节组织，包含链接，控制在 500 字以内。" \
  --name "每周 AI 摘要" \
  --deliver telegram
```

`0 9 * * 1` 是标准的 cron 表达式：每周一上午 9:00。

---

<a id="pattern-3-github-repository-watcher"></a>
## 模式 3：GitHub 仓库监视器

监控仓库中的新 issue、PR 或发布。

```bash
/cron add "every 6h" "检查 GitHub 仓库 NousResearch/hermes-agent：
- 过去 6 小时内新开的 issue
- 过去 6 小时内新开或合并的 PR
- 任何新发布

使用终端运行 gh 命令：
  gh issue list --repo NousResearch/hermes-agent --state open --json number,title,author,createdAt --limit 10
  gh pr list --repo NousResearch/hermes-agent --state all --json number,title,author,createdAt,mergedAt --limit 10

仅筛选过去 6 小时内的项目。如果没有新内容，回复 [SILENT]。
否则，提供活动的简洁摘要。" --name "仓库监视器" --deliver discord
```
:::warning 自包含提示
<a id="self-contained-prompts"></a>
注意提示中包含了具体的 `gh` 命令。cron agent 无法记住之前的运行记录或你的偏好——请把所有信息都写清楚。
:::

---

<a id="pattern-4-data-collection-pipeline"></a>
## 模式 4：数据收集流水线

按固定间隔抓取数据，保存到文件，并检测随时间变化的趋势。这种模式将脚本（用于采集）与 agent（用于分析）结合起来。

```python title="~/.hermes/scripts/collect-prices.py"
import json, os, urllib.request
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.hermes/data/prices")
os.makedirs(DATA_DIR, exist_ok=True)

# 获取当前数据（示例：加密货币价格）
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
data = json.loads(urllib.request.urlopen(url, timeout=30).read())

# 追加到历史记录文件
entry = {"timestamp": datetime.now().isoformat(), "prices": data}
history_file = os.path.join(DATA_DIR, "history.jsonl")
with open(history_file, "a") as f:
    f.write(json.dumps(entry) + "\n")

# 加载近期历史数据用于分析
lines = open(history_file).readlines()
recent = [json.loads(l) for l in lines[-24:]]  # 最近 24 个数据点

# 输出给 agent
print(f"当前：BTC=${data['bitcoin']['usd']}, ETH=${data['ethereum']['usd']}")
print(f"已收集数据点：共计 {len(lines)} 条，展示最近 {len(recent)} 条")
print(f"\n近期历史：")
for r in recent[-6:]:
    print(f"  {r['timestamp']}: BTC=${r['prices']['bitcoin']['usd']}, ETH=${r['prices']['ethereum']['usd']}")
```
```bash
/cron add "every 1h" "分析脚本输出的价格数据。报告：
1. 当前价格
2. 最近6个数据点的趋势方向（上涨/下跌/持平）
3. 任何显著波动（变化超过5%）

如果价格持平且无显著变化，请回复 [SILENT]。
如果有显著波动，请解释发生了什么。" \
  --script ~/.hermes/scripts/collect-prices.py \
  --name "价格追踪器" \
  --deliver telegram
```

脚本负责机械性的数据采集；Agent 则添加了推理层。

---

<a id="pattern-5-multi-skill-workflow"></a>
## 模式 5：多技能工作流

将多个技能串联起来，用于处理复杂的定时任务。技能会在提示词执行前按顺序加载。

```bash
# 使用 arxiv 技能查找论文，然后使用 obsidian 技能保存笔记
/cron add "0 8 * * *" "在 arXiv 上搜索过去一天内关于'语言模型推理'的最有趣的3篇论文。为每篇论文创建一个 Obsidian 笔记，包含标题、作者、摘要总结和主要贡献。" \
  --skill arxiv \
  --skill obsidian \
  --name "论文摘要"
```
从工具直接创建：

```python
cronjob(
    action="create",
    skills=["arxiv", "obsidian"],
    prompt="搜索 arXiv 上过去一天关于'语言模型推理'的论文。将排名前 3 的论文保存为 Obsidian 笔记。",
    schedule="0 8 * * *",
    name="论文摘要",
    deliver="local"
)
```

技能按顺序加载——先加载 `arxiv`（教 Agent 如何搜索论文），再加载 `obsidian`（教如何写笔记）。提示词将两者串联起来。

---

<a id="managing-your-jobs"></a>
## 管理你的任务

```bash
# 列出所有活跃任务
/cron list

# 立即触发某个任务（用于测试）
/cron run <job_id>

# 暂停某个任务（不删除）
/cron pause <job_id>

# 修改运行中任务的调度或提示词
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "更新后的任务描述"

# 为已有任务添加或移除技能
/cron edit <job_id> --skill arxiv --skill obsidian
/cron edit <job_id> --clear-skills

# 永久删除某个任务
/cron remove <job_id>
```

---

<a id="delivery-targets"></a>
## 交付目标
`--deliver` 标志控制结果的去向：

| 目标 | 示例 | 使用场景 |
|--------|---------|----------|
| `origin` | `--deliver origin` | 创建任务的同一聊天（默认） |
| `local` | `--deliver local` | 仅保存到本地文件 |
| `telegram` | `--deliver telegram` | 你的 Telegram 主频道 |
| `discord` | `--deliver discord` | 你的 Discord 主频道 |
| `slack` | `--deliver slack` | 你的 Slack 主频道 |
| 特定聊天 | `--deliver telegram:-1001234567890` | 一个特定的 Telegram 群组 |
| 线程化 | `--deliver telegram:-1001234567890:17585` | 一个特定的 Telegram 主题线程 |

---

<a id="tips"></a>
## 提示

**让提示词自包含。** 在 cron 任务中的 Agent 无法记忆你的对话历史。请直接将 URL、仓库名称、格式偏好和交付指令写在提示词中。

**善用 `[SILENT]`。** 对于监控类任务，始终包含类似“如果没有任何变化，请回复 `[SILENT]`”的指令。这样可以避免通知噪音。

**使用脚本进行数据收集。** `script` 参数可让 Python 脚本处理繁重的工作（HTTP 请求、文件 I/O、状态跟踪）。Agent 仅查看脚本的标准输出，并基于此进行推理。这比让 Agent 自行抓取数据更廉价、更可靠。
**使用 `/cron run` 进行测试。** 在等待调度触发之前，请使用 `/cron run &lt;job_id&gt;` 立即执行并验证输出是否正确。

**调度表达式。** 支持的格式：相对延迟（`30m`）、间隔（`every 2h`）、标准 cron 表达式（`0 9 * * *`）和 ISO 时间戳（`2025-06-15T09:00:00`）。不支持自然语言如 `daily at 9am` — 请改用 `0 9 * * *`。

---

*有关完整的 cron 参考——所有参数、边缘情况和内部机制——请参阅[定时任务（Cron）](/user-guide/features/cron)。*
