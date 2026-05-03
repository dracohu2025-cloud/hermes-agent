---
title: "Imessage — 在 macOS 上通过 imsg CLI 收发 iMessage/SMS"
sidebar_label: "Imessage"
description: "在 macOS 上通过 imsg CLI 收发 iMessage/SMS"
---

{/* 本页面由网站脚本（website/scripts/generate-skill-docs.py）根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Imessage {#imessage}

在 macOS 上通过 imsg CLI 收发 iMessage/SMS。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/imessage` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `iMessage`、`SMS`、`messaging`、`macOS`、`Apple` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="imessage"></a>
# iMessage

使用 `imsg` 通过 macOS Messages.app 读取和发送 iMessage/SMS。

## 前提条件 {#prerequisites}

- **macOS** 且 Messages.app 已登录
- 安装：`brew install steipete/tap/imsg`
- 为终端授予完全磁盘访问权限（系统设置 → 隐私 → 完全磁盘访问权限）
- 在提示时为 Messages.app 授予自动化权限

## 何时使用 {#when-to-use}

- 用户要求发送 iMessage 或短信
- 读取 iMessage 对话历史
- 检查最近的 Messages.app 聊天记录
- 向电话号码或 Apple ID 发送消息

## 何时不使用 {#when-not-to-use}

- Telegram/Discord/Slack/WhatsApp 消息 → 使用相应的网关通道
- 群聊管理（添加/移除成员）→ 不支持
- 批量/群发消息 → 务必先与用户确认

## 快速参考 {#quick-reference}

### 列出聊天 {#list-chats}

```bash
imsg chats --limit 10 --json
```

### 查看历史 {#view-history}

```bash
# 按聊天 ID
imsg history --chat-id 1 --limit 20 --json

# 附带附件信息
imsg history --chat-id 1 --limit 20 --attachments --json
```

### 发送消息 {#send-messages}

```bash
# 仅文本
imsg send --to "+14155551212" --text "Hello!"

# 带附件
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# 强制使用 iMessage 或 SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### 监听新消息 {#watch-for-new-messages}

```bash
imsg watch --chat-id 1 --attachments
```

## 服务选项 {#service-options}

- `--service imessage` — 强制 iMessage（要求收件人已启用 iMessage）
- `--service sms` — 强制 SMS（绿色气泡）
- `--service auto` — 由 Messages.app 决定（默认）

## 规则 {#rules}

1. **发送前务必确认收件人和消息内容**
2. **未经用户明确许可，绝不向未知号码发送消息**
3. **附加文件前确认文件路径存在**
4. **禁止滥发消息** — 限制发送频率

## 示例工作流 {#example-workflow}

用户：“给妈妈发短信说我会晚到”

```bash
# 1. 找到妈妈的聊天
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. 与用户确认：“找到妈妈 +1555123456。通过 iMessage 发送‘我会晚到’？”

# 3. 确认后发送
imsg send --to "+1555123456" --text "I'll be late"
```
