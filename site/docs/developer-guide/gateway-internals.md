---
sidebar_position: 7
title: "网关内部机制"
description: "消息网关如何启动、授权用户、路由会话以及投递消息"
---

# 网关内部机制 {#gateway-internals}

消息网关是一个长期运行的进程，它通过统一的架构将 Hermes 连接到 14 个以上的外部消息平台。

## 关键文件 {#key-files}

| 文件 | 用途 |
|------|------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息分发（约 12,000 行） |
| `gateway/session.py` | `SessionStore` — 会话持久化与会话键构建 |
| `gateway/delivery.py` | 向目标平台/频道发送出站消息 |
| `gateway/pairing.py` | 用于用户授权的 DM 配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为人类可读的名称，用于定时投递 |
| `gateway/hooks.py` | 钩子发现、加载以及生命周期事件分发 |
| `gateway/mirror.py` | 跨会话消息镜像，用于 `send_message` |
| `gateway/status.py` | 针对配置文件作用域的网关实例的令牌锁管理 |
| `gateway/builtin_hooks/` | 始终注册的钩子的扩展点（未提供任何钩子） |
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
└───────┴─────────────┴─────────────┴─────────────┘
```

## 消息流程 {#message-flow}

当消息从任意平台到达时：

1. **平台适配器** 接收原始事件，将其标准化为 `MessageEvent`
2. **基础适配器** 检查活跃会话守卫：
   - 如果 Agent 正在为该会话运行 → 将消息加入队列，设置中断事件
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（内联分发）
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）
   - 检查授权（见下文“授权”部分）
   - 检查是否为斜杠命令 → 分发给命令处理器
   - 检查 Agent 是否已在运行 → 拦截 `/stop`、`/status` 等命令
   - 否则 → 创建 `AIAgent` 实例并运行对话
4. **响应** 通过平台适配器发送回去
### 会话密钥格式 {#session-key-format}

会话密钥编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 chat_id 部分包含线程 ID。**切勿手动构造会话密钥**——始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息防护 {#two-level-message-guard}

当 Agent 正在运行时，传入的消息会经过两个顺序防护：

1. **第 1 级 — 基础适配器**（`gateway/platforms/base.py`）：检查 `_active_sessions`。如果会话处于活动状态，则将消息排入 `_pending_messages` 并设置中断事件。这会在消息*到达*网关运行器之前捕获它们。

2. **第 2 级 — 网关运行器**（`gateway/run.py`）：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并适当路由它们。其他所有内容都会触发 `running_agent.interrupt()`。

在 Agent 被阻塞时必须到达运行器的命令（如 `/approve`）会通过 `await self._message_handler(event)` **内联**分发——它们绕过后台任务系统以避免竞态条件。

## 授权 {#authorization}

网关使用多层授权检查，按顺序评估：

1. **按平台允许所有标志**（例如 `TELEGRAM_ALLOW_ALL_USERS`）——如果设置，该平台上的所有用户都被授权
2. **平台允许列表**（例如 `TELEGRAM_ALLOWED_USERS`）——逗号分隔的用户 ID
3. **DM 配对**——已认证用户可以通过配对码配对新用户
4. **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS`）——如果设置，所有平台上的所有用户都被授权
5. **默认：拒绝**——未授权用户被拒绝

### DM 配对流程 {#dm-pairing-flow}

```text
管理员：/pair
网关："配对码：ABC123。分享给用户。"
新用户：ABC123
网关："已配对！您现在已获得授权。"
```

配对状态持久化存储在 `gateway/pairing.py` 中，重启后仍然保留。

## 斜杠命令分发 {#slash-command-dispatch}

网关中的所有斜杠命令都通过相同的解析管道：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射到规范名称（处理别名、前缀匹配）
2. 规范名称会与 `GATEWAY_KNOWN_COMMANDS` 进行核对
3. `_handle_message()` 中的处理程序根据规范名称进行分发
4. 某些命令受配置限制（`CommandDef` 上的 `gateway_config_gate`）

### 运行中 Agent 防护 {#running-agent-guard}

在 Agent 处理期间不得执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent 正在运行——请等待它完成或先执行 /stop。"
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理。

## 配置来源 {#config-sources}

网关从多个来源读取配置：

| 来源 | 提供内容 |
|--------|-----------------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭据 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖上述任何配置 |
与 CLI（使用带有硬编码默认值的 `load_cli_config()`）不同，网关直接通过 YAML 加载器读取 `config.yaml`。这意味着，CLI 默认字典中存在但用户配置文件中没有的配置键，在 CLI 和网关之间的行为可能不同。

## 平台适配器 {#platform-adapters}

每个消息平台在 `gateway/platforms/` 中都有一个适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — shared logic for all platforms
├── telegram.py          # Telegram Bot API (long polling or webhook)
├── discord.py           # Discord bot via discord.py
├── slack.py             # Slack Socket Mode
├── whatsapp.py          # WhatsApp Business Cloud API
├── signal.py            # Signal via signal-cli REST API
├── matrix.py            # Matrix via mautrix (optional E2EE)
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # Email via IMAP/SMTP
├── sms.py               # SMS via Twilio
├── dingtalk.py          # DingTalk WebSocket
├── feishu.py            # Feishu/Lark WebSocket or webhook
├── wecom.py             # WeCom (WeChat Work) callback
├── weixin.py            # Weixin (personal WeChat) via iLink Bot API
├── bluebubbles.py       # Apple iMessage via BlueBubbles macOS server
├── qqbot.py             # QQ Bot (Tencent QQ) via Official API v2
├── webhook.py           # Inbound/outbound webhook adapter
├── api_server.py        # REST API server adapter
└── homeassistant.py     # Home Assistant conversation integration
```

适配器实现了一个通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息投递
- `on_message()` — 入站消息标准化 → `MessageEvent`

### Token 锁 {#token-locks}

使用唯一凭据连接的适配器会在 `connect()` 中调用 `acquire_scoped_lock()`，在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件同时使用同一个机器人 token。

## 投递路径 {#delivery-path}

出站投递（`gateway/delivery.py`）处理：

- **直接回复** — 将响应发送回原始聊天
- **主频道投递** — 将定时任务输出和后台结果路由到配置的主频道
- **显式目标投递** — `send_message` 工具指定 `telegram:-1001234567890`
- **跨平台投递** — 投递到与原始消息不同的平台

定时任务投递不会镜像到网关会话历史中——它们仅存在于自己的定时任务会话中。这是为了避免消息交替违规而有意为之的设计选择。

## 钩子 {#hooks}

网关钩子是响应生命周期事件的 Python 模块：

### 网关钩子事件 {#gateway-hook-events}

| 事件 | 触发时机 |
|-------|-----------|
| `gateway:startup` | 网关进程启动时 |
| `session:start` | 新的对话会话开始时 |
| `session:end` | 会话完成或超时时 |
| `session:reset` | 用户通过 `/new` 重置会话时 |
| `agent:start` | Agent 开始处理消息时 |
| `agent:step` | Agent 完成一次工具调用迭代时 |
| `agent:end` | Agent 完成并返回响应时 |
| `command:*` | 任何斜杠命令被执行时 |
钩子从 `gateway/builtin_hooks/`（始终激活）和 `~/.hermes/hooks/`（用户安装）中发现。每个钩子是一个包含 `HOOK.yaml` 清单和 `handler.py` 的目录。

## 内存提供者集成 {#memory-provider-integration}

当启用了内存提供者插件（如 Honcho）时：

1. Gateway 会为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化提供者
3. 提供者工具（如 `honcho_profile`、`viking_search`）通过以下路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 当会话结束/重置时，触发 `on_session_end()` 进行清理和最终数据刷新

### 内存刷新生命周期 {#memory-flush-lifecycle}

当会话被重置、恢复或过期时：
1. 内置内存被刷新到磁盘
2. 内存提供者的 `on_session_end()` 钩子触发
3. 一个临时的 `AIAgent` 运行一次仅内存的对话回合
4. 然后上下文被丢弃或归档

## 后台维护 {#background-maintenance}

Gateway 在进行消息处理的同时运行定期维护：

- **定时任务跳动** — 检查作业调度并触发到期的作业
- **会话过期** — 在超时后清理废弃的会话
- **内存刷新** — 在会话过期前主动刷新内存
- **缓存刷新** — 刷新模型列表和提供者状态

## 进程管理 {#process-management}

Gateway 作为一个长期运行的进程运行，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl` (Linux) 或 `launchctl` (macOS) — 服务管理
- `~/.hermes/gateway.pid` 处的 PID 文件 — 按配置域（profile）的进程追踪

**按配置域 vs 全局**：`start_gateway()` 使用按配置域的 PID 文件。`hermes gateway stop` 仅停止当前配置域的 gateway。`hermes gateway stop --all` 使用全局的 `ps aux` 扫描来杀死所有 gateway 进程（在更新期间使用）。

## 相关文档 {#related-docs}

- [会话存储](./session-storage.md)
- [Cron 内部机制](./cron-internals.md)
- [ACP 内部机制](./acp-internals.md)
- [Agent 循环内部机制](./agent-loop.md)
- [Messaging Gateway（用户指南）](/user-guide/messaging)
