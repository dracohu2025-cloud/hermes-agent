---
title: "Watchers — 使用水印去重轮询 RSS、JSON API 和 GitHub"
sidebar_label: "Watchers"
description: "使用水印去重轮询 RSS、JSON API 和 GitHub"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="watchers"></a>
# Watchers

使用水印去重轮询 RSS、JSON API 和 GitHub。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/devops/watchers` 安装 |
| 路径 | `optional-skills/devops/watchers` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `cron`, `polling`, `rss`, `github`, `http`, `automation`, `monitoring` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Watchers

按时间间隔轮询外部源，仅对新项目做出反应。包含三个现成脚本和一个共享水印辅助工具；可将它们接入 cron 任务（或从终端临时运行）。

<a id="when-to-use"></a>
## 何时使用

- 用户想要监控 RSS/Atom 订阅源，并在有新条目时收到通知
- 用户想要监控 GitHub 仓库的 issues / pulls / releases / commits
- 用户想要轮询任意 JSON 端点，并在有新项目时收到通知
- 用户要求“为 X 设置一个 watcher”或“当 X 发生变化时通知我”

<a id="mental-model"></a>
## 心智模型

Watcher 只是一个脚本，它：

1. 从外部源获取数据
2. 与之前见过的 ID 的水印文件进行比较
3. 写回新的水印
4. 将新项目输出到 stdout（若无变化则无输出）

以下脚本处理所有这三个步骤。Agent 通过终端工具运行它们——无论是从 cron 任务、webhook 还是交互式聊天——并报告新内容。

<a id="ready-made-scripts"></a>
## 现成脚本

安装技能后，所有三个脚本都位于 `$HERMES_HOME/skills/devops/watchers/scripts/` 目录下。每个脚本都会读取 `WATCHER_STATE_DIR`（默认为 `$HERMES_HOME/watcher-state/`）中的状态文件，该文件由 `--name` 参数指定。

| 脚本 | 监控内容 | 去重键 |
|---|---|---|
| `watch_rss.py` | RSS 2.0 或 Atom 订阅源 URL | `&lt;guid&gt;` / `&lt;id&gt;` |
| `watch_http_json.py` | 返回对象列表的任意 JSON 端点 | 可配置的 id 字段 |
| `watch_github.py` | 仓库的 GitHub issues / pulls / releases / commits | `id` / `sha` |

所有三个脚本：

- 首次运行会记录基线——不会重放现有订阅源
- 水印是一个有界 ID 集合（最多 500 个），以限制内存使用
- 输出格式：每个项目为 `## <标题>\n&lt;URL&gt;\n\n<可选正文>`
- 无新内容时 stdout 为空——调用者将其视为静默
- 获取错误时返回非零退出码

<a id="usage"></a>
## 用法

直接从终端工具运行 watcher：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_rss.py \
  --name hn --url https://news.ycombinator.com/rss --max 5
```

监控 GitHub 仓库（在 `~/.hermes/.env` 中设置 `GITHUB_TOKEN` 以避免匿名用户 60 次/小时的速率限制）：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_github.py \
  --name hermes-issues --repo NousResearch/hermes-agent --scope issues
```

轮询任意 JSON API：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_http_json.py \
  --name api --url https://api.example.com/events \
  --id-field event_id --items-path data.events
```
<a id="wiring-into-cron"></a>
## 接入 cron

让 Agent 用类似下面的提示词来安排一个 cron 任务：

> 每 15 分钟运行一次 `watch_rss.py --name hn --url https://news.ycombinator.com/rss`。如果脚本有输出，就总结标题并发送。如果没输出，就保持沉默。

Agent 会在 cron 任务的 agent loop 中通过终端工具调用脚本；无需修改 cron 内置的 `--script` 参数。

<a id="state-files"></a>
## 状态文件

每个 watcher 都会写入 `$HERMES_HOME/watcher-state/&lt;name&gt;.json`。查看状态：

```bash
cat $HERMES_HOME/watcher-state/hn.json
```

强制重放（下次运行视为首次轮询）：

```bash
rm $HERMES_HOME/watcher-state/hn.json
```

<a id="writing-your-own"></a>
## 编写自己的 watcher

三个脚本都使用相同的模板：加载水印、获取数据、对比差异、保存状态、输出结果。`scripts/_watermark.py` 是共享的辅助模块；导入它即可免费获得原子写入、有界 ID 集合和首次运行基线。查看三个参考脚本中的任意一个，就能知道所需的样板代码有多简洁。

<a id="common-pitfalls"></a>
## 常见陷阱

1. **每次轮询都打印"没有新项目"的标题。** 调用方依赖空输出来判断静默状态。如果空差异时打印了任何内容，就会刷屏频道。自带的脚本已经处理了这个问题；自定义脚本也必须处理好。
2. **期望首次运行就输出项目。** 不会的——首次运行只是记录基线。如果你需要初始摘要，可以在首次运行后删除状态文件，或者在自定义脚本中添加 `--prime-with-latest N` 参数。
3. **水印无限制增长。** 共享辅助模块将 ID 上限设为 500。对于更新频繁的 feed 可以调高上限；在文件系统受限的环境中可以调低。
4. **把状态目录放在 Agent 沙箱无法写入的位置。** `$HERMES_HOME/watcher-state/` 始终是可写的。Docker/Modal 后端可能无法访问任意主机路径。
