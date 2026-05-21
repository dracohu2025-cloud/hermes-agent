---
sidebar_position: 6
title: "将 MCP 与 Hermes 一起使用"
description: "一份实用指南，教你如何将 MCP 服务器连接到 Hermes Agent，筛选其工具，并在实际工作流中安全地使用它们"
---

<a id="use-mcp-with-hermes"></a>
# 将 MCP 与 Hermes 一起使用

本指南展示了如何在日常工作中真正将 MCP 与 Hermes Agent 结合使用。

如果说功能页面解释的是 MCP 是什么，那么本指南关注的是如何快速、安全地从中获取价值。

<a id="when-should-you-use-mcp"></a>
## 什么时候应该使用 MCP？

在以下情况下使用 MCP：
- 工具已经以 MCP 形式存在，并且你不想构建原生 Hermes 工具
- 你希望 Hermes 通过清晰的 RPC 层操作本地或远程系统
- 你想要对每个服务器进行细粒度的暴露控制
- 你想将 Hermes 连接到内部 API、数据库或公司系统，而无需修改 Hermes 核心

在以下情况下不应使用 MCP：
- 内置的 Hermes 工具已经很好地解决了任务
- 服务器暴露了庞大而危险的工具表面，而你还没有准备好对其进行筛选
- 你只需要一个非常窄的集成，而原生工具会更简单、更安全

<a id="mental-model"></a>
## 思维模型

把 MCP 看作一个适配层：

- Hermes 仍然是 Agent
- MCP 服务器贡献工具
- Hermes 在启动或重新加载时发现这些工具
- 模型可以像使用普通工具一样使用它们
- 你可以控制每个服务器暴露多少内容

最后一点很重要。好的 MCP 使用不是“连接所有东西”，而是“在最小的有用表面上连接正确的东西”。

<a id="step-1-install-mcp-support"></a>
## 第 1 步：安装 MCP 支持

如果你使用标准安装脚本安装了 Hermes，那么 MCP 支持已经包含在内（安装程序会执行 `uv pip install -e ".[all]"`）。

如果你在没有额外扩展的情况下安装了 Hermes，需要单独添加 MCP：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

对于基于 npm 的服务器，请确保 Node.js 和 `npx` 可用。

对于许多 Python MCP 服务器，`uvx` 是一个不错的默认选择。

<a id="step-2-add-one-server-first"></a>
## 第 2 步：先添加一个服务器

从一个安全且单一的服务器开始。

示例：仅访问一个项目目录的文件系统。

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

现在问一些具体的问题：

```text
检查这个项目并总结仓库布局。
```

<a id="step-3-verify-mcp-loaded"></a>
## 第 3 步：验证 MCP 已加载

你可以通过以下方式验证 MCP：

- Hermes 的横幅/状态应在配置后显示 MCP 集成
- 询问 Hermes 它有哪些可用的工具
- 在配置更改后使用 `/reload-mcp`
- 如果服务器连接失败，检查日志

一个实用的测试提示：

```text
告诉我当前有哪些基于 MCP 的工具可用。
```

<a id="step-4-start-filtering-immediately"></a>
## 第 4 步：立即开始筛选

如果服务器暴露了很多工具，不要等到以后才筛选。

<a id="example-whitelist-only-what-you-want"></a>
### 示例：只允许你想要的

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

对于敏感系统，这通常是最好的默认做法。

<a id="wsl2-bridge-hermes-in-wsl-to-windows-chrome"></a>
## WSL2：将 WSL 中的 Hermes 桥接到 Windows Chrome

以下是实际的设置场景：

- Hermes 在 WSL2 内部运行
- 你想要控制的浏览器是你在 Windows 上正常登录的 Chrome
- `/browser connect` 在 WSL 中很别扭或不可靠
在这种设置下，Hermes 并**不**直接连接 Chrome。相反：

- Hermes 在 WSL 中运行
- Hermes 启动一个本地 stdio MCP 服务器
- 该 MCP 服务器通过 Windows 互操作机制（`cmd.exe` 或 `powershell.exe`）启动
- MCP 服务器连接到你正在运行的 Windows Chrome 会话

逻辑模型：

```text
Hermes (WSL) -> MCP stdio 桥接 -> Windows Chrome
```

<a id="why-this-mode-is-useful"></a>
### 为何这种模式有用

- 你可以保留真实的 Windows 浏览器配置、Cookie 和登录状态
- Hermes 仍处于其支持的 Unix 环境（WSL2）中
- 浏览器控制以 MCP 工具的形式暴露，而不是依赖 Hermes 核心的浏览器传输协议

<a id="recommended-server"></a>
### 推荐的服务器

使用 `chrome-devtools-mcp`。

如果你的 Windows Chrome 已经通过 `chrome://inspect/#remote-debugging` 启用了实时远程调试，那么在 WSL 中这样添加：

```bash
hermes mcp add chrome-devtools-win --command cmd.exe --args /c npx -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

保存服务器后：

```bash
hermes mcp test chrome-devtools-win
```

然后启动一个新的 Hermes 会话，或运行：

```text
/reload-mcp
```

<a id="typical-prompt"></a>
### 典型提示词

加载完成后，Hermes 可以直接使用带有 MCP 前缀的浏览器工具。例如：

```text
调用 MCP 工具 mcp_chrome_devtools_win_list_pages，列出当前浏览器标签页。
```

<a id="when-browser-connect-is-the-wrong-tool"></a>
### 何时 `/browser connect` 不适用

如果 Hermes 在 WSL 中运行而 Chrome 在 Windows 上运行，即使 Chrome 已打开且可调试，`/browser connect` 仍可能失败。

常见原因：

- WSL 无法访问 Chrome 暴露给 Windows 工具的同一主机本地端点
- 较新版 Chrome 的实时调试流程与传统的 `ws://localhost:9222` 不同
- 通过 Windows 侧的工具（如 `chrome-devtools-mcp`）更容易附加到浏览器

在这些情况下，请将 `/browser connect` 保留给同环境设置，并使用 MCP 进行 WSL 到 Windows 的浏览器桥接。

<a id="known-pitfalls"></a>
### 已知陷阱

- 从 Windows 挂载路径（如 `/mnt/c/Users/&lt;you&gt;` 或 `/mnt/c/workspace/...`）启动 Hermes，以便通过 MCP 使用 Windows stdio 可执行文件。
- 如果从 `/root` 或 `/home/...` 启动 Hermes，Windows 可能会在 MCP 服务器启动前发出 `UNC` 当前目录警告。
- 如果 `chrome-devtools-mcp --autoConnect` 在枚举页面时超时，请减少 Chrome 中的后台/冻结标签页并重试。

<a id="example-blacklist-dangerous-actions"></a>
### 示例：屏蔽危险操作

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

<a id="example-disable-utility-wrappers-too"></a>
### 示例：也禁用工具包装器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

<a id="what-does-filtering-actually-affect"></a>
## 过滤实际影响什么？

Hermes 中有两类通过 MCP 暴露的功能：

1. 服务器原生的 MCP 工具
   - 通过以下方式过滤：
     - `tools.include`
     - `tools.exclude`

2. Hermes 添加的工具包装器
   - 通过以下方式过滤：
     - `tools.resources`
     - `tools.prompts`

<a id="utility-wrappers-you-may-see"></a>
### 你可能会看到的工具包装器

Resources（资源）：
- `list_resources`
- `read_resource`
Prompts:
- `list_prompts`
- `get_prompt`

这些包装器仅在以下情况下出现：
- 你的配置允许它们，且
- MCP 服务器会话实际支持这些能力

因此，如果某个服务器实际上不具有资源/提示词，Hermes 不会假装它有。

<a id="common-patterns"></a>
## 常见模式

<a id="pattern-1-local-project-assistant"></a>
### 模式 1：本地项目助手

当你希望 Hermes 在受限制的工作空间内进行推理时，对仓库本地的文件系统或 git 服务器使用 MCP。

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

好的提示词：

```text
Review the project structure and identify where configuration lives.
```

```text
Check the local git state and summarize what changed recently.
```

<a id="pattern-2-github-triage-assistant"></a>
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

好的提示词：

```text
List open issues about MCP, cluster them by theme, and draft a high-quality issue for the most common bug.
```

```text
Search the repo for uses of _discover_and_register_server and explain how MCP tools are registered.
```

<a id="pattern-3-internal-api-assistant"></a>
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

好的提示词：

```text
Look up customer ACME Corp and summarize recent invoice activity.
```

在这种场景下，严格的允许列表远胜于排除列表。

<a id="pattern-4-documentation-knowledge-servers"></a>
### 模式 4：文档 / 知识服务器

某些 MCP 服务器暴露的提示词或资源更像共享知识资产，而非直接操作。

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

好的提示词：

```text
List available MCP resources from the docs server, then read the onboarding guide and summarize it.
```

```text
List prompts exposed by the docs server and tell me which ones would help with incident response.
```

<a id="tutorial-end-to-end-setup-with-filtering"></a>
## 教程：带过滤的端到端设置

以下是一个实用的进阶步骤。

<a id="phase-1-add-github-mcp-with-a-tight-whitelist"></a>
### 阶段 1：使用严格白名单添加 GitHub MCP

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

启动 Hermes 并询问：

```text
Search the codebase for references to MCP and summarize the main integration points.
```

<a id="phase-2-expand-only-when-needed"></a>
### 阶段 2：仅在有需要时扩展

如果你稍后还需要更新 issue：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```
然后重新加载：

```text
/reload-mcp
```

<a id="phase-3-add-a-second-server-with-different-policy"></a>
### 阶段三：添加第二个服务器，使用不同的策略

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

现在 Hermes 可以结合它们：

```text
检查本地项目文件，然后创建一个 GitHub Issue，总结你发现的 bug。
```

这就是 MCP 强大的地方：无需修改 Hermes 核心即可实现多系统工作流。

<a id="safe-usage-recommendations"></a>
## 安全使用建议

<a id="prefer-allowlists-for-dangerous-systems"></a>
### 对危险系统优先使用白名单

对于任何涉及金融、面向客户或具有破坏性的场景：
- 使用 `tools.include`
- 从尽可能小的集合开始

<a id="disable-unused-utilities"></a>
### 禁用不需要的实用功能

如果不想让模型浏览服务器提供的资源/提示，请关闭它们：

```yaml
tools:
  resources: false
  prompts: false
```

<a id="keep-servers-scoped-narrowly"></a>
### 将服务器的作用范围保持狭窄

示例：
- filesystem 服务器限定到一个项目目录，而不是整个家目录
- git 服务器指向一个仓库
- 默认暴露大量只读工具的内部 API 服务器

<a id="reload-after-config-changes"></a>
### 配置更改后重新加载

```text
/reload-mcp
```

在更改以下内容后执行此操作：
- include/exclude 列表
- 启用标志
- resources/prompts 开关
- 认证头 / 环境变量

<a id="troubleshooting-by-symptom"></a>
## 按症状排查问题

<a id="the-server-connects-but-the-tools-i-expected-are-missing"></a>
### "服务器已连接，但缺少我期望的工具"

可能的原因：
- 被 `tools.include` 过滤掉
- 被 `tools.exclude` 排除
- 通过 `resources: false` 或 `prompts: false` 禁用了实用包装器
- 服务器实际上不支持 resources/prompts

<a id="the-server-is-configured-but-nothing-loads"></a>
### "服务器已配置，但什么也没有加载"

检查：
- 配置中未保留 `enabled: false`
- 命令/运行时存在（`npx`、`uvx` 等）
- HTTP 端点可达
- 认证环境变量或头部正确

<a id="why-do-i-see-fewer-tools-than-the-mcp-server-advertises"></a>
### "为什么我看到的工具比 MCP 服务器宣传的少？"

因为 Hermes 现在会遵守你的每个服务器策略和基于能力的注册。这是预期行为，通常也是期望的。

<a id="how-do-i-remove-an-mcp-server-without-deleting-the-config"></a>
### "如何在不删除配置的情况下移除 MCP 服务器？"

使用：

```yaml
enabled: false
```

这样会保留配置，但阻止连接和注册。

<a id="recommended-first-mcp-setups"></a>
## 推荐的初始 MCP 配置

适合大多数用户的首次服务器：
- filesystem
- git
- GitHub
- fetch / 文档类 MCP 服务器
- 一个窄范围的内部 API

不适合的首次服务器：
- 大型业务系统，包含大量破坏性操作且未过滤
- 任何你还不理解到足以约束的内容

<a id="related-docs"></a>
## 相关文档

- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [常见问题解答](/reference/faq)
- [斜杠命令](/reference/slash-commands)
