---
title: "Native Mcp — MCP 客户端：连接服务器，注册工具（stdio/HTTP）"
sidebar_label: "Native Mcp"
description: "MCP 客户端：连接服务器，注册工具（stdio/HTTP）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="native-mcp"></a>
# Native Mcp

MCP 客户端：连接服务器，注册工具（stdio/HTTP）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mcp/native-mcp` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `MCP`、`Tools`、`Integrations` |
| 相关技能 | [`mcporter`](/user-guide/skills/optional/mcp/mcp-mcporter) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是一旦此技能被触发，Hermes 所加载的完整技能定义。当技能激活时，Agent 将看到这些指令。
:::

<a id="native-mcp-client"></a>
# Native MCP Client

Hermes Agent 内置了一个 MCP 客户端，它会在启动时连接到 MCP 服务器，发现服务器的工具，并将它们作为一级工具供 Agent 直接调用。无需使用 CLI 桥接——来自 MCP 服务器的工具将与 `terminal`、`read_file` 等内置工具一同出现。

<a id="when-to-use"></a>
## 何时使用

当你希望实现以下目的时，可使用此技能：
- 连接 MCP 服务器，并在 Hermes Agent 中使用它们的工具
- 通过 MCP 添加外部能力（文件系统访问、GitHub、数据库、API 等）
- 运行基于 stdio 的本地 MCP 服务器（npx、uvx 或任意命令）
- 连接远程的 HTTP/StreamableHTTP MCP 服务器
- 让 MCP 工具自动被发现并在每次对话中可用

如果需要从终端临时、一次性调用 MCP 工具（无需任何配置），请改用 `mcporter` 技能。

<a id="prerequisites"></a>
## 前提条件

- **mcp Python 包**——可选依赖项；通过 `pip install mcp` 安装。如果未安装，MCP 支持将被静默禁用。
- **Node.js**——基于 `npx` 的 MCP 服务器（大多数社区服务器）需要此环境
- **uv**——基于 `uvx` 的 MCP 服务器（基于 Python 的服务器）需要此环境

安装 MCP SDK：

```bash
pip install mcp
# 或者，如果使用 uv：
uv pip install mcp
```

<a id="quick-start"></a>
## 快速开始

在 `~/.hermes/config.yaml` 文件的 `mcp_servers` 键下添加 MCP 服务器：

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

重启 Hermes Agent。启动时，它将：
1. 连接到服务器
2. 发现可用的工具
3. 以 `mcp_time_*` 前缀注册这些工具
4. 将它们注入到所有平台工具集中

然后你就可以自然地使用这些工具——只需让 Agent 获取当前时间即可。

<a id="configuration-reference"></a>
## 配置参考

`mcp_servers` 下的每个条目都是一个服务器名称，映射到其配置。有两种传输类型：**stdio**（基于命令）和 **HTTP**（基于 URL）。

<a id="stdio-transport-command-args"></a>
### Stdio 传输（命令 + 参数）

```yaml
mcp_servers:
  server_name:
    command: "npx"             # （必填）要运行的可执行文件
    args: ["-y", "pkg-name"]   # （可选）命令参数，默认值：[]
    env:                       # （可选）子进程的环境变量
      SOME_API_KEY: "value"
    timeout: 120               # （可选）每次工具调用的超时时间（秒），默认值：120
    connect_timeout: 60        # （可选）初始连接超时时间（秒），默认值：60
```
<a id="http-transport-url"></a>
### HTTP 传输（url）

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # （必填）服务器 URL
    headers:                                     # （可选）HTTP 请求头
      Authorization: "Bearer sk-..."
    timeout: 180               # （可选）每次工具调用超时时间（秒），默认：120
    connect_timeout: 60        # （可选）初始连接超时时间（秒），默认：60
```

<a id="all-config-options"></a>
### 所有配置选项

| 选项               | 类型   | 默认值    | 描述                                       |
|-------------------|--------|---------|---------------------------------------------------|
| `command`         | string | --      | 要运行的可执行文件（stdio 传输，必填）     |
| `args`            | list   | `[]`    | 传递给命令的参数                   |
| `env`             | dict   | `{}`    | 子进程的额外环境变量              |
| `url`             | string | --      | 服务器 URL（HTTP 传输，必填）             |
| `headers`         | dict   | `{}`    | 每次请求时发送的 HTTP 请求头              |
| `timeout`         | int    | `120`   | 每次工具调用的超时时长（秒）                  |
| `connect_timeout` | int    | `60`    | 初始连接和发现的超时时间                  |

注意：一个服务器配置必须包含 `command`（stdio）或 `url`（HTTP），不能同时存在。

<a id="how-it-works"></a>
## 工作原理

<a id="startup-discovery"></a>
### 启动时发现（Discovery）

当 Hermes Agent 启动时，在工具初始化期间会调用 `discover_mcp_tools()`：

1. 从 `~/.hermes/config.yaml` 读取 `mcp_servers`
2. 对于每个服务器，在专用的后台事件循环中建立一个连接
3. 初始化 MCP 会话并调用 `list_tools()` 发现可用工具
4. 将每个工具注册到 Hermes 工具注册表中

<a id="tool-naming-convention"></a>
### 工具命名约定

MCP 工具按以下命名模式注册：

```
mcp_{服务器名称}_{工具名称}
```

名称中的连字符和点号会被替换为下划线，以兼容 LLM API。

示例：
- 服务器 `filesystem`，工具 `read_file` → `mcp_filesystem_read_file`
- 服务器 `github`，工具 `list-issues` → `mcp_github_list_issues`
- 服务器 `my-api`，工具 `fetch.data` → `mcp_my_api_fetch_data`

<a id="auto-injection"></a>
### 自动注入

发现后，MCP 工具会自动注入到所有 `hermes-*` 平台工具集（CLI、Discord、Telegram 等）中。这意味着无需额外配置，MCP 工具即可在每次对话中使用。

<a id="connection-lifecycle"></a>
### 连接生命周期

- 每个服务器作为后台守护线程中的一个长驻 asyncio 任务运行
- 连接在 Agent 进程的整个生命周期内保持
- 如果连接断开，会自动重连并采用指数退避策略（最多重试 5 次，最长退避 60 秒）
- Agent 关闭时，所有连接将被优雅关闭

<a id="idempotency"></a>
### 幂等性

`discover_mcp_tools()` 是幂等的——多次调用它只会连接尚未连接的服务器。失败的服务器会在后续调用中重试。

<a id="transport-types"></a>
## 传输类型

<a id="stdio-transport"></a>
### Stdio 传输

最常见的传输方式。Hermes 将 MCP 服务器作为子进程启动，并通过 stdin/stdout 进行通信。
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

子进程会继承一个**经过过滤**的环境（详见下方安全章节），以及你在 `env` 中指定的任何变量。

<a id="http-streamablehttp-transport"></a>
### HTTP / StreamableHTTP 传输

适用于远程或共享的 MCP 服务器。需要 `mcp` 包包含 HTTP 客户端支持（`mcp.client.streamable_http`）。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

如果你安装的 `mcp` 版本不支持 HTTP，该服务器会因 ImportError 而失败，其他服务器则正常运行。

<a id="security"></a>
## 安全

<a id="environment-variable-filtering"></a>
### 环境变量过滤

对于 stdio 服务器，Hermes **不会**将完整的 shell 环境传递给 MCP 子进程。只有以下安全基线变量会被继承：

- `PATH`、`HOME`、`USER`、`LANG`、`LC_ALL`、`TERM`、`SHELL`、`TMPDIR`
- 所有 `XDG_*` 变量

所有其他环境变量（API 密钥、令牌、机密信息）都会被排除，除非你通过 `env` 配置键显式添加它们。这可以防止意外将凭据泄露给不受信任的 MCP 服务器。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # 只有这个令牌会被传递给子进程
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

<a id="credential-stripping-in-error-messages"></a>
### 错误消息中的凭据脱敏

如果 MCP 工具调用失败，错误消息中任何类似凭据的模式都会在展示给 LLM 之前自动脱敏。这包括：

- GitHub PAT（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- Bearer 令牌
- 通用的 `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 模式

<a id="troubleshooting"></a>
## 故障排除

<a id="mcp-sdk-not-available-skipping-mcp-tool-discovery"></a>
### "MCP SDK not available -- skipping MCP tool discovery"

`mcp` Python 包未安装。请安装它：

```bash
pip install mcp
```

<a id="no-mcp-servers-configured"></a>
### "No MCP servers configured"

`~/.hermes/config.yaml` 中没有 `mcp_servers` 键，或者该键为空。请至少添加一个服务器。

<a id="failed-to-connect-to-mcp-server-x"></a>
### "Failed to connect to MCP server 'X'"

常见原因：
- **命令未找到**：`command` 对应的二进制文件不在 PATH 中。请确保 `npx`、`uvx` 或相关命令已安装。
- **包未找到**：对于 npx 服务器，npm 包可能不存在，或者需要在 args 中添加 `-y` 以自动安装。
- **超时**：服务器启动时间过长。请增加 `connect_timeout`。
- **端口冲突**：对于 HTTP 服务器，URL 可能无法访问。

<a id="mcp-server-x-requires-http-transport-but-mcp-client-streamablehttp-is-not-available"></a>
### "MCP server 'X' requires HTTP transport but mcp.client.streamable_http is not available"

你的 `mcp` 包版本不包含 HTTP 客户端支持。请升级：

```bash
pip install --upgrade mcp
```

<a id="tools-not-appearing"></a>
### 工具未显示

- 检查服务器是否列在 `mcp_servers` 下（而不是 `mcp` 或 `servers`）
- 确保 YAML 缩进正确
- 查看 Hermes Agent 启动日志中的连接消息
- 工具名称以 `mcp_{server}_{tool}` 为前缀——请查找该模式

<a id="connection-keeps-dropping"></a>
### 连接持续断开

客户端最多重试 5 次，采用指数退避策略（1 秒、2 秒、4 秒、8 秒、16 秒，上限 60 秒）。如果服务器根本不可达，则在 5 次尝试后放弃。请检查服务器进程和网络连接。
<a id="examples"></a>
## 示例

<a id="time-server-uvx"></a>
### 时间服务器（uvx）

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

注册 `mcp_time_get_current_time` 等工具。

<a id="filesystem-server-npx"></a>
### 文件系统服务器（npx）

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

注册 `mcp_filesystem_read_file`、`mcp_filesystem_write_file`、`mcp_filesystem_list_directory` 等工具。

<a id="github-server-with-authentication"></a>
### 带认证的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

注册 `mcp_github_list_issues`、`mcp_github_create_pull_request` 等工具。

<a id="remote-http-server"></a>
### 远程 HTTP 服务器

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

<a id="multiple-servers"></a>
### 多服务器

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
    timeout: 300
```

所有服务器上的所有工具都会被注册并同时可用。每个服务器的工具名称都带有其服务器名前缀，以避免冲突。

<a id="sampling-server-initiated-llm-requests"></a>
## 采样（服务器发起的 LLM 请求）

Hermes 支持 MCP 的 `sampling/createMessage` 能力 —— MCP 服务器可以在工具执行过程中通过 Agent 请求 LLM 补全。这支持了“Agent 参与式工作流”（数据分析、内容生成、决策制定等）。

**默认启用采样**。按服务器进行配置：

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # 默认：true
      model: "gemini-3-flash" # 模型覆盖（可选）
      max_tokens_cap: 4096    # 每次请求的最大 token 数
      timeout: 30             # LLM 调用超时（秒）
      max_rpm: 10             # 每分钟最大请求数
      allowed_models: []      # 模型白名单（空 = 全部允许）
      max_tool_rounds: 5      # 工具循环上限（0 = 禁用）
      log_level: "info"       # 审计详细程度
```

服务器也可以在采样请求中包含 `tools`，以支持多轮工具增强的工作流。`max_tool_rounds` 配置可防止无限工具循环。每台服务器的审计指标（请求数、错误数、token 数、工具使用次数）可通过 `get_mcp_status()` 追踪。

对于不信任的服务器，可使用 `sampling: { enabled: false }` 禁用采样。

<a id="notes"></a>
## 说明

- 从 Agent 的角度看，MCP 工具是同步调用的，但实际上在专用的后台事件循环中异步运行
- 工具结果以 JSON 返回，格式为 `{"result": "..."}` 或 `{"error": "..."}`
- 原生 MCP 客户端独立于 `mcporter` —— 你可以同时使用两者
- 服务器连接是持久的，并且在同一个 Agent 进程的所有对话中共享
- 添加或移除服务器需要重启 Agent（目前不支持热重载）
