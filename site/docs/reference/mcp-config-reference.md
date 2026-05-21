---
sidebar_position: 8
title: "MCP 配置参考"
description: "Hermes Agent MCP 配置键、过滤语义和实用工具策略的参考"
---

<a id="mcp-config-reference"></a>
# MCP 配置参考

此页面是 MCP 主文档的精简参考指南。

概念指南请参考：
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [将 MCP 与 Hermes 结合使用](/guides/use-mcp-with-hermes)

<a id="root-config-shape"></a>
## 根配置结构

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio servers
    args: []
    env: {}

    # OR
    url: "..."          # HTTP servers
    headers: {}

    enabled: true
    timeout: 120
    connect_timeout: 60
    supports_parallel_tool_calls: false
    tools:
      include: []
      exclude: []
      resources: true
      prompts: true
```

<a id="server-keys"></a>
## 服务器键

| 键 | 类型 | 适用对象 | 含义 |
|---|---|---|---|
| `command` | 字符串 | 标准输入/输出 | 要启动的可执行文件 |
| `args` | 列表 | 标准输入/输出 | 子进程的参数 |
| `env` | 映射 | 标准输入/输出 | 传递给子进程的环境变量 |
| `url` | 字符串 | HTTP | 远程 MCP 端点 |
| `headers` | 映射 | HTTP | 远程服务器请求的头 |
| `enabled` | 布尔值 | 两者 | 当为 false 时完全跳过该服务器 |
| `timeout` | 数字 | 两者 | 工具调用超时 |
| `connect_timeout` | 数字 | 两者 | 初始连接超时 |
| `supports_parallel_tool_calls` | 布尔值 | 两者 | 允许来自此服务器的工具并发运行 |
| `tools` | 映射 | 两者 | 过滤和实用工具策略 |
| `auth` | 字符串 | HTTP | 身份验证方法。设置为 `oauth` 以启用带 PKCE 的 OAuth 2.1 |
| `sampling` | 映射 | 两者 | 服务器发起的 LLM 请求策略（参见 MCP 指南） |

<a id="tools-policy-keys"></a>
## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 白名单服务器原生 MCP 工具 |
| `exclude` | 字符串或列表 | 黑名单服务器原生 MCP 工具 |
| `resources` | 布尔型 | 启用/禁用 `list_resources` 和 `read_resource` |
| `prompts` | 布尔型 | 启用/禁用 `list_prompts` 和 `get_prompt` |

<a id="filtering-semantics"></a>
## 过滤语义

<a id="include"></a>
### `include`

如果设置了 `include`，则仅注册这些服务器原生 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

<a id="exclude"></a>
### `exclude`

如果设置了 `exclude` 但未设置 `include`，则注册除这些名称之外的所有服务器原生 MCP 工具。

```yaml
tools:
  exclude: [delete_customer]
```

<a id="precedence"></a>
### 优先级

如果两者都设置了，`include` 优先。

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

结果：
- `create_issue` 仍然允许
- `delete_issue` 被忽略，因为 `include` 优先

<a id="utility-tool-policy"></a>
## 实用工具策略

Hermes 可以为每个 MCP 服务器注册这些实用工具包装器：

资源：
- `list_resources`
- `read_resource`

提示：
- `list_prompts`
- `get_prompt`

<a id="disable-resources"></a>
### 禁用资源

```yaml
tools:
  resources: false
```

<a id="disable-prompts"></a>
### 禁用提示

```yaml
tools:
  prompts: false
```

<a id="capability-aware-registration"></a>
### 能力感知注册

即使设置了 `resources: true` 或 `prompts: true`，Hermes 也仅在 MCP 会话实际暴露相应能力时才注册这些实用工具。

因此，以下是正常情况：
- 你启用了提示
- 但没有提示实用工具出现
- 因为服务器不支持提示
<a id="enabled-false"></a>
## `enabled: false`

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

行为：
- 不会尝试连接
- 不会发现资源
- 不注册工具
- 配置保留在原位，便于以后复用

<a id="empty-result-behavior"></a>
## 空结果行为

如果过滤移除了所有服务器原生工具，且没有注册任何实用工具，Hermes 不会为该服务器创建一个空的 MCP 运行时工具集。

<a id="example-configs"></a>
## 配置示例

<a id="safe-github-allowlist"></a>
### 安全的 GitHub 白名单

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      resources: false
      prompts: false
```

<a id="stripe-blacklist"></a>
### Stripe 黑名单

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

<a id="resource-only-docs-server"></a>
### 仅资源型文档服务器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

<a id="reloading-config"></a>
## 重新加载配置

修改 MCP 配置后，使用以下命令重新加载服务器：

```text
/reload-mcp
```

<a id="tool-naming"></a>
## 工具命名

服务器原生 MCP 工具会被命名为：

```text
mcp_<server>_<tool>
```

示例：
- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

实用工具遵循相同的前缀模式：
- `mcp_&lt;server&gt;_list_resources`
- `mcp_&lt;server&gt;_read_resource`
- `mcp_&lt;server&gt;_list_prompts`
- `mcp_&lt;server&gt;_get_prompt`

<a id="name-sanitization"></a>
### 名称清理

服务器名称和工具名称中的连字符（`-`）和点号（`.`）在注册前会被替换为下划线。这确保工具名称是 LLM 函数调用 API 的有效标识符。

例如，一个名为 `my-api` 的服务器暴露了一个名为 `list-items.v2` 的工具，会变成：

```text
mcp_my_api_list_items_v2
```

编写 `include` / `exclude` 过滤器时请记住这一点——使用 **原始** MCP 工具名称（带连字符/点号），而不是清理后的版本。

<a id="oauth-2-1-authentication"></a>
## OAuth 2.1 认证

对于需要 OAuth 的 HTTP 服务器，在服务器条目上设置 `auth: oauth`：

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

行为：
- Hermes 使用 MCP SDK 的 OAuth 2.1 PKCE 流程（元数据发现、动态客户端注册、令牌交换和刷新）
- 首次连接时，会打开浏览器窗口进行授权
- 令牌持久化到 `~/.hermes/mcp-tokens/&lt;server&gt;.json`，并在会话间复用
- 令牌刷新是自动的；仅在刷新失败时才需要重新授权
- 仅适用于 HTTP/StreamableHTTP 传输（基于 `url` 的服务器）
