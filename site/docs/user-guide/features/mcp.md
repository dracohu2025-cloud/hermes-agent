---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器，并精确控制 Hermes 加载哪些 MCP 工具"
---

# MCP (Model Context Protocol)

MCP 让 Hermes Agent 能够连接到外部工具服务器，从而使 Agent 可以使用 Hermes 自身之外的工具——如 GitHub、数据库、文件系统、浏览器栈、内部 API 等。

如果你曾希望 Hermes 使用某个已经存在于别处的工具，MCP 通常是最简洁的实现方式。

## MCP 能为你带来什么

- 无需编写原生 Hermes 工具即可访问外部工具生态系统
- 在同一个配置中支持本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 在服务器支持时，提供 MCP 资源（resources）和提示词（prompts）的实用包装器
- 针对每个服务器进行过滤，以便仅向 Hermes 暴露你真正想要的 MCP 工具

## 快速开始

1. 安装 MCP 支持（如果你使用的是标准安装脚本，则已经包含）：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

2. 在 `~/.hermes/config.yaml` 中添加一个 MCP 服务器：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3. 启动 Hermes：

```bash
hermes chat
```

4. 让 Hermes 使用基于 MCP 的功能。

例如：

```text
列出 /home/user/projects 中的文件并总结仓库结构。
```

Hermes 将发现 MCP 服务器的工具，并像使用其他工具一样使用它们。

## 两种 MCP 服务器

### Stdio 服务器

Stdio 服务器作为本地子进程运行，通过 stdin/stdout 进行通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况使用 stdio 服务器：
- 服务器安装在本地
- 你希望低延迟地访问本地资源
- 你正在参考显示 `command`、`args` 和 `env` 的 MCP 服务器文档

### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

在以下情况使用 HTTP 服务器：
- MCP 服务器托管在别处
- 你的组织暴露了内部 MCP 端点
- 你不希望 Hermes 为该集成启动本地子进程

## 基础配置参考

Hermes 从 `~/.hermes/config.yaml` 的 `mcp_servers` 字段读取 MCP 配置。

### 常用键名

| 键名 | 类型 | 含义 |
|---|---|---|
| `command` | string | stdio MCP 服务器的可执行文件 |
| `args` | list | stdio 服务器的参数 |
| `env` | mapping | 传递给 stdio 服务器的环境变量 |
| `url` | string | HTTP MCP 端点 |
| `headers` | mapping | 远程服务器的 HTTP 请求头 |
| `timeout` | number | 工具调用超时时间 |
| `connect_timeout` | number | 初始连接超时时间 |
| `enabled` | bool | 如果为 `false`，Hermes 将完全跳过该服务器 |
| `tools` | mapping | 针对每个服务器的工具过滤和实用程序策略 |

### 最小 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 最小 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## Hermes 如何注册 MCP 工具

Hermes 会为 MCP 工具添加前缀，以免与内置名称冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

在实践中，你通常不需要手动调用带前缀的名称——Hermes 会在正常的推理过程中识别并选择该工具。

## MCP 实用工具

在支持的情况下，Hermes 还会围绕 MCP 资源和提示词注册实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具会按照相同的服务器前缀模式进行注册，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要提示

这些实用工具现在具有能力感知（capability-aware）特性：
- 只有当 MCP 会话确实支持资源操作时，Hermes 才会注册资源实用程序。
- 只有当 MCP 会话确实支持提示词操作时，Hermes 才会注册提示词实用程序。

因此，一个仅暴露可调用工具但不提供资源/提示词的服务器将不会获得这些额外的包装器。

## 针对每个服务器的过滤

你可以控制每个 MCP 服务器向 Hermes 贡献哪些工具，从而实现对工具命名空间的精细化管理。

### 完全禁用某个服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果 `enabled: false`，Hermes 会完全跳过该服务器，甚至不会尝试连接。

### 白名单服务器工具

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues]
```

只有这些指定的 MCP 服务器工具会被注册。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

除了被排除的工具外，所有服务器工具都会被注册。

### 优先级规则

如果两者同时存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 优先。

### 同时过滤实用工具

你还可以单独禁用 Hermes 添加的实用程序包装器：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 禁用了 `list_resources` 和 `read_resource`
- `tools.prompts: false` 禁用了 `list_prompts` 和 `get_prompt`

### 完整示例

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues, search_code]
      prompts: false

  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer]
      resources: false

  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

## 如果所有内容都被过滤掉了会怎样？

如果你的配置过滤掉了所有可调用工具，并且禁用或忽略了所有支持的实用程序，Hermes 不会为该服务器创建空的运行时 MCP 工具集。

这可以保持工具列表的整洁。

## 运行时行为

### 发现阶段

Hermes 在启动时发现 MCP 服务器，并将其工具注册到正常的工具注册表中。

### 动态工具发现

MCP 服务器可以通过发送 `notifications/tools/list_changed` 通知，在运行时其可用工具发生变化时告知 Hermes。当 Hermes 收到此通知时，它会自动重新获取服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp`。

这对于能力会动态变化的 MCP 服务器非常有用（例如，当加载新的数据库模式时添加工具，或当服务下线时移除工具的服务器）。

刷新过程受锁保护，因此来自同一服务器的快速连续通知不会导致重叠刷新。提示词和资源变更通知（`prompts/list_changed`，`resources/list_changed`）会被接收，但目前尚未采取行动。

### 重新加载

如果你修改了 MCP 配置，请使用：

```text
/reload-mcp
```

这将从配置中重新加载 MCP 服务器并刷新可用工具列表。对于由服务器自身推送的运行时工具更改，请参阅上文的[动态工具发现](#dynamic-tool-discovery)。

### 工具集 (Toolsets)

每个配置的 MCP 服务器在贡献至少一个注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集层面对 MCP 服务器进行推理变得更加容易。

## 安全模型

### Stdio 环境过滤

对于 stdio 服务器，Hermes 不会盲目地传递你的完整 shell 环境。
只有明确配置的 `env` 加上安全的基准环境变量会被传递。这减少了意外泄露密钥的风险。

### 配置级曝光控制

新的过滤支持也是一种安全控制手段：
- 禁用你不希望模型看到的危险工具
- 为敏感服务器仅开放最小白名单
- 当你不希望暴露相关接口时，禁用 resource/prompt 封装器

## 示例用例

### 具有最小 Issue 管理界面的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue]
      prompts: false
      resources: false
```

使用方式：

```text
显示标记为 bug 的未解决 issue，然后为不稳定的 MCP 重连行为起草一个新的 issue。
```

### 移除了危险操作的 Stripe 服务器

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

使用方式：

```text
查找最近 10 笔失败的付款，并总结常见的失败原因。
```

### 针对单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

使用方式：

```text
检查项目根目录并解释目录布局。
```

## 故障排除

### MCP 服务器无法连接

检查：

```bash
# 验证 MCP 依赖已安装（标准安装中已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

然后验证你的配置并重启 Hermes。

### 工具未显示

可能的原因：
- 服务器连接失败
- 发现（discovery）失败
- 你的过滤配置排除了这些工具
- 该服务器不存在 utility 能力
- 服务器通过 `enabled: false` 被禁用

如果你是有意进行过滤，那么这是预期结果。

### 为什么 resource 或 prompt 工具没有出现？

因为 Hermes 现在仅在以下两个条件同时满足时才注册这些封装器：
1. 你的配置允许它们
2. 服务器会话实际支持该能力

这是有意为之的，目的是保持工具列表的真实性。

## MCP Sampling 支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这允许 MCP 服务器请求 Hermes 代表它生成文本 —— 这对于需要 LLM 能力但自身没有模型访问权限的服务器非常有用。

对于所有 MCP 服务器，Sampling 默认是**开启的**（只要 MCP SDK 支持）。可以在 `sampling` 键下为每个服务器进行配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # 启用 sampling（默认：true）
      model: "openai/gpt-4o"  # 覆盖 sampling 请求的模型（可选）
      max_tokens_cap: 4096     # 每次 sampling 响应的最大 token 数（默认：4096）
      timeout: 30              # 每次请求的超时秒数（默认：30）
      max_rpm: 10              # 频率限制：每分钟最大请求数（默认：10）
      max_tool_rounds: 5       # sampling 循环中最大工具使用轮数（默认：5）
      allowed_models: []       # 服务器可以请求的模型名称允许列表（为空表示任意）
      log_level: "info"        # 审计日志级别：debug, info, 或 warning（默认：info）
```

Sampling 处理器包含滑动窗口频率限制器、单次请求超时和工具循环深度限制，以防止失控使用。指标（请求计数、错误、使用的 token）按服务器实例进行跟踪。

若要禁用特定服务器的 sampling：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## 将 Hermes 作为 MCP 服务器运行

除了连接**到** MCP 服务器外，Hermes 也可以**作为**一个 MCP 服务器。这让其他具备 MCP 能力的 Agent（如 Claude Code、Cursor、Codex 或任何 MCP 客户端）能够使用 Hermes 的消息传递能力 —— 列出对话、读取消息历史，并在你所有已连接的平台上发送消息。

### 何时使用

- 你希望 Claude Code、Cursor 或其他编程 Agent 通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 你希望有一个单一的 MCP 服务器，能同时桥接到 Hermes 所有已连接的消息平台
- 你已经有一个正在运行且连接了平台的 Hermes 网关

### 快速开始

```bash
hermes mcp serve
```

这将启动一个 stdio MCP 服务器。MCP 客户端（而不是你）负责管理进程的生命周期。

### MCP 客户端配置

将 Hermes 添加到你的 MCP 客户端配置中。例如，在 Claude Code 的 `~/.claude/claude_desktop_config.json` 中：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

或者如果你将 Hermes 安装在了特定位置：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "/home/user/.hermes/hermes-agent/venv/bin/hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 可用工具

该 MCP 服务器暴露了 10 个工具，与 OpenClaw 的频道桥接接口一致，并增加了一个 Hermes 特有的频道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息对话。可按平台过滤或按名称搜索。 |
| `conversation_get` | 通过会话密钥获取单个对话的详细信息。 |
| `messages_read` | 读取对话的近期消息历史。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图像、媒体）。 |
| `events_poll` | 从某个游标位置开始轮询新的对话事件。 |
| `events_wait` | 长轮询 / 阻塞直到下一个事件到达（近乎实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`, `discord:#general`）。 |
| `channels_list` | 列出所有平台中可用的消息目标。 |
| `permissions_list_open` | 列出在此桥接会话期间观察到的待处理审批请求。 |
| `permissions_respond` | 允许或拒绝待处理的审批请求。 |

### 事件系统

该 MCP 服务器包含一个实时事件桥接器，它会轮询 Hermes 的会话数据库以获取新消息。这让 MCP 客户端能够近乎实时地感知传入的对话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（阻塞直到超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`, `approval_requested`, `approval_resolved`

事件队列位于内存中，并在桥接连接时启动。较旧的消息可以通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # 普通模式
hermes mcp serve --verbose    # 在 stderr 输出调试日志
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）读取对话数据。一个后台线程轮询数据库以获取新消息，并维护一个内存中的事件队列。对于发送消息，它使用与 Hermes Agent 本身相同的 `send_message` 基础设施。

对于读取操作（列出对话、读取历史、轮询事件），网关**不需要**运行。对于发送操作，网关**必须**运行，因为平台适配器需要活跃的连接。

### 当前限制

- 仅支持 Stdio 传输（暂无 HTTP MCP 传输）
- 通过经过 mtime 优化的数据库轮询，事件轮询间隔约为 200ms（文件未更改时跳过操作）
- 暂无 `claude/channel` 推送通知协议
- 仅限纯文本发送（无法通过 `messages_send` 发送媒体/附件）

## 相关文档

- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [斜杠命令](/reference/slash-commands)
- [常见问题 (FAQ)](/reference/faq)
