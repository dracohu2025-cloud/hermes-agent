---
sidebar_position: 1
title: "架构"
description: "Hermes Agent 内部机制 —— 主要子系统、执行路径、数据流，以及接下来该读什么"
---

# 架构 {#architecture}

本页是 Hermes Agent 内部机制的顶层地图。先用它理清代码库的整体脉络，再深入各子系统的文档了解实现细节。

## 系统概览 {#system-overview}

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        入口层                                         │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  批量执行器       API 服务器                  Python 库              │
└──────────┬──────────────┬───────────────────────┬───────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Prompt       │  │ Provider     │  │ Tool         │               │
│  │ 构建器        │  │ 解析          │  │ 调度          │               │
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │
│  │ 压缩与缓存    │  │ 3 种 API 模式 │  │ Tool Registry│               │
│  │              │  │ chat_compl.  │  │ (registry.py)│               │
│  │              │  │ codex_resp.  │  │ 47 个 tools  │               │
│  │              │  │ anthropic    │  │ 19 个 toolsets│              │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ Session Storage   │              │ Tool Backends         │
│ (SQLite + FTS5)   │              │ Terminal (6 backends) │
│ hermes_state.py   │              │ Browser (5 backends)  │
│ gateway/session.py│              │ Web (4 backends)      │
└───────────────────┘              │ MCP (dynamic)         │
                                   │ File, Vision, etc.    │
                                   └──────────────────────┘
```

## 目录结构 {#directory-structure}

```text
hermes-agent/
├── run_agent.py              # AIAgent —— 核心对话循环（约 10,700 行）
├── cli.py                    # HermesCLI —— 交互式终端 UI（约 10,000 行）
├── model_tools.py            # Tool 发现、schema 收集、调度
├── toolsets.py               # Tool 分组与平台预设
├── hermes_state.py           # SQLite session/state 数据库，带 FTS5
├── hermes_constants.py       # HERMES_HOME、profile 感知路径
├── batch_runner.py           # 批量轨迹生成
│
├── agent/                    # Agent 内部机制
│   ├── prompt_builder.py     # System prompt 组装
│   ├── context_engine.py     # ContextEngine ABC（可插拔）
│   ├── context_compressor.py # 默认引擎 —— 有损摘要
│   ├── prompt_caching.py     # Anthropic prompt 缓存
│   ├── auxiliary_client.py   # 辅助 LLM，用于副任务（vision、摘要）
│   ├── model_metadata.py     # 模型上下文长度、token 估算
│   ├── models_dev.py         # models.dev 注册表集成
│   ├── anthropic_adapter.py  # Anthropic Messages API 格式转换
│   ├── display.py            # KawaiiSpinner、tool 预览格式化
│   ├── skill_commands.py     # Skill 斜杠命令
│   ├── memory_manager.py    # Memory manager 编排
│   ├── memory_provider.py   # Memory provider ABC
│   └── trajectory.py         # 轨迹保存辅助函数
│
├── hermes_cli/               # CLI 子命令与安装配置
│   ├── main.py               # 入口 —— 所有 `hermes` 子命令（约 6,000 行）
│   ├── config.py             # DEFAULT_CONFIG、OPTIONAL_ENV_VARS、迁移
│   ├── commands.py           # COMMAND_REGISTRY —— 中央斜杠命令定义
│   ├── auth.py               # PROVIDER_REGISTRY、凭据解析
│   ├── runtime_provider.py   # Provider → api_mode + 凭据
│   ├── models.py             # 模型目录、provider 模型列表
│   ├── model_switch.py       # /model 命令逻辑（CLI + gateway 共用）
│   ├── setup.py              # 交互式安装向导（约 3,100 行）
│   ├── skin_engine.py        # CLI 主题引擎
│   ├── skills_config.py      # hermes skills —— 按平台启用/禁用
│   ├── skills_hub.py         # /skills 斜杠命令
│   ├── tools_config.py       # hermes tools —— 按平台启用/禁用
│   ├── plugins.py            # PluginManager —— 发现、加载、钩子
│   ├── callbacks.py          # 终端回调（澄清、sudo、审批）
│   └── gateway.py            # hermes gateway 启动/停止
│
├── tools/                    # Tool 实现（每个 tool 一个文件）
│   ├── registry.py           # 中央 tool 注册表
│   ├── approval.py           # 危险命令检测
│   ├── terminal_tool.py      # Terminal 编排
│   ├── process_registry.py   # 后台进程管理
│   ├── file_tools.py         # read_file、write_file、patch、search_files
│   ├── web_tools.py          # web_search、web_extract
│   ├── browser_tool.py       # 10 个浏览器自动化 tools
│   ├── code_execution_tool.py # execute_code 沙箱
│   ├── delegate_tool.py      # Subagent 委托
│   ├── mcp_tool.py           # MCP 客户端（约 2,200 行）
│   ├── credential_files.py   # 基于文件的凭据透传
│   ├── env_passthrough.py    # 沙箱环境变量透传
│   ├── ansi_strip.py         # ANSI 转义序列剥离
│   └── environments/         # Terminal 后端（local、docker、ssh、modal、daytona、singularity）
│
├── gateway/                  # 消息平台 gateway
│   ├── run.py                # GatewayRunner —— 消息调度（约 9,000 行）
│   ├── session.py            # SessionStore —— 对话持久化
│   ├── delivery.py           # 出站消息投递
│   ├── pairing.py            # DM 配对授权
│   ├── hooks.py              # 钩子发现与生命周期事件
│   ├── mirror.py             # 跨 session 消息镜像
│   ├── status.py             # Token 锁、profile 级进程追踪
│   ├── builtin_hooks/        # 始终注册的钩子
│   └── platforms/            # 18 个适配器：telegram、discord、slack、whatsapp、
│                             #   signal、matrix、mattermost、email、sms、
│                             #   dingtalk、feishu、wecom、wecom_callback、weixin、
│                             #   bluebubbles、qqbot、homeassistant、webhook、api_server
│
├── acp_adapter/              # ACP 服务器（VS Code / Zed / JetBrains）
├── cron/                     # 调度器（jobs.py、scheduler.py）
├── plugins/memory/           # Memory provider 插件
├── plugins/context_engine/   # Context engine 插件
├── environments/             # RL 训练环境（Atropos）
├── skills/                   # 内置 skills（始终可用）
├── optional-skills/          # 官方可选 skills（需显式安装）
├── website/                  # Docusaurus 文档站点
└── tests/                    # Pytest 测试套件（3,000+ 测试）
```
## 数据流 {#data-flow}

### CLI 会话 {#cli-session}

```text
用户输入 → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API 调用 (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → 循环
    → 最终响应 → 展示 → 保存到 SessionDB
```

### Gateway 消息 {#gateway-message}

```text
平台事件 → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → 授权用户
    → 解析会话 key
    → 用会话历史创建 AIAgent
    → AIAgent.run_conversation()
    → 通过 adapter 回传响应
```

### 定时任务（Cron Job） {#cron-job}

```text
调度器触发 → 从 jobs.json 加载到期任务
  → 创建全新 AIAgent（无历史记录）
  → 将附加技能注入为上下文
  → 运行任务提示词
  → 将响应投递到目标平台
  → 更新任务状态和 next_run
```

## 推荐阅读顺序 {#recommended-reading-order}

如果你刚接触这个代码库：

1. **本页** — 先建立整体认知
2. **[Agent 循环内部机制](./agent-loop.md)** — AIAgent 的工作原理
3. **[提示词组装](./prompt-assembly.md)** — 系统提示词的构建方式
4. **[Provider 运行时解析](./provider-runtime.md)** — Provider 如何选择
5. **[添加 Provider](./adding-providers.md)** — 添加新 Provider 的实操指南
6. **[工具运行时](./tools-runtime.md)** — 工具注册表、分发、运行环境
7. **[会话存储](./session-storage.md)** — SQLite 表结构、FTS5、会话血缘
8. **[Gateway 内部机制](./gateway-internals.md)** — 消息平台 Gateway
9. **[上下文压缩与提示词缓存](./context-compression-and-caching.md)** — 压缩与缓存
10. **[ACP 内部机制](./acp-internals.md)** — IDE 集成
11. **[环境、基准测试与数据生成](./environments.md)** — RL 训练

## 主要子系统 {#major-subsystems}

### Agent 循环 {#agent-loop}

同步编排引擎（`run_agent.py` 中的 `AIAgent`）。负责 Provider 选择、提示词构建、工具执行、重试、降级、回调、压缩和持久化。支持三种 API 模式，以适配不同的 Provider 后端。

→ [Agent 循环内部机制](./agent-loop.md)

### 提示词系统 {#prompt-system}

整个对话生命周期中的提示词构建与维护：

- **`prompt_builder.py`** — 组装系统提示词，来源包括：人格定义（SOUL.md）、记忆（MEMORY.md、USER.md）、技能、上下文文件（AGENTS.md、.hermes.md）、工具使用指引，以及模型专属指令
- **`prompt_caching.py`** — 为 Anthropic 的前缀缓存应用 cache 断点
- **`context_compressor.py`** — 当上下文超出阈值时，对对话中间轮次进行摘要

→ [提示词组装](./prompt-assembly.md)、[上下文压缩与提示词缓存](./context-compression-and-caching.md)

### Provider 解析 {#provider-resolution}

一个由 CLI、Gateway、Cron、ACP 及辅助调用共享的运行时解析器。将 `(provider, model)` 元组映射为 `(api_mode, api_key, base_url)`。支持 18+ 个 Provider、OAuth 流程、凭据池和别名解析。

→ [Provider 运行时解析](./provider-runtime.md)

### 工具系统 {#tool-system}

中心化工具注册表（`tools/registry.py`），包含 19 个工具集中的 47 个已注册工具。每个工具文件在导入时自动注册。注册表负责 schema 收集、分发、可用性检查和错误包装。终端工具支持 6 种后端（本地、Docker、SSH、Daytona、Modal、Singularity）。

→ [工具运行时](./tools-runtime.md)

### 会话持久化 {#session-persistence}

基于 SQLite 的会话存储，支持 FTS5 全文检索。会话具备血缘追踪（压缩前后的父子关系）、按平台隔离，以及带并发竞争处理的原子写入。

→ [会话存储](./session-storage.md)

### 消息 Gateway {#messaging-gateway}

长期运行的进程，包含 18 个平台适配器、统一的会话路由、用户授权（白名单 + DM 配对）、斜杠命令分发、Hook 系统、Cron 触发和后台维护。

→ [Gateway 内部机制](./gateway-internals.md)
### 插件系统 {#plugin-system}

三个发现来源：`~/.hermes/plugins/`（用户级）、`.hermes/plugins/`（项目级），以及 pip entry points。插件通过 context API 注册工具、钩子和 CLI 命令。有两种专门的插件类型：memory provider（`plugins/memory/`）和 context engine（`plugins/context_engine/`）。两者都是单选的——每种同时只能激活一个，通过 `hermes plugins` 或 `config.yaml` 配置。

→ [插件指南](/guides/build-a-hermes-plugin)、[Memory Provider 插件](./memory-provider-plugin.md)

### Cron {#cron}

原生的 Agent 任务（不是 shell 任务）。任务以 JSON 存储，支持多种调度格式，可以附加技能和脚本，并投递到任意平台。

→ [Cron 内部机制](./cron-internals.md)

### ACP 集成 {#acp-integration}

通过 stdio/JSON-RPC 将 Hermes 暴露为编辑器原生 Agent，支持 VS Code、Zed 和 JetBrains。

→ [ACP 内部机制](./acp-internals.md)

### RL / 环境 / 轨迹 {#rl-environments-trajectories}

用于评估和 RL 训练的完整环境框架。与 Atropos 集成，支持多种 tool-call 解析器，并生成 ShareGPT 格式的轨迹。

→ [环境、基准测试与数据生成](./environments.md)、[轨迹与训练格式](./trajectory-format.md)

## 设计原则 {#design-principles}

| 原则 | 实际含义 |
|-----------|--------------------------|
| **Prompt 稳定性** | 系统 prompt 在对话过程中不会变化。除了显式用户操作（`/model`）外，不会触发缓存失效的变更。 |
| **可观察的执行** | 每次工具调用都通过回调对用户可见。CLI 显示进度更新（spinner），gateway 显示聊天消息。 |
| **可中断** | API 调用和工具执行可以在执行过程中被用户输入或信号取消。 |
| **平台无关的核心** | 一个 AIAgent 类同时服务 CLI、gateway、ACP、batch 和 API server。平台差异存在于入口点，而非 Agent 内部。 |
| **松耦合** | 可选子系统（MCP、插件、memory provider、RL 环境）使用注册表模式和 check_fn 门控，而非硬依赖。 |
| **Profile 隔离** | 每个 profile（`hermes -p &lt;name&gt;`）拥有独立的 HERMES_HOME、配置、记忆、会话和 gateway PID。多个 profile 可以并发运行。 |

## 文件依赖链 {#file-dependency-chain}

```text
tools/registry.py  (no deps — imported by all tool files)
       ↑
tools/*.py  (each calls registry.register() at import time)
       ↑
model_tools.py  (imports tools/registry + triggers tool discovery)
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

这个链条意味着工具注册发生在 import 时，在创建任何 Agent 实例之前。任何带有顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动发现——无需手动维护 import 列表。
