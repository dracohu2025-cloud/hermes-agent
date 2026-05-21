---
title: "Parallel Cli"
sidebar_label: "Parallel Cli"
description: "Parallel CLI 的可选供应商技能——面向 Agent 的网页搜索、提取、深度研究、信息丰富、FindAll 和监控"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="parallel-cli"></a>
# Parallel Cli

Parallel CLI 的可选供应商技能——面向 Agent 的网页搜索、提取、深度研究、信息丰富、FindAll 和监控。优先使用 JSON 输出和非交互式流程。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/research/parallel-cli` 安装 |
| 路径 | `optional-skills/research/parallel-cli` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Research`, `Web`, `Search`, `Deep-Research`, `Enrichment`, `CLI` |
| 相关技能 | [`duckduckgo-search`](/user-guide/skills/optional/research/research-duckduckgo-search), [`mcporter`](/user-guide/skills/optional/mcp/mcp-mcporter) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Parallel CLI

当用户明确要求使用 Parallel，或者终端原生工作流需要借助 Parallel 的供应商特定栈进行网页搜索、提取、深度研究、信息丰富、实体发现或监控时，请使用 `parallel-cli`。

这是一个可选的第三方工作流，并非 Hermes 核心能力。

重要预期：
- Parallel 是一项付费服务（提供免费套餐），并非完全免费的本地工具。
- 它与 Hermes 原生的 `web_search` / `web_extract` 功能有重叠，因此对于普通查询，默认情况下不要优先使用它。
- 当用户特别提到 Parallel，或者需要 Parallel 的信息丰富、FindAll 或监控工作流等能力时，优先使用此技能。

`parallel-cli` 专为 Agent 设计：
- 通过 `--json` 输出 JSON
- 非交互式命令执行
- 通过 `--no-wait`、`status` 和 `poll` 支持异步长时间运行任务
- 通过 `--previous-interaction-id` 支持上下文链
- 在一个 CLI 中集成了搜索、提取、研究、信息丰富、实体发现和监控

<a id="when-to-use-it"></a>
## 何时使用

在以下情况优先使用此技能：
- 用户明确提到 Parallel 或 `parallel-cli`
- 任务需要比简单的一次性搜索/提取更丰富的工作流
- 需要异步深度研究任务，可以稍后启动并轮询结果
- 需要结构化的信息丰富、FindAll 实体发现或监控

当未特别要求使用 Parallel 时，对于快速的一次性查询，优先使用 Hermes 原生的 `web_search` / `web_extract`。

<a id="installation"></a>
## 安装

尝试环境中侵入性最小的安装方式。

<a id="homebrew"></a>
### Homebrew

```bash
brew install parallel-web/tap/parallel-cli
```

<a id="npm"></a>
### npm

```bash
npm install -g parallel-web-cli
```

<a id="python-package"></a>
### Python 包

```bash
pip install "parallel-web-tools[cli]"
```

<a id="standalone-installer"></a>
### 独立安装程序

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

如果你想要一个隔离的 Python 安装环境，也可以使用 `pipx`：

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```
<a id="authentication"></a>
## 身份认证

交互式登录：

```bash
parallel-cli login
```

无界面 / SSH / CI 环境：

```bash
parallel-cli login --device
```

API 密钥环境变量：

```bash
export PARALLEL_API_KEY="***"
```

验证当前认证状态：

```bash
parallel-cli auth
```

如果认证需要浏览器交互，请使用 `pty=true` 运行。

<a id="core-rule-set"></a>
## 核心规则集

1. 当需要机器可读输出时，始终优先使用 `--json`。
2. 优先使用显式参数和非交互式流程。
3. 对于长时间运行的任务，使用 `--no-wait` 然后使用 `status` / `poll`。
4. 仅引用 CLI 输出返回的 URL。
5. 当可能涉及后续问题时，将大型 JSON 输出保存到临时文件。
6. 仅在真正长时间运行的工作流中使用后台进程；否则在前台运行。
7. 优先使用 Hermes 原生工具，除非用户明确要求 Parallel 或需要 Parallel 专属工作流。

<a id="quick-reference"></a>
## 快速参考

<!-- ascii-guard-ignore -->
```text
parallel-cli
├── auth
├── login
├── logout
├── search
├── extract / fetch
├── research run|status|poll|processors
├── enrich run|status|poll|plan|suggest|deploy
├── findall run|ingest|status|poll|result|enrich|extend|schema|cancel
└── monitor create|list|get|update|delete|events|event-group|simulate
```
<!-- ascii-guard-ignore-end -->

<a id="common-flags-and-patterns"></a>
## 常用标志和模式

常用的有用标志：
- `--json` 用于结构化输出
- `--no-wait` 用于异步任务
- `--previous-interaction-id &lt;id&gt;` 用于复用之前上下文的后续任务
- `--max-results &lt;n&gt;` 用于搜索结果数量
- `--mode one-shot|agentic` 用于搜索行为
- `--include-domains domain1.com,domain2.com`
- `--exclude-domains domain1.com,domain2.com`
- `--after-date YYYY-MM-DD`

方便时从标准输入读取：

```bash
echo "What is the latest funding for Anthropic?" | parallel-cli search - --json
echo "Research question" | parallel-cli research run - --json
```

<a id="search"></a>
## 搜索

用于获取带结构化结果的当前网页查询。

```bash
parallel-cli search "What is Anthropic's latest AI model?" --json
parallel-cli search "SEC filings for Apple" --include-domains sec.gov --json
parallel-cli search "bitcoin price" --after-date 2026-01-01 --max-results 10 --json
parallel-cli search "latest browser benchmarks" --mode one-shot --json
parallel-cli search "AI coding agent enterprise reviews" --mode agentic --json
```

有用的约束：
- `--include-domains` 以限定可信来源
- `--exclude-domains` 以剔除噪音域名
- `--after-date` 用于时效过滤
- `--max-results` 当需要更广泛覆盖时

如果预期会有后续问题，请保存输出：

```bash
parallel-cli search "latest React 19 changes" --json -o /tmp/react-19-search.json
```

总结结果时：
- 先给出答案
- 包含日期、名称和具体事实
- 仅引用返回的来源
- 避免编造 URL 或来源标题

<a id="extraction"></a>
## 提取

用于从 URL 提取干净的内容或 Markdown。

```bash
parallel-cli extract https://example.com --json
parallel-cli extract https://company.com --objective "Find pricing info" --json
parallel-cli extract https://example.com --full-content --json
parallel-cli fetch https://example.com --json
```
当页面范围较广且你只需要某一部分信息时，使用 `--objective`。

<a id="deep-research"></a>
## 深度研究

用于可能需要较长时间的深层多步骤研究任务。

常见的处理器级别：
- `lite` / `base`：更快、更便宜的扫描
- `core` / `pro`：更全面的综合处理
- `ultra`：最繁重的研究任务

<a id="synchronous"></a>
### 同步

```bash
parallel-cli research run \
  "Compare the leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor core \
  --json
```

<a id="async-launch-poll"></a>
### 异步启动 + 轮询

```bash
parallel-cli research run \
  "Compare the leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor ultra \
  --no-wait \
  --json

parallel-cli research status trun_xxx --json
parallel-cli research poll trun_xxx --json
parallel-cli research processors --json
```

<a id="context-chaining-follow-up"></a>
### 上下文串联 / 追问

```bash
parallel-cli research run "What are the top AI coding agents?" --json
parallel-cli research run \
  "What enterprise controls does the top-ranked one offer?" \
  --previous-interaction-id trun_xxx \
  --json
```

推荐的 Hermes 工作流：
1. 使用 `--no-wait --json` 启动
2. 捕获返回的运行/任务 ID
3. 如果用户想继续其他工作，继续执行
4. 稍后调用 `status` 或 `poll`
5. 根据返回的来源生成带有引用的最终报告总结

<a id="enrichment"></a>
## 富化

当用户有 CSV / JSON / 表格形式输入，并且希望通过网上研究推断出额外的列时使用。

<a id="suggest-columns"></a>
### 建议列

```bash
parallel-cli enrich suggest "Find the CEO and annual revenue" --json
```

<a id="plan-a-config"></a>
### 规划配置

```bash
parallel-cli enrich plan -o config.yaml
```

<a id="inline-data"></a>
### 内联数据

```bash
parallel-cli enrich run \
  --data '[{"company": "Anthropic"}, {"company": "Mistral"}]' \
  --intent "Find headquarters and employee count" \
  --json
```

<a id="non-interactive-file-run"></a>
### 非交互式文件运行

```bash
parallel-cli enrich run \
  --source-type csv \
  --source companies.csv \
  --target enriched.csv \
  --source-columns '[{"name": "company", "description": "Company name"}]' \
  --intent "Find the CEO and annual revenue"
```

<a id="yaml-config-run"></a>
### YAML 配置运行

```bash
parallel-cli enrich run config.yaml
```

<a id="status-polling"></a>
### 状态 / 轮询

```bash
parallel-cli enrich status <task_group_id> --json
parallel-cli enrich poll <task_group_id> --json
```

非交互式操作时，请使用显式 JSON 数组来定义列描述。
在报告成功之前，验证输出文件。

<a id="findall"></a>
## FindAll

当用户希望获得一个已发现的数据集（而非简短答案）时，用于网络规模的实体发现。

```bash
parallel-cli findall run "Find AI coding agent startups with enterprise offerings" --json
parallel-cli findall run "AI startups in healthcare" -n 25 --json
parallel-cli findall status <run_id> --json
parallel-cli findall poll <run_id> --json
parallel-cli findall result <run_id> --json
parallel-cli findall schema <run_id> --json
```

当用户希望获得一组可后续审查、筛选或富化的已发现实体时，这项功能比普通搜索更适合。
<a id="monitor"></a>
## Monitor

用于随时间持续进行变更检测。

```bash
parallel-cli monitor list --json
parallel-cli monitor get <monitor_id> --json
parallel-cli monitor events <monitor_id> --json
parallel-cli monitor delete <monitor_id> --json
```

创建通常是敏感部分，因为节奏和交付很重要：

```bash
parallel-cli monitor create --help
```

当用户需要对某个页面或来源进行定期跟踪（而非一次性抓取）时，使用此命令。

<a id="recommended-hermes-usage-patterns"></a>
## 推荐的 Hermes 使用模式

<a id="fast-answer-with-citations"></a>
### 带引用的快速回答
1. 运行 `parallel-cli search ... --json`
2. 解析标题、URL、日期、摘要
3. 仅基于返回的 URL，以内联引用的方式进行总结

<a id="url-investigation"></a>
### URL 调研
1. 运行 `parallel-cli extract URL --json`
2. 如有需要，可以带 `--objective` 或 `--full-content` 重新运行
3. 引用或总结提取到的 Markdown 内容

<a id="long-research-workflow"></a>
### 长篇研究工作流
1. 运行 `parallel-cli research run ... --no-wait --json`
2. 存储返回的 ID
3. 继续其他工作或定期轮询
4. 总结最终报告并附带引用

<a id="structured-enrichment-workflow"></a>
### 结构化扩充工作流
1. 检查输入文件和列
2. 使用 `enrich suggest` 或提供显式扩充列
3. 运行 `enrich run`
4. 根据需要轮询直到完成
5. 在报告成功之前验证输出文件

<a id="error-handling-and-exit-codes"></a>
## 错误处理与退出码

CLI 文档记录了以下退出码：
- `0` 成功
- `2` 输入错误
- `3` 认证错误
- `4` API 错误
- `5` 超时

如果遇到认证错误：
1. 检查 `parallel-cli auth`
2. 确认 `PARALLEL_API_KEY` 或运行 `parallel-cli login` / `parallel-cli login --device`
3. 验证 `parallel-cli` 是否在 `PATH` 中

<a id="maintenance"></a>
## 维护

检查当前认证/安装状态：

```bash
parallel-cli auth
parallel-cli --help
```

更新命令：

```bash
parallel-cli update
pip install --upgrade parallel-web-tools
parallel-cli config auto-update-check off
```

<a id="pitfalls"></a>
## 常见陷阱

- 除非用户明确要求人类可读的输出格式，否则不要省略 `--json`。
- 不要引用 CLI 输出中未出现的来源。
- `login` 可能需要 PTY/浏览器交互。
- 对于短任务，优先前台执行；不要过度使用后台进程。
- 对于大量结果集，将 JSON 保存到 `/tmp/*.json`，而不是把所有内容塞进上下文。
- 当 Hermes 原生工具已经足够时，不要默默选择 Parallel。
- 请记住，这是一个供应商工作流，通常需要账户认证，且超出免费额度后需要付费使用。
