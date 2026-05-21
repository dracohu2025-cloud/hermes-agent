---
sidebar_position: 15
title: "自动化模板"
description: "即用型自动化方案——定时任务、GitHub 事件触发、API Webhook 以及多技能工作流"
---

<a id="automation-templates"></a>
# 自动化模板

常见自动化模式的即用模板。每个模板都使用 Hermes 内置的 [cron 调度器](/user-guide/features/cron) 实现基于时间的触发，以及 [Webhook 平台](/user-guide/messaging/webhooks) 实现基于事件的触发。

每个模板都适用于**任何模型**——不锁定在单一提供商上。

:::tip 三种触发类型
| 触发方式 | 如何工作 | 工具 |
|---------|---------|------|
<a id="three-trigger-types"></a>
| **定时调度** | 按固定节奏运行（每小时、每晚、每周） | `cronjob` 工具或 `/cron` 斜杠命令 |
| **GitHub 事件** | 在 PR 打开、推送、Issue、CI 结果时触发 | Webhook 平台（`hermes webhook subscribe`） |
| **API 调用** | 外部服务向你的端点 POST JSON 数据 | Webhook 平台（config.yaml 路由或 `hermes webhook subscribe`） |

三种方式都支持投递到 Telegram、Discord、Slack、短信、邮件、GitHub 评论或本地文件。
:::

---

<a id="development-workflow"></a>
## 开发工作流

<a id="nightly-backlog-triage"></a>
### 夜间积压任务分类

每晚对新的 Issue 进行标记、优先级排序和总结，并将摘要投递到团队频道。

**触发方式：** 定时调度（每晚）

```bash
hermes cron create "0 2 * * *" \
  "你是一个项目经理，负责对 NousResearch/hermes-agent GitHub 仓库进行积压任务分类。

1. 运行：gh issue list --repo NousResearch/hermes-agent --state open --json number,title,labels,author,createdAt --limit 30
2. 识别过去 24 小时内打开的 Issue
3. 对于每个新 Issue：
   - 建议一个优先级标签（P0-critical、P1-high、P2-medium、P3-low）
   - 建议一个类别标签（bug、feature、docs、security）
   - 写一行分类说明
4. 总结：总打开 Issue 数、今日新增数、按优先级分布

格式化为清晰的摘要。如果没有新 Issue，则回复 [SILENT]。" \
  --name "夜间积压任务分类" \
  --deliver telegram
```

<a id="automatic-pr-code-review"></a>
### 自动 PR 代码审查

每次打开拉取请求时自动进行审查，并将审查评论直接发布在 PR 上。

**触发方式：** GitHub Webhook

**选项 A — 动态订阅（CLI）：**

```bash
hermes webhook subscribe github-pr-review \
  --events "pull_request" \
  --prompt "审查此拉取请求：
仓库：{repository.full_name}
PR #{pull_request.number}：{pull_request.title}
作者：{pull_request.user.login}
操作：{action}
差异 URL：{pull_request.diff_url}

使用以下命令获取差异：curl -sL {pull_request.diff_url}

审查要点：
- 安全问题（注入、认证绕过、代码中的密钥）
- 性能问题（N+1 查询、无限循环、内存泄漏）
- 代码质量（命名、重复、错误处理）
- 新行为缺少测试

发布简洁的审查意见。如果 PR 只是简单的文档/拼写更改，简要说明即可。" \
  --skill github-code-review \
  --deliver github_comment
```

**选项 B — 静态路由（config.yaml）：**

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "your-global-secret"
      routes:
        github-pr-review:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            审查 PR #{pull_request.number}：{pull_request.title}
            仓库：{repository.full_name}
            作者：{pull_request.user.login}
            差异 URL：{pull_request.diff_url}
            审查安全、性能和代码质量。
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{pull_request.number}"
```
然后在 GitHub 中：**Settings → Webhooks → Add webhook** → Payload URL：`http://your-server:8644/webhooks/github-pr-review`，Content type：`application/json`，Secret：`github-webhook-secret`，Events：**Pull requests**。

<a id="docs-drift-detection"></a>
### 文档漂移检测

每周扫描已合并的 PR，以发现需要更新文档的 API 变更。

**触发器：** 定时（每周）

```bash
hermes cron create "0 9 * * 1" \
  "Scan the NousResearch/hermes-agent repo for documentation drift.

1. Run: gh pr list --repo NousResearch/hermes-agent --state merged --json number,title,files,mergedAt --limit 30
2. Filter to PRs merged in the last 7 days
3. For each merged PR, check if it modified:
   - Tool schemas (tools/*.py) — may need docs/reference/tools-reference.md update
   - CLI commands (hermes_cli/commands.py, hermes_cli/main.py) — may need docs/reference/cli-commands.md update
   - Config options (hermes_cli/config.py) — may need docs/user-guide/configuration.md update
   - Environment variables — may need docs/reference/environment-variables.md update
4. Cross-reference: for each code change, check if the corresponding docs page was also updated in the same PR

Report any gaps where code changed but docs didn't. If everything is in sync, respond with [SILENT]." \
  --name "Docs drift detection" \
  --deliver telegram
```

<a id="dependency-security-audit"></a>
### 依赖安全审计

每日扫描项目依赖中的已知漏洞。

**触发器：** 定时（每日）

```bash
hermes cron create "0 6 * * *" \
  "Run a dependency security audit on the hermes-agent project.

1. cd ~/.hermes/hermes-agent && source .venv/bin/activate
2. Run: pip audit --format json 2>/dev/null || pip audit 2>&1
3. Run: npm audit --json 2>/dev/null (in website/ directory if it exists)
4. Check for any CVEs with CVSS score >= 7.0

If vulnerabilities found:
- List each one with package name, version, CVE ID, severity
- Check if an upgrade is available
- Note if it's a direct dependency or transitive

If no vulnerabilities, respond with [SILENT]." \
  --name "Dependency audit" \
  --deliver telegram
```

---

<a id="devops-monitoring"></a>
## DevOps 与监控

<a id="deploy-verification"></a>
### 部署验证

每次部署后触发冒烟测试。你的 CI/CD 管道在部署完成时向 webhook 发送 POST 请求。

**触发器：** API 调用（webhook）

```bash
hermes webhook subscribe deploy-verify \
  --events "deployment" \
  --prompt "A deployment just completed:
Service: {service}
Environment: {environment}
Version: {version}
Deployed by: {deployer}

Run these verification steps:
1. Check if the service is responding: curl -s -o /dev/null -w '%{http_code}' {health_url}
2. Search recent logs for errors: check the deployment payload for any error indicators
3. Verify the version matches: curl -s {health_url}/version

Report: deployment status (healthy/degraded/failed), response time, any errors found.
If healthy, keep it brief. If degraded or failed, provide detailed diagnostics." \
  --deliver telegram
```

你的 CI/CD 管道通过以下方式触发：

```bash
curl -X POST http://your-server:8644/webhooks/deploy-verify \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -d '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}'
```
<a id="alert-triage"></a>
### 告警分类与处理

将监控告警与近期变更关联起来，起草响应方案。适用于 Datadog、PagerDuty、Grafana 或任何支持 POST JSON 的告警系统。

**触发方式：** API 调用（webhook）

```bash
hermes webhook subscribe alert-triage \
  --prompt "收到监控告警：
告警名称：{alert.name}
严重级别：{alert.severity}
服务：{alert.service}
消息：{alert.message}
时间戳：{alert.timestamp}

调查步骤：
1. 在网上搜索此错误模式的已知问题
2. 检查是否与近期部署或配置变更有关
3. 起草一份分类摘要，包括：
   - 可能的原因
   - 建议的第一步处置措施
   - 升级建议（P1-P4）

请简洁明了。此结果将发送到值班频道。" \
  --deliver slack
```

<a id="uptime-monitor"></a>
### 在线状态监控

每 30 分钟检查一次端点，仅在服务宕机时通知。

**触发方式：** 定时调度（每 30 分钟）

```python title="~/.hermes/scripts/check-uptime.py"
import urllib.request, json, time

ENDPOINTS = [
    {"name": "API", "url": "https://api.example.com/health"},
    {"name": "Web", "url": "https://www.example.com"},
    {"name": "Docs", "url": "https://docs.example.com"},
]

results = []
for ep in ENDPOINTS:
    try:
        start = time.time()
        req = urllib.request.Request(ep["url"], headers={"User-Agent": "Hermes-Monitor/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        results.append({"name": ep["name"], "status": resp.getcode(), "ms": elapsed})
    except Exception as e:
        results.append({"name": ep["name"], "status": "DOWN", "error": str(e)})

down = [r for r in results if r.get("status") == "DOWN" or (isinstance(r.get("status"), int) and r["status"] >= 500)]
if down:
    print("OUTAGE DETECTED")
    for r in down:
        print(f"  {r['name']}: {r.get('error', f'HTTP {r[\"status\"]}')} ")
    print(f"\nAll results: {json.dumps(results, indent=2)}")
else:
    print("NO_ISSUES")
```

```bash
hermes cron create "every 30m" \
  "如果脚本输出 OUTAGE DETECTED，请总结哪些服务宕机并推断可能的原因。如果输出 NO_ISSUES，则回复 [SILENT]。" \
  --script ~/.hermes/scripts/check-uptime.py \
  --name "在线状态监控" \
  --deliver telegram
```

---

<a id="research-intelligence"></a>
## 研究与情报

<a id="competitive-repository-scout"></a>
### 竞品仓库侦察

监控竞品仓库，关注有价值的 PR、功能更新和架构决策。

**触发方式：** 定时调度（每天）

```bash
hermes cron create "0 8 * * *" \
  "侦察以下 AI Agent 仓库过去 24 小时的显著动态：

待检查仓库：
- anthropics/claude-code
- openai/codex
- All-Hands-AI/OpenHands
- Aider-AI/aider

对每个仓库：
1. gh pr list --repo <repo> --state all --json number,title,author,createdAt,mergedAt --limit 15
2. gh issue list --repo <repo> --state open --json number,title,labels,createdAt --limit 10

重点关注：
- 正在开发的新功能
- 架构变更
- 我们可以借鉴的集成模式
- 可能同样影响我们的安全修复

忽略常规依赖更新和 CI 修复。如果没有值得关注的内容，回复 [SILENT]。
如果有所发现，请按仓库组织，并对每项内容进行简要分析。" \
  --skill competitive-pr-scout \
  --name "竞品侦察" \
  --deliver telegram
```
<a id="ai-news-digest"></a>
### AI 新闻摘要

每周 AI/ML 发展动态汇总。

**触发方式：** 定时任务（每周）

```bash
hermes cron create "0 9 * * 1" \
  "生成一份涵盖过去 7 天的每周 AI 新闻摘要：

1. 搜索网络上主要的 AI 公告、模型发布和研究突破
2. 搜索 GitHub 上热门的 ML 仓库
3. 在 arXiv 上查找关于语言模型和 Agent 的高引用论文

结构：
## 头条新闻（3-5 条重大新闻）
## 值得关注的论文（2-3 篇论文，每篇附一句话摘要）
## 开源动态（有趣的新仓库或重大发布）
## 行业动向（融资、收购、产品发布）

每条内容控制在 1-2 句话内。包含链接。总字数不超过 600 字。" \
  --name "每周 AI 摘要" \
  --deliver telegram
```

<a id="paper-digest-with-notes"></a>
### 论文摘要与笔记

每日 arXiv 扫描，将摘要保存到你的笔记系统中。

**触发方式：** 定时任务（每日）

```bash
hermes cron create "0 8 * * *" \
  "在 arXiv 上搜索过去一天内关于'语言模型推理'或'工具使用 Agent'的 3 篇最有趣的论文。为每篇论文创建一条 Obsidian 笔记，包含标题、作者、摘要总结、主要贡献，以及与 Hermes Agent 开发的潜在关联。" \
  --skill arxiv --skill obsidian \
  --name "论文摘要" \
  --deliver local
```

---

<a id="github-event-automations"></a>
## GitHub 事件自动化

<a id="issue-auto-labeling"></a>
### Issue 自动打标签

自动为新 issue 打标签并回复。

**触发方式：** GitHub webhook

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "收到新的 GitHub issue：
仓库：{repository.full_name}
Issue #{issue.number}：{issue.title}
作者：{issue.user.login}
操作：{action}
正文：{issue.body}
标签：{issue.labels}

如果这是一个新 issue（action=opened）：
1. 仔细阅读 issue 标题和正文
2. 建议合适的标签（bug、feature、docs、security、question）
3. 如果是 bug 报告，尝试从描述中识别受影响的组件
4. 发布一条有帮助的初始回复，确认已收到该 issue

如果是标签或分配变更，回复 [SILENT]。" \
  --deliver github_comment
```

<a id="ci-failure-analysis"></a>
### CI 失败分析

分析 CI 失败原因并在 PR 上发布诊断信息。

**触发方式：** GitHub webhook

```yaml
# config.yaml 路由
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        ci-failure:
          events: ["check_run"]
          secret: "ci-secret"
          prompt: |
            CI 检查失败：
            仓库：{repository.full_name}
            检查项：{check_run.name}
            状态：{check_run.conclusion}
            PR：#{check_run.pull_requests.0.number}
            详情 URL：{check_run.details_url}

            如果结论是 "failure"：
            1. 如果可访问，从详情 URL 获取日志
            2. 识别失败的可能原因
            3. 建议修复方案
            如果结论是 "success"，回复 [SILENT]。
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{check_run.pull_requests.0.number}"
```
<a id="auto-port-changes-across-repos"></a>
### 跨仓库自动移植变更

当一个仓库中的 PR 合并后，自动将等效变更移植到另一个仓库。

**触发器：** GitHub webhook

```bash
hermes webhook subscribe auto-port \
  --events "pull_request" \
  --prompt "源仓库中的 PR 已合并：
仓库：{repository.full_name}
PR #{pull_request.number}：{pull_request.title}
作者：{pull_request.user.login}
操作：{action}
合并提交：{pull_request.merge_commit_sha}

如果操作为 'closed' 且 pull_request.merged 为 true：
1. 获取差异：curl -sL {pull_request.diff_url}
2. 分析变更内容
3. 判断此变更是否需要移植到等效的 Go SDK
4. 如果需要，创建一个分支，应用等效变更，并在目标仓库上打开一个 PR
5. 在新 PR 描述中引用原始 PR

如果操作不是 'closed' 或未合并，则响应 [SILENT]。" \
  --skill github-pr-workflow \
  --deliver log
```

---

<a id="business-operations"></a>
## 业务运营

<a id="stripe-payment-monitoring"></a>
### Stripe 支付监控

跟踪支付事件并获取失败摘要。

**触发器：** API 调用（webhook）

```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed,charge.dispute.created" \
  --prompt "收到 Stripe 事件：
事件类型：{type}
金额：{data.object.amount} 分（{data.object.currency}）
客户：{data.object.customer}
状态：{data.object.status}

对于 payment_intent.payment_failed：
- 从 {data.object.last_payment_error} 识别失败原因
- 建议这是临时问题（重试）还是永久性问题（联系客户）

对于 charge.dispute.created：
- 标记为紧急
- 总结争议详情

对于 payment_intent.succeeded：
- 仅简要确认

保持回复简洁，适合运营频道。" \
  --deliver slack
```

<a id="daily-revenue-summary"></a>
### 每日收入摘要

每天早上汇总关键业务指标。

**触发器：** 定时任务（每日）

```bash
hermes cron create "0 8 * * *" \
  "生成一份早间业务指标摘要。

搜索网络获取：
1. 当前比特币和以太坊价格
2. 标普500状态（盘前或前收盘价）
3. 过去12小时内的重大科技/AI行业新闻

格式化为简短的早间简报，最多3-4个要点。
以清晰、可快速浏览的消息形式交付。" \
  --name "早间简报" \
  --deliver telegram
```

---

<a id="multi-skill-workflows"></a>
## 多技能工作流

<a id="security-audit-pipeline"></a>
### 安全审计流水线

组合多种技能进行全面的每周安全审查。

**触发器：** 定时任务（每周）

```bash
hermes cron create "0 3 * * 0" \
  "对 hermes-agent 代码库进行全面的安全审计。

1. 检查依赖项漏洞（pip audit, npm audit）
2. 搜索代码库中常见的安全反模式：
   - 硬编码的密钥或 API 密钥
   - SQL 注入向量（查询中的字符串格式化）
   - 路径遍历风险（用户输入直接用于文件路径且未经验证）
   - 不安全的反序列化（pickle.loads, 未使用 SafeLoader 的 yaml.load）
3. 审查最近的提交（过去7天）中与安全相关的变更
4. 检查是否有新增的环境变量未记录在文档中

编写一份安全报告，按严重程度（严重、高、中、低）对发现的问题进行分类。
如果未发现问题，则报告健康状况良好。" \
  --skill codebase-security-audit \
  --name "每周安全审计" \
  --deliver telegram
```
<a id="content-pipeline"></a>
### 内容流水线

按计划研究、起草和准备内容。

**触发方式：** 定时（每周）

```bash
hermes cron create "0 10 * * 3" \
  "研究和起草一篇关于 AI Agent 热门话题的技术博客文章大纲。

1. 搜索本周讨论最多的 AI Agent 话题
2. 挑选与开源 AI Agent 相关且最有趣的一个
3. 创建包含以下内容的大纲：
   - 钩子/引言角度
   - 3-4 个关键章节
   - 适合开发者的技术深度
   - 包含可操作要点的结论
4. 将大纲保存到 ~/drafts/blog-$(date +%Y%m%d).md

大纲保持在约 300 字。这是一个起点，不是最终文章。" \
  --name "博客大纲" \
  --deliver local
```

---

<a id="quick-reference"></a>
## 快速参考

<a id="cron-schedule-syntax"></a>
### Cron 调度语法

| 表达式 | 含义 |
|-----------|---------|
| `every 30m` | 每 30 分钟 |
| `every 2h` | 每 2 小时 |
| `0 2 * * *` | 每天凌晨 2:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `0 9 * * 1-5` | 工作日（周一至周五）上午 9:00 |
| `0 3 * * 0` | 每周日凌晨 3:00 |
| `0 */6 * * *` | 每 6 小时 |

<a id="delivery-targets"></a>
### 交付目标

| 目标 | 标志 | 备注 |
|--------|------|---------|
| 同一聊天 | `--deliver origin` | 默认 — 交付到创建任务的位置 |
| 本地文件 | `--deliver local` | 保存输出，不发送通知 |
| Telegram | `--deliver telegram` | 主频道，或 `telegram:CHAT_ID` 指定频道 |
| Discord | `--deliver discord` | 主频道，或 `discord:CHANNEL_ID` 指定频道 |
| Slack | `--deliver slack` | 主频道 |
| 短信 | `--deliver sms:+15551234567` | 直接发送到手机号 |
| 特定话题 | `--deliver telegram:-100123:456` | Telegram 论坛话题 |

<a id="webhook-template-variables"></a>
### Webhook 模板变量

| 变量 | 描述 |
|----------|-------------|
| `{pull_request.title}` | PR 标题 |
| `{issue.number}` | Issue 编号 |
| `{repository.full_name}` | `owner/repo` |
| `{action}` | 事件动作（opened、closed 等） |
| `{__raw__}` | 完整 JSON 负载（超过 4000 字符时截断） |
| `{sender.login}` | 触发事件的 GitHub 用户 |

<a id="the-silent-pattern"></a>
### [SILENT] 模式

当 cron 任务的响应中包含 `[SILENT]` 时，交付会被抑制。使用此模式可避免在静默运行时产生通知骚扰：

```
如果没有值得注意的事情发生，请回复 [SILENT]。
```

这意味着只有当 Agent 有内容需要报告时，你才会收到通知。
