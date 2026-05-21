---
title: Codex App-Server Runtime（可选）
sidebar_label: Codex App-Server Runtime
---

<a id="codex-app-server-runtime"></a>
# Codex App-Server Runtime

Hermes 可以选择将 `openai/*` 和 `openai-codex/*` 轮次交给 [Codex CLI app-server](https://github.com/openai/codex) 处理，而不是运行自己的工具循环。启用后，终端命令、文件编辑、沙箱和 MCP 工具调用都在 Codex 的运行时中执行——Hermes 则成为其外围壳层（会话数据库、斜杠命令、网关、记忆和技能审查）。

这是**仅限主动启用**的功能。除非你手动开启标志，否则 Hermes 的默认行为保持不变。Hermes 不会自动将你路由到这个运行时。

<a id="why"></a>
## 为什么使用

- 使用与 Codex CLI 相同的认证流程，通过你的 **ChatGPT 订阅**（无需 API 密钥）运行 OpenAI Agent 轮次。
- 使用 **Codex 自带的工具集和沙箱**——`shell` 用于终端/读/写/搜索，`apply_patch` 用于结构化编辑，`update_plan` 用于规划，所有操作都在 seatbelt/landlock 沙箱中运行。
- **原生 Codex 插件**——Linear、GitHub、Gmail、Calendar、Canva 等——通过 `codex plugin` 安装后会自动迁移并在你的 Hermes 会话中生效。
- **Hermes 更丰富的工具也会一起工作**——web_search、web_extract、浏览器自动化、视觉、图像生成、技能和 TTS 通过 MCP 回调工作。Codex 会回调 Hermes 来使用它没有内置的工具。
- **记忆和技能提示持续生效**——Codex 的事件会被映射到 Hermes 的消息格式中，因此自我改进循环看到的是一份正常的对话记录。

<a id="what-tools-the-model-actually-has"></a>
## 模型实际拥有的工具

这是大多数用户最想提前了解的部分。当此运行时启用时，运行你轮次的模型拥有三个独立的工具来源：

<a id="1-codex-s-built-in-toolset-always-on"></a>
### 1. Codex 内置工具集（始终启用）

这些工具随 `codex app-server` 本身一起提供——无需 Hermes 参与，无需 MCP，无需插件。运行时启动后，所有五个工具立即可用：

- **`shell`**——在沙箱内运行任意 shell 命令。模型通过它读取文件（`cat`、`head`、`tail`）、写入文件（`echo > foo`、heredocs）、搜索文件（`find`、`rg`、`grep`）、浏览目录（`ls`、`cd`）、运行构建、管理进程，以及你在 bash 中能做的任何其他操作。
- **`apply_patch`**——以 Codex 的补丁格式应用结构化的多文件差异。模型用它进行非平凡的代码编辑（添加函数、跨文件重构）；单次写入仍可使用 shell heredocs。
- **`update_plan`**——Codex 的内部待办/计划跟踪器。相当于 Hermes 的 `todo` 工具，但完全在 Codex 运行时内部管理。
- **`view_image`**——将本地图像文件加载到对话中，以便模型查看。
- **`web_search`**——配置后，Codex 拥有自己的内置网络搜索。Hermes 也通过下面的回调暴露了 `web_search`（基于 Firecrawl）；模型会选择它更偏好的那个。

因此，**任何你通过终端做的事情——读/写/搜索/查找/运行——Codex 都能原生完成**。沙箱配置文件（启用运行时后默认为 `:workspace`）控制哪些内容可写。

<a id="2-native-codex-plugins-auto-migrated-from-your-codex-plugin-install"></a>
### 2. 原生 Codex 插件（从你的 `codex plugin` 安装自动迁移）
当你启用运行时，Hermes 会查询 codex 的 `plugin/list` RPC，并为每个已安装的插件写入一个 `[plugins."&lt;name&gt;@openai-curated"]` 条目。插件本身由 codex 管理，并需通过 codex 自身的 UI 授权一次。

示例（OpenClaw 帖子里标注为“值得上YouTube”的那些）：

- **Linear** — 查找/更新 issue
- **GitHub** — 搜索代码、查看 PR、评论
- **Gmail** — 读取/发送邮件
- **Google Calendar** — 创建/查找事件
- **Outlook 日历/邮件** — 通过 Microsoft 连接器实现相同功能
- **Canva** — 设计生成
- ……以及通过 `codex plugin marketplace add openai-curated` + `codex plugin install ...` 安装的其他插件

**不会迁移的内容：**
- 你尚未安装的插件 — 先在 Codex 中安装它们。
- ChatGPT 应用市场条目（`app/list`）— 由于你的账户认证，这些已通过 codex 内启用。

<a id="3-hermes-tool-callback-mcp-server-registered-in-codex-config-toml"></a>
### 3. Hermes 工具回调（MCP 服务端，注册在 `~/.codex/config.toml` 中）

Hermes 将自己注册为一个 MCP 服务端，以便 codex 可以回调那些 codex 本身不内置的工具。通过回调可用的工具：

- **`web_search`** / **`web_extract`** — 基于 Firecrawl；对于结构化内容通常比直接抓取更干净。
- **`browser_navigate` / `browser_click` / `browser_type` / `browser_press` / `browser_snapshot` / `browser_scroll` / `browser_back` / `browser_get_images` / `browser_console` / `browser_vision`** — 通过 Camofox 或 Browserbase 实现的完整浏览器自动化。
- **`vision_analyze`** — 调用单独的视觉模型检查图像（与 codex 的 `view_image` 不同，后者将图像加载到对话中）。
- **`image_generate`** — 通过 Hermes 的 image_gen 插件链进行图像生成。
- **`skill_view` / `skills_list`** — 从 Hermes 的技能库中读取。
- **`text_to_speech`** — 通过 Hermes 配置的提供商进行 TTS。

当模型需要这些工具之一时，codex 通过 stdio MCP 生成 `hermes_tools_mcp_server` 子进程，调用通过 `model_tools.handle_function_call()` 分发（与 Hermes 默认运行时相同的代码路径），结果像任何其他 MCP 响应一样返回给 codex。

<a id="what-s-not-available-on-this-runtime"></a>
### 此运行时上不可用的功能

以下四个 Hermes 工具需要正在运行的 AIAgent 上下文（中间循环状态）来分发，而无状态的 MCP 回调无法驱动它们。当你需要其中任何一个时，请切换回默认运行时（`/codex-runtime auto`）：

- **`delegate_task`** — 生成子 Agent（subagents）
- **`memory`** — Hermes 的持久化记忆存储
- **`session_search`** — 跨会话搜索
- **`todo`** — Hermes 的待办事项存储（codex 的 `update_plan` 是运行时内的等价功能）

<a id="workflow-features-goal-kanban-cron"></a>
## 工作流功能（`/goal`、看板、cron）

<a id="goal-the-ralph-loop"></a>
### `/goal`（Ralph 循环）

**此运行时可用。** Goal 通过 `state_meta` 以会话 ID 为键持久化，继续提示通过 `run_conversation()` 作为普通用户消息反馈，codex 原生执行下一步。目标评判器通过辅助客户端运行（在 config.yaml 中通过 `auxiliary.goal_judge` 配置），与当前运行哪个运行时无关。如果 codex 在审批上卡住，评判器的“已阻塞，需要用户输入”裁决是一个干净的退出方式。
**需要注意的一点是：** 每次续写提示（continuation prompt）都是一个全新的 codex 回合，这意味着 codex 会从头重新评估命令审批策略。如果你正在执行一个包含大量写入操作的长周期目标，那么你会看到比单次会话任务更多的审批提示。请设置 `default_permissions = ":workspace"`（当你启用运行时，Hermes 会自动执行此操作），这样简单的工作区写入就不需要提示了。

<a id="kanban-multi-agent-worktree-dispatch"></a>
### 看板（多 Agent 工作树分发）

**在此运行时上可用，但有一个微妙的依赖关系。** 看板分发器会将每个工作进程作为独立的 `hermes chat -q` 子进程启动，该子进程会读取用户的配置——这意味着如果全局设置了 `model.openai_runtime: codex_app_server`，工作进程也会在 codex 运行时上启动。

在 codex 运行时工作进程内部可用的功能：
- Codex 的完整工具集（shell、apply_patch、update_plan、view_image、web_search）——工作进程原生执行其实际任务
- 已迁移的 codex 插件——Linear、GitHub 等
- 用于 browser_*、vision、image_gen、skills、TTS 的 Hermes 工具回调

由于 MCP 回调暴露了它们，因此也可用的功能：
- **`kanban_complete` / `kanban_block` / `kanban_comment` / `kanban_heartbeat`** ——工作进程交接工具。这些工具会读取环境变量 `HERMES_KANBAN_TASK`（由分发器设置），正确进行访问控制，并写入由 `HERMES_KANBAN_DB` 指定的每个看板的 SQLite 数据库。如果回调中没有这些工具，此运行时上的工作进程可以执行其任务，但无法回传结果，会一直挂起直到分发器超时。
- **`kanban_show` / `kanban_list`** ——工作进程用于检查自身上下文的只读看板查询。
- **`kanban_create` / `kanban_unblock` / `kanban_link`** ——仅编排器可用的操作。适用于在 codex 运行时上运行、需要分发新任务的编排器 Agent。

看板工具由分发器设置的环境变量 `HERMES_KANBAN_TASK` 控制——该变量会传播到 codex 子进程（codex 继承环境变量），并从那里传播到生成的 `hermes-tools` MCP 服务器子进程。因此，这些工具能看到正确的任务 ID 并进行正确的访问控制。对于 Codex 应用服务器工作进程，当存在 `HERMES_KANBAN_TASK` 时，Hermes 还会传递狭窄的应用服务器沙箱覆盖：保留 `workspace-write` 沙箱，将**看板数据库目录以及分发器固定的每个看板路径**添加为额外的可写根目录（`HERMES_KANBAN_WORKSPACES_ROOT`、`HERMES_KANBAN_WORKSPACE`、旧版 `HERMES_KANBAN_ROOT`——去重后，数据库目录优先），并默认保持网络禁用。这避免了脆弱的 `:danger-no-sandbox` 变通方案，同时允许 `kanban_complete` / `kanban_block` 更新看板数据库，**并且**允许工作进程在位于数据库目录之外的工作区挂载点下写入报告/工件（例如，在单独驱动器上的 `/media/.../kanban-workspaces/...`——[问题 #27941](https://github.com/NousResearch/hermes-agent/issues/27941)）。

<a id="cron-jobs"></a>
### 定时任务

**未经过专门测试。** 定时任务通过 `cronjob` → `AIAgent.run_conversation` 运行，与 CLI 使用相同的代码路径。如果定时任务的配置中有 `openai_runtime: codex_app_server`，它将在 codex 上运行。同样的工具可用性规则适用——codex 内置工具 + 插件 + MCP 回调可用，Agent 循环工具（delegate_task、memory、session_search、todo）不可用。如果你的定时任务依赖这些工具，请将定时任务限定在使用默认运行时的配置文件中。
<a id="trade-offs"></a>
## 权衡

|  | Hermes 默认运行时 | Codex app-server（可选） |
|---|---|---|
| `delegate_task` 子 Agent | 支持 | 不支持 — 需要 Agent 循环上下文 |
| `memory`、`session_search`、`todo` | 支持 | 不支持 — 需要 Agent 循环上下文 |
| `web_search`、`web_extract` | 支持 | 支持（通过 MCP 回调） |
| 浏览器自动化（Camofox/Browserbase） | 支持 | 支持（通过 MCP 回调） |
| `vision_analyze`、`image_generate` | 支持 | 支持（通过 MCP 回调） |
| `skill_view`、`skills_list` | 支持 | 支持（通过 MCP 回调） |
| `text_to_speech` | 支持 | 支持（通过 MCP 回调） |
| Codex `shell`（终端/读/写/搜索/查找/运行） | — | 支持（Codex 内置） |
| Codex `apply_patch`（结构化多文件编辑） | — | 支持（Codex 内置） |
| Codex `update_plan`（运行时待办事项） | — | 支持（Codex 内置） |
| Codex `view_image`（将图片加载到对话中） | — | 支持（Codex 内置） |
| Codex 沙箱（seatbelt/landlock、配置文件） | — | 支持（Codex 内置） |
| ChatGPT 订阅认证 | — | 支持（通过 `openai-codex` 提供商） |
| 原生 Codex 插件（Linear、GitHub 等） | — | 支持（自动迁移） |
| 用户 MCP 服务器 | 支持 | 支持（自动迁移到 codex） |
| 记忆 + 技能回顾（后台） | 支持 | 支持（通过项目投影） |
| 多轮对话 | 支持 | 支持 |
| `/goal`（Ralph 循环） | 支持 | 支持 |
| 看板工作者调度 | 支持 | 支持（通过回调） |
| 看板编排工具 | 支持 | 支持（通过回调） |
| 所有网关平台 | 支持 | 支持 |
| 非 OpenAI 提供商 | 支持 | 不适用 — 仅限 OpenAI/Codex 范围 |

<a id="prerequisites"></a>
## 前提条件

1. **已安装 Codex CLI：**
   ```bash
   npm i -g @openai/codex
   codex --version   # 0.130.0 或更新版本
   ```
2. **Codex OAuth 登录。** codex 子进程会读取 `~/.codex/auth.json`。有两种方式可以填充它：
   ```bash
   codex login                  # 将令牌写入 ~/.codex/auth.json
   ```
   Hermes 自己的 `hermes auth login codex` 会写入 `~/.hermes/auth.json` — 那是另一个独立的会话。**如果还没做过，请单独运行 `codex login`**。

3. **（可选）安装你想要的 Codex 插件。** 当你启用运行时，Hermes 会自动迁移你通过 Codex CLI 已安装的精选插件：
   ```bash
   codex plugin marketplace add openai-curated
   # 然后通过 codex 的 TUI，安装 Linear / GitHub / Gmail 等
   ```
   Hermes 会自动发现它们，并将 `[plugins."&lt;name&gt;@openai-curated"]` 条目写入 `~/.codex/config.toml`。

<a id="enabling"></a>
## 启用

在 Hermes 会话中：

```
/codex-runtime codex_app_server
```

该命令会：
- 验证 `codex` CLI 是否已安装（如果未安装，会显示安装提示并阻塞）。
- 将 `model.openai_runtime: codex_app_server` 持久化到你的 config.yaml 中。
- 将用户 MCP 服务器从 `~/.hermes/config.yaml` 迁移到 `~/.codex/config.toml`。
- **发现并迁移已安装的原生 Codex 插件**（Linear、GitHub、Gmail、Calendar、Canva 等），通过查询 Codex 的 `plugin/list` RPC 实现。
- **将 Hermes 自己的工具注册为 MCP 服务器**，以便 codex 子进程可以回调使用 codex 未自带的工具。
- **写入 `default_permissions = ":workspace"`**，这样沙箱允许在工作区内写入，而无需每次操作都提示。
- 告诉你哪些内容已被迁移。**下一次**会话时生效 — 当前缓存的 Agent 会保留之前的运行时，以便提示缓存保持有效。
Synonyms：`/codex-runtime on`、`/codex-runtime off`、`/codex-runtime auto`。

若不修改状态，仅检查当前设置：
```
/codex-runtime
```

你也可以在 `~/.hermes/config.yaml` 中手动设置：
```yaml
model:
  openai_runtime: codex_app_server   # 默认值是 "auto"（即 Hermes runtime）
```

<a id="self-improvement-loop-memory-skill-nudges"></a>
## 自我改进循环（记忆 + 技能提示）

Hermes 的后台自我改进基于计数阈值触发：

- 每 10 条用户提示 → 一个分支 review agent 会查看对话，并决定是否应将某些内容保存到记忆。
- 单轮内每 10 次工具迭代 → 与上同理，但针对技能（`skill_manage` 写入）。

**这两者在 codex runtime 上都能正常工作。** codex 路径会将每个已完成的 `commandExecution` / `fileChange` / `mcpToolCall` / `dynamicToolCall` 条目投射成一个合成的 `assistant tool_call` + `tool` 结果消息，因此当 review 运行时，它看到的格式与默认 Hermes runtime 上看到的完全一致。

两者的连接方式对比如下：

| | 默认运行时 | Codex 运行时 |
|---|---|---|
| `_turns_since_memory` 递增 | 每次用户提示，在 run_conversation 的前置循环中 | 相同代码路径，在早期返回之前 |
| `_iters_since_skill` 递增 | 每次工具迭代（在 chat-completions 循环中） | 通过 `turn.tool_iterations` 在 codex turn 返回后 |
| 记忆触发器（`_turns_since_memory >= _memory_nudge_interval`） | 在前置循环中计算，响应后触发 | 在前置循环中计算，传递给 codex helper |
| 技能触发器（`_iters_since_skill >= _skill_nudge_interval`） | 在循环后计算 | 在 codex turn 后计算 |
| `_spawn_background_review(messages_snapshot=..., review_memory=..., review_skills=...)` | 任一触发条件满足时调用 | 任一触发条件满足时同样调用 |

一个小细节：review 分支本身需要调用 Hermes 的 agent-loop 工具（`memory`、`skill_manage`），而这些工具需要 Hermes 自己的调度。因此，当父 agent 运行在 `codex_app_server` 上时，review 分支会被**降级为 `codex_responses`**——相同的 OAuth 凭证、相同的 `openai-codex` 提供者，但直接与 OpenAI 的 Responses API 通信，这样 Hermes 就掌控了循环，agent-loop 工具也能正常工作。这对用户是不可见的。

最终效果：启用 codex runtime 后，你的记忆和技能提示仍然会像往常一样触发。

<a id="how-approvals-work"></a>
## 审批机制

Codex 在执行命令或应用补丁前会请求批准。这些请求会被转换为 Hermes 标准的“危险命令”提示：

```
╭───────────────────────────────────────╮
│ 危险命令                              │
│                                       │
│ /bin/bash -lc 'echo hello > foo.txt'  │
│                                       │
│ ❯ 1. 允许一次                         │
│   2. 本次会话内允许                    │
│   3. 拒绝                             │
│                                       │
│ Codex 请求在 /your/cwd 中执行          │
╰───────────────────────────────────────╯
```

- **允许一次** → 批准该单个命令。
- **本次会话内允许** → Codex 将不再为类似命令重复请求。
- **拒绝** → 命令被拒绝；Codex 以只读模式继续执行。
对于 `apply_patch`（文件编辑）审批，当 codex 通过对应的 `fileChange` 项提供数据时，Hermes 会显示更改摘要（例如 `1 add, 1 update: /tmp/new.py, /tmp/old.py`）。

<a id="permission-profiles"></a>
## 权限配置文件

Codex 内置了三种权限配置文件：
- `:read-only` — 不允许写入；每个 shell 命令都需要审批
- `:workspace` — 允许在当前工作区内写入，无需提示（启用运行时后 Hermes 的默认配置）
- `:danger-no-sandbox` — 完全没有沙箱（除非你理解其含义，否则不要使用）

你可以在 Hermes 管理的代码块之外，通过 `~/.codex/config.toml` 覆盖默认配置：

```toml
default_permissions = ":read-only"
```

（只要你的覆盖配置位于 `# managed by hermes-agent` 标记之外，Hermes 在重新迁移时会保留你的设置。）

<a id="auxiliary-tasks-and-chatgpt-subscription-token-cost"></a>
## 辅助任务与 ChatGPT 订阅 Token 费用

当此运行时与 `openai-codex` 提供者一起启用时，**辅助任务（标题生成、上下文压缩、视觉自动检测、后台自我改进审查分支）默认也会通过你的 ChatGPT 订阅进行**，因为当没有为特定任务设置覆盖时，Hermes 的辅助客户端会使用主提供者/模型。

这并非 `codex_app_server` 特有的行为——现有的 `codex_responses` 路径也是如此——但在这里更为明显，因为你明确选择了订阅计费方式。

要将特定辅助任务路由到更便宜/不同的模型，请在 `~/.hermes/config.yaml` 中设置显式覆盖：

```yaml
auxiliary:
  title_generation:
    provider: openrouter
    model: google/gemini-3-flash-preview
  context_compression:
    provider: openrouter
    model: google/gemini-3-flash-preview
  vision_detect:
    provider: openrouter
    model: google/gemini-3-flash-preview
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

自我改进审查分支通过 `_current_main_runtime()` 继承主运行时，Hermes 会自动将其从 `codex_app_server` 降级为 `codex_responses`（这样该分支才能实际调用 `memory` 和 `skill_manage`——Hermes 自己的 Agent 循环工具）。除非你将辅助任务路由到其他地方，否则该分支仍然使用你的订阅认证。

<a id="editing-codex-config-toml-safely"></a>
## 安全编辑 `~/.codex/config.toml`

Hermes 将其管理的所有内容包裹在两个标记注释之间：

```toml
# managed by hermes-agent — `hermes codex-runtime migrate` regenerates this section
default_permissions = ":workspace"
[mcp_servers.filesystem]
...
[plugins."github@openai-curated"]
...
# end hermes-agent managed section
```

**该代码块之外**的任何内容都属于你。重新运行迁移（通过 `/codex-runtime codex_app_server` 或在你切换运行时启用时）会替换受管理的代码块，但会原样保留其上方和下方的用户内容。这意味着你可以：

- 添加 Hermes 不知道的自定义 MCP 服务器
- 如果你希望收到提示，将 `default_permissions` 覆盖为 `:read-only`
- 配置 codex 专属选项（模型、提供者、otel 等）
- 在 `[permissions.&lt;name&gt;]` 表中添加用户定义的权限配置文件
管理块内的任何内容在下次迁移时都会被覆盖。如果你需要修改管理块，请提交 issue，我们会添加相应开关。

<a id="multi-profile-multi-tenant-setups"></a>
## 多配置文件 / 多租户设置

默认情况下，无论哪个 Hermes 配置文件处于活动状态，Hermes 都会将 codex 子进程指向 `~/.codex/`。这意味着 `hermes -p work` 和 `hermes -p personal` 共享同一个 Codex 身份认证、插件和配置。对于大多数用户来说，这是正确的行为——它与你直接运行 `codex` CLI 的效果一致。

如果你希望每个配置文件有独立的 Codex 环境（独立的身份认证、独立的已安装插件、独立的配置），请为每个配置文件显式设置 `CODEX_HOME`。最干净的方式是将其指向 `HERMES_HOME` 下的一个目录：

```bash
# 在工作配置文件中，你可以这样包装 hermes：
CODEX_HOME=~/.hermes/profiles/work/codex hermes chat
```

设置 `CODEX_HOME` 后，你需要运行一次 `codex login`，这样 OAuth 令牌就会存放在配置文件作用域的路径下。之后，`hermes -p work` 将在独立的 Codex 状态下运行。

我们没有自动作用域化这个设置，因为移动现有用户的 `~/.codex/` 会导致他们的 Codex CLI 身份认证失效——任何已经运行过 `codex login` 的用户都必须重新认证。选择加入比让用户感到意外更安全。

<a id="home-environment-variable-passthrough"></a>
## HOME 环境变量透传

Hermes 在启动 codex app-server 子进程时**不会**重写 `HOME`（我们使用 `os.environ.copy()` 并仅覆盖 `CODEX_HOME` 和 `RUST_LOG`）。这意味着：

- Codex 通过其 `shell` 工具执行的命令会看到真实的用户 `HOME`，并能正确找到 `~/.gitconfig`、`~/.gh/`、`~/.aws/`、`~/.npmrc` 等。
- Codex 的内部状态通过 `CODEX_HOME`（默认指向 `~/.codex/`）保持隔离。

这与 OpenClaw 在早期实验后确定的边界一致：隔离 Codex 的状态，保留用户的家目录。（参见 openclaw/openclaw#81562。）

<a id="mcp-server-migration"></a>
## MCP 服务器迁移

Hermes 的 `mcp_servers` 配置会自动转换为 Codex 期望的 TOML 格式。每次启用运行时都会执行迁移，并且迁移是幂等的——重新运行会替换管理部分，但保留用户编辑过的 Codex 配置。

转换内容如下：

| Hermes (`config.yaml`) | Codex (`config.toml`) |
|---|---|
| `command` + `args` + `env` | stdio 传输 |
| `url` + `headers` | streamable_http 传输 |
| `timeout` | `tool_timeout_sec` |
| `connect_timeout` | `startup_timeout_sec` |
| `enabled: false` | `enabled = false` |

不迁移的内容：
- Hermes 特有的键，如 `sampling`（Codex 的 MCP 客户端没有对应项——这些会被丢弃，并给出每个服务器的警告）。

<a id="native-codex-plugin-migration"></a>
## 原生 Codex 插件迁移

通过 `codex plugin` 安装的插件（Linear、GitHub、Gmail、Calendar、Canva 等）会通过 Codex 的 `plugin/list` RPC 发现。对于每个 `installed: true` 的插件，Hermes 会写入一个 `[plugins."&lt;name&gt;@openai-curated"]` 块，在 Hermes 会话中启用它。

这意味着：当你的朋友说“我在 Codex CLI 中配置了 Calendar 和 GitHub”并启用 Hermes 的 codex 运行时，Hermes 会自动激活它们。无需重新配置。
**未迁移的内容：**
- 你尚未安装的插件——请先在 Codex 中安装它们。
- Codex 报告 `availability != AVAILABLE`（安装损坏、OAuth 过期、已从市场移除等）的插件。这些会被跳过，以避免写入会在激活时失败的配置。
- ChatGPT 应用市场条目（每个账户的 `app/list` 结果——这些已通过你的账户认证在 Codex 中启用）。
- 插件 OAuth——你只需在 Codex 本身中为每个插件授权一次；Hermes 不会触碰凭证。

<a id="hermes-tool-callback-the-new-mcp-server"></a>
## Hermes 工具回调（新的 MCP 服务器）

Codex 的内置工具集涵盖 shell/文件操作/补丁，但不包含网络搜索、浏览器自动化、视觉、图像生成等功能。为了在 Codex 回合中保持这些功能可用，Hermes 在 `~/.codex/config.toml` 中将自己注册为一个 MCP 服务器：

```toml
[mcp_servers.hermes-tools]
command = "/path/to/python"
args = ["-m", "agent.transports.hermes_tools_mcp_server"]
env = { HERMES_HOME = "/your/.hermes", PYTHONPATH = "...", HERMES_QUIET = "1" }
startup_timeout_sec = 30.0
tool_timeout_sec = 600.0
```

当模型调用 `web_search`（或其他暴露的 Hermes 工具）时，Codex 通过 stdio 生成 `hermes_tools_mcp_server` 子进程，请求通过 `model_tools.handle_function_call()` 分发，结果像任何其他 MCP 响应一样被投射回 Codex。

**通过回调可用的工具：** `web_search`、`web_extract`、`browser_navigate`、`browser_click`、`browser_type`、`browser_press`、`browser_snapshot`、`browser_scroll`、`browser_back`、`browser_get_images`、`browser_console`、`browser_vision`、`vision_analyze`、`image_generate`、`skill_view`、`skills_list`、`text_to_speech`。

**不可用的工具：** `delegate_task`、`memory`、`session_search`、`todo`。这些需要正在运行的 AIAgent 上下文来分发（循环中间状态），而无状态的 MCP 回调无法驱动它们。当你需要这些时，请使用默认的 Hermes 运行时（`/codex-runtime auto`）。

<a id="disabling"></a>
## 禁用

随时切换回来：

```
/codex-runtime auto
```

在下一个会话中生效。Codex 管理的块会保留在 `~/.codex/config.toml` 中，这样你以后可以重新启用而无需丢失配置——或者如果你愿意，也可以手动删除它。

<a id="limitations"></a>
## 限制

此运行时是**选择加入的测试版**。截至 Hermes Agent 2026.5 + Codex CLI 0.130.0 版本，以下功能正常工作：

- 多轮对话
- 通过 Hermes UI 批准 `commandExecution` 和 `fileChange`（apply_patch）
- MCP 工具调用（已验证与 `@modelcontextprotocol/server-filesystem` 和新的 `hermes-tools` 回调兼容）
- 原生 Codex 插件迁移（已验证与 Linear / GitHub / Calendar 清单兼容）
- 拒绝/取消路径
- 开关循环
- 记忆和技能提示计数器（已通过集成测试实时验证）
- 通过 Codex 的 Hermes web_search（已实时验证："OpenAI Codex CLI – Getting Started" 端到端返回）

已知限制：

- **Hermes 认证和 Codex 认证是独立的会话。** 你需要同时执行 `codex login` 和 `hermes auth login codex` 才能获得最干净的体验（运行时使用 Codex 的会话进行 LLM 调用）。这是 Hermes 在 `_import_codex_cli_tokens` 中的有意设计选择——Hermes 不会与 Codex CLI 共享 OAuth 状态，以避免在令牌刷新时相互覆盖。
- **`delegate_task`、`memory`、`session_search`、`todo` 在此运行时上不可用。** 它们需要正在运行的 AIAgent 上下文，而无状态的 MCP 回调无法提供。当你需要这些时，请使用 `/codex-runtime auto`。
- **当 Codex 不跟踪变更集时，批准提示中没有内联补丁预览。** Codex 的 `fileChange` 批准参数并不总是携带变更集。Hermes 会在可能时缓存来自相应 `item/started` 通知的数据，但如果批准在项目流式传输之前到达，提示会回退到 Codex 提供的任何 `reason`。
- **亚秒级取消无法保证。** 流中中断（在 Codex 响应时按 Ctrl+C）通过 `turn/interrupt` 发送，但如果 Codex 已经刷新了最终消息，你仍然会收到响应。
如果你发现了 bug，请附上 `hermes logs --since 5m` 的输出[提交一个 issue](https://github.com/NousResearch/hermes-agent/issues)。在标题中注明 `codex-runtime`，以便于分类处理。

<a id="architecture"></a>
## 架构

```
                ┌─── Hermes shell (CLI / TUI / gateway) ───┐
                │  sessions DB · slash commands · memory   │
                │  & skill review · cron · session pickers │
                └──┬──────────────────────────────────────┬┘
                   │ user_message               final     │
                   ▼                            text +    │
        ┌──────────────────────────────────┐   projected  │
        │  AIAgent.run_conversation()       │   messages   │
        │   if api_mode == codex_app_server │              │
        │     → CodexAppServerSession       │              │
        │   else: chat_completions / codex_responses (default)
        └────┬─────────────────────────────┘              │
             │ JSON-RPC over stdio                        │
             ▼                                            │
        ┌──────────────────────────────────┐              │
        │  codex app-server (子进程)        │──────────────┘
        │   thread/start, turn/start        │
        │   item/* 通知                     │
        │   shell + apply_patch + update_plan│
        │   view_image + sandbox            │
        │   ┌─────────────────────────┐     │
        │   │  MCP 客户端              │     │
        │   │  ├─ 用户 MCP 服务器      │     │
        │   │  ├─ 原生插件             │     │
        │   │  │   (linear, github,   │     │
        │   │  │    gmail, calendar,  │     │
        │   │  │    canva, ...)       │     │
        │   │  └─ hermes-tools ───────┼─────────────────┐
        │   │       (回调到           │     │           │
        │   │        Hermes 更丰富的  │     │           │
        │   │        工具)            │     │           │
        │   └─────────────────────────┘     │           │
        └──────────────────────────────────┘           │
                                                        │
                                                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  hermes_tools_mcp_server.py (按需启动的子进程)            │
        │   web_search, web_extract, browser_*, vision_analyze,    │
        │   image_generate, skill_view, skills_list, text_to_speech│
        └──────────────────────────────────────────────────────────┘
```

有关实现细节，请参阅 [PR #24182](https://github.com/NousResearch/hermes-agent/pull/24182) 和 [Codex app-server 协议 README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)。
