---
title: "Himalaya — Himalaya CLI：通过终端使用 IMAP/SMTP 收发邮件"
sidebar_label: "Himalaya"
description: "Himalaya CLI：通过终端使用 IMAP/SMTP 收发邮件"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="himalaya"></a>
# Himalaya

Himalaya CLI：通过终端使用 IMAP/SMTP 收发邮件。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/email/himalaya` |
| 版本 | `1.1.0` |
| 作者 | 社区 |
| 许可协议 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Email`, `IMAP`, `SMTP`, `CLI`, `Communication` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是在触发此技能时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="himalaya-email-cli"></a>
# Himalaya 邮件 CLI

Himalaya 是一款 CLI 邮件客户端，可通过终端使用 IMAP、SMTP、Notmuch 或 Sendmail 后端管理邮件。

<a id="references"></a>
## 参考文档

- `references/configuration.md`（配置文件设置 + IMAP/SMTP 身份验证）
- `references/message-composition.md`（用于撰写邮件的 MML 语法）

<a id="prerequisites"></a>
## 先决条件

1. 已安装 Himalaya CLI（运行 `himalaya --version` 确认）
2. 配置文件 `~/.config/himalaya/config.toml`
3. 已配置 IMAP/SMTP 凭据（密码安全存储）

<a id="installation"></a>
### 安装

```bash
# 预编译二进制（Linux/macOS — 推荐）
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# macOS 通过 Homebrew
brew install himalaya

# 或通过 cargo（任何安装了 Rust 的平台）
cargo install himalaya --locked
```

<a id="configuration-setup"></a>
## 配置设置

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

# 文件夹别名（himalaya v1.2.0+ 语法）。当服务器的文件夹名称与 himalaya 的规范名称
# （inbox/sent/drafts/trash）不匹配时必须使用。Gmail 是常见情况——请参阅
# `references/configuration.md` 了解 `[Gmail]/Sent Mail` 的映射。
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

> **关于别名语法的注意事项。** v1.2.0 之前的文档使用了
> `[accounts.NAME.folder.alias]` 子节（单数 `alias`）。
> v1.2.0 会静默忽略该形式——TOML 解析正常，但别名解析器不会读取它，
> 每次查找都会回退到规范名称。在 Gmail 上，这意味着 SMTP 投递成功后
> “保存到已发送”会失败，`himalaya message send` 以非零退出。
> 任何在该退出码上重试的调用者（Agent、脚本、用户）都会重新执行整个发送过程
> ——包括 SMTP——产生重复邮件发送给收件人。始终使用 `folder.aliases.X`
> （复数、点号分隔的键，直接放在 `[accounts.NAME]` 下）。
<a id="hermes-integration-notes"></a>
## Hermes 集成说明

- **读取、列出、搜索、移动、删除** 均直接通过终端工具完成
- **撰写/回复/转发** 建议使用管道输入（`cat << EOF | himalaya template send`）以确保可靠性。交互式 `$EDITOR` 模式在 `pty=true` + 后台 + 进程工具配合下可用，但需要了解编辑器及其命令
- 使用 `--output json` 获取结构化输出，便于程序解析
- `himalaya account configure` 向导需要交互输入——请使用 PTY 模式：`terminal(command="himalaya account configure", pty=true)`

<a id="common-operations"></a>
## 常见操作

<a id="list-folders"></a>
### 列出文件夹

```bash
himalaya folder list
```

<a id="list-emails"></a>
### 列出邮件

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

<a id="search-emails"></a>
### 搜索邮件

```bash
himalaya envelope list from john@example.com subject meeting
```

<a id="read-an-email"></a>
### 读取邮件

按 ID 读取邮件（显示纯文本）：

```bash
himalaya message read 42
```

导出原始 MIME：

```bash
himalaya message export 42 --full
```

<a id="reply-to-an-email"></a>
### 回复邮件

要以非交互方式从 Hermes 回复，请读取原始邮件，编写回复，然后通过管道发送：

```bash
# 获取回复模板，编辑后发送
himalaya template reply 42 | sed 's/^$/\n您的回复内容放在这里\n/' | himalaya template send
```

或者手动构建回复：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: 原始主题
In-Reply-To: <原始邮件ID>

在此处填写回复内容。
EOF
```

回复所有人（交互模式——需要 $EDITOR，建议改用上面的模板方式）：

```bash
himalaya message reply 42 --all
```

<a id="forward-an-email"></a>
### 转发邮件

```bash
# 获取转发模板并通过管道修改
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

<a id="write-a-new-email"></a>
### 撰写新邮件

**非交互方式（在 Hermes 中使用此方式）**——通过 stdin 管道传递邮件内容：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: 测试邮件

来自 Himalaya 的问候！
EOF
```

或者使用标题标志：

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:测试" "邮件正文在此"
```

注意：`himalaya message write` 如果没有管道输入，会打开 `$EDITOR`。这可以通过 `pty=true` + 后台模式工作，但管道方式更简单可靠。

<a id="move-copy-emails"></a>
### 移动/复制邮件

移动到文件夹：

```bash
himalaya message move 42 "Archive"
```

复制到文件夹：

```bash
himalaya message copy 42 "Important"
```

<a id="delete-an-email"></a>
### 删除邮件

```bash
himalaya message delete 42
```

<a id="manage-flags"></a>
### 管理标志

添加标志：

```bash
himalaya flag add 42 --flag seen
```

移除标志：

```bash
himalaya flag remove 42 --flag seen
```

<a id="multiple-accounts"></a>
## 多账户

列出账户：

```bash
himalaya account list
```

使用特定账户：

```bash
himalaya --account work envelope list
```
<a id="attachments"></a>
## 附件

从邮件中保存附件：

```bash
himalaya attachment download 42
```

保存到指定目录：

```bash
himalaya attachment download 42 --dir ~/Downloads
```

<a id="output-formats"></a>
## 输出格式

大部分命令支持使用 `--output` 输出结构化结果：

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

<a id="debugging"></a>
## 调试

启用调试日志：

```bash
RUST_LOG=debug himalaya envelope list
```

带完整回溯的详细跟踪：

```bash
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

<a id="tips"></a>
## 提示

- 使用 `himalaya --help` 或 `himalaya &lt;command&gt; --help` 查看详细用法。
- 邮件 ID 基于当前文件夹，切换文件夹后需要重新列表。
- 如需编写带有附件的富文本邮件，请使用 MML 语法（参见 `references/message-composition.md`）。
- 使用 `pass`、系统钥匙串或能输出密码的命令安全存储密码。
