---
title: "Fastmcp — 使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器"
sidebar_label: "Fastmcp"
description: "使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

<a id="fastmcp"></a>
# Fastmcp

使用 FastMCP 在 Python 中构建、测试、检查、安装和部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、暴露资源或提示、或为 Claude Code、Cursor 或 HTTP 部署准备 FastMCP 服务器的场景。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mcp/fastmcp` 安装 |
| 路径 | `optional-skills/mcp/fastmcp` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `MCP`, `FastMCP`, `Python`, `Tools`, `Resources`, `Prompts`, `Deployment` |
| 相关技能 | [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp), [`mcporter`](/user-guide/skills/optional/mcp/mcp-mcporter) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时所看到的指令。
:::

# FastMCP

使用 FastMCP 在 Python 中构建 MCP 服务器，在本地验证它们，将它们安装到 MCP 客户端，并将它们部署为 HTTP 端点。

<a id="when-to-use"></a>
## 何时使用

当任务涉及以下内容时，请使用此技能：

- 用 Python 创建新的 MCP 服务器
- 将 API、数据库、CLI 或文件处理工作流包装为 MCP 工具
- 除工具外，还暴露资源或提示
- 在将服务器接入 Hermes 或其他客户端之前，使用 FastMCP CLI 对服务器进行冒烟测试
- 将服务器安装到 Claude Code、Claude Desktop、Cursor 或类似的 MCP 客户端
- 为 HTTP 部署准备 FastMCP 服务器仓库

如果服务器已经存在，只需将其连接到 Hermes，请使用 `native-mcp`。如果目标是临时通过 CLI 访问现有的 MCP 服务器而不是构建一个，则使用 `mcporter`。

<a id="prerequisites"></a>
## 先决条件

首先在运行环境中安装 FastMCP：

```bash
pip install fastmcp
fastmcp version
```

对于 API 模板，如果尚未安装 `httpx`，请安装它：

```bash
pip install httpx
```

<a id="included-files"></a>
## 包含的文件

<a id="templates"></a>
### 模板

- `templates/api_wrapper.py` - 支持认证头部的 REST API 包装器
- `templates/database_server.py` - 只读 SQLite 查询服务器
- `templates/file_processor.py` - 文本文件检查和搜索服务器

<a id="scripts"></a>
### 脚本

- `scripts/scaffold_fastmcp.py` - 复制起始模板并替换服务器名称占位符

<a id="references"></a>
### 参考

- `references/fastmcp-cli.md` - FastMCP CLI 工作流程、安装目标和部署检查

<a id="workflow"></a>
## 工作流程

<a id="1-pick-the-smallest-viable-server-shape"></a>
### 1. 选择最小的可行服务器形态

首先选择最窄的有用覆盖面：

- API 包装器：从 1-3 个高价值端点开始，而不是整个 API
- 数据库服务器：暴露只读内省和受限的查询路径
- 文件处理器：暴露带有显式路径参数的确定性操作
- 提示/资源：仅当客户端需要可复用的提示模板或可发现的文档时才添加
相比工具模糊的大型服务器，更倾向于命名清晰、文档字符串和 schema 完善的精简服务器。

<a id="2-scaffold-from-a-template"></a>
### 2. 从模板搭建

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

如果手动复制，请将 `__SERVER_NAME__` 替换为实际的服务器名称。

<a id="3-implement-tools-first"></a>
### 3. 优先实现工具

在添加资源或提示之前，先从 `@mcp.tool` 函数开始。

工具设计规则：

- 为每个工具取一个基于动词的具体名称
- 将文档字符串写成面向用户的工具描述
- 保持参数明确且带有类型声明
- 尽可能返回结构化的 JSON 安全数据
- 尽早验证不安全的输入
- 第一个版本默认优先使用只读行为

好的工具示例：

- `get_customer`
- `search_tickets`
- `describe_table`
- `summarize_text_file`

差的工具示例：

- `run`
- `process`
- `do_thing`

<a id="4-add-resources-and-prompts-only-when-they-help"></a>
### 4. 仅在需要时添加资源和提示

当客户端需要获取稳定的只读内容（如 schema、策略文档或生成的报告）时，添加 `@mcp.resource`。

当服务器需要为某个已知工作流提供可复用的提示模板时，添加 `@mcp.prompt`。

不要将每个文档都转为提示。建议按照以下原则划分：

- 动作 → 工具
- 数据/文档检索 → 资源
- 可复用的 LLM 指令 → 提示

<a id="5-test-the-server-before-integrating-it-anywhere"></a>
### 5. 在集成前先测试服务器

使用 FastMCP CLI 进行本地验证：

```bash
fastmcp inspect acme_server.py:mcp
fastmcp list acme_server.py --json
fastmcp call acme_server.py search_resources query=router limit=5 --json
```

快速迭代调试时，可在本地运行服务器：

```bash
fastmcp run acme_server.py:mcp
```

在本地测试 HTTP 传输：

```bash
fastmcp run acme_server.py:mcp --transport http --host 127.0.0.1 --port 8000
fastmcp list http://127.0.0.1:8000/mcp --json
fastmcp call http://127.0.0.1:8000/mcp search_resources query=router --json
```

在声称服务器可用之前，始终对每个新工具至少运行一次真实的 `fastmcp call`。

<a id="6-install-into-a-client-when-local-validation-passes"></a>
### 6. 本地验证通过后安装到客户端

FastMCP 可以将服务器注册到支持的 MCP 客户端：

```bash
fastmcp install claude-code acme_server.py
fastmcp install claude-desktop acme_server.py
fastmcp install cursor acme_server.py -e .
```

使用 `fastmcp discover` 检查机器上已配置的命名 MCP 服务器。

当目标是集成 Hermes 时，有两种方式：

- 在 `~/.hermes/config.yaml` 中使用 `native-mcp` 技能配置服务器，或
- 在开发过程中继续使用 FastMCP CLI 命令，直到接口稳定为止

<a id="7-deploy-after-the-local-contract-is-stable"></a>
### 7. 本地契约稳定后再部署

对于托管部署，Prefect Horizon 是 FastMCP 文档中最直接的方式。部署前请运行：

```bash
fastmcp inspect acme_server.py:mcp
```

确保仓库中包含：
- 一个包含 FastMCP 服务器对象的 Python 文件
- `requirements.txt` 或 `pyproject.toml`
- 部署所需的任何环境变量文档

对于通用 HTTP 托管，先在本地验证 HTTP 传输，然后部署到任何支持 Python 且能暴露服务器端口的平台上。

<a id="common-patterns"></a>
## 常见模式

<a id="api-wrapper-pattern"></a>
### API 包装器模式

在将 REST 或 HTTP API 暴露为 MCP 工具时使用。

推荐的首个切片：

- 一个读取路径
- 一个列表/搜索路径
- 可选健康检查

实现说明：

- 将认证信息放在环境变量中，不要硬编码
- 将请求逻辑集中到一个辅助函数中
- 用简洁的上下文暴露 API 错误
- 在返回前规范化不一致的上游负载

从 `templates/api_wrapper.py` 开始。

<a id="database-pattern"></a>
### 数据库模式

在暴露安全查询和检查能力时使用。

推荐的首个切片：

- `list_tables`
- `describe_table`
- 一个受限的只读查询工具

实现说明：

- 默认使用只读数据库访问
- 在早期版本中拒绝非 `SELECT` 的 SQL
- 限制行数
- 返回行和列名

从 `templates/database_server.py` 开始。

<a id="file-processor-pattern"></a>
### 文件处理器模式

在服务器需要按需检查或转换文件时使用。

推荐的首个切片：

- 总结文件内容
- 在文件中搜索
- 提取确定性元数据

实现说明：

- 接受显式文件路径
- 检查缺失文件和编码失败
- 限制预览和结果数量
- 除非需要特定的外部工具，否则避免调用 shell

从 `templates/file_processor.py` 开始。

<a id="quality-bar"></a>
## 质量标准

在交付 FastMCP 服务器之前，请验证以下所有内容：

- 服务器能正常导入
- `fastmcp inspect &lt;file.py:mcp&gt;` 执行成功
- `fastmcp list &lt;server spec&gt; --json` 执行成功
- 每个新工具至少有一个真实的 `fastmcp call`
- 环境变量已记录
- 工具表面足够小，无需猜测即可理解

<a id="troubleshooting"></a>
## 故障排除

<a id="fastmcp-command-missing"></a>
### FastMCP 命令缺失

在活动环境中安装该包：

```bash
pip install fastmcp
fastmcp version
```

<a id="fastmcp-inspect-fails"></a>
### `fastmcp inspect` 失败

检查：

- 文件导入时没有导致崩溃的副作用
- FastMCP 实例在 `&lt;file.py:object&gt;` 中命名正确
- 模板中的可选依赖已安装

<a id="tool-works-in-python-but-not-through-cli"></a>
### 工具在 Python 中工作但无法通过 CLI 运行

运行：

```bash
fastmcp list server.py --json
fastmcp call server.py your_tool_name --json
```

这通常能暴露命名不匹配、缺少必需参数或不可序列化的返回值。

<a id="hermes-cannot-see-the-deployed-server"></a>
### Hermes 无法看到已部署的服务器

服务器构建部分可能正确，但 Hermes 配置不正确。加载 `native-mcp` 技能并在 `~/.hermes/config.yaml` 中配置服务器，然后重启 Hermes。

<a id="references"></a>
## 参考

有关 CLI 详情、安装目标和部署检查，请阅读 `references/fastmcp-cli.md`。
