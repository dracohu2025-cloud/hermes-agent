---
sidebar_position: 9
---

# 添加平台适配器 {#adding-a-platform-adapter}

本指南介绍如何为 Hermes 网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、企业微信等），使用户能够通过该服务与 Agent 进行交互。

:::tip
添加平台有两种方式：
- **插件方式**（推荐给社区/第三方）：将插件目录放入 `~/.hermes/plugins/` 中——无需修改任何核心代码。请参见下方的[插件路径](#plugin-path-recommended)。
- **内置方式**：需要修改代码、配置和文档中的 20 多个文件。请使用下方的[内置检查清单](#step-by-step-checklist)。
:::

## 架构概览 {#architecture-overview}

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ 网关运行器 ↔ AIAgent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现以下方法：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*（抽象方法）*
- **`disconnect()`** — 干净地关闭连接 *（抽象方法）*
- **`send()`** — 向聊天发送文本消息 *（抽象方法）*
- **`send_typing()`** — 显示正在输入指示（可选覆盖）
- **`get_chat_info()`** — 返回聊天元数据（可选覆盖）

入站消息由适配器接收，并通过 `self.handle_message(event)` 转发，基类会将其路由到网关运行器。

## 插件路径（推荐） {#plugin-path-recommended}

插件系统允许你在不修改任何 Hermes 核心代码的情况下添加平台适配器。你的插件是一个包含两个文件的目录：

```
~/.hermes/plugins/my-platform/
  PLUGIN.yaml      # 插件元数据
  adapter.py       # 适配器类 + register() 入口点
```

### PLUGIN.yaml {#plugin-yaml}

```yaml
name: my-platform
version: 1.0.0
description: 我的自定义消息平台适配器
requires_env:
  - MY_PLATFORM_TOKEN
  - MY_PLATFORM_CHANNEL
```

### adapter.py {#adapter-py}

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


def register(ctx):
    """插件入口点——由 Hermes 插件系统调用。"""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # 每个平台用户授权的环境变量
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # 智能分块的消息长度限制（0 表示无限制）
        max_message_length=4000,
        # 注入到系统提示中的 LLM 指导
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
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
### 配置 {#configuration}

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

或者通过环境变量配置（适配器在 `__init__` 中读取）。

### 插件系统自动处理的内容 {#what-the-plugin-system-handles-automatically}

当你调用 `ctx.register_platform()` 时，以下集成点会自动为你处理——无需修改核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 在内置 if/elif 链之前检查注册表 |
| 配置解析 | `Platform._missing_()` 接受任何平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` |
| 用户授权 | 检查 `allowed_users_env` / `allow_all_env` |
| Cron 投递 | `Platform()` 解析任何已注册的名称 |
| send_message 工具 | 通过实时网关适配器路由 |
| Webhook 跨平台投递 | 检查注册表中已知的平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 插件平台包含在枚举中 |
| 系统提示提示 | `platform_hint` 注入到 LLM 上下文中 |
| 消息分块 | `max_message_length` 用于智能拆分 |
| PII 脱敏 | `pii_safe` 标志 |
| `hermes status` | 显示带有 `(plugin)` 标签的插件平台 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台出现在按平台配置中 |
| Token 锁（多配置文件） | 在 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 当插件缺失时输出描述性日志 |

### 参考实现 {#reference-implementation}

请参阅仓库中的 `plugins/platforms/irc/` 目录，获取一个完整的工作示例——一个零外部依赖的完整异步 IRC 适配器。

---

<a id="step-by-step-checklist-built-in-path"></a>
## 分步检查清单（内置路径） {#step-by-step-checklist}

:::note
此检查清单适用于将平台直接添加到 Hermes 核心代码库——通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#plugin-path-recommended)。
:::

### 1. 平台枚举 {#1-platform-enum}

在 `gateway/config.py` 中将你的平台添加到 `Platform` 枚举中：

```python
class Platform(str, Enum):
    # ... 现有平台 ...
    NEWPLAT = "newplat"
```

### 2. 适配器文件 {#2-adapter-file}

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
        # 建立连接，开始轮询/webhook
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

### 3. 网关配置 (`gateway/config.py`) {#3-gateway-config-gateway-config-py}

三个接触点：

1. **`get_connected_platforms()`** — 添加对你平台所需凭证的检查
2. **`load_gateway_config()`** — 添加令牌环境变量映射条目：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — 将所有 `NEWPLAT_*` 环境变量映射到配置

### 4. 网关运行器 (`gateway/run.py`) {#4-gateway-runner-gateway-run-py}

六个接触点：

1. **`_create_adapter()`** — 添加一个 `elif platform == Platform.NEWPLAT:` 分支
2. **`_is_user_authorized()` allowed_users 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` allow_all 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **早期环境变量检查 `_any_allowlist` 元组** — 添加 `"NEWPLAT_ALLOWED_USERS"`
5. **早期环境变量检查 `_allow_all` 元组** — 添加 `"NEWPLAT_ALLOW_ALL_USERS"`
6. **`_UPDATE_ALLOWED_PLATFORMS` 冻结集合** — 添加 `Platform.NEWPLAT`

### 5. 跨平台投递 {#5-cross-platform-delivery}

1. **`gateway/platforms/webhook.py`** — 将 `"newplat"` 添加到投递类型元组
2. **`cron/scheduler.py`** — 添加到 `_KNOWN_DELIVERY_PLATFORMS` 冻结集合和 `_deliver_result()` 平台映射

### 6. CLI 集成 {#6-cli-integration}

1. **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS`
2. **`hermes_cli/gateway.py`** — 向 `_PLATFORMS` 列表添加条目，包含 key、label、emoji、token_var、setup_instructions 和 vars
3. **`hermes_cli/platforms.py`** — 添加 `PlatformInfo` 条目，包含 label 和 default_toolset（由 `skills_config` 和 `tools_config` TUI 使用）
4. **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可委托给 `gateway.py`），并将元组添加到消息平台列表
5. **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — 将 `"newplat": "NEWPLAT_TOKEN"` 添加到平台检测字典

### 7. 工具 {#7-tools}

1. **`tools/send_message_tool.py`** — 将 `"newplat": Platform.NEWPLAT` 添加到平台映射
2. **`tools/cronjob_tools.py`** — 将 `newplat` 添加到投递目标描述字符串

### 8. 工具集 {#8-toolsets}

1. **`toolsets.py`** — 添加 `"hermes-newplat"` 工具集定义，包含 `_HERMES_CORE_TOOLS`
2. **`toolsets.py`** — 将 `"hermes-newplat"` 添加到 `"hermes-gateway"` 的包含列表

### 9. 可选：平台提示 {#9-optional-platform-hints}

**`agent/prompt_builder.py`** — 如果你的平台有特定的渲染限制（不支持 Markdown、消息长度限制等），向 `_PLATFORM_HINTS` 字典添加一个条目。这会将平台特定的指导注入到系统提示中：

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

### 10. 测试 {#10-tests}

创建 `tests/gateway/test_newplat.py`，覆盖以下内容：

- 从配置构建适配器
- 消息事件构建
- 发送方法（模拟外部 API）
- 平台特定功能（加密、路由等）

### 11. 文档 {#11-documentation}

| 文件 | 添加内容 |
|------|----------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台设置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台对比表、架构图、工具集表格、安全部分、下一步链接 |
| `website/docs/reference/environment-variables.md` | 所有 NEWPLAT_* 环境变量 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集 |
| `website/docs/integrations/index.md` | 平台链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器数量 + 列表 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件列表 |

## 一致性审计 {#parity-audit}

在将新平台的 PR 标记为完成之前，请对照已有平台进行一致性审计：

```bash
# 查找所有提及参考平台的 .py 文件
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# 查找所有提及新平台的 .py 文件
search_files "newplat" output_mode="files_only" file_glob="*.py"

# 第一组中有但第二组中没有的文件，就是潜在缺口
```

对 `.md` 和 `.ts` 文件重复此操作。调查每个缺口——是平台枚举（需要更新）还是平台特定引用（跳过）？

## 常见模式 {#common-patterns}

### 长轮询适配器 {#long-poll-adapters}

如果您的适配器使用长轮询（如 Telegram 或微信），请使用轮询循环任务：

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

### 回调/Webhook 适配器 {#callback-webhook-adapters}

如果平台将消息推送到您的端点（如企业微信回调），请运行一个 HTTP 服务器：

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

对于响应时限严格的平台（例如企业微信的 5 秒限制），请始终立即确认，稍后通过 API 主动发送 Agent 的回复。Agent 会话运行 3–30 分钟——在回调响应窗口内进行内联回复是不可行的。

### 令牌锁 {#token-locks}

如果适配器使用唯一凭据保持持久连接，请添加一个作用域锁，以防止两个配置文件使用同一凭据：
```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("令牌已被其他配置文件使用")
        return False
    # ... 连接

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## 参考实现 {#reference-implementations}

| 适配器 | 模式 | 复杂度 | 适合参考的场景 |
|---------|---------|------------|-------------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密 |
| `wecom_callback.py` | 回调/webhook | 中等 | HTTP 服务器、AES 加密、多应用 |
| `telegram.py` | 长轮询 + Bot API | 高 | 功能完备的适配器，支持群组和线程 |
