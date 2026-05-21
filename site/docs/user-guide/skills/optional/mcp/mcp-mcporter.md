---
title: "Mcporter"
sidebar_label: "Mcporter"
description: "使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能 SKILL.md 自动生成。请编辑 SKILL.md 源文件，而非此页面。 */}

<a id="mcporter"></a>
# Mcporter

使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mcp/mcporter` 安装 |
| 路径 | `optional-skills/mcp/mcporter` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `MCP`, `Tools`, `API`, `Integrations`, `Interop` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当此技能激活时，Agent 会将其视为指令。
:::

# mcporter

使用 `mcporter` 直接从终端发现、调用和管理 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 服务器与工具。

<a id="prerequisites"></a>
## 前提条件

需要 Node.js：
```bash
# 无需安装（通过 npx 运行）
npx mcporter list

# 或全局安装
npm install -g mcporter
```

<a id="quick-start"></a>
## 快速开始

```bash
# 列出本机已配置的 MCP 服务器
mcporter list

# 列出特定服务器的工具及其 schema 详情
mcporter list <server> --schema

# 调用一个工具
mcporter call <server.tool> key=value
```

<a id="discovering-mcp-servers"></a>
## 发现 MCP 服务器

mcporter 会自动发现本机上由其他 MCP 客户端（如 Claude Desktop、Cursor 等）配置的服务器。如需寻找新的可用服务器，可浏览 [mcpfinder.dev](https://mcpfinder.dev) 或 [mcp.so](https://mcp.so) 等注册中心，然后通过 ad-hoc 方式连接：

```bash
# 通过 URL 连接到任何 MCP 服务器（无需配置）
mcporter list --http-url https://some-mcp-server.com --name my_server

# 或临时运行一个 stdio 服务器
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem" --name fs
```

<a id="calling-tools"></a>
## 调用工具

```bash
# key=value 语法
mcporter call linear.list_issues team=ENG limit:5

# 函数语法
mcporter call "linear.create_issue(title: \"Bug fix needed\")"

# 临时 HTTP 服务器（无需配置）
mcporter call https://api.example.com/mcp.fetch url=https://example.com

# 临时 stdio 服务器
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com

# JSON 负载
mcporter call <server.tool> --args '{"limit": 5}'

# 机器可读的输出（推荐 Hermes 使用）
mcporter call <server.tool> key=value --output json
```

<a id="auth-and-config"></a>
## 认证与配置

```bash
# 服务器的 OAuth 登录
mcporter auth <server | url> [--reset]

# 管理配置
mcporter config list
mcporter config get <key>
mcporter config add <server>
mcporter config remove <server>
mcporter config import <path>
```

配置文件位置：`./config/mcporter.json`（可使用 `--config` 覆盖）。

<a id="daemon"></a>
## 守护进程

用于保持持久服务器连接：
```bash
mcporter daemon start
mcporter daemon status
mcporter daemon stop
mcporter daemon restart
```

<a id="code-generation"></a>
## 代码生成
```bash
# Generate a CLI wrapper for an MCP server
mcporter generate-cli --server <name>
mcporter generate-cli --command <url>

# Inspect a generated CLI
mcporter inspect-cli <path> [--json]

# Generate TypeScript types/client
mcporter emit-ts <server> --mode client
mcporter emit-ts <server> --mode types
```

<a id="notes"></a>
## 注意事项

- 使用 `--output json` 获取结构化输出，更易于解析
- 临时服务器（HTTP URL 或 `--stdio` 命令）无需任何配置即可工作——适用于一次性调用
- OAuth 认证可能需要交互式浏览器流程——如有需要，可使用 `terminal(command="mcporter auth &lt;server&gt;", pty=true)`
