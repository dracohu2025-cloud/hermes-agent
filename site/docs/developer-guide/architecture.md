---
sidebar_position: 1
title: "架构"
description: "Hermes Agent 内部结构 — 主要子系统、执行路径、数据流以及后续阅读指南"
---

# 架构

本页面是 Hermes Agent 内部结构的顶层地图。你可以通过它快速熟悉代码库，然后深入查阅特定子系统的文档以了解实现细节。

## 系统概览

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        入口点                                        │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  批处理运行器      API 服务器                   Python 库              │
└──────────┬──────────────┬───────────────────────┬────────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                           │
│                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │ Prompt        │ │ Provider     │ │ Tool         │                │
│  │ Builder       │ │ Resolution   │ │ Dispatch     │                │
│  │ (prompt_      │ │ (runtime_    │ │ (model_      │                │
│  │  builder.py)  │ │  provider.py)│ │  tools.py)   │                │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                │
│         │                │                │                          │
│  ┌──────┴───────┐ ┌──────┴───────┐ ┌──────┴───────┐                │
│  │ 压缩与缓存     │ │ 3 种 API 模式  │ │ 工具注册表     │                │
│  │              │ │ chat_compl.  │ │ (registry.py)│                │
│  │              │ │ codex_resp.  │ │ 48 个工具     │                │
│  │              │ │ anthropic    │ │ 40 个工具集    │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ 会话存储           │              │ 工具后端              │
│ (SQLite + FTS5)   │              │ 终端 (6 个后端)       │
│ hermes_state.py   │              │ 浏览器 (5 个后端)     │
│ gateway/session.py│              │ Web (4 个后端)       │
└───────────────────┘              │ MCP (动态)           │
                                   │ 文件、视觉等          │
                                   └──────────────────────┘
```

## 目录结构

```text
hermes-agent/
├── run_agent.py              # AIAgent — 核心对话循环 (~9,200 行)
├── cli.py                    # HermesCLI — 交互式终端 UI (~8,500 行)
├── model_tools.py            # 工具发现、模式收集、调度
├── toolsets.py               # 工具分组和平台预设
├── hermes_state.py           # 带有 FTS5 的 SQLite 会话/状态数据库
├── hermes_constants.py       # HERMES_HOME，感知配置文件的路径
├── batch_runner.py           # 批处理轨迹生成
│
├── agent/                    # Agent 内部组件
│   ├── prompt_builder.py     # 系统提示词组装
│   ├── context_compressor.py # 对话压缩算法
│   ├── prompt_caching.py     # Anthropic 提示词缓存
│   ├── auxiliary_client.py   # 用于辅助任务（视觉、摘要）的辅助 LLM
│   ├── model_metadata.py     # 模型上下文长度、Token 估算
│   ├── models_dev.py         # models.dev 注册表集成
│   ├── anthropic_adapter.py  # Anthropic Messages API 格式转换
│   ├── display.py            # KawaiiSpinner，工具预览格式化
│   ├── skill_commands.py     # 技能斜杠命令
│   ├── memory_manager.py    # 内存管理器编排
│   ├── memory_provider.py   # 内存提供程序抽象基类 (ABC)
│   └── trajectory.py         # 轨迹保存辅助工具
│
├── hermes_cli/               # CLI 子命令和设置
│   ├── main.py               # 入口点 — 所有 `hermes` 子命令 (~5,500 行)
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, 迁移
│   ├── commands.py           # COMMAND_REGISTRY — 核心斜杠命令定义
│   ├── auth.py               # PROVIDER_REGISTRY, 凭据解析
│   ├── runtime_provider.py   # Provider → api_mode + 凭据
│   ├── models.py             # 模型目录，提供程序模型列表
│   ├── model_switch.py       # /model 命令逻辑 (CLI 与网关共享)
│   ├── setup.py              # 交互式设置向导 (~3,100 行)
│   ├── skin_engine.py        # CLI 主题引擎
│   ├── skills_config.py      # hermes 技能 — 按平台启用/禁用
│   ├── skills_hub.py         # /skills 斜杠命令
│   ├── tools_config.py       # hermes 工具 — 按平台启用/禁用
│   ├── plugins.py            # PluginManager — 发现、加载、钩子
│   ├── callbacks.py          # 终端回调 (clarify, sudo, approval)
│   └── gateway.py            # hermes 网关启动/停止
│
├── tools/                    # 工具实现（每个工具一个文件）
│   ├── registry.py           # 核心工具注册表
│   ├── approval.py           # 危险命令检测
│   ├── terminal_tool.py      # 终端编排
│   ├── process_registry.py   # 后台进程管理
│   ├── file_tools.py         # read_file, write_file, patch, search_files
│   ├── web_tools.py          # web_search, web_extract
│   ├── browser_tool.py       # 11 个浏览器自动化工具
│   ├── code_execution_tool.py # execute_code 沙箱
│   ├── delegate_tool.py      # 子 Agent 委派
│   ├── mcp_tool.py           # MCP 客户端 (~2,200 行)
│   ├── credential_files.py   # 基于文件的凭据透传
│   ├── env_passthrough.py    # 沙箱环境变量透传
│   ├── ansi_strip.py         # ANSI 转义字符剥离
│   └── environments/         # 终端后端 (local, docker, ssh, modal, daytona, singularity)
│
├── gateway/                  # 消息平台网关
│   ├── run.py                # GatewayRunner — 消息调度 (~7,500 行)
│   ├── session.py            # SessionStore — 会话持久化
│   ├── delivery.py           # 出站消息投递
│   ├── pairing.py            # 私信 (DM) 配对授权
│   ├── hooks.py              # 钩子发现和生命周期事件
│   ├── mirror.py             # 跨会话消息镜像
│   ├── status.py             # Token 锁，基于配置文件的进程跟踪
│   ├── builtin_hooks/        # 常驻钩子
│   └── platforms/            # 15 个适配器：telegram, discord, slack, whatsapp,
│                             #   signal, matrix, mattermost, email, sms,
│                             #   dingtalk, feishu, wecom, bluebubbles, homeassistant, webhook
│
├── acp_adapter/              # ACP 服务器 (VS Code / Zed / JetBrains)
├── cron/                     # 调度器 (jobs.py, scheduler.py)
├── plugins/memory/           # 内存提供程序插件
├── environments/             # RL 训练环境 (Atropos)
├── skills/                   # 捆绑技能（始终可用）
├── optional-skills/          # 官方可选技能（需显式安装）
├── website/                  # Docusaurus 文档站点
└── tests/                    # Pytest 测试套件 (~3,000+ 测试)
```

## 数据流

### CLI 会话

```text
用户输入 → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API 调用 (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → 循环
    → 最终响应 → 显示 → 保存至 SessionDB
```

### 网关消息

```text
平台事件 → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → 用户授权
    → 解析会话密钥
    → 使用会话历史创建 AIAgent
    → AIAgent.run_conversation()
    → 通过适配器投递响应
```
### Cron Job

```text
Scheduler tick → load due jobs from jobs.json
  → create fresh AIAgent (no history)
  → inject attached skills as context
  → run job prompt
  → deliver response to target platform
  → update job state and next_run
```

## 推荐阅读顺序

如果你是刚接触代码库：

1. **本页面** — 快速了解概况
2. **[Agent Loop 内部原理](./agent-loop.md)** — AIAgent 的工作方式
3. **[Prompt 组装](./prompt-assembly.md)** — 系统 prompt 的构建过程
4. **[Provider 运行时解析](./provider-runtime.md)** — 如何选择 Provider
5. **[添加 Provider](./adding-providers.md)** — 添加新 Provider 的实践指南
6. **[工具运行时](./tools-runtime.md)** — 工具注册、调度与环境
7. **[会话存储](./session-storage.md)** — SQLite 架构、FTS5 与会话血缘
8. **[网关内部原理](./gateway-internals.md)** — 消息平台网关
9. **[上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)** — 压缩与缓存机制
10. **[ACP 内部原理](./acp-internals.md)** — IDE 集成
11. **[环境、基准测试与数据生成](./environments.md)** — RL 训练

## 主要子系统

### Agent Loop

同步编排引擎（位于 `run_agent.py` 中的 `AIAgent`）。负责处理 Provider 选择、prompt 构建、工具执行、重试、回退、回调、压缩和持久化。支持三种 API 模式以适配不同的 Provider 后端。

→ [Agent Loop 内部原理](./agent-loop.md)

### Prompt 系统

贯穿整个对话生命周期的 prompt 构建与维护：

- **`prompt_builder.py`** — 从以下内容组装系统 prompt：个性设定 (SOUL.md)、记忆 (MEMORY.md, USER.md)、技能、上下文文件 (AGENTS.md, .hermes.md)、工具使用指南以及特定模型的指令
- **`prompt_caching.py`** — 应用 Anthropic 缓存断点以实现前缀缓存
- **`context_compressor.py`** — 当上下文超过阈值时，对对话中间轮次进行总结

→ [Prompt 组装](./prompt-assembly.md), [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)

### Provider 解析

由 CLI、网关、Cron、ACP 和辅助调用共享的运行时解析器。将 `(provider, model)` 元组映射为 `(api_mode, api_key, base_url)`。处理 18+ 个 Provider、OAuth 流程、凭据池和别名解析。

→ [Provider 运行时解析](./provider-runtime.md)

### 工具系统

中央工具注册表 (`tools/registry.py`)，包含 20 个工具集中的 47 个已注册工具。每个工具文件在导入时会自动注册。注册表负责模式收集、调度、可用性检查和错误包装。终端工具支持 6 种后端（本地、Docker、SSH、Daytona、Modal、Singularity）。

→ [工具运行时](./tools-runtime.md)

### 会话持久化

基于 SQLite 的会话存储，支持 FTS5 全文搜索。会话具有血缘追踪（跨压缩的父/子关系）、平台隔离以及带冲突处理的原子写入功能。

→ [会话存储](./session-storage.md)

### 消息网关

长驻进程，包含 14 个平台适配器、统一会话路由、用户授权（允许列表 + 私信配对）、斜杠命令调度、钩子系统、Cron 定时任务以及后台维护功能。

→ [网关内部原理](./gateway-internals.md)

### 插件系统

三种发现来源：`~/.hermes/plugins/`（用户级）、`.hermes/plugins/`（项目级）以及 pip 入口点。插件通过上下文 API 注册工具、钩子和 CLI 命令。内存 Provider 是一种特殊的插件类型，位于 `plugins/memory/` 下。

→ [插件指南](/guides/build-a-hermes-plugin), [内存 Provider 插件](./memory-provider-plugin.md)

### Cron

一等公民 Agent 任务（非 shell 任务）。任务存储在 JSON 中，支持多种调度格式，可附加技能和脚本，并可交付到任何平台。

→ [Cron 内部原理](./cron-internals.md)

### ACP 集成

通过 stdio/JSON-RPC 将 Hermes 暴露为编辑器原生 Agent，支持 VS Code、Zed 和 JetBrains。

→ [ACP 内部原理](./acp-internals.md)

### RL / 环境 / 轨迹

用于评估和 RL 训练的完整环境框架。与 Atropos 集成，支持多种工具调用解析器，并生成 ShareGPT 格式的轨迹。

→ [环境、基准测试与数据生成](./environments.md), [轨迹与训练格式](./trajectory-format.md)

## 设计原则

| 原则 | 实际含义 |
|-----------|--------------------------|
| **Prompt 稳定性** | 系统 prompt 在对话中途不会改变。除明确的用户操作 (`/model`) 外，不会发生破坏缓存的变更。 |
| **执行可观测性** | 每个工具调用都通过回调对用户可见。CLI（加载动画）和网关（聊天消息）中均有进度更新。 |
| **可中断性** | API 调用和工具执行可以在运行中被用户输入或信号取消。 |
| **平台无关核心** | 单个 AIAgent 类服务于 CLI、网关、ACP、批处理和 API 服务器。平台差异存在于入口点，而非 Agent 本身。 |
| **松耦合** | 可选子系统（MCP、插件、内存 Provider、RL 环境）使用注册表模式和 check_fn 门控，而非硬依赖。 |
| **配置隔离** | 每个配置 (`hermes -p <name>`) 都有自己的 HERMES_HOME、配置、内存、会话和网关 PID。多个配置可以同时运行。 |

## 文件依赖链

```text
tools/registry.py  (无依赖 — 被所有工具文件导入)
       ↑
tools/*.py  (每个文件在导入时调用 registry.register())
       ↑
model_tools.py  (导入 tools/registry + 触发工具发现)
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

此链条意味着工具注册发生在导入时，即在创建任何 Agent 实例之前。添加新工具需要在 `model_tools.py` 的 `_discover_tools()` 列表中添加导入。
