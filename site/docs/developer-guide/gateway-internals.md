---
sidebar_position: 7
title: "Gateway 内部原理"
description: "消息 Gateway 如何启动、授权用户、路由会话以及投递消息"
---

# Gateway 内部原理

消息 Gateway 是一个持久运行的进程，它通过统一的架构将 Hermes 连接到 14 个以上的外部消息平台。

## 关键文件

| 文件 | 用途 |
|------|---------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令（slash commands）、消息分发（约 7,500 行） |
| `gateway/session.py` | `SessionStore` — 对话持久化和会话键（session key）构建 |
| `gateway/delivery.py` | 向目标平台/频道投递出站消息 |
| `gateway/pairing.py` | 用于用户授权的私聊配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为易读名称，用于定时任务（cron）投递 |
| `gateway/hooks.py` | Hook 的发现、加载和生命周期事件分发 |
| `gateway/mirror.py` | 用于 `send_message` 的跨会话消息镜像 |
| `gateway/status.py` | 针对 Profile 作用域的 Gateway 实例进行 Token 锁管理 |
| `gateway/builtin_hooks/` | 始终注册的 Hook（例如 BOOT.md 系统提示词 Hook） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

## 架构概览

```text
┌─────────────────────────────────────────────────┐
│                 GatewayRunner                     │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram  │  │ Discord  │  │  Slack   │  ...  │
│  │ 适配器     │  │ 适配器     │  │ 适配器     │       │
│  └─────┬─────┘  └─────┬────┘  └─────┬────┘       │
│        │              │              │             │
│        └──────────────┼──────────────┘             │
│                       ▼                            │
│              _handle_message()                     │
│                       │                            │
│          ┌────────────┼────────────┐               │
│          ▼            ▼            ▼               │
│   斜杠命令分发      AIAgent 创建    队列/后台会话      │
│                       │                            │
│                       ▼                            │
│              SessionStore                          │
│           (SQLite 持久化)                           │
└─────────────────────────────────────────────────┘
```

## 消息流

当消息从任何平台到达时：

1. **平台适配器**接收原始事件，并将其规范化为 `MessageEvent`。
2. **基础适配器（Base adapter）**检查活动会话守卫（session guard）：
   - 如果 Agent 正在为此会话运行 → 将消息加入队列，设置中断事件。
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（内联分发）。
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）。
   - 检查授权（见下文“授权”部分）。
   - 检查是否为斜杠命令 → 分发给命令处理器。
   - 检查 Agent 是否已在运行 → 拦截 `/stop`、`/status` 等命令。
   - 否则 → 创建 `AIAgent` 实例并运行对话。
4. **响应**通过平台适配器发回。

### 会话键格式

会话键编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛话题、Discord 线程、Slack 线程）可能会在 `chat_id` 部分包含线程 ID。**切勿手动构建会话键** —— 请始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息守卫

当 Agent 处于活动运行状态时，输入的消息会依次通过两个守卫：

1. **第一级 — 基础适配器** (`gateway/platforms/base.py`)：检查 `_active_sessions`。如果会话处于活动状态，则将消息排入 `_pending_messages` 队列并设置中断事件。这会在消息到达 Gateway Runner *之前* 拦截它们。

2. **第二级 — Gateway Runner** (`gateway/run.py`)：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并进行相应路由。其他所有内容都会触发 `running_agent.interrupt()`。

在 Agent 被阻塞时必须到达 Runner 的命令（如 `/approve`）会通过 `await self._message_handler(event)` **内联**分发 —— 它们绕过后台任务系统以避免竞态条件。

## 授权

Gateway 使用多层授权检查，按顺序评估：

1. **每平台全允许标志**（例如 `TELEGRAM_ALLOW_ALL_USERS`） — 如果设置，该平台上的所有用户均获得授权。
2. **平台允许列表**（例如 `TELEGRAM_ALLOWED_USERS`） — 逗号分隔的用户 ID。
3. **私聊配对（DM pairing）** — 已认证的用户可以通过配对码配对新用户。
4. **全局全允许** (`GATEWAY_ALLOW_ALL_USERS`) — 如果设置，所有平台上的所有用户均获得授权。
5. **默认：拒绝** — 未经授权的用户将被拒绝。

### 私聊配对流程

```text
管理员: /pair
Gateway: "配对码: ABC123。请分享给用户。"
新用户: ABC123
Gateway: "配对成功！你现在已获得授权。"
```

配对状态持久化在 `gateway/pairing.py` 中，重启后依然有效。

## 斜杠命令分发

Gateway 中的所有斜杠命令都通过相同的解析流水线：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射到规范名称（处理别名、前缀匹配）。
2. 根据 `GATEWAY_KNOWN_COMMANDS` 检查规范名称。
3. `_handle_message()` 中的处理器根据规范名称进行分发。
4. 某些命令受配置限制（`CommandDef` 上的 `gateway_config_gate`）。

### 运行中 Agent 守卫

在 Agent 处理过程中绝对不能执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent 正在运行 — 请等待其完成或先执行 /stop。"
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理逻辑。

## 配置源

Gateway 从多个来源读取配置：

| 来源 | 提供内容 |
|--------|-----------------|
| `~/.hermes/.env` | API 密钥、Bot Token、平台凭据 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖上述任何项 |

与 CLI（使用带有硬编码默认值的 `load_cli_config()`）不同，Gateway 直接通过 YAML 加载器读取 `config.yaml`。这意味着存在于 CLI 默认字典中但不在用户配置文件中的配置键，在 CLI 和 Gateway 之间的行为可能会有所不同。

## 平台适配器

每个消息平台在 `gateway/platforms/` 中都有一个适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — 所有平台的共享逻辑
├── telegram.py          # Telegram Bot API (长轮询或 Webhook)
├── discord.py           # 通过 discord.py 实现的 Discord Bot
├── slack.py             # Slack Socket 模式
├── whatsapp.py          # WhatsApp 商业云 API
├── signal.py            # 通过 signal-cli REST API 实现的 Signal
├── matrix.py            # 通过 matrix-nio 实现的 Matrix (可选 E2EE)
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # 通过 IMAP/SMTP 实现的电子邮件
├── sms.py               # 通过 Twilio 实现的短信
├── dingtalk.py          # 钉钉 WebSocket
├── feishu.py            # 飞书 WebSocket 或 Webhook
├── wecom.py             # 企业微信回调
├── webhook.py           # 入站/出站 Webhook 适配器
├── api_server.py        # REST API 服务器适配器
└── homeassistant.py     # Home Assistant 对话集成
```

适配器实现通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息投递
- `on_message()` — 入站消息规范化 → `MessageEvent`

### Token 锁

使用唯一凭据连接的适配器会在 `connect()` 中调用 `acquire_scoped_lock()`，并在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个 Profile 同时使用同一个 Bot Token。

## 投递路径

出站投递 (`gateway/delivery.py`) 处理：
- **直接回复** — 将响应发送回原始聊天
- **主频道投递 (Home channel delivery)** — 将 cron 任务输出和后台结果路由到配置的主频道
- **显式目标投递** — `send_message` 工具指定 `telegram:-1001234567890`
- **跨平台投递** — 投递到与原始消息不同的平台

Cron 任务的投递内容**不会**镜像到 Gateway 会话历史中 —— 它们仅存在于各自的 cron 会话中。这是一个刻意的设计选择，旨在避免消息交替冲突。

## Hooks

Gateway hooks 是响应生命周期事件的 Python 模块：

### Gateway Hook 事件

| 事件 | 触发时机 |
|-------|-----------|
| `gateway:startup` | Gateway 进程启动 |
| `session:start` | 新的对话会话开始 |
| `session:end` | 会话完成或超时 |
| `session:reset` | 用户使用 `/new` 重置会话 |
| `agent:start` | Agent 开始处理消息 |
| `agent:step` | Agent 完成一次工具调用迭代 |
| `agent:end` | Agent 完成并返回响应 |
| `command:*` | 执行任何斜杠命令 |

Hooks 从 `gateway/builtin_hooks/`（始终激活）和 `~/.hermes/hooks/`（用户安装）中发现。每个 hook 都是一个包含 `HOOK.yaml` 清单文件和 `handler.py` 的目录。

## 记忆提供者 (Memory Provider) 集成

当启用记忆提供者插件（例如 Honcho）时：

1. Gateway 为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化提供者
3. 提供者工具（例如 `honcho_profile`、`viking_search`）通过以下路径路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 在会话结束/重置时，触发 `on_session_end()` 进行清理和最终数据刷新（flush）

### 记忆刷新生命周期

当会话被重置、恢复或过期时：
1. 内置记忆被刷新到磁盘
2. 记忆提供者的 `on_session_end()` hook 触发
3. 一个临时的 `AIAgent` 运行一次仅限记忆的对话轮次
4. 随后上下文被丢弃或归档

## 后台维护

Gateway 在处理消息的同时运行定期维护任务：

- **Cron 滴答 (Cron ticking)** — 检查任务计划并触发到期的任务
- **会话过期** — 在超时后清理被放弃的会话
- **记忆刷新** — 在会话过期前主动刷新记忆
- **缓存刷新** — 刷新模型列表和提供者状态

## 进程管理

Gateway 作为一个长期运行的进程，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl` (Linux) 或 `launchctl` (macOS) — 服务管理
- PID 文件位于 `~/.hermes/gateway.pid` — Profile 作用域的进程跟踪

**Profile 作用域 vs 全局**：`start_gateway()` 使用 Profile 作用域的 PID 文件。`hermes gateway stop` 仅停止当前 Profile 的 Gateway。`hermes gateway stop --all` 使用全局 `ps aux` 扫描来杀死所有 Gateway 进程（在更新期间使用）。

## 相关文档

- [会话存储 (Session Storage)](./session-storage.md)
- [Cron 内部原理](./cron-internals.md)
- [ACP 内部原理](./acp-internals.md)
- [Agent Loop 内部原理](./agent-loop.md)
- [消息 Gateway (用户指南)](/user-guide/messaging)
