---
sidebar_position: 7
title: "Gateway 内部机制"
description: "消息网关如何启动、授权用户、路由会话以及投递消息"
---

# Gateway 内部机制 {#gateway-internals}

消息网关是一个长期运行的进程，它通过统一的架构将 Hermes 连接到 14 个以上的外部消息平台。

## 关键文件 {#key-files}

| 文件 | 用途 |
|------|---------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息分发（约 9,000 行） |
| `gateway/session.py` | `SessionStore` — 对话持久化和会话键构造 |
| `gateway/delivery.py` | 向目标平台/频道投递出站消息 |
| `gateway/pairing.py` | 用户授权的 DM 配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为可读名称，用于定时任务投递 |
| `gateway/hooks.py` | Hook 发现、加载和生命周期事件分发 |
| `gateway/mirror.py` | `send_message` 的跨会话消息镜像 |
| `gateway/status.py` | 面向 profile 的 Gateway 实例的令牌锁管理 |
| `gateway/builtin_hooks/` | 始终注册的 Hook（例如 BOOT.md 系统提示 Hook） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

## 架构概览 {#architecture-overview}

```text
┌─────────────────────────────────────────────────┐
│                  GatewayRunner                  │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram │  │ Discord  │  │  Slack   │       │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │
│       └─────────────┼─────────────┘             │
│                     ▼                           │
│              _handle_message()                  │
│                     │                           │
│         ┌───────────┼───────────┐               │
│         ▼           ▼           ▼               │
│  Slash command   AIAgent    Queue/BG            │
│    dispatch      creation   sessions            │
│                     │                           │
│                     ▼                           │
│                 SessionStore                    │
│              (SQLite persistence)               │
└─────────────────────────────────────────────────┘
```

## 消息流转 {#message-flow}

当消息从任意平台到达时：

1. **平台适配器**接收原始事件，将其规范化为 `MessageEvent`
2. **基础适配器**检查活跃会话守卫：
   - 如果该会话已有 Agent 在运行 → 将消息入队，设置中断事件
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（直接内联分发）
3. **GatewayRunner._handle_message()** 接收该事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）
   - 检查授权（见下文"授权"部分）
   - 检查是否为斜杠命令 → 分发给命令处理器
   - 检查是否已有 Agent 在运行 → 拦截 `/stop`、`/status` 等命令
   - 否则 → 创建 `AIAgent` 实例并运行对话
4. **响应**通过平台适配器发回

### 会话键格式 {#session-key-format}

会话键编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持话题的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 chat_id 部分包含话题 ID。**永远不要手动构造会话键** —— 始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息守卫 {#two-level-message-guard}

当 Agent 正在活跃运行时，传入的消息会依次通过两级守卫：

1. **第一级 —— 基础适配器**（`gateway/platforms/base.py`）：检查 `_active_sessions`。如果会话处于活跃状态，将消息放入 `_pending_messages` 队列并设置中断事件。这在消息到达 GatewayRunner 之前就将其拦截。

2. **第二级 —— GatewayRunner**（`gateway/run.py`）：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并将其路由到相应位置。其他所有内容都会触发 `running_agent.interrupt()`。
需要在 Agent 被阻塞时也能送达 runner 的命令（如 `/approve`）会通过 `await self._message_handler(event)` **内联**派发——它们绕过后台任务系统，以避免竞态条件。

## 授权 {#authorization}

Gateway 采用多层授权检查，按顺序评估：

1. **按平台放行全部**（如 `TELEGRAM_ALLOW_ALL_USERS`）—— 若设置，则该平台所有用户均获授权
2. **平台白名单**（如 `TELEGRAM_ALLOWED_USERS`）—— 逗号分隔的用户 ID
3. **DM 配对** —— 已认证用户可通过配对码配对新用户
4. **全局放行全部**（`GATEWAY_ALLOW_ALL_USERS`）—— 若设置，则所有平台的所有用户均获授权
5. **默认：拒绝** —— 未授权用户将被拒绝

### DM 配对流程 {#dm-pairing-flow}

```text
Admin: /pair
Gateway: "Pairing code: ABC123. Share with the user."
New user: ABC123
Gateway: "Paired! You're now authorized."
```

配对状态持久化存储在 `gateway/pairing.py` 中，重启后仍然保留。

## Slash 命令派发 {#slash-command-dispatch}

Gateway 中的所有 slash 命令都经过同一套解析流水线：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射为规范名称（处理别名、前缀匹配）
2. 规范名称与 `GATEWAY_KNOWN_COMMANDS` 进行比对
3. `_handle_message()` 中的处理器根据规范名称进行派发
4. 部分命令受配置管控（`CommandDef` 上的 `gateway_config_gate`）

### 运行中 Agent 拦截 {#running-agent-guard}

在 Agent 处理期间不得执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent is running — wait for it to finish or /stop first."
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理逻辑。

## 配置来源 {#config-sources}

Gateway 从多个来源读取配置：

| 来源 | 提供的内容 |
|------|-----------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭证 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖上述任意配置 |

与 CLI 不同（CLI 使用 `load_cli_config()` 并带有硬编码默认值），Gateway 直接通过 YAML 加载器读取 `config.yaml`。这意味着存在于 CLI 默认值字典中、但不在用户配置文件中的配置键，在 CLI 和 Gateway 之间的行为可能有所不同。

## 平台适配器 {#platform-adapters}

每个消息平台在 `gateway/platforms/` 中都有对应的适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — 所有平台的共享逻辑
├── telegram.py          # Telegram Bot API（长轮询或 Webhook）
├── discord.py           # 通过 discord.py 接入的 Discord 机器人
├── slack.py             # Slack Socket Mode
├── whatsapp.py          # WhatsApp Business Cloud API
├── signal.py            # 通过 signal-cli REST API 接入的 Signal
├── matrix.py            # 通过 mautrix 接入的 Matrix（可选 E2EE）
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # 通过 IMAP/SMTP 接入的邮件
├── sms.py               # 通过 Twilio 接入的短信
├── dingtalk.py          # 钉钉 WebSocket
├── feishu.py            # 飞书/Lark WebSocket 或 Webhook
├── wecom.py             # 企业微信（WeChat Work）回调
├── weixin.py            # 微信（个人微信）通过 iLink Bot API
├── bluebubbles.py       # 通过 BlueBubbles macOS 服务器接入的 Apple iMessage
├── qqbot.py             # QQ 机器人（腾讯 QQ）通过官方 API v2
├── webhook.py           # 入站/出站 Webhook 适配器
├── api_server.py        # REST API 服务器适配器
└── homeassistant.py     # Home Assistant 对话集成
```

适配器实现通用接口：
- `connect()` / `disconnect()` —— 生命周期管理
- `send_message()` —— 出站消息投递
- `on_message()` —— 入站消息标准化 → `MessageEvent`

### 令牌锁 {#token-locks}

使用唯一凭证连接的适配器会在 `connect()` 中调用 `acquire_scoped_lock()`，在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件同时使用同一个机器人令牌。
## 投递路径 {#delivery-path}

外发投递（`gateway/delivery.py`）负责处理：

- **直接回复** — 将响应发送回原始聊天
- **Home channel 投递** — 将定时任务输出和后台结果路由到配置的 home channel
- **显式目标投递** — `send_message` 工具指定 `telegram:-1001234567890`
- **跨平台投递** — 投递到与原始消息不同的平台

定时任务投递**不会**镜像到 Gateway 会话历史中 — 它们只存在于自己的定时任务会话里。这是有意为之的设计，以避免消息交替违规。

## 钩子 {#hooks}

Gateway 钩子是响应生命周期事件的 Python 模块：

### Gateway 钩子事件 {#gateway-hook-events}

| 事件 | 触发时机 |
|------|---------|
| `gateway:startup` | Gateway 进程启动 |
| `session:start` | 新对话会话开始 |
| `session:end` | 会话完成或超时 |
| `session:reset` | 用户使用 `/new` 重置会话 |
| `agent:start` | Agent 开始处理消息 |
| `agent:step` | Agent 完成一次工具调用迭代 |
| `agent:end` | Agent 完成并返回响应 |
| `command:*` | 执行任何斜杠命令 |

钩子从 `gateway/builtin_hooks/`（始终激活）和 `~/.hermes/hooks/`（用户安装）中自动发现。每个钩子是一个目录，包含 `HOOK.yaml` 清单文件和 `handler.py`。

## 记忆提供方集成 {#memory-provider-integration}

当记忆提供方插件（例如 Honcho）启用时：

1. Gateway 为每条消息创建一个带会话 ID 的 `AIAgent`
2. `MemoryManager` 用会话上下文初始化提供方
3. 提供方工具（例如 `honcho_profile`、`viking_search`）按以下路径路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 会话结束/重置时，`on_session_end()` 触发以进行清理和最终数据刷盘

### 记忆刷盘生命周期 {#memory-flush-lifecycle}

当会话被重置、恢复或过期时：
1. 内置记忆刷盘到磁盘
2. 记忆提供方的 `on_session_end()` 钩子触发
3. 临时 `AIAgent` 运行一次仅记忆的对话轮次
4. 上下文随后被丢弃或归档

## 后台维护 {#background-maintenance}

Gateway 在处理消息的同时运行定期维护：

- **定时任务 tick** — 检查任务调度并触发到期任务
- **会话过期** — 超时后清理废弃会话
- **记忆刷盘** — 在会话过期前主动刷盘记忆
- **缓存刷新** — 刷新模型列表和提供方状态

## 进程管理 {#process-management}

Gateway 作为长期运行的进程，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl`（Linux）或 `launchctl`（macOS）— 服务管理
- PID 文件位于 `~/.hermes/gateway.pid` — 按 Profile 的进程追踪

**Profile 作用域 vs 全局**：`start_gateway()` 使用 Profile 作用域的 PID 文件。`hermes gateway stop` 只停止当前 Profile 的 Gateway。`hermes gateway stop --all` 使用全局 `ps aux` 扫描来终止所有 Gateway 进程（更新时使用）。

## 相关文档 {#related-docs}

- [Session Storage](./session-storage.md)
- [Cron Internals](./cron-internals.md)
- [ACP Internals](./acp-internals.md)
- [Agent Loop Internals](./agent-loop.md)
- [Messaging Gateway（用户指南）](/user-guide/messaging)
