---
sidebar_position: 9
---

<a id="adding-a-platform-adapter"></a>
# 添加平台适配器

本指南介绍如何为 Hermes 网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、企业微信等），使用户能够通过该服务与 Agent 交互。

:::tip
添加平台有两种方式：
- **插件方式**（推荐给社区/第三方）：将插件目录放入 `~/.hermes/plugins/` —— 无需修改任何核心代码。详见下面的 [插件方式（推荐）](#plugin-path-recommended)。
- **内建方式**：需要修改代码、配置和文档中的 20+ 个文件。请使用下面的 [内建检查清单](#step-by-step-checklist)。
:::

<a id="architecture-overview"></a>
## 架构概览

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ Gateway Runner ↔ AIAgent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现：

- **`connect()`** —— 建立连接（WebSocket、长轮询、HTTP 服务器等）*（抽象方法）*
- **`disconnect()`** —— 干净地关闭 *（抽象方法）*
- **`send()`** —— 向聊天发送文本消息 *（抽象方法）*
- **`send_typing()`** —— 显示输入状态指示器（可选覆写）
- **`get_chat_info()`** —— 返回聊天元数据（可选覆写）

入站消息由适配器接收，并通过 `self.handle_message(event)` 转发，基类会将其路由到 gateway runner。

<a id="plugin-path-recommended"></a>
## 插件方式（推荐）

插件系统允许你在不修改任何核心 Hermes 代码的情况下添加平台适配器。你的插件是一个包含两个文件的目录：

```
~/.hermes/plugins/my-platform/
  PLUGIN.yaml      # 插件元数据
  adapter.py       # 适配器类 + register() 入口点
```

<a id="plugin-yaml"></a>
### PLUGIN.yaml

插件元数据。`requires_env` 和 `optional_env` 块会自动填充 `hermes config` UI 条目（详见下面的 [在 hermes config 中暴露环境变量](#surfacing-env-vars-in-hermes-config)）。

```yaml
name: my-platform
label: My Platform
kind: platform
version: 1.0.0
description: 我的自定义消息平台适配器
author: Your Name
requires_env:
  - MY_PLATFORM_TOKEN          # 纯字符串即可
  - name: MY_PLATFORM_CHANNEL  # 或使用丰富的字典以提升用户体验
    description: "要加入的频道"
    prompt: "频道"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "用于定时任务投递的默认频道"
    password: false
```

<a id="adapter-py"></a>
### adapter.py

```python
import os
from gateway.platforms.base import (
    BasePlatformAdapter, SendResult, MessageEvent, MessageType,
)
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self) -> bool:
        # 连接到平台 API，启动监听器
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # 通过平台 API 发送消息
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}


def check_requirements() -> bool:
    return bool(os.getenv("MY_PLATFORM_TOKEN"))


def validate_config(config) -> bool:
    extra = getattr(config, "extra", {}) or {}
    return bool(os.getenv("MY_PLATFORM_TOKEN") or extra.get("token"))


def _env_enablement() -> dict | None:
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {"chat_id": home, "name": "Home"}
    return seed


def register(ctx):
    """插件入口点 —— 由 Hermes 插件系统调用。"""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # 环境变量驱动的自动配置 —— 在构造适配器之前，从环境变量中
        # 填充 PlatformConfig.extra。详见下面的“环境变量驱动的自动配置”部分。
        env_enablement_fn=_env_enablement,
        # Cron 默认频道投递支持。允许 deliver=my_platform 的 cron 任务
        # 无需修改 cron/scheduler.py 即可路由。详见下面的“Cron 投递”部分。
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
        # 按平台限制用户授权的环境变量
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # 消息长度限制，用于智能分块（0 表示不限制）
        max_message_length=4000,
        # 注入到系统提示中的 LLM 指导信息
        platform_hint=(
            "你正在通过 My Platform 进行聊天。"
            "它支持 Markdown 格式。"
        ),
        # 显示
        emoji="💬",
    )

    # 可选：注册平台特定的工具
    ctx.register_tool(
        name="my_platform_search",
        toolset="my_platform",
        schema={...},
        handler=my_search_handler,
    )
```
<a id="configuration"></a>
### 配置

用户在 `config.yaml` 中配置平台：

```yaml
gateway:
  platforms:
    my_platform:
      enabled: true
      extra:
        token: "..."
        channel: "#general"
```

或通过环境变量（适配器在 `__init__` 中读取）。

<a id="what-the-plugin-system-handles-automatically"></a>
### 插件系统自动处理的内容

当你调用 `ctx.register_platform()` 时，以下集成点会自动为你处理——无需修改核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 注册表在内置 if/elif 链之前被检查 |
| 配置解析 | `Platform._missing_()` 接受任何平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` |
| 用户授权 | 检查 `allowed_users_env` / `allow_all_env` |
| 仅环境变量自动启用 | `env_enablement_fn` 向 `PlatformConfig.extra` + `home_channel` 注入种子值 |
| YAML 配置桥接 | `apply_yaml_config_fn` 将 `config.yaml` 的键转换为环境变量 / 额外参数 |
| Cron 消息投递 | `cron_deliver_env_var` 使 `deliver=&lt;name&gt;` 生效 |
| `hermes config` UI 条目 | `plugin.yaml` 中的 `requires_env` / `optional_env` 自动填充 |
| send_message 工具 | 通过实时网关适配器路由 |
| Webhook 跨平台投递 | 在注册表中查找已知平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 插件平台包含在枚举中 |
| 系统提示提示语 | `platform_hint` 注入到 LLM 上下文中 |
| 消息分块 | `max_message_length` 用于智能分割 |
| PII 脱敏 | `pii_safe` 标志 |
| `hermes status` | 显示插件平台并附带 `(plugin)` 标签 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台出现在按平台配置中 |
| Token 锁定（多配置） | 在 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 当插件缺失时记录描述性日志 |

<a id="env-driven-auto-configuration"></a>
## 环境变量驱动的自动配置

大多数用户通过将环境变量放入 `~/.hermes/.env` 来设置平台，而不是编辑 `config.yaml`。`env_enablement_fn` 钩子使你的插件能够在 **适配器构建之前** 拾取这些环境变量，这样 `hermes gateway status`、`get_connected_platforms()` 和 cron 投递无需实例化平台 SDK 就能看到正确的状态。

```python
def _env_enablement() -> dict | None:
    """Seed PlatformConfig.extra from env vars.

    Called by the platform registry during load_gateway_config().
    Return None when the platform isn't minimally configured — the
    caller then skips auto-enabling. Return a dict to seed extras.

    The special 'home_channel' key is extracted and becomes a proper
    HomeChannel dataclass on the PlatformConfig; every other key is
    merged into PlatformConfig.extra.
    """
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {
            "chat_id": home,
            "name": os.getenv("MY_PLATFORM_HOME_CHANNEL_NAME", "Home"),
        }
    return seed


def register(ctx):
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        # ... other fields
    )
```
<a id="yamlenv-config-bridge"></a>
## YAML→环境变量配置桥接

有些用户更喜欢在 `config.yaml` 中配置（`my_platform.require_mention`、`my_platform.allowed_channels` 等），而不是使用环境变量。`apply_yaml_config_fn` 钩子让你的插件自己处理这个转换，而不需要强制核心的 `gateway/config.py` 了解你平台的 YAML 结构。

```python
import os

def _apply_yaml_config(yaml_cfg: dict, platform_cfg: dict) -> dict | None:
    """将 config.yaml `my_platform:` 的键转换为环境变量或额外参数。

    yaml_cfg     — 完整的顶层解析后的 config.yaml 字典
    platform_cfg — 平台自身的子字典（yaml_cfg.get("my_platform", {})）

    可以直接修改 os.environ（使用 `not os.getenv(...)` 守卫来保持
    环境变量优先级高于 YAML）并/或返回一个字典合并到
    PlatformConfig.extra。如果不需要额外参数则返回 None 或 {}。
    """
    if "require_mention" in platform_cfg and not os.getenv("MY_PLATFORM_REQUIRE_MENTION"):
        os.environ["MY_PLATFORM_REQUIRE_MENTION"] = str(platform_cfg["require_mention"]).lower()
    allowed = platform_cfg.get("allowed_channels")
    if allowed is not None and not os.getenv("MY_PLATFORM_ALLOWED_CHANNELS"):
        if isinstance(allowed, list):
            allowed = ",".join(str(v) for v in allowed)
        os.environ["MY_PLATFORM_ALLOWED_CHANNELS"] = str(allowed)
    return None  # 没有额外内容需要合并到 PlatformConfig.extra

def register(ctx):
    ctx.register_platform(
        name="my_platform",
        ...,
        apply_yaml_config_fn=_apply_yaml_config,
    )
```

该钩子在 `load_gateway_config()` 期间被调用，位于通用共享键循环（处理 `unauthorized_dm_behavior`、`notice_delivery`、`reply_prefix`、`require_mention` 等常见键）之后，以及 `_apply_env_overrides()` 之前，因此你的插件只需要桥接**特定于平台**的键。

钩子抛出的异常会被捕获并在调试级别记录——一个行为异常的插件永远不会中止网关配置加载。

<a id="cron-delivery"></a>
## 定时任务投递

要让 `deliver=my_platform` 的定时任务路由到已配置的首页频道，请将 `cron_deliver_env_var` 设置为保存默认聊天/房间/频道 ID 的环境变量名：

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

调度器在解析 `deliver=my_platform` 任务的首页目标时会读取这个环境变量，同时也会在 `_KNOWN_DELIVERY_PLATFORMS` 类型的检查中将该平台视为有效的定时任务目标。如果你的 `env_enablement_fn` 提供了一个 `home_channel` 字典（见上文），那么该字典优先——`cron_deliver_env_var` 是在环境变量注入之前运行的定时任务的回退方案。

<a id="out-of-process-cron-delivery"></a>
### 跨进程定时任务投递

`cron_deliver_env_var` 让你的平台成为可识别的 `deliver=` 目标。为了让实际发送操作在定时任务与网关运行于不同进程时（即 `hermes cron run` 独立于 `hermes gateway`）成功，请注册一个 `standalone_sender_fn`：

```python
async def _standalone_send(
    pconfig,
    chat_id,
    message,
    *,
    thread_id=None,
    media_files=None,
    force_document=False,
):
    """打开一个临时连接/获取一个新的令牌，发送，然后关闭。"""
    # ... 打开连接，发送消息，返回结果 ...
    return {"success": True, "message_id": "..."}
    # 或者 {"error": "..."}

ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
    standalone_sender_fn=_standalone_send,
)
```
为什么这个钩子是必要的：内置平台（Telegram、Discord、Slack 等）在 `tools/send_message_tool.py` 中提供了直接的 REST 辅助函数，这样 cron 可以在不将网关保留在同一进程中的情况下进行投递。插件平台历史上依赖于 `_gateway_runner_ref()`，该函数在网关进程外部返回 `None`，因此如果没有 `standalone_sender_fn`，cron 端的发送会失败，并提示 `No live adapter for platform '&lt;name&gt;'`。

该函数接收与实时适配器相同的 `pconfig` 和 `chat_id`，以及可选的 `thread_id`、`media_files` 和 `force_document` 关键字参数。返回 `{"success": True, "message_id": ...}` 表示投递成功；返回 `{"error": "..."}` 则会在 cron 的 `delivery_errors` 中显示该消息。函数内部抛出的异常会被调度器捕获，并报告为 `Plugin standalone send failed: &lt;reason&gt;`。参考实现位于 `plugins/platforms/{irc,teams,google_chat}/adapter.py`。

<a id="surfacing-env-vars-in-hermes-config"></a>
## 在 `hermes config` 中暴露环境变量

`hermes_cli/config.py` 在导入时扫描 `plugins/platforms/*/plugin.yaml`，并从 `requires_env` 和（可选的）`optional_env` 块中自动填充 `OPTIONAL_ENV_VARS`。使用富字典形式来提供适当的描述、提示、密码标志和 URL——CLI 设置界面会自动拾取它们。

```yaml
# plugins/platforms/my_platform/plugin.yaml
name: my_platform-platform
label: My Platform
kind: platform
version: 1.0.0
description: >
  My Platform gateway adapter for Hermes Agent.
author: Your Name
requires_env:
  - name: MY_PLATFORM_TOKEN
    description: "Bot API token from the My Platform console"
    prompt: "My Platform bot token"
    url: "https://my-platform.example.com/bots"
    password: true
  - name: MY_PLATFORM_CHANNEL
    description: "Channel to join (e.g. #hermes)"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery (defaults to MY_PLATFORM_CHANNEL)"
    prompt: "Home channel (or empty)"
    password: false
  - name: MY_PLATFORM_ALLOWED_USERS
    description: "Comma-separated user IDs allowed to talk to the bot"
    prompt: "Allowed users (comma-separated)"
    password: false
```

**支持的字典键：** `name`（必需）、`description`、`prompt`、`url`、`password`（布尔值；当省略时，会根据 `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` 后缀自动检测）、`category`（默认为 `"messaging"`）。

纯字符串条目（`- MY_PLATFORM_TOKEN`）仍然有效——它们会从插件的 `label` 自动派生出一个通用描述。如果 `OPTIONAL_ENV_VARS` 中已存在同一变量的硬编码条目，则优先使用该条目（向后兼容）；`plugin.yaml` 形式作为后备。

<a id="platform-specific-slow-llm-ux"></a>
## 平台特定的慢 LLM 用户体验

某些平台存在限制，会改变慢速 LLM 响应的呈现方式：

- **LINE** 会发放一个一次性 *回复令牌*，该令牌在入站事件后大约 60 秒过期。使用该令牌回复是免费的；回退到计费的 Push API 则不是。如果 LLM 在截止时间前未完成，那么选择就是“消耗付费的 Push 配额”或“在回复令牌过期前用它做点更聪明的事”。
- **WhatsApp** 会在 24 小时后将会话标记为非活跃，之后只接受模板消息。
- **SMS** 没有打字指示器或渐进式更新的概念——长响应看起来就像机器人离线了。
以下是文档片段的中文翻译：

这些是基础 `BasePlatformAdapter` 无法预料的真实约束。插件接口特意留出了空间，让适配器可以在基础类型循环之上叠加平台特定的用户体验，而无需扩展关键字参数列表。

<a id="pattern-subclass-keeptyping-to-layer-mid-flight-ux"></a>
### 模式：子类化 `_keep_typing` 以叠加中途用户体验

`BasePlatformAdapter._keep_typing` 是打字指示器的“心跳”——它在 LLM 生成响应时作为后台任务运行，并在响应送达时被取消。要在某个阈值（例如 45 秒时发送“仍在思考”气泡）处叠加平台特定的行为，你可以在适配器中重写 `_keep_typing`，在 `super()._keep_typing()` 之外安排自己的任务，并在 `finally` 块中清理它：

```python
class LineAdapter(BasePlatformAdapter):
    async def _keep_typing(self, chat_id: str, *args, **kwargs) -> None:
        if self.slow_response_threshold <= 0:
            await super()._keep_typing(chat_id, *args, **kwargs)
            return

        async def _fire_at_threshold() -> None:
            try:
                await asyncio.sleep(self.slow_response_threshold)
            except asyncio.CancelledError:
                raise
            # 在此处执行平台特定的工作——对于 LINE，使用缓存的回复令牌
            # 发送一个模板按钮“获取答案”气泡，
            # 以便用户稍后通过回传回调中的新（免费）回复令牌获取缓存的响应。
            await self._send_slow_response_button(chat_id)

        side_task = asyncio.create_task(_fire_at_threshold())
        try:
            await super()._keep_typing(chat_id, *args, **kwargs)
        finally:
            if not side_task.done():
                side_task.cancel()
                try:
                    await side_task
                except (asyncio.CancelledError, Exception):
                    pass
```

关键点：

- **始终 `await super()._keep_typing(...)`。** 打字心跳本身就有用——不要替换它，而是在它上面叠加。
- **在 `finally` 中清理侧边任务。** 当 LLM 完成（或 `/stop` 取消运行）时，网关会取消打字任务。你的侧边任务也必须观察这个取消动作，否则它会持续存在，并可能在响应已送达后触发。
- **与 `interrupt_session_activity` 配合使用**，以在用户发出 `/stop` 时解决任何残留的 UX 状态。对于 LINE，这意味着将回传缓存条目从 `PENDING` 转换为 `ERROR`，以便持久的“获取答案”按钮发送“运行已被中断”消息，而不是循环等待。

<a id="pattern-subclass-send-to-route-through-a-cache-instead-of-sending-immediately"></a>
### 模式：子类化 `send` 以通过缓存路由，而不是立即发送

如果你的慢响应 UX 将响应缓存起来供后续检索（LINE 的回传流程），那么你的 `send` 重写需要识别三种模式：

1. **该聊天有挂起的回传操作** → 将响应缓存在 request_id 下，不发送任何可见内容。
2. **系统忙碌确认**（`⚡ 中断中`、`⏳ 已排队`、`⏩ 已转向`）→ 绕过缓存，直接发送可见内容，以便用户看到网关对其输入的响应。
3. **正常响应** → 照常通过回复令牌或推送发送。
```python
async def send(self, chat_id: str, content: str, **kw) -> SendResult:
    if _is_system_bypass(content):
        return await self._send_text_chunks(chat_id, content, force_push=False)
    pending_rid = self._pending_buttons.get(chat_id)
    if pending_rid:
        self._cache.set_ready(pending_rid, content)
        return SendResult(success=True, message_id=pending_rid)
    return await self._send_text_chunks(chat_id, content, force_push=False)
```

`_SYSTEM_BYPASS_PREFIXES` 是网关自身的忙碌确认前缀（`⚡`、`⏳`、`⏩`、`💾`）。无论缓存的 UX 状态如何，始终让这些内容可见地通过。

<a id="when-this-pattern-is-appropriate"></a>
### 何时适合使用此模式

在以下情况下，使用 typing-loop 覆盖方法：

- 平台出站 API 有严格的时间窗口约束（一次性回复令牌、过期的粘性会话等）**并且**
- 在该平台上，*可见的飞行中气泡* 是可接受的 UX。

在以下情况下，使用更简单的 `slow_response_threshold = 0` 始终 Push 路径：

- 平台没有有意义的免费与付费区分，**或者**
- 用户社区更喜欢“加载中… 加载中… 完成”这种静默后响应的方式，而不是交互式中间气泡。

LINE 两者都支持：对于免费的回发获取，阈值默认为 45 秒，而 `LINE_SLOW_RESPONSE_THRESHOLD=0` 则回退到“始终 Push 回退”。

<a id="reference-implementation"></a>
### 参考实现

有关完整的 LINE 回发实现，请参阅 `plugins/platforms/line/adapter.py` —— 一个 `RequestCache` 状态机（`PENDING → READY → DELIVERED`，加上用于 `/stop` 的 `ERROR`），一个在阈值时触发 Template Buttons 气泡的 `_keep_typing` 覆盖，一个通过缓存路由的 `send` 覆盖，以及一个解决孤立 PENDING 条目的 `interrupt_session_activity` 覆盖。

<a id="reference-implementations-plugin-path"></a>
### 参考实现（插件路径）

有关完整的工作示例，请参阅仓库中的 `plugins/platforms/irc/` —— 一个零外部依赖的完整异步 IRC 适配器。`plugins/platforms/teams/` 涵盖 Bot Framework / Adaptive Cards，`plugins/platforms/google_chat/` 涵盖基于 OAuth 的 REST API，`plugins/platforms/line/` 涵盖具有平台特定慢 LLM UX 的 webhook 驱动消息 API。

---

<a id="step-by-step-checklist-built-in-path"></a>
## 逐步检查清单（内置路径）

:::note
此检查清单适用于将平台直接添加到 Hermes 核心代码库 —— 通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#plugin-path-recommended)。
:::

<a id="1-platform-enum"></a>
### 1. 平台枚举

将你的平台添加到 `gateway/config.py` 的 `Platform` 枚举中：

```python
class Platform(str, Enum):
    # ... 现有平台 ...
    NEWPLAT = "newplat"
```

<a id="2-adapter-file"></a>
### 2. 适配器文件

创建 `gateway/platforms/newplat.py`：

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

def check_newplat_requirements() -> bool:
    """如果依赖可用则返回 True。"""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # 从 config.extra 字典读取配置
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self) -> bool:
        # 设置连接，开始轮询/webhook
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._running = False
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # 通过平台 API 发送消息
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}
```
对于入站消息，构建一个 `MessageEvent` 并调用 `self.handle_message(event)`：

```python
source = self.build_source(
    chat_id=chat_id,
    chat_name=name,
    chat_type="dm",  # 或 "group"
    user_id=user_id,
    user_name=user_name,
)
event = MessageEvent(
    text=content,
    message_type=MessageType.TEXT,
    source=source,
    message_id=msg_id,
)
await self.handle_message(event)
```

<a id="3-gateway-config-gateway-config-py"></a>
### 3. 网关配置 (`gateway/config.py`)

三个接触点：

1. **`get_connected_platforms()`** — 添加对平台必要凭证的检查
2. **`load_gateway_config()`** — 添加 token 环境变量映射条目：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — 将所有 `NEWPLAT_*` 环境变量映射到配置

<a id="4-gateway-runner-gateway-run-py"></a>
### 4. 网关运行器 (`gateway/run.py`)

六个接触点：

1. **`_create_adapter()`** — 添加一个 `elif platform == Platform.NEWPLAT:` 分支
2. **`_is_user_authorized()` allowed_users 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` allow_all 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **早期环境检查 `_any_allowlist` 元组** — 添加 `"NEWPLAT_ALLOWED_USERS"`
5. **早期环境检查 `_allow_all` 元组** — 添加 `"NEWPLAT_ALLOW_ALL_USERS"`
6. **`_UPDATE_ALLOWED_PLATFORMS` 冻结集合** — 添加 `Platform.NEWPLAT`

<a id="5-cross-platform-delivery"></a>
### 5. 跨平台投递

1. **`gateway/platforms/webhook.py`** — 将 `"newplat"` 添加到投递类型元组
2. **`cron/scheduler.py`** — 添加到 `_KNOWN_DELIVERY_PLATFORMS` 冻结集合和 `_deliver_result()` 平台映射

<a id="6-cli-integration"></a>
### 6. CLI 集成

1. **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS`
2. **`hermes_cli/gateway.py`** — 在 `_PLATFORMS` 列表中添加条目，包含 key、label、emoji、token_var、setup_instructions 和 vars
3. **`hermes_cli/platforms.py`** — 添加包含 label 和 default_toolset 的 `PlatformInfo` 条目（供 `skills_config` 和 `tools_config` TUI 使用）
4. **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可委托给 `gateway.py`），并将元组添加到消息平台列表
5. **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — 将 `"newplat": "NEWPLAT_TOKEN"` 添加到平台检测字典

<a id="7-tools"></a>
### 7. 工具

1. **`tools/send_message_tool.py`** — 将 `"newplat": Platform.NEWPLAT` 添加到平台映射
2. **`tools/cronjob_tools.py`** — 将 `newplat` 添加到投递目标描述字符串

<a id="8-toolsets"></a>
### 8. 工具集

1. **`toolsets.py`** — 添加 `"hermes-newplat"` 工具集定义，包含 `_HERMES_CORE_TOOLS`
2. **`toolsets.py`** — 将 `"hermes-newplat"` 添加到 `"hermes-gateway"` 的 includes 列表

<a id="9-optional-platform-hints"></a>
### 9. 可选：平台提示

**`agent/prompt_builder.py`** — 如果你的平台有特定的渲染限制（不支持 Markdown、消息长度限制等），请在 `_PLATFORM_HINTS` 字典中添加条目。这会将平台特定的指导信息注入系统提示：

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "You are chatting via NewPlat. It supports markdown formatting "
        "but has a 4000-character message limit."
    ),
}
```
并非所有平台都需要提示——只有当 Agent 的行为应有所不同时才添加。

<a id="10-tests"></a>
### 10. 测试

创建 `tests/gateway/test_newplat.py`，包含以下测试：

- 从配置构建适配器
- 消息事件构建
- 发送方法（模拟外部 API）
- 平台特定功能（加密、路由等）

<a id="11-documentation"></a>
### 11. 文档

| 文件 | 添加内容 |
|------|----------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台设置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台对比表、架构图、工具集表格、安全章节、下一步链接 |
| `website/docs/reference/environment-variables.md` | 所有 `NEWPLAT_*` 环境变量 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集 |
| `website/docs/integrations/index.md` | 平台链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器数量 + 列表 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件列表 |

<a id="parity-audit"></a>
## 对等审计

在标记新平台 PR 为完成之前，请针对一个已有平台执行对等审计：

```bash
# 查找所有提及参考平台的 .py 文件
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# 查找所有提及新平台的 .py 文件
search_files "newplat" output_mode="files_only" file_glob="*.py"

# 第一个集合中有但第二个集合中没有的文件，是潜在差距
```

对 `.md` 和 `.ts` 文件重复此操作。检查每个差距——是平台枚举（需要更新）还是平台特定引用（跳过）。

<a id="common-patterns"></a>
## 常见模式

<a id="long-poll-adapters"></a>
### 长轮询适配器

如果你的适配器使用长轮询（如 Telegram 或微信），请使用轮询循环任务：

```python
async def connect(self):
    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()

async def _poll_loop(self):
    while self._running:
        messages = await self._fetch_updates()
        for msg in messages:
            await self.handle_message(self._build_event(msg))
```

<a id="callback-webhook-adapters"></a>
### 回调/Webhook 适配器

如果平台将消息推送到你的端点（如企业微信回调），则运行一个 HTTP 服务器：

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... 启动 aiohttp 服务器
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # 立即确认
```

对于响应截止时间严格的平台（例如企业微信的 5 秒限制），务必立即确认，随后通过 API 主动投递 Agent 的回复。Agent 会话运行时长 3–30 分钟——在回调响应窗口内进行内联回复是不可行的。

<a id="token-locks"></a>
### 令牌锁

如果适配器持有带有唯一凭证的持久连接，请添加一个作用域锁，以防止两个配置文件使用同一凭证：
```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("令牌已被其他配置使用")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

<a id="reference-implementations"></a>
## 参考实现

| 适配器 | 模式 | 复杂度 | 良好参考示例 |
|---------|---------|------------|-------------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密 |
| `wecom_callback.py` | 回调/webhook | 中等 | HTTP 服务器、AES 加密、多应用 |
| `telegram.py` | 长轮询 + Bot API | 高 | 功能完整的适配器，支持群组和线程 |
