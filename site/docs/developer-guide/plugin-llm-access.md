---
sidebar_position: 11
title: "插件 LLM 访问"
description: "通过 ctx.llm 在插件内部执行任意 LLM 调用——聊天或结构化输出、同步或异步。宿主持有认证、故障关闭信任门、可选 JSON Schema 校验。"
---

<a id="plugin-llm-access"></a>
# 插件 LLM 访问

`ctx.llm` 是插件进行 LLM 调用的受支持方式。聊天补全、结构化提取、同步、异步、带或不带图片——同一套接口、同一道信任门、同一组宿主持有的凭证。

当插件需要做一些涉及模型但不属于 Agent 对话范围的事情时，就会用到它。一个钩子将工具错误重写成非技术人员能读懂的语句；一个网关适配器在入站消息入队前进行转换；一条斜杠命令总结长粘贴内容；一个定时任务对昨天的活动评分并在状态板上写一行；一个预过滤器决定消息是否值得唤醒 Agent。

这些任务不应让 Agent 参与循环。它们只需一次 LLM 调用、一个类型化的答案，然后结束。

<a id="the-smallest-possible-call"></a>
## 最简单的一次调用

```python
result = ctx.llm.complete(messages=[{"role": "user", "content": "ping"}])
return result.text
```

一行就是整个 API。没有密钥、没有提供商配置、没有 SDK 初始化。插件会使用用户当前正在使用的提供商和模型运行——当用户切换提供商时，插件会自动跟随。

<a id="a-more-complete-chat-example"></a>
## 一个更完整的聊天示例

```python
result = ctx.llm.complete(
    messages=[
        {"role": "system", "content": "将错误重写为非技术人员可执行的一个短句。"},
        {"role": "user",   "content": traceback_text},
    ],
    max_tokens=64,
    purpose="hooks.error-rewrite",
)
return result.text
```

`purpose` 是一个自由格式的审计字符串——它会出现在 `agent.log` 和 `result.audit` 中，方便运维人员查看哪个插件发起了哪个调用。可选，但对于频繁触发的调用建议使用。

<a id="structured-output"></a>
## 结构化输出

当插件需要类型化的答案时，切换到结构化通道：

```python
result = ctx.llm.complete_structured(
    instructions="对此支持回复的紧急程度进行评分（0–1）并选择一个类别。",
    input=[{"type": "text", "text": message_body}],
    json_schema=TRIAGE_SCHEMA,
    purpose="support.triage",
    temperature=0.0,
    max_tokens=128,
)

if result.parsed["urgency"] > 0.8:
    await dispatch_to_oncall(result.parsed["category"], message_body)
```

宿主向提供商请求 JSON 输出，本地解析作为回退，如果安装了 `jsonschema` 则根据你的 schema 进行校验，然后通过 `result.parsed` 返回 Python 对象。如果模型无法生成有效的 JSON，则 `result.parsed` 为 `None`，`result.text` 携带原始响应。

<a id="what-this-lane-gives-you"></a>
## 该通道提供的能力

* **一次调用，四种形态。** `complete()` 用于聊天，`complete_structured()` 用于类型化 JSON，`acomplete()` 和 `acomplete_structured()` 用于 asyncio。相同的参数，相同的结果对象。
* **宿主持有凭证。** OAuth 令牌、刷新流程、凭证池、每个任务的辅助覆盖——Hermes 已有的所有凭证概念都适用。插件看不到任何令牌；宿主通过 `result.audit` 对调用进行归因。
* **有界。** 单次同步或异步调用。没有流式、没有工具循环、没有需要管理的对话状态。给定输入、获取结果、返回。
* **故障关闭信任。** 你从未配置过的插件不能自行选择提供商、模型、Agent 或存储的凭证。默认姿势是“使用用户正在使用的内容”。运维人员在 `config.yaml` 中为每个插件选择特定的覆盖项。
<a id="quick-start"></a>
## 快速开始

下面提供两个完整的插件示例——一个用于聊天补全，一个用于结构化提取。两者都包含在单个 `register(ctx)` 函数中，无需任何外部配置即可针对用户当前激活的模型运行。

<a id="chat-completion-tldr"></a>
### 聊天补全 — `/tldr`

```python
def register(ctx):
    ctx.register_command(
        name="tldr",
        handler=lambda raw: _tldr(ctx, raw),
        description="将提供的文本总结为一段话。",
        args_hint="<text>",
    )


def _tldr(ctx, raw_args: str) -> str:
    text = raw_args.strip()
    if not text:
        return "用法：/tldr <要总结的文本>"
    result = ctx.llm.complete(
        messages=[
            {"role": "system",
             "content": "将用户的文本总结为一段紧凑的文字。不要加开场白。"},
            {"role": "user", "content": text},
        ],
        max_tokens=256,
        temperature=0.3,
        purpose="tldr",
    )
    return result.text
```

`result.text` 是模型的响应；`result.usage` 包含 token 计数；`result.provider` 和 `result.model` 包含归属信息。

<a id="structured-extraction-paste-to-tasks"></a>
### 结构化提取 — `/paste-to-tasks`

```python
def register(ctx):
    ctx.register_command(
        name="paste-to-tasks",
        handler=lambda raw: _paste_to_tasks(ctx, raw),
        description="将自由格式的会议记录转换为结构化任务。",
        args_hint="<text>",
    )


_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "owner":  {"type": "string"},
                    "action": {"type": "string"},
                    "due":    {"type": "string", "description": "ISO 日期或留空"},
                },
                "required": ["action"],
            },
        },
    },
    "required": ["tasks"],
}


def _paste_to_tasks(ctx, raw_args: str) -> str:
    if not raw_args.strip():
        return "用法：/paste-to-tasks <会议记录>"
    result = ctx.llm.complete_structured(
        instructions=(
            "从这些会议记录中提取具体的行动项。"
            "每个可操作的行对应一个任务。如果没有指定负责人，则将 'owner' 留空。"
        ),
        input=[{"type": "text", "text": raw_args}],
        json_schema=_TASKS_SCHEMA,
        schema_name="meeting.tasks",
        purpose="paste-to-tasks",
        temperature=0.0,
        max_tokens=512,
    )
    if result.parsed is None:
        return f"无法解析响应。原始输出：\n{result.text}"
    lines = [f"- [{t.get('owner') or '?'}] {t['action']}" for t in result.parsed["tasks"]]
    return "\n".join(lines) or "(未找到任务)"
```

第三个包含图片输入的完整示例位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) 仓库中（参考插件的配套仓库——不随 hermes-agent 本身打包）。关于异步接口（使用 `asyncio.gather()` 的 `acomplete()` / `acomplete_structured()`），请参见同一仓库中的 [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example)。
<a id="when-to-use-which"></a>
## 何时使用哪种方法

| 您想要… | 使用 |
|---|---|
| 自由格式文本回复（翻译、摘要、重写、生成） | `complete()` |
| 多轮提示（系统提示 + 少量示例 + 用户输入） | `complete()` |
| 返回类型化字典，并按 schema 校验 | `complete_structured()` |
| 图像或文本输入，返回类型化字典 | `complete_structured()` |
| 从异步代码中调用同一接口（网关适配器、异步钩子） | `acomplete()` / `acomplete_structured()` |

其余一切——提供者选择、模型解析、认证、回退、超时、视觉路由——在这四个方法中完全相同。

<a id="api-surface"></a>
## API 接口

`ctx.llm` 是 `agent.plugin_llm.PluginLlm` 的一个实例。

<a id="complete"></a>
### `complete()`

```python
result = ctx.llm.complete(
    messages=[{"role": "user", "content": "Hi"}],
    provider=None,         # optional, gated — Hermes provider id (e.g. "openrouter")
    model=None,            # optional, gated — whatever string that provider expects
    temperature=None,
    max_tokens=None,
    timeout=None,          # seconds
    agent_id=None,         # optional, gated
    profile=None,          # optional, gated — explicit auth-profile name
    purpose="optional-audit-string",
)
# → PluginLlmCompleteResult(text, provider, model, agent_id, usage, audit)
```

普通对话补全。`messages` 采用标准 OpenAI 格式——由多个 `{"role": "...", "content": "..."}` 字典构成的列表。多轮提示（系统提示 + 少量用户/助手示例对 + 最终用户输入）与直接使用 OpenAI SDK 时的行为完全一致。

`provider=` 和 `model=` 相互独立，且与宿主主配置（`model.provider` + `model.model`）具有相同的格式。仅设置 `model=` 时，使用用户当前激活的提供者，但更换其模型。同时设置两者则完全切换提供者。未获操作员授权擅自设置任一参数都会引发 `PluginLlmTrustError`。

<a id="completestructured"></a>
### `complete_structured()`

```python
result = ctx.llm.complete_structured(
    instructions="What you want extracted.",
    input=[
        {"type": "text",  "text": "..."},
        {"type": "image", "data": b"...", "mime_type": "image/png"},
        {"type": "image", "url":  "https://..."},
    ],
    json_schema={...},     # optional — triggers parsed result + validation
    json_mode=False,       # set True without a schema to ask for JSON anyway
    schema_name=None,      # optional human-readable schema name
    system_prompt=None,
    provider=None,         # optional, gated
    model=None,            # optional, gated
    temperature=None,
    max_tokens=None,
    timeout=None,
    agent_id=None,
    profile=None,
    purpose=None,
)
# → PluginLlmStructuredResult(text, provider, model, agent_id,
#                             usage, parsed, content_type, audit)
```

输入类型为文本或图像块（原始字节会自动以 base64 编码为 `data:` URL）。当提供 `json_schema` 或设置 `json_mode=True` 时，宿主通过 `response_format` 请求 JSON 输出，并在本地作为后备进行解析；如果安装了 `jsonschema` 库，还会根据你提供的 schema 进行校验。
* `result.content_type == "json"` — `result.parsed` 是一个符合你定义的 schema 的 Python 对象。
* `result.content_type == "text"` — 解析或验证失败；请检查 `result.text` 获取原始模型响应。

<a id="async"></a>
### 异步

```python
result = await ctx.llm.acomplete(messages=...)
result = await ctx.llm.acomplete_structured(instructions=..., input=...)
```

参数和返回类型与同步版本相同。在网关适配器、异步钩子或任何已在 asyncio 循环上运行的插件代码中使用。

<a id="result-attributes"></a>
### 返回属性

```python
@dataclass
class PluginLlmCompleteResult:
    text: str                    # 助手的响应
    provider: str                # 例如 "openrouter", "anthropic"
    model: str                   # 提供商为此调用返回的模型名称
    agent_id: str                # 使用了哪个 Agent 的模型/认证
    usage: PluginLlmUsage        # token 数 + 缓存 + 费用估算
    audit: Dict[str, Any]        # plugin_id, purpose, profile

@dataclass
class PluginLlmStructuredResult(PluginLlmCompleteResult):
    parsed: Optional[Any]        # 当 content_type == "json" 时的 JSON 对象
    content_type: str            # "json" 或 "text"
    # audit 中还包含 schema_name（如果提供了）
```

当提供商返回这些字段时，`usage` 包含 `input_tokens`、`output_tokens`、`total_tokens`、`cache_read_tokens`、`cache_write_tokens` 和 `cost_usd`。

<a id="trust-gate"></a>
## 信任门控

默认行为是失败时关闭。如果没有 `plugins.entries` 配置块，插件可以：

* 针对用户当前激活的提供商和模型，运行四个方法中的任意一个；
* 设置请求塑形参数（`temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`）；

……仅此而已。在操作员选择加入之前，`provider=`、`model=`、`agent_id=` 和 `profile=` 参数会抛出 `PluginLlmTrustError`。

**大多数插件不需要这一节。** 只调用 `ctx.llm.complete(messages=...)` 且不带任何覆盖参数的插件，将使用用户当前激活的配置运行，无需任何配置。下面的配置块仅适用于插件想要明确指定与用户不同的模型或提供商的情况。

```yaml
plugins:
  entries:
    my-plugin:
      llm:
        # 允许此插件选择不同的 Hermes 提供商
        # （必须是 Hermes 已知的提供商——与 `hermes model` 和 config.yaml model.provider 中的名称相同）
        allow_provider_override: true

        # 可选地限制允许的提供商。使用 ["*"] 表示任意。
        allowed_providers:
          - openrouter
          - anthropic

        # 允许此插件请求特定的模型。
        allow_model_override: true

        # 可选地限制允许的模型。使用 ["*"] 表示任意。
        # 模型名称会与插件发送的字符串进行精确匹配——Hermes 不会进行查找。
        allowed_models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-5-haiku

        # 允许跨 Agent 调用（很少见）。
        allow_agent_id_override: false

        # 允许插件请求特定的存储认证配置（例如，同一提供商上的不同 OAuth 账户）。
        allow_profile_override: false
```
插件 ID 是扁平插件的清单 `name:` 字段，或是嵌套插件（如 `image_gen/openai`、`memory/honcho` 等）的路径派生键。

<a id="what-the-gate-enforces"></a>
### 门控机制强制的内容

| 覆盖项           | 默认值   | 配置键                              |
| ---------------- | -------- | ----------------------------------- |
| `provider=`      | 拒绝     | `allow_provider_override: true`     |
| ↳ 允许列表       | —        | `allowed_providers: [...]`          |
| `model=`         | 拒绝     | `allow_model_override: true`        |
| ↳ 允许列表       | —        | `allowed_models: [...]`             |
| `agent_id=`      | 拒绝     | `allow_agent_id_override: true`     |
| `profile=`       | 拒绝     | `allow_profile_override: true`      |

每个覆盖项都是独立门控的。授予 `allow_model_override` **不会**同时授予 `allow_provider_override`——一个被信任可以选择模型的插件，仍然会被限制在用户的当前提供商上，除非它也获得了提供商门控权限。

<a id="what-the-gate-does-not-need-to-enforce"></a>
### 门控机制不需要强制的内容

* 请求塑形参数——`temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`、`schema_name`、`json_mode`——始终允许；它们不涉及凭证或路由选择。
* 默认拒绝策略意味着一个未配置的插件仍然可以执行有用的工作——它只是使用当前激活的提供商和模型运行。操作员只需要为那些希望进行更精细路由的插件考虑 `plugins.entries` 配置。

<a id="what-the-host-owns"></a>
## 宿主负责的内容

以下是 `ctx.llm` 为插件所做工作的完整列表，这样你就不必自己处理了：

* **提供商解析。** 从用户配置中读取 `model.provider` + `model.model`（或在受信任时使用显式覆盖项）。
* **认证。** 从 `~/.hermes/auth.json` / 环境变量中拉取 API 密钥、OAuth 令牌或刷新令牌，包括配置了凭证池时的情况。插件永远不会看到它们。
* **视觉路由。** 当提供了图像输入且用户当前激活的文本模型仅支持文本时，宿主会自动回退到配置的视觉模型。
* **回退链。** 如果用户的主提供商返回 5xx 或 429 错误，请求会在向插件返回错误之前，先经过 Hermes 常规的聚合器感知回退机制。
* **超时。** 遵循你的 `timeout=` 参数，回退到 `auxiliary.&lt;task&gt;.timeout` 配置或全局辅助默认值。
* **JSON 塑形。** 当你请求 JSON 时，向提供商发送 `response_format`，然后如果提供商返回了代码围栏响应，则在本地重新解析。
* **Schema 验证。** 当安装了 `jsonschema` 时，根据你的 `json_schema` 进行验证；否则记录一条调试日志并跳过严格验证。
* **审计日志。** 每次调用都会在 `agent.log` 中写入一条 INFO 级别的日志，包含插件 ID、提供商/模型、用途和令牌总数。

<a id="what-the-plugin-owns"></a>
## 插件负责的内容

* **请求形状。** 聊天使用 `messages`，结构化使用 `instructions` + `input`。插件构建提示词；宿主运行它。
* **Schema。** 你希望返回的任何形状。宿主不会为你推断它。
* **错误处理。** `complete_structured()` 在输入为空或 schema 验证失败时抛出 `ValueError`。当门控机制拒绝覆盖项时，会触发 `PluginLlmTrustError`。其他任何情况（提供商 5xx、未配置凭证、超时）都会抛出 `auxiliary_client.call_llm()` 抛出的任何异常。
* **成本。** 每次调用都会消耗用户付费提供商的使用量。不要在每个网关消息上都循环调用 `complete()` 而不考虑令牌消耗。
<a id="where-this-fits-in-the-plugin-surface"></a>
## 这在插件接口中的位置

现有的 `ctx.*` 方法扩展了 Hermes 的某个子系统：

| `ctx.register_tool` | 为 Agent 添加一个可调用的工具 |
| `ctx.register_platform` | 接入新的网关适配器 |
| `ctx.register_image_gen_provider` | 替换图像生成后端 |
| `ctx.register_memory_provider` | 替换内存后端 |
| `ctx.register_context_engine` | 替换上下文压缩器 |
| `ctx.register_hook` | 观察生命周期事件 |

`ctx.llm` 是第一个让插件能够运行用户正在与之对话的同一模型的接口，且是**带外**（out of band）的，不需要以上任何组件。这就是它唯一的工作。如果你的插件需要注册一个 Agent 调用的工具，请使用 `register_tool`；如果需要响应某个生命周期事件，请使用 `register_hook`；如果需要自行发起模型调用——无论是否结构化——请使用 `ctx.llm`。

<a id="reference"></a>
## 参考

* 实现：[`agent/plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/plugin_llm.py)
* 测试：[`tests/agent/test_plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_plugin_llm.py)
* 参考插件（配套仓库）：
  * [`plugin-llm-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) — 同步结构化提取（带图像输入）
  * [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example) — 使用 `asyncio.gather()` 的异步示例
* 辅助客户端（底层引擎）：参见 [Provider Runtime](/developer-guide/provider-runtime)。
