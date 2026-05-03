---
title: "Apple Reminders — 通过 remindctl 管理 Apple Reminders：添加、列出、完成"
sidebar_label: "Apple Reminders"
description: "通过 remindctl 管理 Apple Reminders：添加、列出、完成"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Apple Reminders {#apple-reminders}

通过 remindctl 管理 Apple Reminders：添加、列出、完成。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/apple-reminders` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `Reminders`、`tasks`、`todo`、`macOS`、`Apple` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="apple-reminders"></a>
# Apple Reminders

使用 `remindctl` 直接从终端管理 Apple Reminders。任务通过 iCloud 在所有 Apple 设备间同步。

## 前提条件 {#prerequisites}

- 安装了 Reminders.app 的 **macOS**
- 安装：`brew install steipete/tap/remindctl`
- 在提示时授予 Reminders 权限
- 检查：`remindctl status` / 请求授权：`remindctl authorize`

## 何时使用 {#when-to-use}

- 用户提到“提醒”或“Reminders app”
- 创建带有截止日期的个人待办事项，并同步到 iOS
- 管理 Apple Reminders 列表
- 用户希望任务出现在他们的 iPhone/iPad 上

## 何时不使用 {#when-not-to-use}

- 安排 Agent 提醒 → 改用 cronjob 工具
- 日历事件 → 使用 Apple Calendar 或 Google Calendar
- 项目任务管理 → 使用 GitHub Issues、Notion 等
- 如果用户说“提醒我”但实际是指 Agent 提醒 → 先澄清

## 快速参考 {#quick-reference}

### 查看提醒 {#view-reminders}

```bash
remindctl                    # 今天的提醒
remindctl today              # 今天
remindctl tomorrow           # 明天
remindctl week               # 本周
remindctl overdue            # 已过期
remindctl all                # 所有
remindctl 2026-01-04         # 指定日期
```

### 管理列表 {#manage-lists}

```bash
remindctl list               # 列出所有列表
remindctl list Work          # 显示指定列表
remindctl list Projects --create    # 创建列表
remindctl list Work --delete        # 删除列表
```

### 创建提醒 {#create-reminders}

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### 完成 / 删除 {#complete-delete}

```bash
remindctl complete 1 2 3          # 按 ID 完成
remindctl delete 4A83 --force     # 按 ID 删除
```

### 输出格式 {#output-formats}

```bash
remindctl today --json       # JSON 格式，便于脚本处理
remindctl today --plain      # TSV 格式
remindctl today --quiet      # 仅显示计数
```

## 日期格式 {#date-formats}

`--due` 和日期过滤器接受的格式：
- `today`、`tomorrow`、`yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601（`2026-01-04T12:34:56Z`）

## 规则 {#rules}

1. 当用户说“提醒我”时，请澄清：是 Apple Reminders（同步到手机）还是 Agent 的 cronjob 提醒
2. 创建前务必确认提醒内容和截止日期
3. 使用 `--json` 进行程序化解析
