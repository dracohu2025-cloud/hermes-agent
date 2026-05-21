---
sidebar_position: 4
title: "MCP（模型上下文协议）"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器，并精确控制 Hermes 加载哪些 MCP 工具"
---

<a id="mcp-model-context-protocol"></a>
# MCP（模型上下文协议）

MCP 让 Hermes Agent 能够连接到外部工具服务器，从而使 Agent 可以使用 Hermes 本身之外的工具——例如 GitHub、数据库、文件系统、浏览器栈、内部 API 等。

如果你曾希望 Hermes 使用某个已经存在于其他地方的现有工具，MCP 通常是最简洁的实现方式。

<a id="what-mcp-gives-you"></a>
## MCP 能为你带来什么

- 无需先编写原生 Hermes 工具，即可访问外部工具生态
- 在同一配置中同时支持本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，提供 MCP 资源和提示的实用包装器
- 支持按服务器进行过滤，因此你只暴露希望 Hermes 看到的 MCP 工具

<a id="quick-start"></a>
## 快速开始

1. 安装 MCP 支持（如果你使用了标准安装脚本，则已包含）：

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

4. 让 Hermes 使用基于 MCP 的能力。

例如：

```text
列出 /home/user/projects 中的文件，并总结仓库结构。
```

Hermes 会自动发现 MCP 服务器的工具，并像使用其他工具一样使用它们。

<a id="two-kinds-of-mcp-servers"></a>
## 两种 MCP 服务器

<a id="stdio-servers"></a>
### Stdio 服务器

Stdio 服务器作为本地子进程运行，通过标准输入/输出进行通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况下使用 stdio 服务器：
- 服务器已安装在本地
- 你需要低延迟访问本地资源
- 你遵循的 MCP 服务器文档中展示了 `command`、`args` 和 `env`

<a id="http-servers"></a>
### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

在以下情况下使用 HTTP 服务器：
- MCP 服务器托管在其他地方
- 你的组织暴露了内部 MCP 端点
- 你不想让 Hermes 为该集成启动本地子进程

<a id="basic-configuration-reference"></a>
## 基本配置参考

Hermes 从 `~/.hermes/config.yaml` 的 `mcp_servers` 下读取 MCP 配置。

<a id="common-keys"></a>
### 通用键

| 键 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行文件 |
| `args` | 列表 | stdio 服务器的参数 |
| `env` | 映射 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 端点 |
| `headers` | 映射 | 远程服务器的 HTTP 头 |
| `timeout` | 数字 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 初始连接超时时间 |
| `enabled` | 布尔值 | 如果为 `false`，Hermes 将完全跳过该服务器 |
| `supports_parallel_tool_calls` | 布尔值 | 如果为 `true`，该服务器的工具可以并发运行 |
| `tools` | 映射 | 按服务器进行工具过滤和实用策略配置 |
<a id="minimal-stdio-example"></a>
### 最小化 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

<a id="minimal-http-example"></a>
### 最小化 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

<a id="built-in-presets"></a>
## 内置预设

对于已知的 MCP 服务器，`hermes mcp add` 支持 `--preset` 标志，可自动填充传输细节，免去查找命令和参数的麻烦。预设只提供默认值——你在同一命令行上传入的其他内容（环境变量、请求头、过滤规则）仍然会覆盖预设。

| 预设 | 绑定的内容 |
|---|---|
| `codex` | Codex CLI 的 MCP 服务器（`codex mcp-server` 基于 stdio）。需要 `codex` CLI 在 PATH 中。 |

```bash
# 一行命令将 Codex CLI 添加为 MCP 服务器
hermes mcp add codex --preset codex
```

这相当于写入以下配置：

```yaml
mcp_servers:
  codex:
    command: "codex"
    args: ["mcp-server"]
```

你可以选择任何本地名称（例如 `hermes mcp add my-codex --preset codex` 也是可以的）；预设仅提供 `command`/`args` 的默认值。

<a id="how-hermes-registers-mcp-tools"></a>
## Hermes 如何注册 MCP 工具

Hermes 会给 MCP 工具添加前缀，以避免与内置名称冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

在实际使用中，你通常无需手动调用带前缀的名称——Hermes 会在正常推理过程中看到该工具并自动选择它。

<a id="mcp-utility-tools"></a>
## MCP 实用工具

当支持时，Hermes 还会围绕 MCP 资源和提示注册一些实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具按服务器注册，使用相同的前缀模式，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

<a id="important"></a>
### 重要提示

这些实用工具现在具备能力感知：
- Hermes 仅当 MCP 会话实际支持资源操作时，才注册资源实用工具
- Hermes 仅当 MCP 会话实际支持提示操作时，才注册提示实用工具

因此，如果一个服务器暴露了可调用的工具但没有资源/提示，则不会获得这些额外的封装。

<a id="per-server-filtering"></a>
## 按服务器过滤

你可以控制每个 MCP 服务器向 Hermes 贡献哪些工具，从而实现对工具命名空间的细粒度管理。

<a id="disable-a-server-entirely"></a>
### 完全禁用某个服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果 `enabled: false`，Hermes 会完全跳过该服务器，甚至不尝试建立连接。

<a id="whitelist-server-tools"></a>
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

仅注册这些 MCP 服务器工具。

<a id="blacklist-server-tools"></a>
### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```
除被排除的工具外，所有服务器工具都将注册。

<a id="precedence-rule"></a>
### 优先级规则

如果两者都存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 优先。

<a id="filter-utility-tools-too"></a>
### 同时过滤工具类工具

你还可以单独禁用 Hermes 添加的实用工具包装器：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 会禁用 `list_resources` 和 `read_resource`
- `tools.prompts: false` 会禁用 `list_prompts` 和 `get_prompt`

<a id="full-example"></a>
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

<a id="what-happens-if-everything-is-filtered-out"></a>
## 如果所有内容都被过滤掉会发生什么？

如果您的配置过滤掉了所有可调用工具，并禁用或省略了所有支持的实用工具，Hermes 不会为该服务器创建空的运行时 MCP 工具集。

这样可以保持工具列表的整洁。

<a id="runtime-behavior"></a>
## 运行时行为

<a id="discovery-time"></a>
### 发现时间

Hermes 在启动时发现 MCP 服务器，并将其工具注册到普通的工具注册中心中。

<a id="dynamic-tool-discovery"></a>
### 动态工具发现 {#dynamic-tool-discovery}

MCP 服务器可以在运行时通过发送 `notifications/tools/list_changed` 通知来告知 Hermes 其可用工具发生变化。Hermes 收到此通知后，会自动重新获取服务器的工具列表并更新注册中心——无需手动执行 `/reload-mcp`。

这对于能力动态变化的 MCP 服务器非常有用（例如，当加载新的数据库模式时添加工具，或当服务离线时移除工具的服务器）。

刷新操作受锁保护，因此来自同一服务器的快速通知不会导致重叠刷新。提示和资源变更通知（`prompts/list_changed`、`resources/list_changed`）会被接收，但尚未对其执行操作。

<a id="reloading"></a>
### 重载

如果更改了 MCP 配置，请使用：

```text
/reload-mcp
```

这会从配置中重新加载 MCP 服务器，并刷新可用工具列表。对于服务器自身推送的运行时工具变更，请参见上面的[动态工具发现](#dynamic-tool-discovery)。

<a id="toolsets"></a>
### 工具集

每个配置的 MCP 服务器在提供至少一个已注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集级别更容易理解 MCP 服务器。

<a id="security-model"></a>
## 安全模型

<a id="stdio-env-filtering"></a>
### Stdio 环境变量过滤

对于 stdio 服务器，Hermes 不会盲目地传递您的完整 shell 环境。

只有明确配置的 `env` 加上安全基线会被传递。这减少了意外的秘密泄露。

<a id="config-level-exposure-control"></a>
### 配置级的暴露控制

新的过滤支持也是一种安全控制：
- 禁用您不希望模型看到的危险工具
- 为敏感服务器仅暴露最小白名单
- 当您不希望暴露该表面时禁用资源/提示包装器
<a id="example-use-cases"></a>
## 使用示例

<a id="github-server-with-a-minimal-issue-management-surface"></a>
### 提供极简问题管理功能的 GitHub 服务器

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

使用方式如下：

```text
Show me open issues labeled bug, then draft a new issue for the flaky MCP reconnection behavior.
```

<a id="stripe-server-with-dangerous-actions-removed"></a>
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

使用方式如下：

```text
Look up the last 10 failed payments and summarize common failure reasons.
```

<a id="filesystem-server-for-a-single-project-root"></a>
### 单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

使用方式如下：

```text
Inspect the project root and explain the directory layout.
```

<a id="troubleshooting"></a>
## 故障排除

<a id="mcp-server-not-connecting"></a>
### MCP 服务器无法连接

检查：

```bash
# 确认 MCP 依赖已安装（标准安装中已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

然后验证配置并重启 Hermes。

<a id="tools-not-appearing"></a>
### 工具未出现

可能的原因：
- 服务器连接失败
- 发现过程失败
- 你的过滤配置排除了这些工具
- 该服务器上不存在此 utility 能力
- 服务器已通过 `enabled: false` 禁用

如果你是有意过滤的，则属于预期行为。

<a id="why-didn-t-resource-or-prompt-utilities-appear"></a>
### 为什么 resource 或 prompt utility 没有出现？

因为 Hermes 现在只在以下两个条件都为真时才注册这些包装器：
1. 你的配置允许它们
2. 服务器会话实际支持该能力

这是有意为之，可以保持工具列表的准确性。

<a id="parallel-tool-calls"></a>
## 并行工具调用

默认情况下，MCP 工具是顺序执行的——一次一个。如果你的 MCP 服务器暴露的工具可以安全地并发运行（例如只读查询、独立的 API 调用），你可以选择开启并行执行：

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

当 `supports_parallel_tool_calls` 为 `true` 时，Hermes 可以在单个工具调用批次中同时执行该服务器上的多个工具，就像它对内置只读工具（web_search、read_file 等）所做的那样。

:::caution
仅为工具能安全同时运行的 MCP 服务器启用并行调用。如果工具会读写共享状态、文件、数据库或外部资源，请在启用该设置前检查读写竞态条件。
:::

<a id="mcp-sampling-support"></a>
## MCP Sampling 支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这允许 MCP 服务器要求 Hermes 代其生成文本——适用于需要 LLM 能力但自身没有模型访问权限的服务器。

Sampling 默认对所有 MCP 服务器**启用**（前提是 MCP SDK 支持）。可以在每个服务器下的 `sampling` 键中配置：
```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # Enable sampling (default: true)
      model: "openai/gpt-4o"  # Override model for sampling requests (optional)
      max_tokens_cap: 4096     # Max tokens per sampling response (default: 4096)
      timeout: 30              # Timeout in seconds per request (default: 30)
      max_rpm: 10              # Rate limit: max requests per minute (default: 10)
      max_tool_rounds: 5       # Max tool-use rounds in sampling loops (default: 5)
      allowed_models: []       # Allowlist of model names the server may request (empty = any)
      log_level: "info"        # Audit log level: debug, info, or warning (default: info)
```

采样处理器包含一个滑动窗口速率限制器、每个请求的超时机制以及工具循环深度限制，以防止无节制使用。每个服务器实例会跟踪指标（请求计数、错误数、消耗的 token 数）。

要禁用某个服务器的采样：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

<a id="running-hermes-as-an-mcp-server"></a>
## 以 MCP 服务器模式运行 Hermes

除了连接到 MCP 服务器，Hermes 本身也可以**成为**一个 MCP 服务器。这让其他具备 MCP 能力的 agents（如 Claude Code、Cursor、Codex 或任何 MCP 客户端）能够使用 Hermes 的消息功能——列出对话、读取消息历史以及在所有已连接的平台上发送消息。

<a id="when-to-use-this"></a>
### 适用场景

- 你想让 Claude Code、Cursor 或其他编码 agent 通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 你想要一个单一的 MCP 服务器，一次性桥接到 Hermes 所连接的所有消息平台
- 你已经有一个正在运行的 Hermes 网关，并且已经连接了各个平台

<a id="quick-start"></a>
### 快速启动

```bash
hermes mcp serve
```

这会启动一个 stdio MCP 服务器。MCP 客户端（而不是你）负责管理进程生命周期。

<a id="mcp-client-configuration"></a>
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

或者如果你在特定位置安装了 Hermes：

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

<a id="available-tools"></a>
### 可用工具

MCP 服务器暴露了 10 个工具，对应于 OpenClaw 的通道桥接接口，外加一个 Hermes 专用的通道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息对话。可按平台过滤或按名称搜索。 |
| `conversation_get` | 通过会话键获取单个对话的详细信息。 |
| `messages_read` | 读取某个对话的最近消息历史。 |
| `attachments_fetch` | 提取特定消息中的非文本附件（图片、媒体）。 |
| `events_poll` | 从某个游标位置开始轮询新的对话事件。 |
| `events_wait` | 长轮询 / 阻塞直到下一个事件到达（近实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上可用的消息目标。 |
| `permissions_list_open` | 列出在此桥接会话期间观察到的待审批请求。 |
| `permissions_respond` | 允许或拒绝一个待处理的审批请求。 |
<a id="event-system"></a>
### 事件系统

MCP 服务器包含一个实时事件桥接器，它会轮询 Hermes 的会话数据库以获取新消息。这使得 MCP 客户端能够近乎实时地感知传入的对话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（阻塞直到超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`

事件队列位于内存中，并在桥接器连接时启动。旧消息可通过 `messages_read` 获取。

<a id="options"></a>
### 选项

```bash
hermes mcp serve              # 正常模式
hermes mcp serve --verbose    # 在 stderr 上输出调试日志
```

<a id="how-it-works"></a>
### 工作原理

MCP 服务器直接从 Hermes 的会话存储（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）读取会话数据。一个后台线程轮询数据库以获取新消息，并维护一个内存中的事件队列。对于发送消息，它使用与 Hermes Agent 自身相同的 `send_message` 基础设施。

网关**不需要**运行即可执行读取操作（列出会话、读取历史记录、轮询事件）。但发送操作**确实需要**网关运行，因为平台适配器需要保持活动连接。

<a id="current-limits"></a>
### 当前限制

- 内嵌的 `hermes mcp serve` 当前仅暴露一个**仅 stdio** 的 MCP 服务器。如果你需要 HTTP MCP 服务器，请运行一个独立的适配器——或者更常见的做法是，使用 Hermes 的 MCP **客户端** 侧，它已经支持 stdio 和 HTTP（在 `mcp_servers.yaml` / `config.yaml` 中配置 `url` + `headers`；参见上文中的 [HTTP 服务器](#http-servers)）。
- 事件轮询间隔约 200ms，通过 mtime 优化的数据库轮询实现（文件未变化时跳过工作）
- 尚未支持 `claude/channel` 推送通知协议
- 仅支持纯文本发送（无法通过 `messages_send` 发送媒体/附件）

<a id="related-docs"></a>
## 相关文档

- [将 MCP 与 Hermes 搭配使用](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [斜杠命令](/reference/slash-commands)
- [常见问题](/reference/faq)
