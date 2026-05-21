---
sidebar_position: 12
title: "将脚本输出管道到消息平台"
description: "使用 `hermes send` 将任何 shell 脚本、定时任务、CI 钩子或监控守护进程的文本发送到 Telegram、Discord、Slack、Signal 等平台。"
---

<a id="pipe-script-output-to-messaging-platforms"></a>
# 将脚本输出管道到消息平台

`hermes send` 是一个轻量、可编写脚本的 CLI 工具，可以将消息推送到 Hermes 已配置的任何消息平台。可以将其视为跨平台的 `curl` 通知工具——你无需运行网关，无需 LLM，也无需在每个脚本中重新粘贴机器人令牌。

适用场景：

- 系统监控（内存、磁盘、GPU 温度、长时间运行的任务完成）
- CI/CD 通知（部署完成、测试失败）
- 需要将结果通知你的定时任务脚本
- 从终端快速发送一次性消息
- 将任何工具的输出管道到任何地方（`make | hermes send --to slack:#builds`）

该命令复用 `hermes gateway` 已使用的相同凭证和平台适配器，因此无需维护第二套配置。

---

<a id="quick-start"></a>
## 快速开始

```bash
# 将纯文本发送到平台的默认频道
hermes send --to telegram "deploy finished"

# 通过管道传入标准输出
echo "RAM 92%" | hermes send --to telegram:-1001234567890

# 发送文件
hermes send --to discord:#ops --file /tmp/report.md

# 附加主题/标题行
hermes send --to slack:#eng --subject "[CI] build.log" --file build.log

# 线程目标（Telegram 话题、Discord 线程）
hermes send --to telegram:-1001234567890:17585 "threaded reply"

# 列出所有已配置的目标
hermes send --list

# 按平台筛选
hermes send --list telegram
```

---

<a id="argument-reference"></a>
## 参数参考

| 标志 | 描述 |
|------|------|
| `-t, --to TARGET` | 目标。参见[目标格式](#target-formats)。 |
| `message` (位置参数) | 消息文本。省略时从 `--file` 或标准输入读取。 |
| `-f, --file PATH` | 从文件读取内容。`--file -` 强制从标准输入读取。 |
| `-s, --subject LINE` | 在内容前添加标题/主题行。 |
| `-l, --list` | 列出可用的目标。可选的位置参数平台筛选器。 |
| `-q, --quiet` | 成功时不在标准输出显示（仅返回退出码——适合脚本使用）。 |
| `--json` | 发送后输出原始的 JSON 结果。 |
| `-h, --help` | 显示内置帮助文本。 |
<a id="target-formats"></a>
### 目标格式

| 格式 | 示例 | 含义 |
|--------|---------|---------|
| `platform` | `telegram` | 发送到该平台配置的默认频道 |
| `platform:chat_id` | `telegram:-1001234567890` | 指定数字化的聊天/群组/用户 |
| `platform:chat_id:thread_id` | `telegram:-1001234567890:17585` | 指定线程或 Telegram 论坛主题 |
| `platform:#channel` | `discord:#ops` | 人类可读的频道名（根据频道目录解析） |
| `platform:+E164` | `signal:+15551234567` | 使用电话号码寻址的平台：Signal、SMS、WhatsApp |

Hermes 自带适配器的任何平台都可作为目标：
`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、
`mattermost`、`feishu`、`dingtalk`、`wecom`、`weixin`、`email` 等。

<a id="exit-codes"></a>
### 退出码

| 退出码 | 含义 |
|------|---------|
| `0` | 发送（或列出）成功 |
| `1` | 平台层面投递失败（认证、权限、网络问题） |
| `2` | 用法 / 参数 / 配置错误 |

退出码遵循标准的 Unix 惯例，因此你的脚本可以像对待 `curl` 或 `grep` 一样，根据它们进行分支处理。

---

<a id="message-body-resolution"></a>
## 消息正文解析

`hermes send` 按以下顺序解析消息正文：

1. **位置参数** — `hermes send --to telegram "hi"`
2. **`--file PATH`** — `hermes send --to telegram --file msg.txt`
3. **管道标准输入** — `echo hi | hermes send --to telegram`

当标准输入为 TTY（即没有管道输入）时，Hermes **不会**等待输入——而是给出清晰的用法错误提示。这可以防止脚本因意外省略正文内容而卡住。
---

<a id="real-world-examples"></a>
## 真实场景示例

<a id="monitoring-memory-disk-alerts"></a>
### 监控：内存 / 磁盘告警

将 watchdog 中零散的 `curl https://api.telegram.org/...` 调用替换为一行可移植的命令：

```bash
#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  hermes send --to telegram --subject "⚠ MEMORY WARNING" \
    "RAM ${ram_pct}% on $(hostname)"
fi
```

由于 `hermes send` 复用了你的 Hermes 配置，同一脚本在安装了 Hermes 的任何主机上都能工作——无需手动向每台机器的环境变量里导出 bot token。

:::tip 不要让告警针对网关自身
对于 watchdog 在网关自身出现故障时（如 OOM 告警、磁盘满告警）可能触发的场景，请继续使用最小化的 `curl` 调用，而不是 `hermes send`。如果 Python 解释器因机器负载过高而无法加载，你仍然需要那条告警能发出去。
:::
<a id="don-t-alert-the-gateway-about-itself"></a>

<a id="ci-cd-build-and-test-results"></a>
### CI / CD：构建与测试结果

```bash
# 在 .github/workflows/deploy.yml 或任何 CI 脚本中
if ./scripts/deploy.sh; then
  hermes send --to slack:#deploys "✅ ${CI_COMMIT_SHA:0:7} deployed"
else
  tail -n 100 deploy.log | hermes send \
    --to slack:#deploys --subject "❌ deploy failed"
  exit 1
fi
```

<a id="cron-daily-report"></a>
### Cron：每日报告

```bash
# Crontab 条目
0 9 * * * /usr/local/bin/generate-metrics.sh \
  | /home/me/.hermes/bin/hermes send \
      --to telegram --subject "Daily metrics $(date +%Y-%m-%d)"
```

<a id="long-running-tasks-ping-when-done"></a>
### 长时间运行的任务：完成后发送通知

```bash
./train.py --epochs 200 && \
  hermes send --to telegram "training done" || \
  hermes send --to telegram "training failed (exit $?)"
```
<a id="scripting-with-json-and-quiet"></a>
### 使用 `--json` 和 `--quiet` 进行脚本编写

```bash
# 如果发送失败则硬性终止脚本；成功时不输出日志
hermes send --to telegram --quiet "keepalive" || {
  echo "Telegram 发送失败" >&2
  exit 1
}

# 捕获消息 ID，用于后续编辑或线程操作
msg_id=$(hermes send --to discord:#ops --json "build started" \
  | jq -r .message_id)
```

---

<a id="does-hermes-send-need-the-gateway-running"></a>
## `hermes send` 是否需要网关运行？

**通常不需要。** 对于任何使用机器人令牌的平台——Telegram、Discord、Slack、Signal、SMS、WhatsApp Cloud API 以及大多数其他平台——`hermes send` 会直接使用 `~/.hermes/.env` 和 `~/.hermes/config.yaml` 中的凭据调用平台的 REST 端点。它是一个独立的子进程，消息发送完毕后立即退出。

只有依赖持久化适配器连接的**插件平台**才需要网关保持运行（例如，一个保持长连接 WebSocket 的自定义插件）。在这种情况下，你会收到一条明确的错误提示，指向网关；启动网关 `hermes gateway start` 后再重试。

---

<a id="listing-and-discovering-targets"></a>
## 列出和发现目标

在向特定频道发送消息之前，你可以检查可用的目标：

```bash
# 列出所有已配置平台的所有目标
hermes send --list

# 仅列出 Telegram 目标
hermes send --list telegram

# 机器可读格式输出
hermes send --list --json
```

列表由 `~/.hermes/channel_directory.json` 生成，网关在运行时每隔几分钟刷新一次该文件。如果你看到“尚未发现任何频道”，请启动一次网关（`hermes gateway start`），以便它填充缓存。
人类友好的名称（`discord:#ops`、`slack:#engineering`）会在发送时根据此缓存进行解析，因此你无需记住数字 ID。

---

<a id="comparison-with-other-approaches"></a>
## 与其他方法的比较

| 方法 | 多平台 | 复用 Hermes 凭证 | 需要网关 | 最佳适用场景 |
|----------|----------------|---------------------|---------------|----------|
| `hermes send` | ✅ | ✅ | 否（机器人令牌） | 以下所有场景 |
| 对每个平台使用原始 `curl` | 每个平台单独编写脚本 | 手动 | 否 | 关键监控程序 |
| 带 `--deliver` 的 `cron` 任务 | ✅ | ✅ | 否 | 定时 Agent 任务 |
| `send_message` Agent 工具 | ✅ | ✅ | 否 | Agent 循环内部 |

`hermes send` 有意设计为最简单的接口。如果你需要让 Agent 决定说什么，请在聊天或 cron 任务中使用 `send_message` 工具。如果你需要定时运行并生成 LLM 内容，请使用 `cronjob(action='create', prompt=...)` 并指定 `deliver='telegram:...'`。如果你只需要传递原始字符串，请使用 `hermes send`。

---

<a id="related"></a>
## 相关文档

- [使用 Cron 自动化一切](/guides/automate-with-cron) — 定时任务，其输出会自动投递到任何平台。
- [网关内部机制](/developer-guide/gateway-internals) — `hermes send` 与 cron 投递共享的投递路由器。
- [消息平台设置](/user-guide/messaging/) — 每个平台的一次性配置。
