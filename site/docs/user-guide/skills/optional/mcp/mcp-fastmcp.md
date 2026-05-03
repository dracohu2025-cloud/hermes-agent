---
title: "Fastmcp — 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器"
sidebar_label: "Fastmcp"
description: "使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Fastmcp {#fastmcp}

使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示、或为 Claude Code、Cursor 或 HTTP 部署准备 FastMCP 服务器。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mcp/fastmcp` 安装 |
| 路径 | `optional-skills/mcp/fastmcp` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `MCP`、`FastMCP`、`Python`、`Tools`、`Resources`、`Prompts`、`Deployment` |
| 相关技能 | [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp)、[`mcporter`](/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="fastmcp"></a>
# FastMCP

使用 Python 中的 FastMCP 构建 MCP 服务器，在本地验证它们，将它们安装到 MCP 客户端中，并将其部署为 HTTP 端点。

## 何时使用 {#when-to-use}

当任务需要以下操作时使用此技能：

- 在 Python 中创建新的 MCP 服务器
- 将 API、数据库、CLI 或文件处理工作流封装为 MCP 工具
- 除了工具之外，还暴露资源或提示
- 在将服务器接入 Hermes 或其他客户端之前，使用 FastMCP CLI 对服务器进行冒烟测试
- 将服务器安装到 Claude Code、Claude Desktop、Cursor 或类似的 MCP 客户端中
- 为 HTTP 部署准备 FastMCP 服务器仓库

如果服务器已存在且仅需连接到 Hermes，请使用 `native-mcp`。如果目标是临时通过 CLI 访问现有 MCP 服务器而非构建新服务器，请使用 `mcporter`。

## 前提条件 {#prerequisites}

首先在工作环境中安装 FastMCP：

```bash
pip install fastmcp
fastmcp version
```

对于 API 模板，如果尚未安装 `httpx`，请安装：

```bash
pip install httpx
```

## 包含的文件 {#included-files}

### 模板 {#templates}

- `templates/api_wrapper.py` - 支持认证头的 REST API 封装
- `templates/database_server.py` - 只读 SQLite 查询服务器
- `templates/file_processor.py` - 文本文件检查与搜索服务器

### 脚本 {#scripts}

- `scripts/scaffold_fastmcp.py` - 复制启动模板并替换服务器名称占位符

### 参考 {#references}

- `references/fastmcp-cli.md` - FastMCP CLI 工作流、安装目标和部署检查

## 工作流 {#workflow}

### 1. 选择最小的可行服务器形态 {#1-pick-the-smallest-viable-server-shape}

首先选择最窄的有用表面区域：

- API 封装：从 1-3 个高价值端点开始，而不是整个 API
- 数据库服务器：暴露只读内省和受限的查询路径
- 文件处理器：暴露确定性操作，并带有显式路径参数
- 提示/资源：仅当客户端需要可复用的提示模板或可发现的文档时才添加

优先选择名称、文档字符串和模式良好的小型服务器，而不是工具模糊的大型服务器。
### 2. 从模板搭建 {#2-scaffold-from-a-template}

直接复制模板或使用脚手架辅助工具：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py \
  --template api_wrapper \
  --name "Acme API" \
  --output ./acme_server.py
```

可用模板列表：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py --list
```

如果手动复制，请将 `__SERVER_NAME__` 替换为真实的服务器名称。

### 3. 先实现工具 {#3-implement-tools-first}

在添加资源或提示之前，先从 `@mcp.tool` 函数开始。

工具设计规则：

- 为每个工具赋予一个具体的、基于动词的名称
- 将文档字符串编写为面向用户的工具描述
- 保持参数明确且带有类型
- 尽可能返回结构化的 JSON 安全数据
- 尽早验证不安全的输入
- 在第一个版本中默认优先采用只读行为

好的工具示例：

- `get_customer`
- `search_tickets`
- `describe_table`
- `summarize_text_file`

差的工具示例：

- `run`
- `process`
- `do_thing`

### 4. 仅在必要时添加资源和提示 {#4-add-resources-and-prompts-only-when-they-help}

当客户端需要获取稳定的只读内容（如模式、策略文档或生成的报告）时，添加 `@mcp.resource`。

当服务器需要为已知工作流提供可复用的提示模板时，添加 `@mcp.prompt`。

不要将每个文档都变成提示。优先选择：

- 工具用于操作
- 资源用于数据/文档检索
- 提示用于可复用的 LLM 指令

### 5. 在集成到任何地方之前先测试服务器 {#5-test-the-server-before-integrating-it-anywhere}

使用 FastMCP CLI 进行本地验证：

```bash
fastmcp inspect acme_server.py:mcp
fastmcp list acme_server.py --json
fastmcp call acme_server.py search_resources query=router limit=5 --json
```

为了快速迭代调试，在本地运行服务器：

```bash
fastmcp run acme_server.py:mcp
```

在本地测试 HTTP 传输：

```bash
fastmcp run acme_server.py:mcp --transport http --host 127.0.0.1 --port 8000
fastmcp list http://127.0.0.1:8000/mcp --json
fastmcp call http://127.0.0.1:8000/mcp search_resources query=router --json
```

在声称服务器工作之前，始终对每个新工具至少运行一次真实的 `fastmcp call`。

### 6. 本地验证通过后安装到客户端 {#6-install-into-a-client-when-local-validation-passes}

FastMCP 可以将服务器注册到支持的 MCP 客户端：

```bash
fastmcp install claude-code acme_server.py
fastmcp install claude-desktop acme_server.py
fastmcp install cursor acme_server.py -e .
```

使用 `fastmcp discover` 检查机器上已配置的命名 MCP 服务器。

如果目标是集成 Hermes，可以：

- 使用 `native-mcp` 技能在 `~/.hermes/config.yaml` 中配置服务器，或者
- 在开发过程中继续使用 FastMCP CLI 命令，直到接口稳定

### 7. 本地契约稳定后部署 {#7-deploy-after-the-local-contract-is-stable}

对于托管部署，Prefect Horizon 是 FastMCP 文档中最直接说明的路径。部署前：

```bash
fastmcp inspect acme_server.py:mcp
```

确保仓库包含：

- 包含 FastMCP 服务器对象的 Python 文件
- `requirements.txt` 或 `pyproject.toml`
- 部署所需的任何环境变量文档
对于通用 HTTP 托管，先在本地验证 HTTP 传输，再部署到任何能够暴露服务器端口的 Python 兼容平台。

## 常见模式 {#common-patterns}

### API 封装模式 {#api-wrapper-pattern}

用于将 REST 或 HTTP API 作为 MCP 工具暴露时。

推荐优先实现：

- 一个读取路径
- 一个列表/搜索路径
- 可选健康检查

实现注意事项：

- 将认证信息放在环境变量中，不要硬编码
- 将请求逻辑集中到一个辅助函数中
- 以简洁的上下文暴露 API 错误
- 在返回前规范化不一致的上游负载

从 `templates/api_wrapper.py` 开始。

### 数据库模式 {#database-pattern}

用于暴露安全查询和检查能力时。

推荐优先实现：

- `list_tables`
- `describe_table`
- 一个受限制的只读查询工具

实现注意事项：

- 默认使用只读数据库访问
- 在早期版本中拒绝非 `SELECT` 的 SQL
- 限制行数
- 返回行以及列名

从 `templates/database_server.py` 开始。

### 文件处理器模式 {#file-processor-pattern}

用于服务器需要按需检查或转换文件时。

推荐优先实现：

- 总结文件内容
- 在文件中搜索
- 提取确定性元数据

实现注意事项：

- 接受明确的文件路径
- 检查文件缺失和编码失败
- 限制预览内容和结果数量
- 除非需要特定的外部工具，否则避免调用 shell

从 `templates/file_processor.py` 开始。

## 质量标准 {#quality-bar}

在交付 FastMCP 服务器之前，请验证以下所有事项：

- 服务器能够无错误导入
- `fastmcp inspect &lt;file.py:mcp&gt;` 成功
- `fastmcp list &lt;server spec&gt; --json` 成功
- 每个新工具至少有真实的 `fastmcp call` 调用
- 环境变量已记录
- 工具表面足够小，无需猜测即可理解

## 故障排除 {#troubleshooting}

### FastMCP 命令缺失 {#fastmcp-command-missing}

在激活的环境中安装包：

```bash
pip install fastmcp
fastmcp version
```

### `fastmcp inspect` 失败 {#fastmcp-inspect-fails}

检查以下内容：

- 文件导入时没有导致崩溃的副作用
- FastMCP 实例在 `&lt;file.py:object&gt;` 中正确命名
- 模板中的可选依赖已安装

### 工具在 Python 中工作但通过 CLI 不行 {#tool-works-in-python-but-not-through-cli}

运行：

```bash
fastmcp list server.py --json
fastmcp call server.py your_tool_name --json
```

这通常能暴露命名不匹配、缺少必需参数或不可序列化的返回值。

### Hermes 无法看到部署的服务器 {#hermes-cannot-see-the-deployed-server}

服务器构建部分可能是正确的，但 Hermes 配置不正确。加载 `native-mcp` 技能，并在 `~/.hermes/config.yaml` 中配置服务器，然后重启 Hermes。

## 参考 {#references}

关于 CLI 细节、安装目标和部署检查，请阅读 `references/fastmcp-cli.md`。
