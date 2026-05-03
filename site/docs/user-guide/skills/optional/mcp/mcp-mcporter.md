---
title: "Mcporter"
sidebar_label: "Mcporter"
description: "使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Mcporter {#mcporter}

使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mcp/mcporter` 安装 |
| 路径 | `optional-skills/mcp/mcporter` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `MCP`、`Tools`、`API`、`Integrations`、`Interop` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="mcporter"></a>
# mcporter

使用 `mcporter` 直接从终端发现、调用和管理 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 服务器和工具。

## 前提条件 {#prerequisites}

需要 Node.js：
```bash
# 无需安装（通过 npx 运行）
npx mcporter list

# 或全局安装
npm install -g mcporter
```

## 快速开始 {#quick-start}

```bash
# 列出本机上已配置的 MCP 服务器
mcporter list

# 列出特定服务器的工具及其架构详情
mcporter list <server> --schema

# 调用工具
mcporter call <server.tool> key=value
```

## 发现 MCP 服务器 {#discovering-mcp-servers}

mcporter 会自动发现本机上由其他 MCP 客户端（如 Claude Desktop、Cursor 等）配置的服务器。要查找可用的新服务器，可以浏览 [mcpfinder.dev](https://mcpfinder.dev) 或 [mcp.so](https://mcp.so) 等注册中心，然后临时连接：

```bash
# 通过 URL 连接到任何 MCP 服务器（无需配置）
mcporter list --http-url https://some-mcp-server.com --name my_server

# 或临时运行一个 stdio 服务器
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem" --name fs
```

## 调用工具 {#calling-tools}

```bash
# 键=值 语法
mcporter call linear.list_issues team=ENG limit:5

# 函数语法
mcporter call "linear.create_issue(title: \"Bug fix needed\")"

# 临时 HTTP 服务器（无需配置）
mcporter call https://api.example.com/mcp.fetch url=https://example.com

# 临时 stdio 服务器
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com

# JSON 负载
mcporter call <server.tool> --args '{"limit": 5}'

# 机器可读输出（推荐用于 Hermes）
mcporter call <server.tool> key=value --output json
```

## 认证与配置 {#auth-and-config}

```bash
# 为服务器进行 OAuth 登录
mcporter auth <server | url> [--reset]

# 管理配置
mcporter config list
mcporter config get <key>
mcporter config add <server>
mcporter config remove <server>
mcporter config import <path>
```

配置文件位置：`./config/mcporter.json`（可通过 `--config` 覆盖）。

## 守护进程 {#daemon}

用于持久化服务器连接：
```bash
mcporter daemon start
mcporter daemon status
mcporter daemon stop
mcporter daemon restart
```

## 代码生成 {#code-generation}

```bash
# 为 MCP 服务器生成 CLI 包装器
mcporter generate-cli --server <name>
mcporter generate-cli --command <url>

# 检查生成的 CLI
mcporter inspect-cli <path> [--json]

# 生成 TypeScript 类型/客户端
mcporter emit-ts <server> --mode client
mcporter emit-ts <server> --mode types
```
## 注意事项 {#notes}

- 使用 `--output json` 获取结构化输出，更易于解析
- 临时服务器（HTTP URL 或 `--stdio` 命令）无需任何配置即可工作——适用于一次性调用
- OAuth 认证可能需要交互式浏览器流程——如有需要，请使用 `terminal(command="mcporter auth &lt;server&gt;", pty=true)`
