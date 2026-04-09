---
sidebar_position: 7
title: "Gateway Internals"
description: "消息网关如何启动、授权用户、路由会话以及投递消息"
---

# Gateway Internals

消息网关是一个长驻进程，通过统一的架构将 Hermes 连接到 14 个以上的外部消息平台。

## 关键文件

| 文件 | 用途 |
|------|---------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息分发（约 7,500 行） |
| `gateway/session.py` | `SessionStore` — 对话持久化和会话键构建 |
| `gateway/delivery.py` | 向目标平台/频道投递出站消息 |
| `gateway/pairing.py` | 用于用户授权的私信（DM）配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为人类可读的名称，用于定时任务投递 |
| `gateway/hooks.py` | Hook 的发现、加载和生命周期事件分发 |
| `gateway/mirror.py` | 用于 `send_message` 的跨会话消息镜像 |
| `gateway/status.py` | 针对配置了 Profile 的网关实例进行令牌锁管理 |
| `gateway/builtin_hooks/` | 始终注册的 Hook（例如 BOOT.md 系统提示词 Hook） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

## 架构概览

```text
┌─────────────────────────────────────────────────┐
│                 GatewayRunner                     │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram  │  │ Discord  │  │  Slack   │  ...  │
│  │ Adapter   │  │ Adapter  │  │ Adapter  │       │
│  └─────┬─────┘  └─────┬────┘  └─────┬────┘       │
│        │              │              │             │
│        └──────────────┼──────────────┘             │
│                       ▼                            │
│              _handle_message()                     │
│                       │                            │
│          ┌────────────┼────────────┐               │
│          ▼            ▼            ▼               │
│   Slash command   AIAgent      Queue/BG            │
│    dispatch       creation     sessions            │
│                       │                            │
│                       ▼                            │
│              SessionStore                          │
│           (SQLite persistence)                     │
└─────────────────────────────────────────────────┘
```

## 消息流

当来自任何平台的消息到达时：

1. **平台适配器**接收原始事件，并将其标准化为 `MessageEvent`。
2. **基础适配器**检查活跃会话防护（guard）：
   - 如果该会话已有 Agent 正在运行 → 将消息入队，并设置中断事件。
   - 如果是 `/approve`、`/deny`、`/stop` → 跳过防护（直接内联分发）。
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）。
   - 检查授权（见下文“授权”部分）。
   - 检查是否为斜杠命令 → 分发给命令处理器。
   - 检查 Agent 是否已在运行 → 拦截如 `/stop`、`/status` 等命令。
   - 否则 → 创建 `AIAgent` 实例并运行对话。
4. **响应**通过平台适配器发送回原平台。

### 会话键格式

会话键编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 `chat_id` 部分包含线程 ID。**切勿手动构建会话键** — 请始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息防护

当 Agent 正在运行时，传入的消息会经过两个连续的防护层：

1. **第一级 — 基础适配器** (`gateway/platforms/base.py`)：检查 `_active_sessions`。如果会话处于活跃状态，则将消息放入 `_pending_messages` 队列并设置中断事件。这会在消息到达网关运行器之前将其拦截。

2. **第二级 — 网关运行器** (`gateway/run.py`)：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并进行相应路由。其他所有消息都会触发 `running_agent.interrupt()`。

当 Agent 被阻塞时，必须到达运行器的命令（如 `/approve`）会通过 `await self._message_handler(event)` **内联**分发 — 它们会绕过后台任务系统，以避免竞态条件。

## 授权

网关使用多层授权检查，按顺序评估：

1. **平台级全员允许标志**（例如 `TELEGRAM_ALLOW_ALL_USERS`）— 如果设置，该平台上的所有用户均获授权。
2. **平台白名单**（例如 `TELEGRAM_ALLOWED_USERS`）— 以逗号分隔的用户 ID。
3. **私信（DM）配对** — 已认证用户可以通过配对码配对新用户。
4. **全局全员允许** (`GATEWAY_ALLOW_ALL_USERS`) — 如果设置，所有平台上的所有用户均获授权。
5. **默认：拒绝** — 未经授权的用户将被拒绝。

### 私信（DM）配对流程

```text
Admin: /pair
Gateway: "Pairing code: ABC123. Share with the user."
New user: ABC123
Gateway: "Paired! You're now authorized."
```

配对状态持久化在 `gateway/pairing.py` 中，重启后依然有效。

## 斜杠命令分发

网关中的所有斜杠命令都流经相同的解析管道：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射为规范名称（处理别名、前缀匹配）。
2. 将规范名称与 `GATEWAY_KNOWN_COMMANDS` 进行比对。
3. `_handle_message()` 中的处理器根据规范名称进行分发。
4. 部分命令受配置限制（`CommandDef` 上的 `gateway_config_gate`）。

### 运行中 Agent 防护

在 Agent 处理期间不得执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent is running — wait for it to finish or /stop first."
```

旁路命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理逻辑。

## 配置来源

网关从多个来源读取配置：

| 来源 | 提供内容 |
|--------|-----------------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭据 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖上述任何配置 |

与 CLI（使用带有硬编码默认值的 `load_cli_config()`）不同，网关直接通过 YAML 加载器读取 `config.yaml`。这意味着存在于 CLI 默认字典中但不在用户配置文件中的配置键，在 CLI 和网关之间的表现可能不同。

## 平台适配器

每个消息平台在 `gateway/platforms/` 中都有一个适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — 所有平台的共享逻辑
├── telegram.py          # Telegram Bot API (长轮询或 Webhook)
├── discord.py           # Discord 机器人 (通过 discord.py)
├── slack.py             # Slack Socket Mode
├── whatsapp.py          # WhatsApp Business Cloud API
├── signal.py            # Signal (通过 signal-cli REST API)
├── matrix.py            # Matrix (通过 matrix-nio，可选 E2EE)
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # 电子邮件 (通过 IMAP/SMTP)
├── sms.py               # 短信 (通过 Twilio)
├── dingtalk.py          # 钉钉 WebSocket
├── feishu.py            # 飞书/Lark WebSocket 或 Webhook
├── wecom.py             # 企业微信回调
├── bluebubbles.py       # Apple iMessage (通过 BlueBubbles macOS 服务器)
├── webhook.py           # 入站/出站 Webhook 适配器
├── api_server.py        # REST API 服务器适配器
└── homeassistant.py     # Home Assistant 对话集成
```

适配器实现了一个通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息投递
- `on_message()` — 入站消息标准化 → `MessageEvent`

### 令牌锁

使用唯一凭据连接的适配器会在 `connect()` 中调用 `acquire_scoped_lock()`，并在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个 Profile 同时使用同一个机器人令牌。
## 投递路径

外发投递（`gateway/delivery.py`）处理以下内容：

- **直接回复** — 将响应发送回原始聊天窗口
- **主频道投递** — 将定时任务输出和后台结果路由到配置的主频道
- **显式目标投递** — 使用 `send_message` 工具指定目标，例如 `telegram:-1001234567890`
- **跨平台投递** — 投递到与原始消息不同的平台

定时任务的投递不会被镜像到网关会话历史记录中，它们仅存在于各自的定时任务会话中。这是一个刻意的设计选择，旨在避免消息交替冲突。

## 钩子（Hooks）

网关钩子是响应生命周期事件的 Python 模块：

### 网关钩子事件

| 事件 | 触发时机 |
|-------|-----------|
| `gateway:startup` | 网关进程启动时 |
| `session:start` | 新的对话会话开始时 |
| `session:end` | 会话结束或超时时 |
| `session:reset` | 用户通过 `/new` 重置会话时 |
| `agent:start` | Agent 开始处理消息时 |
| `agent:step` | Agent 完成一次工具调用迭代时 |
| `agent:end` | Agent 完成任务并返回响应时 |
| `command:*` | 执行任何斜杠命令时 |

钩子从 `gateway/builtin_hooks/`（始终处于活动状态）和 `~/.hermes/hooks/`（用户安装）中发现。每个钩子都是一个包含 `HOOK.yaml` 清单文件和 `handler.py` 的目录。

## 内存提供程序集成

当启用内存提供程序插件（例如 Honcho）时：

1. 网关会为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化提供程序
3. 提供程序工具（例如 `honcho_profile`、`viking_search`）通过以下路径路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 在会话结束/重置时，触发 `on_session_end()` 进行清理和最终数据刷新

### 内存刷新生命周期

当会话被重置、恢复或过期时：
1. 内置内存被刷新到磁盘
2. 触发内存提供程序的 `on_session_end()` 钩子
3. 一个临时的 `AIAgent` 运行仅限内存的对话轮次
4. 上下文随后被丢弃或归档

## 后台维护

网关在处理消息的同时运行周期性维护任务：

- **定时任务触发** — 检查作业计划并触发到期的作业
- **会话过期** — 在超时后清理废弃的会话
- **内存刷新** — 在会话过期前主动刷新内存
- **缓存刷新** — 刷新模型列表和提供程序状态

## 进程管理

网关作为一个长驻进程运行，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl` (Linux) 或 `launchctl` (macOS) — 服务管理
- `~/.hermes/gateway.pid` 处的 PID 文件 — 配置文件作用域的进程跟踪

**配置文件作用域与全局**：`start_gateway()` 使用配置文件作用域的 PID 文件。`hermes gateway stop` 仅停止当前配置文件的网关。`hermes gateway stop --all` 使用全局 `ps aux` 扫描来终止所有网关进程（在更新期间使用）。

## 相关文档

- [会话存储](./session-storage.md)
- [定时任务内部原理](./cron-internals.md)
- [ACP 内部原理](./acp-internals.md)
- [Agent 循环内部原理](./agent-loop.md)
- [消息网关（用户指南）](/user-guide/messaging)
