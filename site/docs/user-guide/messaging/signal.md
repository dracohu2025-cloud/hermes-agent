---
sidebar_position: 6
title: "Signal"
description: "通过 signal-cli 守护进程将 Hermes Agent 设置为 Signal 信使机器人"
---

# Signal 设置 {#signal-setup}

Hermes 通过以 HTTP 模式运行的 [signal-cli](https://github.com/AsamK/signal-cli) 守护进程连接到 Signal。该适配器通过 SSE（服务器推送事件）实时流式传输消息，并通过 JSON-RPC 发送响应。

Signal 是最注重隐私的主流信使——默认端到端加密、开源协议、最小化元数据收集。这使得它非常适合安全敏感的 Agent 工作流。

:::info 无需新的 Python 依赖
<a id="no-new-python-dependencies"></a>
Signal 适配器使用 `httpx`（Hermes 已有的核心依赖）进行所有通信。不需要额外的 Python 包。你只需要在外部安装 signal-cli。
:::

---

<a id="prerequisites"></a>
## 前提条件 {#no-new-python-dependencies}

- **signal-cli** — 基于 Java 的 Signal 客户端（[GitHub](https://github.com/AsamK/signal-cli)）
- **Java 17+** 运行时 — signal-cli 所需
- **一个已安装 Signal 的手机号码**（用于作为辅助设备关联）

### 安装 signal-cli {#installing-signal-cli}

```bash
# macOS
brew install signal-cli

# Linux（下载最新版本）
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} \
  https://github.com/AsamK/signal-cli/releases/latest | sed 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
sudo tar xf "signal-cli-${VERSION}.tar.gz" -C /opt
sudo ln -sf "/opt/signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/
```

:::caution
signal-cli **不在** apt 或 snap 仓库中。上面的 Linux 安装方式直接从 [GitHub releases](https://github.com/AsamK/signal-cli/releases) 下载。
:::

---

## 步骤 1：关联你的 Signal 账号 {#step-1-link-your-signal-account}

Signal-cli 以**关联设备**的方式工作——就像 WhatsApp Web，但用于 Signal。你的手机仍然是主设备。

```bash
# 生成关联 URI（显示二维码或链接）
signal-cli link -n "HermesAgent"
```

1. 在手机上打开 **Signal**
2. 进入 **设置 → 关联设备**
3. 点击 **关联新设备**
4. 扫描二维码或输入 URI

---

## 步骤 2：启动 signal-cli 守护进程 {#step-2-start-the-signal-cli-daemon}

```bash
# 将 +1234567890 替换为你的 Signal 手机号码（E.164 格式）
signal-cli --account +1234567890 daemon --http 127.0.0.1:8080
```

:::tip
让它在后台保持运行。你可以使用 `systemd`、`tmux`、`screen`，或者将其作为服务运行。
:::

验证它是否在运行：

```bash
curl http://127.0.0.1:8080/api/v1/check
# 应返回：{"versions":{"signal-cli":...}}
```

---

## 步骤 3：配置 Hermes {#step-3-configure-hermes}

最简单的方式：

```bash
hermes gateway setup
```

从平台菜单中选择 **Signal**。向导将：

1. 检查 signal-cli 是否已安装
2. 提示输入 HTTP URL（默认：`http://127.0.0.1:8080`）
3. 测试与守护进程的连接
4. 询问你的账号手机号码
5. 配置允许的用户和访问策略

### 手动配置 {#manual-configuration}

添加到 `~/.hermes/.env`：

```bash
# 必填
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1234567890

# 安全（推荐）
SIGNAL_ALLOWED_USERS=+1234567890,+0987654321    # 逗号分隔的 E.164 号码或 UUID

# 可选
SIGNAL_GROUP_ALLOWED_USERS=groupId1,groupId2     # 启用群组（省略则禁用，* 表示全部）
SIGNAL_HOME_CHANNEL=+1234567890                  # 定时任务的默认投递目标
```
然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机自启系统服务
```

---

## 访问控制 {#access-control}

### 私信访问 {#dm-access}

私信访问的规则与其他所有 Hermes 平台一致：

1. **设置了 `SIGNAL_ALLOWED_USERS`** → 只有这些用户可以发消息
2. **未设置白名单** → 未知用户会收到一个私信配对码（通过 `hermes pairing approve signal CODE` 批准）
3. **`SIGNAL_ALLOW_ALL_USERS=true`** → 任何人都可以发消息（请谨慎使用）

### 群组访问 {#group-access}

群组访问由环境变量 `SIGNAL_GROUP_ALLOWED_USERS` 控制：

| 配置 | 行为 |
|------|------|
| 未设置（默认） | 忽略所有群组消息。机器人只响应私信。 |
| 设置为群组 ID | 仅监控列出的群组（例如 `groupId1,groupId2`）。 |
| 设置为 `*` | 机器人响应其所在的所有群组。 |

---

## 功能特性 {#features}

### 附件 {#attachments}

该适配器支持双向发送和接收媒体。

**接收**（用户 → Agent）：

- **图片** — PNG、JPEG、GIF、WebP（通过魔数自动检测）
- **音频** — MP3、OGG、WAV、M4A（如果配置了 Whisper，语音消息会被转写）
- **文档** — PDF、ZIP 及其他文件类型

**发送**（Agent → 用户）：

Agent 可以通过响应中的 `MEDIA:` 标签发送媒体文件。支持以下发送方式：

- **图片** — `send_multiple_images` 和 `send_image_file` 以原生 Signal 附件形式发送 PNG、JPEG、GIF、WebP
- **语音** — `send_voice` 以附件形式发送音频文件（OGG、MP3、WAV、M4A、AAC）
- **视频** — `send_video` 发送 MP4 视频文件
- **文档** — `send_document` 发送任意文件类型（PDF、ZIP 等）

所有外发媒体都通过 Signal 的标准附件 API 发送。与某些平台不同，Signal 在协议层面不区分语音消息和文件附件。

附件大小限制：**100 MB**（双向）。
:::warning
**Signal 服务器会对附件上传进行限速**，适配器使用调度器处理多图片发送，将图片按 32 张一组分批，并限制上传速度以匹配 Signal 服务器策略。
:::

### 原生格式、回复引用和表情反应 {#native-formatting-reply-quotes-and-reactions}

Signal 消息会以**原生格式**渲染，而不是显示字面的 Markdown 字符。适配器将 Markdown（`**粗体**`、`*斜体*`、`` `代码` ``、`~~删除线~~`、`||剧透||`、标题）转换为 Signal 的 `bodyRanges`，因此文本在接收方客户端上会以真实样式显示，而不是可见的 `**` / `` ` `` 字符。

**回复引用。** 当 Hermes 回复特定消息时，现在会发布一条原生回复，引用原始消息——与 Signal 用户自己使用“回复”功能时看到的 UI 效果相同。对于响应入站消息生成的回复，这是自动完成的。

**表情反应。** Agent 可以通过标准反应 API 对消息做出反应；反应在 Signal 中会以被引用消息上的表情反应形式呈现，而不是作为额外文本。
这些都不需要额外配置——在最近的 signal-cli 版本中，这些功能默认已内置。如果你的 `signal-cli` 版本过旧，Hermes 会回退到明文投递并记录一次一次性警告。

### 输入指示器 {#typing-indicators}

机器人在处理消息时会发送输入指示器，每 8 秒刷新一次。

### 手机号脱敏 {#phone-number-redaction}

所有手机号在日志中会自动脱敏：
- `+15551234567` → `+155****4567`
- 这同时适用于 Hermes 网关日志和全局脱敏系统

### 给自己发消息（单号码设置） {#note-to-self-single-number-setup}

如果你将 signal-cli 作为**链接的辅助设备**运行在自己的手机号上（而不是使用单独的机器人号码），你可以通过 Signal 的“给自己发消息”功能与 Hermes 交互。

只需从你的手机给自己发送一条消息——signal-cli 会捕获它，Hermes 会在同一对话中回复。

**工作原理：**
- “给自己发消息”的消息以 `syncMessage.sentMessage` 信封形式到达
- 适配器会检测这些消息是否发往机器人自己的账户，并将其作为常规入站消息处理
- 回声防护（发送时间戳追踪）可防止无限循环——机器人自己的回复会被自动过滤掉

**无需额外配置。** 只要 `SIGNAL_ACCOUNT` 与你的手机号匹配，此功能就会自动生效。

### 健康监控 {#health-monitoring}

适配器会监控 SSE 连接，并在以下情况下自动重连：
- 连接断开（采用指数退避：2 秒 → 60 秒）
- 120 秒内未检测到任何活动（向 signal-cli 发送 ping 以验证）

---

## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|------|----------|
| **设置时出现“无法访问 signal-cli”** | 确保 signal-cli 守护进程正在运行：`signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080` |
| **收不到消息** | 检查 `SIGNAL_ALLOWED_USERS` 是否包含发送者的号码（E.164 格式，带 `+` 前缀） |
| **“PATH 中未找到 signal-cli”** | 安装 signal-cli 并确保它在 PATH 中，或使用 Docker |
| **连接持续断开** | 检查 signal-cli 日志中的错误。确保已安装 Java 17+。 |
| **群组消息被忽略** | 使用特定群组 ID 配置 `SIGNAL_GROUP_ALLOWED_USERS`，或使用 `*` 允许所有群组。 |
| **机器人不回复任何人** | 配置 `SIGNAL_ALLOWED_USERS`，使用私信配对，或通过网关策略显式允许所有用户（如果你希望更广泛的访问权限）。 |
| **重复消息** | 确保只有一个 signal-cli 实例在监听你的手机号 |

---

## 安全 {#security}

:::warning
**始终配置访问控制。** 机器人默认拥有终端访问权限。如果没有 `SIGNAL_ALLOWED_USERS` 或私信配对，网关会拒绝所有传入消息作为安全措施。
:::

- 所有日志输出中的手机号都会被脱敏
- 使用私信配对或显式允许列表来安全地添加新用户
- 除非你特别需要群组支持，否则保持群组禁用，或者只允许你信任的群组
- Signal 的端到端加密保护传输中的消息内容
- `~/.local/share/signal-cli/` 中的 signal-cli 会话数据包含账户凭据——请像保护密码一样保护它
---

## 环境变量参考 {#environment-variables-reference}

| 变量 | 是否必需 | 默认值 | 说明 |
|----------|----------|---------|-------------|
| `SIGNAL_HTTP_URL` | 是 | — | signal-cli HTTP 端点 |
| `SIGNAL_ACCOUNT` | 是 | — | 机器人电话号码（E.164 格式） |
| `SIGNAL_ALLOWED_USERS` | 否 | — | 以逗号分隔的电话号码/UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 否 | — | 要监控的群组 ID，或使用 `*` 监控所有群组（省略则禁用群组功能） |
| `SIGNAL_ALLOW_ALL_USERS` | 否 | `false` | 允许任何用户交互（跳过白名单） |
| `SIGNAL_HOME_CHANNEL` | 否 | — | 定时任务的默认投递目标 |
