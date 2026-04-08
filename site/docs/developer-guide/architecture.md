---
sidebar_position: 1
title: "架构"
description: "Hermes Agent 内部机制 —— 主要子系统、执行路径、数据流以及后续阅读指南"
---

# 架构

本页面是 Hermes Agent 内部机制的高层级地图。你可以通过它在代码库中定位，然后深入阅读特定子系统的文档以了解实现细节。

## 系统概览

```text
┌─────────────────────────────────────────────────────────────────────┐
│                          入口点 (Entry Points)                       │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  Batch Runner    API Server                  Python Library          │
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
│  │ Compression  │ │ 3 API Modes  │ │ Tool Registry│                │
│  │ & Caching    │ │ chat_compl.  │ │ (registry.py)│                │
│  │              │ │ codex_resp.  │ │ 48 tools     │                │
│  │              │ │ anthropic    │ │ 40 toolsets   │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
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

## 目录结构

```text
hermes-agent/
├── run_agent.py              # AIAgent — 核心对话循环 (~9,200 行)
├── cli.py                    # HermesCLI — 交互式终端 UI (~8,500 行)
├── model_tools.py            # 工具发现、Schema 收集、分发
├── toolsets.py               # 工具分组和平台预设
├── hermes_state.py           # 带有 FTS5 的 SQLite 会话/状态数据库
├── hermes_constants.py       # HERMES_HOME，感知 Profile 的路径
├── batch_runner.py           # 批量轨迹 (trajectory) 生成
│
├── agent/                    # Agent 内部组件
│   ├── prompt_builder.py     # 系统提示词组装
│   ├── context_compressor.py # 对话压缩算法
│   ├── prompt_caching.py     # Anthropic 提示词缓存
│   ├── auxiliary_client.py   # 用于辅助任务的 LLM (视觉、摘要)
│   ├── model_metadata.py     # 模型上下文长度、Token 估算
│   ├── models_dev.py         # models.dev 注册表集成
│   ├── anthropic_adapter.py  # Anthropic Messages API 格式转换
│   ├── display.py            # KawaiiSpinner，工具预览格式化
│   ├── skill_commands.py     # Skill 斜杠命令
│   ├── memory_manager.py    # 记忆管理器编排
│   ├── memory_provider.py   # 记忆提供者抽象基类 (ABC)
│   └── trajectory.py         # 轨迹保存辅助工具
│
├── hermes_cli/               # CLI 子命令和设置
│   ├── main.py               # 入口点 — 所有 `hermes` 子命令 (~5,500 行)
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, 迁移
│   ├── commands.py           # COMMAND_REGISTRY — 中央斜杠命令定义
│   ├── auth.py               # PROVIDER_REGISTRY, 凭据解析
│   ├── runtime_provider.py   # Provider → api_mode + 凭据
│   ├── models.py             # 模型目录，Provider 模型列表
│   ├── model_switch.py       # /model 命令逻辑 (CLI 与 Gateway 共享)
│   ├── setup.py              # 交互式设置向导 (~3,100 行)
│   ├── skin_engine.py        # CLI 主题引擎
│   ├── skills_config.py      # hermes skills — 按平台启用/禁用
│   ├── skills_hub.py         # /skills 斜杠命令
│   ├── tools_config.py       # hermes tools — 按平台启用/禁用
│   ├── plugins.py            # PluginManager — 发现、加载、钩子
│   ├── callbacks.py          # 终端回调 (澄清、sudo、审批)
│   └── gateway.py            # hermes gateway 启动/停止
│
├── tools/                    # 工具实现 (每个工具一个文件)
│   ├── registry.py           # 中央工具注册表
│   ├── approval.py           # 危险命令检测
│   ├── terminal_tool.py      # 终端编排
│   ├── process_registry.py   # 后台进程管理
│   ├── file_tools.py         # read_file, write_file, patch, search_files
│   ├── web_tools.py          # web_search, web_extract
│   ├── browser_tool.py       # 11 个浏览器自动化工具
│   ├── code_execution_tool.py # execute_code 沙箱
│   ├── delegate_tool.py      # Sub-agent 委派
│   ├── mcp_tool.py           # MCP 客户端 (~2,200 行)
│   ├── credential_files.py   # 基于文件的凭据透传
│   ├── env_passthrough.py    # 沙箱的环境变量透传
│   ├── ansi_strip.py         # ANSI 转义字符去除
│   └── environments/         # 终端后端 (local, docker, ssh, modal, daytona, singularity)
│
├── gateway/                  # 消息平台网关
│   ├── run.py                # GatewayRunner — 消息分发 (~7,500 行)
│   ├── session.py            # SessionStore — 对话持久化
│   ├── delivery.py           # 出站消息投递
│   ├── pairing.py            # 私聊配对授权
│   ├── hooks.py              # 钩子发现和生命周期事件
│   ├── mirror.py             # 跨会话消息镜像
│   ├── status.py             # Token 锁，Profile 作用域的进程追踪
│   ├── builtin_hooks/        # 始终注册的钩子
│   └── platforms/            # 14 个适配器: telegram, discord, slack, whatsapp,
│                             #   signal, matrix, mattermost, email, sms,
│                             #   dingtalk, feishu, wecom, homeassistant, webhook
│
├── acp_adapter/              # ACP 服务端 (VS Code / Zed / JetBrains)
├── cron/                     # 调度器 (jobs.py, scheduler.py)
├── plugins/memory/           # 记忆提供者插件
├── environments/             # 强化学习训练环境 (Atropos)
├── skills/                   # 内置技能 (始终可用)
├── optional-skills/          # 官方可选技能 (需显式安装)
├── website/                  # Docusaurus 文档网站
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
    → 有工具调用? → model_tools.handle_function_call() → 循环
    → 最终响应 → 显示 → 保存到 SessionDB
```

### Gateway 消息

```text
平台事件 → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → 授权用户
    → 解析会话密钥 (session key)
    → 使用会话历史创建 AIAgent
    → AIAgent.run_conversation()
    → 通过适配器将响应投递回去
```
### Cron Job

```text
Scheduler tick → 从 jobs.json 加载到期任务
  → 创建全新的 AIAgent (无历史记录)
  → 将关联的 skills 作为上下文注入
  → 运行任务 prompt
  → 将响应交付至目标平台
  → 更新任务状态和 next_run
```

## 推荐阅读顺序

如果你是第一次接触该代码库：

1. **本页面** — 快速了解概况
2. **[Agent Loop 内部机制](./agent-loop.md)** — AIAgent 的工作原理
3. **[Prompt 组装](./prompt-assembly.md)** — 系统 prompt 的构建方式
4. **[Provider 运行时解析](./provider-runtime.md)** — 如何选择 Provider
5. **[添加 Provider](./adding-providers.md)** — 添加新 Provider 的实践指南
6. **[Tools 运行时](./tools-runtime.md)** — 工具注册、分发与环境
7. **[会话存储](./session-storage.md)** — SQLite 模式、FTS5 与会话谱系
8. **[网关内部机制](./gateway-internals.md)** — 消息平台网关
9. **[上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)** — 压缩与缓存机制
10. **[ACP 内部机制](./acp-internals.md)** — IDE 集成
11. **[环境、基准测试与数据生成](./environments.md)** — 强化学习（RL）训练

## 主要子系统

### Agent Loop

同步编排引擎（`run_agent.py` 中的 `AIAgent`）。负责 Provider 选择、Prompt 构建、工具执行、重试、回退、回调、压缩和持久化。支持三种 API 模式以适配不同的 Provider 后端。

→ [Agent Loop 内部机制](./agent-loop.md)

### Prompt 系统

负责在对话生命周期内构建和维护 Prompt：

- **`prompt_builder.py`** — 从以下来源组装系统 Prompt：人格设定 (SOUL.md)、记忆 (MEMORY.md, USER.md)、技能 (skills)、上下文文件 (AGENTS.md, .hermes.md)、工具使用指南以及特定模型的指令。
- **`prompt_caching.py`** — 应用 Anthropic 缓存断点进行前缀缓存。
- **`context_compressor.py`** — 当上下文超过阈值时，对中间对话轮次进行摘要。

→ [Prompt 组装](./prompt-assembly.md), [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)

### Provider 解析

由 CLI、网关、Cron、ACP 和辅助调用共享的运行时解析器。将 `(provider, model)` 元组映射为 `(api_mode, api_key, base_url)`。处理 18 个以上的 Provider、OAuth 流程、凭据池和别名解析。

→ [Provider 运行时解析](./provider-runtime.md)

### 工具系统 (Tool System)

中央工具注册表 (`tools/registry.py`)，包含分布在 20 个工具集中的 47 个已注册工具。每个工具文件在导入时自动注册。注册表负责 Schema 收集、分发、可用性检查和错误封装。终端工具支持 6 种后端（本地、Docker、SSH、Daytona、Modal、Singularity）。

→ [Tools 运行时](./tools-runtime.md)

### 会话持久化

基于 SQLite 的会话存储，支持 FTS5 全文搜索。会话具有谱系追踪（跨压缩的父/子关系）、各平台隔离以及带冲突处理的原子写入。

→ [Session Storage](./session-storage.md)

### 消息网关 (Messaging Gateway)

长期运行的进程，拥有 14 个平台适配器、统一的会话路由、用户授权（白名单 + 私聊配对）、斜杠命令分发、钩子系统、Cron 触发和后台维护。

→ [Gateway Internals](./gateway-internals.md)

### 插件系统

三个发现源：`~/.hermes/plugins/`（用户）、`.hermes/plugins/`（项目）和 pip 入口点。插件通过上下文 API 注册工具、钩子和 CLI 命令。记忆 Provider 是 `plugins/memory/` 下的一种特殊插件类型。

→ [插件指南](/guides/build-a-hermes-plugin), [记忆 Provider 插件](./memory-provider-plugin.md)

### Cron

一等公民级别的 Agent 任务（而非 shell 任务）。任务存储在 JSON 中，支持多种调度格式，可以关联技能和脚本，并交付到任何平台。

→ [Cron 内部机制](./cron-internals.md)

### ACP 集成

通过 stdio/JSON-RPC 将 Hermes 作为编辑器原生 Agent 暴露给 VS Code、Zed 和 JetBrains。

→ [ACP 内部机制](./acp-internals.md)

### RL / 环境 / 轨迹 (Trajectories)

用于评估和强化学习训练的完整环境框架。与 Atropos 集成，支持多种工具调用解析器，并生成 ShareGPT 格式的轨迹数据。

→ [环境、基准测试与数据生成](./environments.md), [轨迹与训练格式](./trajectory-format.md)

## 设计原则

| 原则 | 实践中的含义 |
|-----------|--------------------------|
| **Prompt 稳定性** | 系统 Prompt 在对话中途不会改变。除了显式的用户操作（如 `/model`）外，不存在破坏缓存的变动。 |
| **可观测执行** | 每一个工具调用都通过回调对用户可见。在 CLI（进度条）和网关（聊天消息）中提供进度更新。 |
| **可中断性** | API 调用和工具执行可以被用户输入或信号中途取消。 |
| **平台无关核心** | 同一个 AIAgent 类服务于 CLI、网关、ACP、批量运行器和 API 服务器。平台差异存在于入口点，而非 Agent 内部。 |
| **松耦合** | 可选子系统（MCP、插件、记忆 Provider、RL 环境）使用注册表模式和 `check_fn` 门控，而非硬依赖。 |
| **配置隔离 (Profile isolation)** | 每个配置（`hermes -p <name>`）拥有独立的 HERMES_HOME、配置、记忆、会话和网关 PID。多个配置可并发运行。 |

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

这条链意味着工具注册发生在导入阶段，早于任何 Agent 实例的创建。添加新工具需要在 `model_tools.py` 的 `_discover_tools()` 列表中添加导入。
