---
sidebar_position: 6
title: "在 Hermes 中使用 MCP"
description: "将 MCP 服务连接到 Hermes Agent、过滤其工具并在实际工作流中安全使用它们的实用指南"
---

# 在 Hermes 中使用 MCP

本指南将展示如何在日常工作流中实际使用 MCP 与 Hermes Agent。

如果说功能介绍页解释了什么是 MCP，那么本指南则侧重于如何快速、安全地从中获取价值。

## 什么时候该使用 MCP？

在以下情况下使用 MCP：
- 某个工具已经以 MCP 形式存在，且你不想构建原生的 Hermes 工具
- 你希望 Hermes 通过一个清晰的 RPC 层对本地或远程系统进行操作
- 你希望对每个服务进行细粒度的曝光控制
- 你希望在不修改 Hermes 核心代码的情况下，将 Hermes 连接到内部 API、数据库或公司系统

在以下情况下不要使用 MCP：
- 内置的 Hermes 工具已经能很好地解决问题
- 该服务暴露了大量危险的工具接口，而你还没准备好对其进行过滤
- 你只需要一个非常简单的集成，此时原生工具会更简单、更安全

## 心理模型

将 MCP 视为一个适配层：

- Hermes 仍然是 Agent
- MCP 服务提供工具
- Hermes 在启动或重载时发现这些工具
- 模型可以像使用普通工具一样使用它们
- 你可以控制每个服务中有多少内容是可见的

最后一点至关重要。良好的 MCP 使用习惯不是“连接一切”，而是“以最小的有用接口连接正确的东西”。

## 第 1 步：安装 MCP 支持

如果你是使用标准安装脚本安装的 Hermes，那么 MCP 支持已经包含在内了（安装程序运行了 `uv pip install -e ".[all]"`）。

如果你安装时没有包含额外组件，需要单独添加 MCP 支持：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

对于基于 npm 的服务，请确保 Node.js 和 `npx` 可用。

对于许多 Python MCP 服务，使用 `uvx` 是一个不错的默认选择。

## 第 2 步：先添加一个服务

从单个、安全的服务开始。

例如：仅限访问一个项目目录的文件系统访问权限。

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

然后启动 Hermes：

```bash
hermes chat
```

现在尝试问一些具体的问题：

```text
检查这个项目并总结代码库的布局。
```

## 第 3 步：验证 MCP 是否加载

你可以通过以下几种方式验证 MCP：

- 配置完成后，Hermes 的横幅/状态应显示 MCP 集成信息
- 询问 Hermes 它有哪些可用工具
- 在修改配置后使用 `/reload-mcp`
- 如果服务连接失败，请检查日志

一个实用的测试提示词：

```text
告诉我当前有哪些由 MCP 支持的工具可用。
```

## 第 4 步：立即开始过滤

如果服务暴露了大量工具，不要等到以后再处理。

### 示例：仅将你需要的工具加入白名单

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

对于敏感系统，这通常是最佳的默认做法。

### 示例：黑名单禁用危险操作

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 示例：同时禁用辅助封装器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

## 过滤实际上会影响什么？

Hermes 中由 MCP 暴露的功能分为两类：

1. 服务原生 MCP 工具
- 使用以下项过滤：
  - `tools.include`
  - `tools.exclude`

2. Hermes 添加的辅助封装器
- 使用以下项过滤：
  - `tools.resources`
  - `tools.prompts`

### 你可能会看到的辅助封装器

资源（Resources）：
- `list_resources`
- `read_resource`

提示词（Prompts）：
- `list_prompts`
- `get_prompt`

这些封装器仅在以下情况出现：
- 你的配置允许它们，且
- 该 MCP 服务会话确实支持这些功能

因此，如果服务本身不支持资源/提示词，Hermes 不会假装它有。

## 常见模式

### 模式 1：本地项目助手

当你希望 Hermes 在限定的工作空间内进行推理时，为本地项目文件系统或 git 服务使用 MCP。

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

推荐提示词：

```text
审查项目结构并确定配置文件的位置。
```

```text
检查本地 git 状态并总结最近的更改。
```

### 模式 2：GitHub 分类助手

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false
```

推荐提示词：

```text
列出关于 MCP 的待处理 issue，按主题进行归类，并针对最常见的 bug 起草一个高质量的 issue。
```

```text
在代码库中搜索 _discover_and_register_server 的使用情况，并解释 MCP 工具是如何注册的。
```

### 模式 3：内部 API 助手

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      include: [list_customers, get_customer, list_invoices]
      resources: false
      prompts: false
```

推荐提示词：

```text
查找客户 ACME Corp 并总结最近的发票活动。
```

在这种场景下，严格的白名单比黑名单要好得多。

### 模式 4：文档 / 知识服务

某些 MCP 服务暴露的提示词或资源更像是共享的知识资产，而不是直接的操作。

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

推荐提示词：

```text
列出文档服务中可用的 MCP 资源，然后阅读入门指南并进行总结。
```

```text
列出文档服务暴露的提示词，并告诉我哪些提示词对事件响应有帮助。
```

## 教程：带过滤的端到端设置

这是一个实际的操作流程。

### 阶段 1：添加带严格白名单的 GitHub MCP

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
      prompts: false
      resources: false
```

启动 Hermes 并提问：

```text
在代码库中搜索对 MCP 的引用，并总结主要的集成点。
```

### 阶段 2：仅在需要时扩展

如果你稍后也需要更新 issue：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

然后重载：

```text
/reload-mcp
```

### 阶段 3：添加具有不同策略的第二个服务

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
```

现在 Hermes 可以将它们结合起来：

```text
检查本地项目文件，然后创建一个 GitHub issue 来总结你发现的 bug。
```

这就是 MCP 强大的地方：无需更改 Hermes 核心即可实现跨系统工作流。

## 安全使用建议

### 对危险系统优先使用允许列表（Allowlists）

对于任何涉及财务、面向客户或具有破坏性的操作：
- 使用 `tools.include`
- 从尽可能小的工具集开始

### 禁用未使用的辅助工具

如果你不希望模型浏览服务提供的资源/提示词，请关闭它们：

```yaml
tools:
  resources: false
  prompts: false
```

### 保持服务范围狭窄

示例：
- 文件系统服务的根目录设为一个项目目录，而不是你的整个家目录
- git 服务指向单个代码库
- 内部 API 服务默认仅暴露偏向读取的工具
### 配置更改后重新加载

```text
/reload-mcp
```

在修改以下内容后请执行此操作：
- include/exclude 列表
- enabled 标志
- resources/prompts 开关
- 认证请求头（auth headers）/ 环境变量（env）

## 按症状排查问题

### “服务器已连接，但我预期的工具缺失了”

可能的原因：
- 被 `tools.include` 过滤掉了
- 被 `tools.exclude` 排除掉了
- 通过 `resources: false` 或 `prompts: false` 禁用了工具封装器
- 服务器实际上并不支持 resources/prompts

### “服务器已配置，但没有任何内容加载”

检查：
- 配置中是否遗留了 `enabled: false`
- 命令/运行时环境是否存在（`npx`, `uvx` 等）
- HTTP 端点是否可访问
- 认证环境变量或请求头是否正确

### “为什么我看到的工具比 MCP server 宣称的要少？”

因为 Hermes 现在会遵循你为每个服务器设置的策略以及感知能力的注册机制。这是预期行为，通常也是我们希望看到的结果。

### “如何在不删除配置的情况下移除一个 MCP server？”

使用：

```yaml
enabled: false
```

这会保留配置，但会阻止连接和注册。

## 推荐的初次 MCP 设置

适合大多数用户的入门级服务器：
- filesystem
- git
- GitHub
- fetch / 文档类 MCP servers
- 单个功能明确的内部 API

不建议作为首选的服务器：
- 包含大量破坏性操作且没有过滤机制的大型业务系统
- 任何你了解不够深入、无法对其进行限制的系统

## 相关文档

- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [FAQ](/reference/faq)
- [Slash Commands](/reference/slash-commands)
