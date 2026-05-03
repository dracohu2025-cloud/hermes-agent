---
title: "Parallel Cli"
sidebar_label: "Parallel Cli"
description: "Parallel CLI 的可选供应商技能——Agent 原生网络搜索、提取、深度研究、丰富化、FindAll 和监控"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Parallel Cli {#parallel-cli}

Parallel CLI 的可选供应商技能——Agent 原生网络搜索、提取、深度研究、丰富化、FindAll 和监控。优先使用 JSON 输出和非交互式流程。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/research/parallel-cli` 安装 |
| 路径 | `optional-skills/research/parallel-cli` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `Research`, `Web`, `Search`, `Deep-Research`, `Enrichment`, `CLI` |
| 相关技能 | [`duckduckgo-search`](/user-guide/skills/optional/research/research-duckduckgo-search), [`mcporter`](/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="parallel-cli"></a>
# Parallel CLI

当用户明确要求使用 Parallel，或者终端原生工作流受益于 Parallel 的供应商特定栈（用于网络搜索、提取、深度研究、丰富化、实体发现或监控）时，使用 `parallel-cli`。

这是一个可选第三方工作流，并非 Hermes 核心能力。

重要期望：
- Parallel 是一项付费服务（提供免费套餐），并非完全免费的本地工具。
- 它与 Hermes 原生 `web_search` / `web_extract` 功能重叠，因此对于普通查询，默认不要优先使用它。
- 当用户特别提到 Parallel，或需要 Parallel 的丰富化、FindAll 或监控工作流等能力时，优先使用此技能。

`parallel-cli` 专为 Agent 设计：
- 通过 `--json` 输出 JSON
- 非交互式命令执行
- 通过 `--no-wait`、`status` 和 `poll` 实现异步长时间运行任务
- 通过 `--previous-interaction-id` 实现上下文链
- 在一个 CLI 中完成搜索、提取、研究、丰富化、实体发现和监控

## 何时使用 {#when-to-use-it}

在以下情况优先使用此技能：
- 用户明确提到 Parallel 或 `parallel-cli`
- 任务需要比简单的一次性搜索/提取更丰富的工作流
- 需要可以启动并稍后轮询的异步深度研究任务
- 需要结构化丰富化、FindAll 实体发现或监控

当未特别要求 Parallel 时，对于快速一次性查询，优先使用 Hermes 原生 `web_search` / `web_extract`。

## 安装 {#installation}

尝试环境中可用的侵入性最小的安装方式。

### Homebrew {#homebrew}

```bash
brew install parallel-web/tap/parallel-cli
```

### npm {#npm}

```bash
npm install -g parallel-web-cli
```

### Python 包 {#python-package}

```bash
pip install "parallel-web-tools[cli]"
```

### 独立安装程序 {#standalone-installer}

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

如果需要隔离的 Python 安装，也可以使用 `pipx`：

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

## 身份验证 {#authentication}
交互式登录：

```bash
parallel-cli login
```

无头模式 / SSH / CI：

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

## 核心规则集 {#core-rule-set}

1. 需要机器可读输出时，始终优先使用 `--json`。
2. 优先使用显式参数和非交互式流程。
3. 对于长时间运行的任务，使用 `--no-wait`，然后通过 `status` / `poll` 查看。
4. 只引用 CLI 输出返回的 URL。
5. 如果后续可能有问题，将大型 JSON 输出保存到临时文件。
6. 仅对真正长时间运行的工作流使用后台进程；否则在前台运行。
7. 除非用户明确要求使用 Parallel 或需要 Parallel 专属工作流，否则优先使用 Hermes 原生工具。

## 快速参考 {#quick-reference}

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

## 常用标志和模式 {#common-flags-and-patterns}

常用的标志：
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
echo "Anthropic 最新融资情况如何？" | parallel-cli search - --json
echo "研究问题" | parallel-cli research run - --json
```

## 搜索 {#search}

用于当前网络查询，返回结构化结果。

```bash
parallel-cli search "Anthropic 最新的 AI 模型是什么？" --json
parallel-cli search "苹果公司的 SEC 文件" --include-domains sec.gov --json
parallel-cli search "比特币价格" --after-date 2026-01-01 --max-results 10 --json
parallel-cli search "最新浏览器基准测试" --mode one-shot --json
parallel-cli search "AI 编程 Agent 企业评测" --mode agentic --json
```

有用的约束条件：
- `--include-domains` 缩小到可信来源
- `--exclude-domains` 排除噪音域名
- `--after-date` 按时效性过滤
- `--max-results` 当需要更广覆盖时使用

如果预期会有后续问题，保存输出：

```bash
parallel-cli search "React 19 最新变化" --json -o /tmp/react-19-search.json
```

总结结果时：
- 先给出答案
- 包含日期、名称和具体事实
- 只引用返回的来源
- 不要编造 URL 或来源标题

## 提取 {#extraction}

用于从 URL 提取干净内容或 Markdown。

```bash
parallel-cli extract https://example.com --json
parallel-cli extract https://company.com --objective "查找定价信息" --json
parallel-cli extract https://example.com --full-content --json
parallel-cli fetch https://example.com --json
```
当页面内容宽泛且你只需要某一部分信息时，使用 `--objective`。

## 深度研究 {#deep-research}

用于可能需要较长时间的深层多步研究任务。

常见处理器层级：
- `lite` / `base`：更快、更便宜的扫描
- `core` / `pro`：更全面的综合
- `ultra`：最繁重的研究任务

### 同步 {#synchronous}

```bash
parallel-cli research run \
  "Compare the leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor core \
  --json
```

### 异步启动 + 轮询 {#async-launch-poll}

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

### 上下文链式追问 / 跟进 {#context-chaining-follow-up}

```bash
parallel-cli research run "What are the top AI coding agents?" --json
parallel-cli research run \
  "What enterprise controls does the top-ranked one offer?" \
  --previous-interaction-id trun_xxx \
  --json
```

推荐的 Hermes 工作流：
1. 使用 `--no-wait --json` 启动
2. 捕获返回的 run/task ID
3. 如果用户想继续其他工作，则继续推进
4. 稍后调用 `status` 或 `poll`
5. 根据返回的源数据，用引用信息总结最终报告

## 数据丰富 {#enrichment}

当用户有 CSV/JSON/表格输入，并希望从网络研究中推断出额外的列时使用。

### 建议列 {#suggest-columns}

```bash
parallel-cli enrich suggest "Find the CEO and annual revenue" --json
```

### 规划配置 {#plan-a-config}

```bash
parallel-cli enrich plan -o config.yaml
```

### 内联数据 {#inline-data}

```bash
parallel-cli enrich run \
  --data '[{"company": "Anthropic"}, {"company": "Mistral"}]' \
  --intent "Find headquarters and employee count" \
  --json
```

### 非交互式文件运行 {#non-interactive-file-run}

```bash
parallel-cli enrich run \
  --source-type csv \
  --source companies.csv \
  --target enriched.csv \
  --source-columns '[{"name": "company", "description": "Company name"}]' \
  --intent "Find the CEO and annual revenue"
```

### YAML 配置运行 {#yaml-config-run}

```bash
parallel-cli enrich run config.yaml
```

### 状态 / 轮询 {#status-polling}

```bash
parallel-cli enrich status <task_group_id> --json
parallel-cli enrich poll <task_group_id> --json
```

在非交互式操作时，请使用显式的 JSON 数组来定义列。
在报告成功之前，请验证输出文件。

## FindAll {#findall}

当用户想要一个发现的数据集而不是简短答案时，用于网络规模的实体发现。

```bash
parallel-cli findall run "Find AI coding agent startups with enterprise offerings" --json
parallel-cli findall run "AI startups in healthcare" -n 25 --json
parallel-cli findall status <run_id> --json
parallel-cli findall poll <run_id> --json
parallel-cli findall result <run_id> --json
parallel-cli findall schema <run_id> --json
```

当用户想要一组可后续审查、过滤或丰富的已发现实体时，这比普通搜索更合适。
## 监控 {#monitor}

用于随时间持续检测变化。

```bash
parallel-cli monitor list --json
parallel-cli monitor get <monitor_id> --json
parallel-cli monitor events <monitor_id> --json
parallel-cli monitor delete <monitor_id> --json
```

创建通常是最敏感的部分，因为运行节奏和交付方式很重要：

```bash
parallel-cli monitor create --help
```

当用户希望持续追踪某个页面或来源，而不是一次性抓取时，使用此命令。

## 推荐的 Hermes 使用模式 {#recommended-hermes-usage-patterns}

### 带引用的快速回答 {#fast-answer-with-citations}
1. 运行 `parallel-cli search ... --json`
2. 解析标题、URL、日期、摘录
3. 仅使用返回的 URL 中的内联引用进行总结

### URL 调查 {#url-investigation}
1. 运行 `parallel-cli extract URL --json`
2. 如果需要，重新运行并添加 `--objective` 或 `--full-content`
3. 引用或总结提取出的 Markdown 内容

### 长研究流程 {#long-research-workflow}
1. 运行 `parallel-cli research run ... --no-wait --json`
2. 保存返回的 ID
3. 继续其他工作或定期轮询
4. 使用引用总结最终报告

### 结构化扩充流程 {#structured-enrichment-workflow}
1. 检查输入文件和列
2. 使用 `enrich suggest` 或提供明确的扩充列
3. 运行 `enrich run`
4. 如果需要，轮询直到完成
5. 在报告成功之前验证输出文件

## 错误处理与退出码 {#error-handling-and-exit-codes}

CLI 文档中记录了以下退出码：
- `0` 成功
- `2` 错误输入
- `3` 认证错误
- `4` API 错误
- `5` 超时

如果遇到认证错误：
1. 检查 `parallel-cli auth`
2. 确认 `PARALLEL_API_KEY` 或运行 `parallel-cli login` / `parallel-cli login --device`
3. 验证 `parallel-cli` 是否在 `PATH` 中

## 维护 {#maintenance}

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

## 常见陷阱 {#pitfalls}

- 除非用户明确需要人类可读的格式化输出，否则不要省略 `--json`。
- 不要引用 CLI 输出中未出现的来源。
- `login` 可能需要 PTY/浏览器交互。
- 短任务优先在前台执行，不要过度使用后台进程。
- 对于大型结果集，将 JSON 保存到 `/tmp/*.json`，而不是把所有内容塞进上下文。
- 当 Hermes 原生工具已经足够时，不要默默选择 Parallel。
- 请记住，这是一个供应商工作流，通常需要账户认证以及免费额度之外的付费使用。
