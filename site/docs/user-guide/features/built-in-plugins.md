---
sidebar_position: 12
sidebar_label: "内置插件"
title: "内置插件"
description: "Hermes Agent 随附的插件，通过生命周期钩子自动运行——包括磁盘清理等"
---

<a id="built-in-plugins"></a>
# 内置插件

Hermes 附带了一小组与仓库捆绑的插件。它们位于 `&lt;repo&gt;/plugins/&lt;name&gt;/` 目录下，并与用户安装在 `~/.hermes/plugins/` 中的插件一起自动加载。它们使用与第三方插件相同的插件接口——钩子、工具、斜杠命令——只是维护在仓库内部。

关于通用插件系统的介绍，请参阅[插件](/user-guide/features/plugins)页面；要编写自己的插件，请参考[构建 Hermes 插件](/guides/build-a-hermes-plugin)。

<a id="how-discovery-works"></a>
## 发现机制

`PluginManager` 按顺序扫描四个来源：

1. **捆绑** — `&lt;repo&gt;/plugins/&lt;name&gt;/`（本文档所介绍的内容）
2. **用户** — `~/.hermes/plugins/&lt;name&gt;/`
3. **项目** — `./.hermes/plugins/&lt;name&gt;/`（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4. **Pip 入口点** — `hermes_agent.plugins`

当名称冲突时，后发现的来源会覆盖先发现的——例如，一个名为 `disk-cleanup` 的用户插件会替换掉同名的捆绑插件。

`plugins/memory/` 和 `plugins/context_engine/` 被有意排除在捆绑扫描之外。这些目录使用它们自己的发现路径，因为记忆提供者和上下文引擎是通过 `hermes memory setup` 或配置中的 `context.engine` 进行配置的单选提供者。

<a id="bundled-plugins-are-opt-in"></a>
## 捆绑插件默认不启用

捆绑插件默认是禁用的。发现机制会找到它们（它们会出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中），但在你明确启用之前，它们都不会加载：

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml` 配置：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这与用户安装插件的机制相同。捆绑插件永远不会自动启用——无论是全新安装，还是现有用户升级到更新的 Hermes 版本。你总是需要明确选择启用。

要再次关闭某个捆绑插件：

```bash
hermes plugins disable disk-cleanup
# 或者：从 config.yaml 的 plugins.enabled 中移除它
```

<a id="currently-shipped"></a>
## 当前随附的插件

仓库在 `plugins/` 目录下提供了以下捆绑插件。所有插件都需要手动启用——通过 `hermes plugins enable <名称>` 来启用。

| 插件 | 类型 | 用途 |
|---|---|---|
| `disk-cleanup` | 钩子 + 斜杠命令 | 自动追踪临时文件并在会话结束时清理 |
| `observability/langfuse` | 钩子 | 将对话轮次/LLM 调用/工具追踪到 [Langfuse](https://langfuse.com) |
| `spotify` | 后端（7 个工具） | 原生 Spotify 播放、队列、搜索、歌单、专辑、音乐库 |
| `google_meet` | 独立 | 加入 Meet 通话、实时字幕转录、可选的实时双工音频 |
| `image_gen/openai` | 图像后端 | OpenAI `gpt-image-2` 图像生成后端（FAL 的替代方案） |
| `image_gen/openai-codex` | 图像后端 | 通过 Codex OAuth 进行 OpenAI 图像生成 |
| `image_gen/xai` | 图像后端 | xAI `grok-2-image` 后端 |
| `hermes-achievements` | 仪表盘标签页 | 基于你真实的 Hermes 会话历史生成的 Steam 风格可收集徽章 |
| `kanban/dashboard` | 仪表盘标签页 | 用于多 Agent 调度器的看板 UI——任务、评论、扇出、看板切换。请参阅[看板多 Agent](./kanban.md)。 |
<a id="disk-cleanup"></a>
### disk-cleanup

自动追踪并移除会话期间产生的临时文件——测试脚本、临时输出、cron 日志、过期的 Chrome 配置文件——无需 Agent 记得调用某个工具。

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 在 `HERMES_HOME` 或 `/tmp/hermes-*` 内创建了匹配 `test_*`、`tmp_*` 或 `*.test.*` 的文件时，静默将其追踪为 `test` / `temp` / `cron-output`。 |
| `on_session_end` | 如果在该轮对话中自动追踪了任何测试文件，则执行安全的 `quick` 清理并记录一行摘要。否则保持静默。 |

**删除规则：**

| 类别 | 阈值 | 确认 |
|---|---|---|
| `test` | 每次会话结束 | 从不 |
| `temp` | 追踪后超过 7 天 | 从不 |
| `cron-output` | 追踪后超过 14 天 | 从不 |
| HERMES_HOME 下的空目录 | 始终 | 从不 |
| `research` | 超过 30 天，且超出最新的 10 个 | 始终（仅 deep 模式） |
| `chrome-profile` | 追踪后超过 14 天 | 始终（仅 deep 模式） |
| 大于 500 MB 的文件 | 从不自动 | 始终（仅 deep 模式） |

**斜杠命令** — `/disk-cleanup` 在 CLI 和 gateway 会话中均可使用：

```
/disk-cleanup status                     # 分类统计 + 最大的 10 个文件
/disk-cleanup dry-run                    # 预览但不删除
/disk-cleanup quick                      # 立即执行安全清理
/disk-cleanup deep                       # quick + 列出需要确认的项目
/disk-cleanup track <path> <category>    # 手动追踪
/disk-cleanup forget <path>              # 停止追踪（不删除文件）
```

**状态** — 所有数据存放在 `$HERMES_HOME/disk-cleanup/` 目录下：

| 文件 | 内容 |
|---|---|
| `tracked.json` | 被追踪的路径，包含类别、大小和时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 仅追加的审计日志，记录每次追踪/跳过/拒绝/删除操作 |

**安全性** — 清理操作仅触及 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径。Windows 挂载点（`/mnt/c/...`）会被拒绝。已知的顶级状态目录（`logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/`、`plugins/`、`disk-cleanup/` 自身）即使为空也永远不会被删除——新安装的环境不会在第一次会话结束时被清空。

**启用：** `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 中勾选）。

**再次禁用：** `hermes plugins disable disk-cleanup`。

<a id="observability-langfuse"></a>
### observability/langfuse {#observabilitylangfuse}

将 Hermes 的对话轮次、LLM 调用和工具调用追踪到 [Langfuse](https://langfuse.com)——一个开源的 LLM 可观测性平台。每个轮次一个 span，每个 API 调用一个 generation，每个工具调用一个 tool observation。使用量统计、按类型划分的 token 计数和成本估算均来自 Hermes 标准的 `agent.usage_pricing` 数据，因此 Langfuse 仪表盘上看到的分类（input / output / `cache_read_input_tokens` / `cache_creation_input_tokens` / `reasoning_tokens`）与 `hermes logs` 中显示的一致。
该插件采用故障开放策略：即使未安装 SDK、缺少凭据或 Langfuse 出现瞬时错误，所有钩子都会静默无操作，不会影响 agent loop。

**设置：**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

或者在交互式 `hermes plugins` 界面中勾选。然后将凭据放入 `~/.hermes/.env`：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # 或你的自托管 URL
```

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或复用）每个回合的根 span "Hermes turn"。为此次 API 调用启动一个 `generation` 子观察，并将最近的序列化消息作为输入。 |
| `post_api_request` / `post_llm_call` | 关闭 generation，附上 `usage_details`、`cost_details`、`finish_reason`、助手输出和工具调用。如果没有工具调用且内容非空，则关闭该回合。 |
| `pre_tool_call` | 启动一个 `tool` 子观察，附带清理后的 `args`。 |
| `post_tool_call` | 关闭工具观察，附带清理后的 `result`。`read_file` 的载荷会被摘要（显示头尾和省略行数），从而确保读取大文件时不超过 `HERMES_LANGFUSE_MAX_CHARS`。 |

会话分组通过 `langfuse.propagate_attributes` 以 Hermes 会话 ID（或子 Agents 的任务 ID）为键，因此单个 `hermes chat` 会话中的所有内容都在同一个 Langfuse 会话下。

**验证：**

```bash
hermes plugins list                 # observability/langfuse 应显示 "enabled"
hermes chat -q "hello"              # 在 Langfuse UI 中查看 "Hermes turn" 追踪
```

**可选调优**（在 `.env` 中）：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 追踪的环境标签（`production`、`staging`等） |
| `HERMES_LANGFUSE_RELEASE` | — | 发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容/工具参数/工具结果的每字段截断长度 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 详细插件日志，写入 `agent.log` |

以 Hermes 为前缀的变量和标准 SDK 环境变量（`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）均可使用——两者同时设置时，以 Hermes 前缀的为准。

**性能：** Langfuse 客户端在第一次钩子调用后会被缓存。如果缺少凭据或 SDK，该判断也会被缓存——后续的钩子会快速返回，无需重新检查环境变量或重载配置。

**禁用：** `hermes plugins disable observability/langfuse`。插件模块仍会被发现，但模块代码不会运行，直到你重新启用。

<a id="googlemeet"></a>
### google_meet

让 Agent 能够 **加入、转录并参与 Google Meet 通话**——记录会议内容、会后总结讨论、跟进具体要点，并且（可选地）通过 TTS 将回复语音播报回通话中。

**新增功能：**

- 一个无头虚拟参与者，使用浏览器自动化加入 Meet 链接
- 通过配置的 STT 提供者实时转录会议音频
- 一套 `meet_summarize` / `meet_speak` / `meet_followup` 工具集，Agent 在听到内容后调用以执行操作
- 会后产物（转录文本、带说话人标注的笔记、行动项）保存至 `~/.hermes/cache/google_meet/&lt;meeting_id&gt;/`
**设置：**

```bash
hermes plugins enable google_meet
# 首次使用时，插件会提示通过 OAuth 流程登录 ——
# 需要一个拥有 Meet 访问权限的 Google 账号。如果会议启用了“仅限受邀参与者加入”，则可能需要主持人批准。
```

在聊天中使用：

> “加入 meet.google.com/abc-defg-hij 并做笔记。通话结束后，给我发送一份包含待办事项的摘要。”

Agent 会启动加入会议，随着通话进行将转录内容流式传输回其上下文，并在会议结束时（或你让它停止时）生成一份结构化的摘要。

**适用场景：** 定期的每日站会，希望机器人为你转录并总结，方便异步参会者；类似取证式的访谈，需要结构化笔记；任何原本需要使用 Fireflies / Otter / Grain 的场景。如果你不希望 AI 旁听，就不要启用。

**禁用：** `hermes plugins disable google_meet`。任何缓存的转录内容和录音会保留在 `~/.hermes/cache/google_meet/` 中，直到你手动删除它们。

<a id="hermes-achievements"></a>
### hermes-achievements

在仪表盘中添加了一个 **Steam 风格的成就标签页** —— 基于你的真实 Hermes 会话历史生成的 60 多个可收集的分层徽章。涵盖工具链成就、调试模式、编程心流连击、技能/内存使用、模型/提供者多样性、生活习惯（周末和夜间会话）。最初由 [@PCinkusz](https://github.com/PCinkusz) 作为外部插件编写；后被纳入主代码库，以便与 Hermes 特性变化保持同步。

**工作原理：**

- 在仪表盘后端扫描你的整个 `~/.hermes/state.db` 会话历史
- 每个会话的统计数据会按 `(started_at, last_active)` 指纹进行缓存，因此后续扫描时只会重新分析新的或发生变化的会话
- 首次扫描会在后台线程中进行 —— 仪表盘不会阻塞等待，即便数据库中有数千个会话也如此
- 解锁状态持久化到 `$HERMES_HOME/plugins/hermes-achievements/state.json`

**等级递进：** 铜 → 银 → 金 → 钻石 → 奥林匹斯。每张卡片都显示一个“计数依据”部分，列出所追踪的具体指标。

**成就状态：**

| 状态 | 含义 |
|---|---|
| 已解锁 | 至少达成一个等级 |
| 已发现 | 已知成就，进度可见，但尚未获得 |
| 秘密 | 隐藏，直到 Hermes 在你的历史中检测到首个相关信号 |

**API** — 路由挂载在 `/api/plugins/hermes-achievements/` 下：

| 端点 | 用途 |
|---|---|
| `GET /achievements` | 完整目录及每个徽章的解锁状态（首次冷扫描进行时返回一个 pending 占位符） |
| `GET /scan-status` | 后台扫描器的状态：`idle` / `running` / `failed`，最近一次持续时间，运行次数 |
| `GET /recent-unlocks` | 最近解锁的二十个徽章，最新排在最前 |
| `GET /sessions/{id}/badges` | 主要在某个特定会话中获得的徽章 |
| `POST /rescan` | 手动同步重新扫描（会阻塞；当用户点击重新扫描按钮时使用） |
| `POST /reset-state` | 清除解锁历史和缓存的快照 |
**State files** — 位于 `$HERMES_HOME/plugins/hermes-achievements/` 下：

| 文件 | 内容 |
|---|---|
| `state.json` | 解锁历史：你获得了哪些徽章以及获得时间。在 Hermes 更新中保持稳定。 |
| `scan_snapshot.json` | 上次完成的扫描负载（仪表盘加载时立即提供） |
| `scan_checkpoint.json` | 按指纹（fingerprint）键控的每会话统计缓存（使热重扫速度更快） |

**性能说明：**

- 对约 8,000 个会话进行冷扫描需要几分钟。它会在首次仪表盘请求时在后台线程中运行；UI 会显示一个待办占位符，并轮询 `/scan-status`。
- **冷扫描期间的增量结果** — 扫描器大约每 250 个会话发布一次部分快照，因此每次仪表盘刷新都会显示更多已解锁的徽章，无需长时间盯着零。
- 热重扫会复用每个会话的统计信息（其 `started_at` + `last_active` 指纹与检查点匹配）——即使历史数据量很大，也能在几秒内完成。
- 内存快照 TTL 为 120 秒；过期请求会立即提供旧快照并触发后台刷新。你永远不需要因为 TTL 过期而等待旋转动画。

**启用：** 无需启用——`hermes-achievements` 是一个纯仪表盘插件（没有生命周期钩子，没有模型可见工具）。它会在首次启动时自动注册为 `hermes dashboard` 中的一个标签。`plugins.enabled` 配置仅控制生命周期/工具插件；仪表盘插件完全通过其 `dashboard/manifest.json` 发现。

**选择退出：** 删除或重命名 `plugins/hermes-achievements/dashboard/manifest.json`，或者在 `~/.hermes/plugins/hermes-achievements/` 中使用同名且不提供仪表盘的用户插件覆盖它。该插件在 `$HERMES_HOME/plugins/hermes-achievements/` 下的状态文件会保留——重新安装可保留你的解锁历史。

<a id="adding-a-bundled-plugin"></a>
## 添加内置插件

内置插件的编写方式与任何其他 Hermes 插件完全相同——请参阅[构建一个 Hermes 插件](/guides/build-a-hermes-plugin)。唯一区别是：

- 目录位于 `&lt;repo&gt;/plugins/&lt;name&gt;/` 而不是 `~/.hermes/plugins/&lt;name&gt;/`
- 在 `hermes plugins list` 中，清单源报告为 `bundled`
- 同名的用户插件会覆盖内置版本

满足以下条件时，插件适合内置：

- 没有可选依赖项（或者它们已经是 `pip install .[all]` 的依赖项）
- 该行为对大多数用户有益，且是选择退出（opt-out）而非选择加入（opt-in）
- 其逻辑涉及生命周期钩子，否则 agent 需要记得手动调用
- 它补充了核心能力，而没有扩大模型可见的工具表面

反例——应保持为用户可安装插件而非内置的：需要 API 密钥的第三方集成、小众工作流、大型依赖树、以及任何会默认显著改变 agent 行为的东西。
