---
sidebar_position: 4
title: "MCP（模型上下文协议）"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器——并精确控制 Hermes 加载哪些 MCP 工具"
---

# MCP（模型上下文协议）

MCP 让 Hermes Agent 能够连接到外部工具服务器，从而使用那些不在 Hermes 内部的工具——比如 GitHub、数据库、文件系统、浏览器栈、内部 API 等等。

如果你曾经想让 Hermes 使用已经存在于其他地方的工具，MCP 通常是最干净利落的方式。

## MCP 带给你的好处

- 无需先编写本地 Hermes 工具，就能访问外部工具生态
- 同一配置中支持本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，提供 MCP 资源和提示的实用封装
- 支持按服务器过滤，只暴露你希望 Hermes 看到的 MCP 工具

## 快速开始

1. 安装 MCP 支持（如果你用的是标准安装脚本，已经包含了）：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

2. 在 `~/.hermes/config.yaml` 中添加 MCP 服务器：

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

4. 让 Hermes 使用 MCP 支持的功能。

例如：

```text
列出 /home/user/projects 目录下的文件，并总结仓库结构。
```

Hermes 会发现 MCP 服务器的工具，并像使用其他工具一样调用它们。

## 两种 MCP 服务器类型

### Stdio 服务器

Stdio 服务器作为本地子进程运行，通过 stdin/stdout 通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

使用 stdio 服务器的场景：
- 服务器安装在本地
- 需要低延迟访问本地资源
- 遵循 MCP 服务器文档中展示的 `command`、`args` 和 `env` 配置

### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

使用 HTTP 服务器的场景：
- MCP 服务器托管在远程
- 组织内部暴露了 MCP 内部端点
- 不希望 Hermes 为该集成启动本地子进程

## 基础配置参考

Hermes 从 `~/.hermes/config.yaml` 的 `mcp_servers` 节读取 MCP 配置。

### 常用键名

| 键名 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行命令 |
| `args` | 列表 | stdio 服务器的参数 |
| `env` | 映射 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 端点地址 |
| `headers` | 映射 | 远程服务器的 HTTP 头 |
| `timeout` | 数字 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 初始连接超时时间 |
| `enabled` | 布尔 | 如果为 `false`，Hermes 会完全跳过该服务器 |
| `tools` | 映射 | 按服务器过滤工具和实用策略 |

### 最简 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 最简 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## Hermes 如何注册 MCP 工具

Hermes 会给 MCP 工具加前缀，避免与内置名称冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

实际上，你通常不需要手动调用带前缀的名称——Hermes 会自动识别并在推理过程中选择合适的工具。

## MCP 实用工具

当服务器支持时，Hermes 还会注册围绕 MCP 资源和提示的实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具按服务器同样使用前缀模式注册，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要说明

这些实用工具现在具备能力感知：
- 只有当 MCP 会话实际支持资源操作时，Hermes 才注册资源相关工具
- 只有当 MCP 会话实际支持提示操作时，Hermes 才注册提示相关工具

因此，如果服务器只暴露可调用工具，但没有资源或提示，则不会注册这些额外的封装工具。

## 按服务器过滤

你可以控制每个 MCP 服务器贡献给 Hermes 的工具，实现对工具命名空间的精细管理。

### 完全禁用服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果设置 `enabled: false`，Hermes 会完全跳过该服务器，甚至不尝试连接。

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

只注册这些 MCP 服务器工具。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

注册该服务器的所有工具，除了被排除的。

### 优先级规则

如果同时存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

以 `include` 为准。

### 也过滤实用工具

你还可以单独禁用 Hermes 添加的实用封装：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 禁用 `list_resources` 和 `read_resource`
- `tools.prompts: false` 禁用 `list_prompts` 和 `get_prompt`

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

## 如果所有工具都被过滤掉会怎样？

如果配置过滤掉了所有可调用工具，并且禁用了或省略了所有支持的实用工具，Hermes 不会为该服务器创建空的运行时 MCP 工具集。

这样可以保持工具列表的整洁。

## 运行时行为

### 发现阶段

Hermes 在启动时发现 MCP 服务器，并将它们的工具注册到常规工具注册表中。

### 动态工具发现 {#dynamic-tool-discovery}

MCP 服务器可以通过发送 `notifications/tools/list_changed` 通知，告知 Hermes 其可用工具在运行时发生变化。Hermes 收到该通知后，会自动重新获取服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp`。

这对那些能力动态变化的 MCP 服务器非常有用（例如，加载新数据库模式时添加工具，或服务下线时移除工具）。

刷新操作有锁保护，避免同一服务器的快速连续通知导致刷新重叠。提示和资源变更通知（`prompts/list_changed`、`resources/list_changed`）目前已接收但尚未处理。

### 重新加载

如果你修改了 MCP 配置，使用：

```text
/reload-mcp
```

这会从配置重新加载 MCP 服务器并刷新可用工具列表。对于服务器主动推送的运行时工具变更，请参见上文的[动态工具发现](#dynamic-tool-discovery)。

### 工具集

每个配置的 MCP 服务器在贡献至少一个注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这样可以更方便地从工具集层面管理 MCP 服务器。

## 安全模型

### Stdio 环境过滤

对于 stdio 服务器，Hermes 不会盲目传递你完整的 shell 环境。
只有显式配置的 `env` 加上一个安全的基线会被传递。这可以减少意外泄露秘密的风险。

### 配置级别的暴露控制

新的过滤支持也是一种安全控制手段：
- 禁用你不希望模型看到的危险工具
- 仅为敏感服务器暴露最小的白名单
- 当你不想暴露资源/提示包装时禁用它们

## 示例用例

### 具有最小问题管理界面的 GitHub 服务器

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

使用示例：

```text
Show me open issues labeled bug, then draft a new issue for the flaky MCP reconnection behavior.
```

### 移除危险操作的 Stripe 服务器

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

使用示例：

```text
Look up the last 10 failed payments and summarize common failure reasons.
```

### 针对单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

使用示例：

```text
Inspect the project root and explain the directory layout.
```

## 故障排查

### MCP 服务器无法连接

检查：

```bash
# 验证 MCP 依赖是否已安装（标准安装已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

然后验证你的配置并重启 Hermes。

### 工具未显示

可能原因：
- 服务器连接失败
- 发现失败
- 你的过滤配置排除了这些工具
- 该服务器不支持该实用功能
- 服务器被设置为 `enabled: false` 禁用

如果你是有意进行过滤，这是正常现象。

### 为什么资源或提示实用工具没有出现？

因为 Hermes 现在只有在以下两个条件都满足时才注册这些包装器：
1. 你的配置允许它们
2. 服务器会话实际支持该功能

这是有意为之，保证工具列表的准确性。

## MCP 采样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这允许 MCP 服务器代表自己让 Hermes 生成文本——适用于需要 LLM 功能但没有自己模型访问权限的服务器。

采样对所有 MCP 服务器默认**启用**（前提是 MCP SDK 支持）。可在每个服务器下通过 `sampling` 键配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # 启用采样（默认：true）
      model: "openai/gpt-4o"  # 采样请求覆盖模型（可选）
      max_tokens_cap: 4096     # 每次采样响应最大 token 数（默认：4096）
      timeout: 30              # 每次请求超时秒数（默认：30）
      max_rpm: 10              # 速率限制：每分钟最大请求数（默认：10）
      max_tool_rounds: 5       # 采样循环中最大工具使用轮数（默认：5）
      allowed_models: []       # 服务器可请求的模型白名单（空表示任意）
      log_level: "info"        # 审计日志级别：debug、info 或 warning（默认：info）
```

采样处理器包含滑动窗口速率限制、每请求超时和工具循环深度限制，防止滥用。指标（请求数、错误、使用的 token）按服务器实例跟踪。

要禁用某个服务器的采样：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## 以 MCP 服务器身份运行 Hermes {#running-hermes-as-an-mcp-server}

除了连接**到** MCP 服务器，Hermes 也可以**作为** MCP 服务器。这让其他支持 MCP 的 Agents（Claude Code、Cursor、Codex 或任何 MCP 客户端）使用 Hermes 的消息功能——列出会话、读取消息历史、跨所有连接平台发送消息。

### 何时使用

- 你希望 Claude Code、Cursor 或其他编码 Agent 通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 你想要一个 MCP 服务器桥接 Hermes 所有连接的消息平台
- 你已经有一个运行中的 Hermes 网关连接了多个平台

### 快速开始

```bash
hermes mcp serve
```

这会启动一个 stdio MCP 服务器。MCP 客户端（不是你）管理进程生命周期。

### MCP 客户端配置

将 Hermes 添加到你的 MCP 客户端配置。例如，在 Claude Code 的 `~/.claude/claude_desktop_config.json` 中：

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

或者如果你把 Hermes 安装在特定位置：

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

MCP 服务器暴露了 10 个工具，匹配 OpenClaw 的频道桥接界面外加 Hermes 特有的频道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息会话。可按平台过滤或按名称搜索。 |
| `conversation_get` | 通过会话键获取单个会话的详细信息。 |
| `messages_read` | 读取会话的近期消息历史。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图片、媒体）。 |
| `events_poll` | 从游标位置轮询新的会话事件。 |
| `events_wait` | 长轮询/阻塞直到下一个事件到达（近实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上的可用消息目标。 |
| `permissions_list_open` | 列出本桥接会话中观察到的待审批请求。 |
| `permissions_respond` | 允许或拒绝待审批请求。 |

### 事件系统

MCP 服务器包含一个实时事件桥，轮询 Hermes 的会话数据库以获取新消息。这让 MCP 客户端几乎实时感知新会话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（阻塞，最长到超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`

事件队列在内存中，连接桥接时启动。旧消息可通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # 普通模式
hermes mcp serve --verbose    # 在 stderr 输出调试日志
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储读取会话数据（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）。后台线程轮询数据库获取新消息，维护内存中的事件队列。发送消息时，使用与 Hermes Agent 本身相同的 `send_message` 基础设施。

读取操作（列会话、读历史、轮询事件）不需要网关运行。发送操作需要网关运行，因为平台适配器需要保持活跃连接。

### 当前限制

- 仅支持 stdio 传输（尚无 HTTP MCP 传输）
- 事件轮询通过 mtime 优化的数据库轮询，间隔约 200ms（文件未变时跳过）
- 尚无 `claude/channel` 推送通知协议
- 仅支持文本发送（`messages_send` 不支持媒体/附件发送）

## 相关文档

- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [斜杠命令](/reference/slash-commands)
- [常见问题](/reference/faq)
