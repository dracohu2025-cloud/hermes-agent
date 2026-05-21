---
sidebar_position: 7
title: "网关内部机制"
description: "消息网关如何启动、授权用户、路由会话以及投递消息"
---

<a id="gateway-internals"></a>
# 网关内部机制

消息网关是一个长期运行的进程，通过统一的架构将 Hermes 连接到 20 多个外部消息平台。

<a id="key-files"></a>
## 关键文件

| 文件 | 用途 |
|------|------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息分发（大文件；查看 git 获取当前行数） |
| `gateway/session.py` | `SessionStore` — 会话持久化与会话键构建 |
| `gateway/delivery.py` | 向目标平台/频道发送出站消息 |
| `gateway/pairing.py` | 用于用户授权的 DM 配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为人类可读的名称，用于定时投递 |
| `gateway/hooks.py` | Hook 发现、加载及生命周期事件分发 |
| `gateway/mirror.py` | 跨会话消息镜像，用于 `send_message` |
| `gateway/status.py` | 针对 profile 作用域的网关实例的令牌锁管理 |
| `gateway/builtin_hooks/` | 始终注册的 Hook 的扩展点（未提供任何内容） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

<a id="architecture-overview"></a>
## 架构概览

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

<a id="message-flow"></a>
## 消息流程

当消息从任意平台到达时：

1. **平台适配器** 接收原始事件，将其标准化为 `MessageEvent`
2. **基础适配器** 检查活跃会话守卫：
   - 如果该会话的 Agent 正在运行 → 将消息加入队列，设置中断事件
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（内联分发）
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话键（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）
   - 检查授权（见下方授权部分）
   - 检查是否为斜杠命令 → 分发给命令处理器
   - 检查 Agent 是否已在运行 → 拦截 `/stop`、`/status` 等命令
   - 否则 → 创建 `AIAgent` 实例并运行对话
4. **响应** 通过平台适配器发送回去
<a id="session-key-format"></a>
### 会话密钥格式

会话密钥编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 `chat_id` 部分包含线程 ID。**切勿手动构造会话密钥** — 请始终使用 `gateway/session.py` 中的 `build_session_key()`。

<a id="two-level-message-guard"></a>
### 两级消息防护

当 Agent 正在运行时，传入的消息会经过两个顺序防护：

1. **第 1 级 — 基础适配器**（`gateway/platforms/base.py`）：检查 `_active_sessions`。如果会话处于活动状态，则将消息排队到 `_pending_messages` 中并设置中断事件。这会在消息*到达* gateway runner 之前捕获它们。

2. **第 2 级 — Gateway runner**（`gateway/run.py`）：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并适当路由。其他所有内容都会触发 `running_agent.interrupt()`。

必须在 Agent 被阻塞时到达 runner 的命令（例如 `/approve`）会通过 `await self._message_handler(event)` **内联**分发 — 它们绕过后台任务系统以避免竞态条件。

<a id="authorization"></a>
## 授权

Gateway 使用多层授权检查，按顺序评估：

1. **每平台允许所有标志**（例如 `TELEGRAM_ALLOW_ALL_USERS`）— 如果设置，则该平台上的所有用户均被授权
2. **平台白名单**（例如 `TELEGRAM_ALLOWED_USERS`）— 以逗号分隔的用户 ID
3. **DM 配对** — 已认证用户可以通过配对码配对新用户
4. **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS`）— 如果设置，则所有平台上的所有用户均被授权
5. **默认：拒绝** — 未授权用户被拒绝

<a id="dm-pairing-flow"></a>
### DM 配对流程

```text
管理员：/pair
Gateway："配对码：ABC123。分享给用户。"
新用户：ABC123
Gateway："配对成功！你现在已获得授权。"
```

配对状态持久化存储在 `gateway/pairing.py` 中，并在重启后保持。

<a id="slash-command-dispatch"></a>
## 斜杠命令分发

Gateway 中的所有斜杠命令都流经相同的解析管道：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射到规范名称（处理别名、前缀匹配）
2. 将规范名称与 `GATEWAY_KNOWN_COMMANDS` 进行比对
3. `_handle_message()` 中的处理程序根据规范名称进行分发
4. 某些命令受配置门控（`CommandDef` 上的 `gateway_config_gate`）

<a id="running-agent-guard"></a>
### 运行中 Agent 防护

在 Agent 正在处理时不得执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent 正在运行 — 请等待它完成或使用 /stop 先停止。"
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理。

<a id="config-sources"></a>
## 配置源

Gateway 从多个来源读取配置：

| 来源 | 提供内容 |
|--------|-----------------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭证 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖以上任何配置 |
与 CLI（使用硬编码默认值的 `load_cli_config()`）不同，gateway 通过 YAML 加载器直接读取 `config.yaml`。这意味着，CLI 默认字典中存在但用户配置文件中没有的配置键，在 CLI 和 gateway 之间可能表现不同。

<a id="platform-adapters"></a>
## 平台适配器

每个消息平台在 `gateway/platforms/` 中都有一个适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — 所有平台的共享逻辑
├── telegram.py          # Telegram Bot API（长轮询或 webhook）
├── discord.py           # 通过 discord.py 实现的 Discord 机器人
├── slack.py             # Slack Socket Mode
├── whatsapp.py          # WhatsApp Business Cloud API
├── signal.py            # 通过 signal-cli REST API 实现的 Signal
├── matrix.py            # 通过 mautrix 实现的 Matrix（可选的 E2EE）
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # 通过 IMAP/SMTP 实现的电子邮件
├── sms.py               # 通过 Twilio 实现的短信
├── dingtalk.py          # 钉钉 WebSocket
├── feishu.py            # 飞书/ Lark WebSocket 或 webhook
├── wecom.py             # 企业微信回调
├── weixin.py            # 通过 iLink Bot API 实现的微信（个人微信）
├── bluebubbles.py       # 通过 BlueBubbles macOS 服务器实现的 Apple iMessage
├── qqbot/               # 通过官方 API v2 实现的 QQ 机器人（子包：adapter.py, crypto.py, keyboards.py, …）
├── yuanbao.py           # 元宝（腾讯）私信/群组适配器
├── feishu_comment.py    # 飞书文档/云盘评论回复处理器
├── msgraph_webhook.py   # Microsoft Graph 变更通知 webhook（Teams, Outlook 等）
├── webhook.py           # 入站/出站 webhook 适配器
├── api_server.py        # REST API 服务器适配器
└── homeassistant.py     # Home Assistant 对话集成
```

适配器实现了一个通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息投递
- `on_message()` — 入站消息标准化 → `MessageEvent`

<a id="token-locks"></a>
### Token 锁

使用唯一凭据连接的适配器会在 `connect()` 中调用 `acquire_scoped_lock()`，并在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件同时使用同一个机器人 token。

<a id="delivery-path"></a>
## 投递路径

出站投递（`gateway/delivery.py`）处理：

- **直接回复** — 将响应发送回原始聊天
- **Home 频道投递** — 将定时任务输出和后台结果路由到配置的 home 频道
- **显式目标投递** — `send_message` 工具指定 `telegram:-1001234567890`，或 [`hermes send` CLI](/guides/pipe-script-output) 为 shell 脚本封装相同的工具
- **跨平台投递** — 投递到与原始消息不同的平台

定时任务投递不会镜像到 gateway 会话历史中——它们仅存在于自己的定时任务会话中。这是一个有意设计的选择，以避免消息交替违规。

<a id="hooks"></a>
## 钩子

Gateway 钩子是响应生命周期事件的 Python 模块：
<a id="gateway-hook-events"></a>
### Gateway Hook 事件

| 事件 | 触发时机 |
|-------|-----------|
| `gateway:startup` | Gateway 进程启动 |
| `session:start` | 新的对话会话开始 |
| `session:end` | 会话完成或超时 |
| `session:reset` | 用户通过 `/new` 重置会话 |
| `agent:start` | Agent 开始处理一条消息 |
| `agent:step` | Agent 完成一次工具调用迭代 |
| `agent:end` | Agent 完成并返回响应 |
| `command:*` | 任意斜杠命令被执行 |

Hook 从 `gateway/builtin_hooks/`（一个扩展点——在已发布的分发版中目前为空；`_register_builtin_hooks()` 是一个无操作 stub）和 `~/.hermes/hooks/`（用户安装的 Hook）中发现。每个 Hook 是一个目录，包含 `HOOK.yaml` 清单和 `handler.py`。

<a id="memory-provider-integration"></a>
## Memory Provider 集成

当启用了 memory provider 插件（例如 Honcho）时：

1. Gateway 会为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化 provider
3. Provider 工具（例如 `honcho_profile`、`viking_search`）通过以下路径路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 当会话结束/重置时，触发 `on_session_end()` 以进行清理和最终数据刷新

<a id="memory-flush-lifecycle"></a>
### Memory 刷新生命周期

当会话被重置、恢复或过期时：
1. 内置 memories 被刷新到磁盘
2. Memory provider 的 `on_session_end()` hook 触发
3. 一个临时的 `AIAgent` 运行一次仅针对 memory 的对话回合
4. 上下文随后被丢弃或归档

<a id="background-maintenance"></a>
## 后台维护

Gateway 在处理消息的同时运行定期维护：

- **Cron 定时触发** — 检查作业调度并执行到期作业
- **会话过期** — 清除超时后的废弃会话
- **Memory 刷新** — 在会话过期前主动刷新 memory
- **缓存刷新** — 刷新模型列表和 provider 状态

<a id="process-management"></a>
## 进程管理

Gateway 作为一个长生命周期进程运行，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl`（Linux）或 `launchctl`（macOS）— 服务管理
- PID 文件位于 `~/.hermes/gateway.pid` — 按 profile 作用域的进程跟踪

**Profile 作用域 vs 全局**：`start_gateway()` 使用按 profile 作用域的 PID 文件。`hermes gateway stop` 仅停止当前 profile 的 gateway。`hermes gateway stop --all` 使用全局 `ps aux` 扫描来杀死所有 gateway 进程（用于更新时）。

<a id="related-docs"></a>
## 相关文档

- [会话存储](./session-storage.md)
- [Cron 内部实现](./cron-internals.md)
- [ACP 内部实现](./acp-internals.md)
- [Agent Loop 内部实现](./agent-loop.md)
- [消息网关（用户指南）](/user-guide/messaging)
