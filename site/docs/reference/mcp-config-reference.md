---
sidebar_position: 8
title: "MCP 配置参考"
description: "Hermes Agent MCP 配置键、过滤语义及工具策略参考"
---

# MCP 配置参考

本文档是主 MCP 文档的简明参考手册。

概念性指南请参阅：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)

## 根配置结构

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio 服务器
    args: []
    env: {}

    # 或
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

## 服务器配置键

| 键 | 类型 | 适用对象 | 含义 |
|---|---|---|---|
| `command` | 字符串 | stdio | 要启动的可执行文件 |
| `args` | 列表 | stdio | 子进程的参数 |
| `env` | 映射 | stdio | 传递给子进程的环境变量 |
| `url` | 字符串 | HTTP | 远程 MCP 端点 |
| `headers` | 映射 | HTTP | 远程服务器请求的请求头 |
| `enabled` | 布尔值 | 两者 | 为 false 时完全跳过该服务器 |
| `timeout` | 数字 | 两者 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 两者 | 初始连接超时时间 |
| `tools` | 映射 | 两者 | 过滤和工具策略 |

## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 服务器原生 MCP 工具的白名单 |
| `exclude` | 字符串或列表 | 服务器原生 MCP 工具的黑名单 |
| `resources` | 类布尔值 | 启用/禁用 `list_resources` + `read_resource` |
| `prompts` | 类布尔值 | 启用/禁用 `list_prompts` + `get_prompt` |

## 过滤语义

### `include`

如果设置了 `include`，则只注册这些服务器原生的 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

如果设置了 `exclude` 且未设置 `include`，则注册除这些名称外的所有服务器原生 MCP 工具。

```yaml
tools:
  exclude: [delete_customer]
```

### 优先级

如果两者都设置，`include` 优先。

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

结果：
- `create_issue` 仍然被允许
- `delete_issue` 被忽略，因为 `include` 优先级更高

## 工具策略

Hermes 可能会为每个 MCP 服务器注册以下工具包装器：

资源类：
- `list_resources`
- `read_resource`

提示类：
- `list_prompts`
- `get_prompt`

### 禁用资源工具

```yaml
tools:
  resources: false
```

### 禁用提示工具

```yaml
tools:
  prompts: false
```

### 基于能力的注册

即使 `resources: true` 或 `prompts: true`，Hermes 也只在 MCP 会话实际暴露相应能力时，才会注册这些工具。

因此以下情况是正常的：
- 你启用了提示工具
- 但没有出现提示相关的工具
- 因为服务器不支持提示功能

## `enabled: false`

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

行为：
- 不尝试连接
- 不进行发现
- 不注册工具
- 配置保留，供后续重用

## 空结果行为

如果过滤移除了所有服务器原生工具，且没有注册任何工具，Hermes 不会为该服务器创建空的 MCP 运行时工具集。

## 配置示例

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

### 仅资源的文档服务器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

## 重新加载配置

更改 MCP 配置后，使用以下命令重新加载服务器：

```text
/reload-mcp
```

## 工具命名

服务器原生的 MCP 工具变为：

```text
mcp_<server>_<tool>
```

示例：
- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

工具遵循相同的前缀模式：
- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`
