---
sidebar_position: 8
title: "MCP 配置参考"
description: "Hermes Agent MCP 配置项、过滤语义及工具策略参考"
---

# MCP 配置参考 {#mcp-config-reference}

本页面是 MCP 主文档的简明参考手册。

有关概念性指南，请参阅：
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)

## 根配置结构 {#root-config-shape}

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio 服务器
    args: []
    env: {}

    # 或者
    url: "..."          # HTTP 服务器
    headers: {}

    enabled: true
    timeout: 120
    connect_timeout: 60
    tools:
      include: []
      exclude: []
      resources: true
      prompts: true
```

## 服务器配置项 (Server keys) {#server-keys}

| 键名 | 类型 | 适用范围 | 含义 |
|---|---|---|---|
| `command` | string | stdio | 要启动的可执行文件 |
| `args` | list | stdio | 传递给子进程的参数 |
| `env` | mapping | stdio | 传递给子进程的环境变量 |
| `url` | string | HTTP | 远程 MCP 端点地址 |
| `headers` | mapping | HTTP | 远程服务器请求的 HTTP 头 |
| `enabled` | bool | 两者均适用 | 为 false 时完全跳过该服务器 |
| `timeout` | number | 两者均适用 | 工具调用超时时间 |
| `connect_timeout` | number | 两者均适用 | 初始连接超时时间 |
| `tools` | mapping | 两者均适用 | 过滤规则与工具策略 |
| `auth` | string | HTTP | 身份验证方式。设置为 `oauth` 以启用带 PKCE 的 OAuth 2.1 |
| `sampling` | mapping | 两者均适用 | 服务器发起的 LLM 请求策略（见 MCP 指南） |

## `tools` 策略配置项 {#tools-policy-keys}

| 键名 | 类型 | 含义 |
|---|---|---|
| `include` | string 或 list | 服务器原生 MCP 工具的白名单 |
| `exclude` | string 或 list | 服务器原生 MCP 工具的黑名单 |
| `resources` | bool-like | 启用/禁用 `list_resources` + `read_resource` |
| `prompts` | bool-like | 启用/禁用 `list_prompts` + `get_prompt` |

## 过滤语义 {#filtering-semantics}

### `include` {#include}

如果设置了 `include`，则仅注册指定的服务器原生 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude` {#exclude}

如果设置了 `exclude` 而未设置 `include`，则除了名单中的工具外，所有服务器原生 MCP 工具都会被注册。

```yaml
tools:
  exclude: [delete_customer]
```

### 优先级 {#precedence}

如果两者都设置了，以 `include` 为准。

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

结果：
- `create_issue` 仍被允许
- `delete_issue` 被忽略，因为 `include` 具有更高优先级

## 工具策略 (Utility-tool policy) {#utility-tool-policy}

Hermes 可能会为每个 MCP 服务器注册以下工具包装器：

资源 (Resources)：
- `list_resources`
- `read_resource`

提示词 (Prompts)：
- `list_prompts`
- `get_prompt`

### 禁用资源 {#disable-resources}

```yaml
tools:
  resources: false
```

### 禁用提示词 {#disable-prompts}

```yaml
tools:
  prompts: false
```

### 基于能力的注册 {#capability-aware-registration}

即使设置了 `resources: true` 或 `prompts: true`，Hermes 也只有在 MCP 会话确实暴露了相应能力时，才会注册这些工具。

因此，以下情况是正常的：
- 你启用了提示词 (prompts)
- 但没有出现提示词相关的工具
- 因为该服务器本身不支持提示词功能

## `enabled: false` {#enabled-false}

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

行为：
- 不尝试连接
- 不进行发现 (discovery)
- 不注册工具
- 配置保留在原处以便日后重用

## 空结果行为 {#empty-result-behavior}

如果过滤规则移除了所有服务器原生工具，且没有注册任何工具，Hermes 不会为该服务器创建空的 MCP 运行时工具集。

## 配置示例 {#example-configs}

### 安全的 GitHub 白名单 {#safe-github-allowlist}

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

### Stripe 黑名单 {#stripe-blacklist}

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 仅限资源的文档服务器 {#resource-only-docs-server}

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

## 重新加载配置 {#reloading-config}

更改 MCP 配置后，使用以下命令重新加载服务器：

```text
/reload-mcp
```

## 工具命名规则 {#tool-naming}

服务器原生 MCP 工具的命名格式为：

```text
mcp_<server>_<tool>
```

示例：
- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

工具也遵循相同的前缀模式：
- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`

### 名称清洗 (Sanitization) {#name-sanitization}

在注册之前，服务器名称和工具名称中的连字符 (`-`) 和点 (`.`) 都会被替换为下划线。这确保了工具名称是 LLM 函数调用 API 的有效标识符。

例如，一个名为 `my-api` 的服务器暴露了一个名为 `list-items.v2` 的工具，其名称将变为：

```text
mcp_my_api_list_items_v2
```

在编写 `include` / `exclude` 过滤器时请记住这一点——请使用 **原始** MCP 工具名称（带有连字符/点），而不是清洗后的版本。

## OAuth 2.1 身份验证 {#oauth-2-1-authentication}

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
- 令牌将持久化到 `~/.hermes/mcp-tokens/<server>.json` 并在不同会话间重用
- 令牌刷新是自动的；只有在刷新失败时才会重新授权
- 仅适用于 HTTP/StreamableHTTP 传输（基于 `url` 的服务器）
