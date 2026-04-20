---
sidebar_position: 6
title: "Signal"
description: "通过 signal-cli 守护进程将 Hermes Agent 设置为 Signal 机器人"
---

# Signal 设置 {#signal-setup}

Hermes 通过以 HTTP 模式运行的 [signal-cli](https://github.com/AsamK/signal-cli) 守护进程连接到 Signal。适配器通过 SSE (Server-Sent Events) 实时流式传输消息，并通过 JSON-RPC 发送响应。

Signal 是最注重隐私的主流通讯软件 —— 默认端到端加密、开源协议、极少收集元数据。这使其成为处理安全敏感型 Agent 工作流的理想选择。

:::info 无需新增 Python 依赖
Signal 适配器使用 `httpx`（已是 Hermes 的核心依赖）进行所有通信。不需要安装额外的 Python 包。你只需要在外部安装好 signal-cli 即可。
:::

---

## 前提条件 {#prerequisites}

- **signal-cli** — 基于 Java 的 Signal 客户端 ([GitHub](https://github.com/AsamK/signal-cli))
- **Java 17+** 运行时 — signal-cli 运行必需
- **一个手机号** 且已安装 Signal（用于关联为副设备）

### 安装 signal-cli {#installing-signal-cli}

```bash
# macOS
<a id="no-new-python-dependencies"></a>
brew install signal-cli

# Linux (下载最新发行版)
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} \
  https://github.com/AsamK/signal-cli/releases/latest | sed 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
sudo tar xf "signal-cli-${VERSION}.tar.gz" -C /opt
sudo ln -sf "/opt/signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/
```

:::caution
signal-cli **不在** apt 或 snap 仓库中。上述 Linux 安装方式是直接从 [GitHub releases](https://github.com/AsamK/signal-cli/releases) 下载的。
:::

---

## 第 1 步：关联你的 Signal 账号 {#step-1-link-your-signal-account}

Signal-cli 以**关联设备**的方式工作 —— 类似于 WhatsApp 网页版，但针对的是 Signal。你的手机仍然是主设备。

```bash
# 生成关联 URI（会显示二维码或链接）
signal-cli link -n "HermesAgent"
```

1. 在手机上打开 **Signal**
2. 进入 **设置 → 已关联设备**
3. 点击 **关联新设备**
4. 扫描二维码或输入 URI

---

## 第 2 步：启动 signal-cli 守护进程 {#step-2-start-the-signal-cli-daemon}

```bash
# 将 +1234567890 替换为你的 Signal 手机号（E.164 格式）
signal-cli --account +1234567890 daemon --http 127.0.0.1:8080
```

:::tip
请保持此进程在后台运行。你可以使用 `systemd`、`tmux`、`screen` 或将其作为服务运行。
:::

验证是否运行成功：

```bash
curl http://127.0.0.1:8080/api/v1/check
# 应该返回：{"versions":{"signal-cli":...}}
```

---

## 第 3 步：配置 Hermes {#step-3-configure-hermes}

最简单的方法：

```bash
hermes gateway setup
```

从平台菜单中选择 **Signal**。向导将执行以下操作：

1. 检查是否安装了 signal-cli
2. 提示输入 HTTP URL（默认：`http://127.0.0.1:8080`）
3. 测试与守护进程的连通性
4. 询问你的账号手机号
5. 配置允许的用户和访问策略

### 手动配置 {#manual-configuration}

添加到 `~/.hermes/.env`：

```bash
# 必填
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1234567890

# 安全（推荐）
SIGNAL_ALLOWED_USERS=+1234567890,+0987654321    # 逗号分隔的 E.164 号码或 UUID

# 选填
SIGNAL_GROUP_ALLOWED_USERS=groupId1,groupId2     # 启用群组（留空则禁用，* 代表所有）
SIGNAL_HOME_CHANNEL=+1234567890                  # cron 任务的默认发送目标
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 作为用户服务安装
sudo hermes gateway install --system   # 仅限 Linux：开机自启系统服务
```

---

## 访问控制 {#access-control}

### 私聊 (DM) 访问 {#dm-access}

私聊访问遵循与其他所有 Hermes 平台相同的模式：

1. **设置了 `SIGNAL_ALLOWED_USERS`** → 只有这些用户可以发消息
2. **未设置允许列表** → 未知用户会收到私聊配对码（通过 `hermes pairing approve signal CODE` 批准）
3. **`SIGNAL_ALLOW_ALL_USERS=true`** → 任何人都可以发消息（请谨慎使用）

### 群组访问 {#group-access}

群组访问由 `SIGNAL_GROUP_ALLOWED_USERS` 环境变量控制：

| 配置 | 行为 |
|---------------|----------|
| 未设置（默认） | 忽略所有群组消息。Agent 仅响应私聊。 |
| 设置群组 ID | 仅监听列表中的群组（例如 `groupId1,groupId2`）。 |
| 设置为 `*` | Agent 会在它加入的任何群组中做出响应。 |

---

## 功能特性 {#features}

### 附件 {#attachments}

适配器支持双向发送和接收媒体文件。

**接收**（用户 → Agent）：

- **图片** — PNG, JPEG, GIF, WebP（通过 magic bytes 自动检测）
- **音频** — MP3, OGG, WAV, M4A（如果配置了 Whisper，语音消息将被转录）
- **文档** — PDF, ZIP 及其他文件类型

**发送**（Agent → 用户）：

Agent 可以通过响应中的 `MEDIA:` 标签发送媒体文件。支持以下交付方法：

- **图片** — `send_image_file` 将 PNG, JPEG, GIF, WebP 作为原生 Signal 附件发送
- **语音** — `send_voice` 将音频文件（OGG, MP3, WAV, M4A, AAC）作为附件发送
- **视频** — `send_video` 发送 MP4 视频文件
- **文档** — `send_document` 发送任何文件类型（PDF, ZIP 等）

所有发出的媒体都通过 Signal 的标准附件 API 进行。与其他一些平台不同，Signal 在协议层级不区分语音消息和文件附件。

附件大小限制：**100 MB**（双向）。

### 输入状态指示 {#typing-indicators}

Agent 在处理消息时会发送“正在输入”指示，每 8 秒刷新一次。

### 手机号脱敏 {#phone-number-redaction}

日志中的所有手机号都会自动脱敏：
- `+15551234567` → `+155****4567`
- 这适用于 Hermes 网关日志和全局脱敏系统

### 备忘录 (Note to Self) 模式（单号码设置） {#note-to-self-single-number-setup}

如果你在自己的手机号上将 signal-cli 作为**关联副设备**运行（而不是使用单独的机器人号码），你可以通过 Signal 的“备忘录 (Note to Self)”功能与 Hermes 交互。

只需从手机给自己发消息 —— signal-cli 会接收到它，Hermes 会在同一个对话中回复。

**工作原理：**
- “备忘录”消息以 `syncMessage.sentMessage` 信封形式到达
- 适配器检测到这些消息是发给 Agent 自身账号的，并将其作为常规上行消息处理
- 回声保护（发送时间戳追踪）可防止无限循环 —— Agent 自身的回复会被自动过滤掉

**无需额外配置。** 只要 `SIGNAL_ACCOUNT` 与你的手机号匹配，该功能就会自动生效。

### 健康监测 {#health-monitoring}

适配器会监控 SSE 连接，并在以下情况自动重连：
- 连接断开（使用指数退避策略：2秒 → 60秒）
- 120 秒内未检测到活动（会 ping signal-cli 进行验证）

---

## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|---------|----------|
| 设置时提示 **"Cannot reach signal-cli"** | 确保 signal-cli 守护进程正在运行：`signal-cli --account +你的号码 daemon --http 127.0.0.1:8080` |
| **收不到消息** | 检查 `SIGNAL_ALLOWED_USERS` 是否包含了发送者的 E.164 格式号码（带 `+` 前缀） |
| **"signal-cli not found on PATH"** | 安装 signal-cli 并确保它在 PATH 中，或者使用 Docker |
| **连接不断断开** | 检查 signal-cli 日志中的错误。确保安装了 Java 17+。 |
| **群组消息被忽略** | 配置 `SIGNAL_GROUP_ALLOWED_USERS` 为特定的群组 ID，或设为 `*` 允许所有群组。 |
| **Agent 不回复任何人** | 配置 `SIGNAL_ALLOWED_USERS`，使用私聊配对，或者如果你希望更广泛的访问权限，在网关策略中显式允许所有用户。 |
| **消息重复** | 确保只有一个 signal-cli 实例在监听你的手机号 |

---

## 安全性 {#security}

:::warning
**务必配置访问控制。** Agent 默认拥有终端访问权限。如果没有设置 `SIGNAL_ALLOWED_USERS` 或进行私聊配对，网关会出于安全考虑拒绝所有传入消息。
:::

- 所有日志输出中的手机号都会被脱敏
- 使用私聊配对或显式允许列表来安全地接入新用户
- 除非明确需要群组支持，否则请保持群组禁用，或者仅将你信任的群组加入允许列表
- Signal 的端到端加密保护传输中的消息内容
- `~/.local/share/signal-cli/` 中的 signal-cli 会话数据包含账号凭据 —— 请像保护密码一样保护它
---

## 环境变量参考 {#environment-variables-reference}

| 变量 | 是否必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `SIGNAL_HTTP_URL` | 是 | — | signal-cli HTTP 接口地址 |
| `SIGNAL_ACCOUNT` | 是 | — | Bot 的电话号码 (E.164 格式) |
| `SIGNAL_ALLOWED_USERS` | 否 | — | 允许访问的电话号码或 UUID，多个以逗号分隔 |
| `SIGNAL_GROUP_ALLOWED_USERS` | 否 | — | 要监听的群组 ID，或使用 `*` 表示所有群组（留空则禁用群组功能） |
| `SIGNAL_ALLOW_ALL_USERS` | 否 | `false` | 允许任何用户进行交互（跳过白名单检查） |
| `SIGNAL_HOME_CHANNEL` | 否 | — | 定时任务（cron jobs）的默认发送目标 |
