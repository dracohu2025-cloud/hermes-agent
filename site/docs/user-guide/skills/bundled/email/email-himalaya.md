---
title: "Himalaya — Himalaya CLI: 在终端中收发 IMAP/SMTP 邮件"
sidebar_label: "Himalaya"
description: "Himalaya CLI: 在终端中收发 IMAP/SMTP 邮件"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Himalaya {#himalaya}

Himalaya CLI：在终端中收发 IMAP/SMTP 邮件。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/email/himalaya` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `Email`、`IMAP`、`SMTP`、`CLI`、`Communication` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

# Himalaya 邮件 CLI {#himalaya-email-cli}

Himalaya 是一个 CLI 邮件客户端，让你可以通过终端使用 IMAP、SMTP、Notmuch 或 Sendmail 后端来管理邮件。

## 参考 {#references}

- `references/configuration.md`（配置文件设置 + IMAP/SMTP 认证）
- `references/message-composition.md`（用于编写邮件的 MML 语法）

## 前置条件 {#prerequisites}

1. 已安装 Himalaya CLI（运行 `himalaya --version` 验证）
2. 配置文件位于 `~/.config/himalaya/config.toml`
3. 已配置 IMAP/SMTP 凭据（密码安全存储）

### 安装 {#installation}

```bash
# 预编译二进制（Linux/macOS — 推荐）
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# macOS 通过 Homebrew
brew install himalaya

# 或通过 cargo（任何支持 Rust 的平台）
cargo install himalaya --locked
```

## 配置设置 {#configuration-setup}

运行交互式向导来设置账户：

```bash
himalaya account configure
```

或手动创建 `~/.config/himalaya/config.toml`：

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"  # 或使用 keyring

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"
```

## Hermes 集成说明 {#hermes-integration-notes}

- **读取、列出、搜索、移动、删除** — 所有这些操作都直接通过终端工具完成
- **编写/回复/转发** — 推荐使用管道输入（`cat << EOF | himalaya template send`）以确保可靠性。交互式 `$EDITOR` 模式可与 `pty=true` + 后台 + 进程工具配合使用，但需要了解编辑器及其命令
- 使用 `--output json` 获取结构化输出，便于程序化解析
- `himalaya account configure` 向导需要交互式输入 — 请使用 PTY 模式：`terminal(command="himalaya account configure", pty=true)`

## 常用操作 {#common-operations}

### 列出文件夹 {#list-folders}

```bash
himalaya folder list
```

### 列出邮件 {#list-emails}

列出收件箱（默认）中的邮件：
```bash
himalaya envelope list
```

列出特定文件夹中的邮件：

```bash
himalaya envelope list --folder "Sent"
```

分页列出：

```bash
himalaya envelope list --page 1 --page-size 20
```

### 搜索邮件 {#search-emails}

```bash
himalaya envelope list from john@example.com subject meeting
```

### 阅读邮件 {#read-an-email}

按 ID 阅读邮件（显示纯文本）：

```bash
himalaya message read 42
```

导出原始 MIME：

```bash
himalaya message export 42 --full
```

### 回复邮件 {#reply-to-an-email}

要从 Hermes 以非交互方式回复，请先阅读原始邮件，编写回复内容，然后通过管道发送：

```bash
# 获取回复模板，编辑后发送
himalaya template reply 42 | sed 's/^$/\n你的回复内容在这里\n/' | himalaya template send
```

或者手动构建回复：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: 原始主题
In-Reply-To: <原始消息ID>

你的回复内容。
EOF
```

回复全部（交互式——需要 $EDITOR，建议改用上面的模板方式）：

```bash
himalaya message reply 42 --all
```

### 转发邮件 {#forward-an-email}

```bash
# 获取转发模板并通过管道修改
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

### 撰写新邮件 {#write-a-new-email}

**非交互式（在 Hermes 中使用此方式）**——通过 stdin 管道发送消息：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: 测试消息

来自 Himalaya 的问候！
EOF
```

或者使用 headers 标志：

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "消息正文"
```

注意：`himalaya message write` 如果没有通过管道输入，会打开 `$EDITOR`。这在 `pty=true` + 后台模式下可行，但管道方式更简单可靠。

### 移动/复制邮件 {#move-copy-emails}

移动到文件夹：

```bash
himalaya message move 42 "Archive"
```

复制到文件夹：

```bash
himalaya message copy 42 "Important"
```

### 删除邮件 {#delete-an-email}

```bash
himalaya message delete 42
```

### 管理标记 {#manage-flags}

添加标记：

```bash
himalaya flag add 42 --flag seen
```

移除标记：

```bash
himalaya flag remove 42 --flag seen
```

## 多账户 {#multiple-accounts}

列出账户：

```bash
himalaya account list
```

使用特定账户：

```bash
himalaya --account work envelope list
```

## 附件 {#attachments}

保存邮件中的附件：

```bash
himalaya attachment download 42
```

保存到指定目录：

```bash
himalaya attachment download 42 --dir ~/Downloads
```

## 输出格式 {#output-formats}

大多数命令支持 `--output` 以输出结构化内容：

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

## 调试 {#debugging}

启用调试日志：

```bash
RUST_LOG=debug himalaya envelope list
```

带回溯的完整跟踪：

```bash
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## 提示 {#tips}

- 使用 `himalaya --help` 或 `himalaya &lt;command&gt; --help` 查看详细用法。
- 消息 ID 相对于当前文件夹；切换文件夹后请重新列出。
- 要撰写带附件的富文本邮件，请使用 MML 语法（参见 `references/message-composition.md`）。
- 使用 `pass`、系统密钥环或输出密码的命令安全存储密码。
