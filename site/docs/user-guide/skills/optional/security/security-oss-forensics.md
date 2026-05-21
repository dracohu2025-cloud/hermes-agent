---
title: "Oss Forensics — 供应链调查、证据恢复与 GitHub 仓库取证分析"
sidebar_label: "Oss Forensics"
description: "供应链调查、证据恢复与 GitHub 仓库取证分析"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="oss-forensics"></a>
# Oss Forensics

供应链调查、证据恢复与 GitHub 仓库取证分析。
涵盖已删除提交恢复、强制推送检测、IOC 提取、多源证据收集、
假设形成/验证以及结构化取证报告。
灵感来源于 RAPTOR 的 1800+ 行 OSS Forensics 系统。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/oss-forensics` 安装 |
| 路径 | `optional-skills/security/oss-forensics` |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="oss-security-forensics-skill"></a>
# OSS 安全取证技能

一个用于研究开源供应链攻击的 7 阶段多 Agent 调查框架。
改编自 RAPTOR 的取证系统。涵盖 GitHub Archive、Wayback Machine、GitHub API、
本地 git 分析、IOC 提取、基于证据的假设形成与验证，
以及最终取证报告生成。
---

<a id="anti-hallucination-guardrails"></a>
## ⚠️ 反幻觉护栏

在每次调查步骤之前请先阅读以下内容。违反这些规则将导致报告无效。

1. **证据优先原则**：任何报告、假设或摘要中的每一项主张都必须引用至少一个证据 ID（`EV-XXXX`）。禁止出现没有引用的断言。
2. **各司其职**：每个子 Agent（调查员）只有一个数据源。不要混合使用数据源。GH Archive 调查员不查询 GitHub API，反之亦然。角色边界是硬性的。
3. **事实与假设分离**：所有未经核实的推论都要标注 `[HYPOTHESIS]`。只有经过原始来源验证的陈述才能作为事实陈述。
4. **禁止捏造证据**：假设验证器在接受假设之前，必须机械地检查每个被引用的证据 ID 是否确实存在于证据存储中。
5. **反驳需有据可查**：没有具体、有证据支持的反驳论点，就不能驳回一个假设。“未发现证据”不足以反驳——它只会使假设变得不确定。
6. **SHA/URL 双重验证**：任何作为证据引用的提交 SHA、URL 或外部标识符，在标记为已验证之前，必须至少从两个来源独立确认。
7. **可疑代码规则**：切勿在本地运行在被调查仓库中找到的代码。仅进行静态分析，或在沙盒环境中使用 `execute_code`。
8. **机密信息编辑**：调查过程中发现的任何 API 密钥、令牌或凭证都必须在最终报告中编辑掉。仅在内部记录它们。

> **路径约定**：在本技能中，`SKILL_DIR` 指代该技能安装目录的根目录（即包含此 `SKILL.md` 的文件夹）。当技能被加载时，请将 `SKILL_DIR` 解析为实际路径——例如 `~/.hermes/skills/security/oss-forensics/` 或对应的 `optional-skills/` 目录。所有脚本和模板引用均相对于该路径。
<a id="phase-0-initialization"></a>
## 阶段 0：初始化

1. 创建调查工作目录：
   ```bash
   mkdir investigation_$(echo "REPO_NAME" | tr '/' '_')
   cd investigation_$(echo "REPO_NAME" | tr '/' '_')
   ```
2. 初始化证据存储：
   ```bash
   python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list
   ```
3. 复制取证报告模板：
   ```bash
   cp SKILL_DIR/templates/forensic-report.md ./investigation-report.md
   ```
4. 创建一个 `iocs.md` 文件，用于跟踪已发现的入侵指标（Indicators of Compromise）。
5. 记录调查开始时间、目标仓库以及声明的调查目标。

---

<a id="phase-1-prompt-parsing-and-ioc-extraction"></a>
## 阶段 1：提示解析与 IOC 提取

**目标**：从用户请求中提取所有结构化调查目标。

**操作**：
- 解析用户提示，提取：
  - 目标仓库（`owner/repo`）
  - 目标参与者（GitHub 用户名、电子邮件地址）
  - 关注的时间窗口（提交日期范围、PR 时间戳）
  - 提供的入侵指标：提交 SHA、文件路径、包名、IP 地址、域名、API 密钥/令牌、恶意 URL
  - 任何关联的厂商安全报告或博客文章
**工具**：仅推理，或使用 `execute_code` 从大文本块中通过正则提取。

**输出**：将提取的 IOC 填入 `iocs.md`。每个 IOC 必须包含：
- 类型（可选值：COMMIT_SHA、FILE_PATH、API_KEY、SECRET、IP_ADDRESS、DOMAIN、PACKAGE_NAME、ACTOR_USERNAME、MALICIOUS_URL、OTHER）
- 值
- 来源（用户提供、推断）

**参考**：IOC 分类法请参见 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md)。

---

<a id="phase-2-parallel-evidence-collection"></a>
## 阶段 2：并行证据收集

使用 `delegate_task`（批处理模式，最多 3 个并发）生成最多 5 个专业调查子 Agent。每个调查者拥有**单一数据源**，且不得混合来源。

> **编排器说明**：在每项委托任务的 `context` 字段中传入阶段 1 的 IOC 列表和调查时间窗口。

---

<a id="investigator-1-local-git-investigator"></a>
### 调查者 1：本地 Git 调查者

**角色边界**：你仅查询本地 Git 仓库。不得调用任何外部 API。
**Actions**:
```bash
# 克隆仓库
git clone https://github.com/OWNER/REPO.git target_repo && cd target_repo

# 完整提交日志（含统计信息）
git log --all --full-history --stat --format="%H|%ae|%an|%ai|%s" > ../git_log.txt

# 检测强制推送证据（孤立/悬空提交）
git fsck --lost-found --unreachable 2>&1 | grep commit > ../dangling_commits.txt

# 检查 reflog 以发现重写的历史
git reflog --all > ../reflog.txt

# 列出所有分支（包括已删除的远程引用）
git branch -a -v > ../branches.txt

# 查找可疑的大二进制文件添加
git log --all --diff-filter=A --name-only --format="%H %ai" -- "*.so" "*.dll" "*.exe" "*.bin" > ../binary_additions.txt

# 检查 GPG 签名异常
git log --show-signature --format="%H %ai %aN" > ../signature_check.txt 2>&1
```

**需要收集的证据**（通过 `python3 SKILL_DIR/scripts/evidence-store.py add` 添加）：
- 每个悬空提交的 SHA → 类型：`git`
- 强制推送证据（显示历史重写的 reflog）→ 类型：`git`
- 来自已验证贡献者的未签名提交 → 类型：`git`
- 可疑的二进制文件添加 → 类型：`git`
**参考**：关于如何访问强制推送的提交，请参见 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)。

---

<a id="investigator-2-github-api-investigator"></a>
### 调查者 2：GitHub API 调查者

**角色边界**：你仅查询 GITHUB REST API。不要在本机运行 git 命令。

**操作**：
```bash
# 提交记录（分页）
curl -s "https://api.github.com/repos/OWNER/REPO/commits?per_page=100" > api_commits.json

# 拉取请求（包括已关闭/已删除的）
curl -s "https://api.github.com/repos/OWNER/REPO/pulls?state=all&per_page=100" > api_prs.json

# 问题
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=all&per_page=100" > api_issues.json

# 贡献者与协作者变更
curl -s "https://api.github.com/repos/OWNER/REPO/contributors" > api_contributors.json

# 仓库事件（最近 300 条）
curl -s "https://api.github.com/repos/OWNER/REPO/events?per_page=100" > api_events.json

# 检查特定可疑提交 SHA 的详细信息
curl -s "https://api.github.com/repos/OWNER/REPO/git/commits/SHA" > commit_detail.json

# 发布版本
curl -s "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" > api_releases.json

# 检查某个提交是否存在（强制推送的提交在 commits/ 上可能返回 404，但在 git/commits/ 上会成功）
curl -s "https://api.github.com/repos/OWNER/REPO/commits/SHA" | jq .sha
```
**交叉引用目标**（将标记差异作为证据）：
- 存档中存在 PR，但 API 中缺失 → 删除证据
- 存档事件中有贡献者，但贡献者列表中不存在 → 权限撤销证据
- 存档的 PushEvents 中有提交，但 API 提交列表中不存在 → 强制推送/删除证据

**参考**：参见 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md) 了解 GH 事件类型。

---

<a id="investigator-3-wayback-machine-investigator"></a>
### 调查员 3：Wayback Machine 调查员

**角色边界**：你只能查询 WAYBACK MACHINE CDX API。请勿使用 GitHub API。

**目标**：恢复已删除的 GitHub 页面（README、问题、PR、发布版本、维基页面）。

**操作**：
```bash
# 搜索仓库主页的存档快照
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO&output=json&limit=100&from=YYYYMMDD&to=YYYYMMDD" > wayback_main.json

# 搜索某个已删除的具体问题
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/issues/NUM&output=json&limit=50" > wayback_issue_NUM.json

# 搜索某个已删除的具体 PR
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/pull/NUM&output=json&limit=50" > wayback_pr_NUM.json

# 获取页面的最佳快照
# 使用 Wayback Machine URL：https://web.archive.org/web/TIMESTAMP/ORIGINAL_URL
# 示例：https://web.archive.org/web/20240101000000*/github.com/OWNER/REPO

# 高级：搜索已删除的发布版本/标签
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/releases/tag/*&output=json" > wayback_tags.json

# 高级：搜索历史维基变更
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/wiki/*&output=json" > wayback_wiki.json
```
**需要收集的证据**：
- 已删除问题/PR的归档快照及其内容
- 展示变更历史的README历史版本
- 存在于归档中但在当前GitHub状态中缺失的内容证据

**参考**：参见 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md) 了解CDX API参数。

---

<a id="investigator-4-gh-archive-bigquery-investigator"></a>
### 调查员 4：GH Archive / BigQuery 调查员

**角色边界**：你**仅**通过BIGQUERY查询GITHUB ARCHIVE。这是所有公开GitHub事件的防篡改记录。

> **先决条件**：需要具有BigQuery访问权限的Google Cloud凭据（`gcloud auth application-default login`）。如果不可用，请跳过此调查员并在报告中注明。

**成本优化规则**（强制要求）：
1. 每次查询前，务必先运行 `--dry_run` 来预估成本。
2. 使用 `_TABLE_SUFFIX` 按日期范围过滤，尽量减少扫描的数据量。
3. 只SELECT你需要的列。
4. 除非是聚合操作，否则要添加LIMIT。
```bash
# 模板：针对 OWNER/REPO 的 PushEvent 进行安全的 BigQuery 查询
bq query --use_legacy_sql=false --dry_run "
SELECT created_at, actor.login, payload.commits, payload.before, payload.head,
       payload.size, payload.distinct_size
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'PushEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 1000
"
# 如果成本可接受，去掉 --dry_run 重新运行

# 检测强制推送：distinct_size 为零的 PushEvent 表示提交被强制擦除
# payload.distinct_size = 0 AND payload.size > 0 → 强制推送指示器

# 检查已删除的分支事件
bq query --use_legacy_sql=false "
SELECT created_at, actor.login, payload.ref, payload.ref_type
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'DeleteEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 200
"
```

**需要收集的证据**：
- 强制推送事件（payload.size > 0, payload.distinct_size = 0）
- 针对分支/标签的 DeleteEvent
- 可疑 CI/CD 自动化的 WorkflowRunEvent
- 位于 git 日志“缺口”之前的 PushEvent（重写证据）
**参考**：所有 12 种事件类型及查询模式，请参见 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md)。

---

<a id="investigator-5-ioc-enrichment-investigator"></a>
### 调查员 5：IOC 丰富调查员

**角色边界**：你仅能使用被动公开来源，对第一阶段已有的 IOC 进行丰富。不得执行目标仓库中的任何代码。

**操作**：
- 对于每个提交 SHA：尝试通过直接 GitHub URL（`github.com/OWNER/REPO/commit/SHA.patch`）进行恢复
- 对于每个域名/IP：检查被动 DNS、WHOIS 记录（通过 `web_extract` 在公开 WHOIS 服务上查询）
- 对于每个包名：检查 npm/PyPI 上是否存在匹配的恶意包报告
- 对于每个行为者用户名：检查 GitHub 个人资料、贡献历史、账号年龄
- 使用 3 种方法恢复强制推送的提交（参见 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)）

## 阶段 4：假设形成

一个假设必须：
- 陈述一个具体的断言（例如，“行为者 X 在 DATE 对 BRANCH 进行了强制推送以擦除提交 SHA”）
- 引用至少 2 个支持该断言的证据 ID（`EV-XXXX`、`EV-YYYY`）
- 指出哪些证据可以反驳它
- 在验证之前标记为 `[HYPOTHESIS]`
**常见假设模板**（参见 [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md)）：
- 维护者失陷：合法账户在接管后被用来注入恶意代码
- 依赖混淆：包名抢注，以拦截安装过程
- CI/CD 注入：恶意修改工作流，在构建过程中运行代码
- 域名仿冒攻击：名称极为相似的包，针对拼写错误的用户
- 凭据泄漏：令牌/密钥被意外提交，然后通过强制推送来擦除

针对每一个假设，生成一个 `delegate_task` 子 Agent，在确认之前尝试寻找反驳证据。

---

<a id="phase-5-hypothesis-validation"></a>
## 阶段 5：假设验证

验证子 Agent 必须机械地检查以下内容：

1.  对于每个假设，提取所有引用的证据 ID。
2.  验证每个 ID 在 `evidence.json` 中存在（如果任何 ID 缺失，则视为严重失败 → 该假设被拒绝，因为可能存在捏造）。
3.  验证每条 `[VERIFIED]` 证据都有来自 2 个以上来源的确认。
4.  检查逻辑一致性：证据所描绘的时间线是否支持该假设？
5.  检查替代解释：同样的证据模式是否可能源于良性原因？
**输出**：
- `VALIDATED`（已验证）：所有证据均已引用、核实，逻辑一致，无其他合理解释。
- `INCONCLUSIVE`（无定论）：证据支持假设，但存在其他解释或证据不足。
- `REJECTED`（已驳回）：缺少证据 ID，未经验证的证据被当作事实引用，检测到逻辑不一致。

被驳回的假设会反馈到阶段 4 进行优化（最多迭代 3 次）。

---

<a id="phase-6-final-report-generation"></a>
## 阶段 6：生成最终报告

使用 [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) 中的模板填充 `investigation-report.md`。

**必填章节**：
- 执行摘要：一段话的结论（已攻陷 / 干净 / 无定论），并附置信度
- 时间线：按时间顺序重建所有重要事件，并引用证据
- 已验证的假设：每个假设的状态及支持证据 ID
- 证据登记表：所有 `EV-XXXX` 条目的表格，包含来源、类型和验证状态
- IOC 列表：所有提取并富集的入侵指标
- 监管链：证据的收集方式、来源及时间戳
- 建议：若检测到入侵，立即采取的缓解措施；监控建议
**报告规则**：
- 每条事实陈述必须至少包含一个 `[EV-XXXX]` 引用
- 执行摘要必须说明置信度（高 / 中 / 低）
- 所有机密/凭据必须涂抹为 `[REDACTED]`

---

<a id="phase-7-completion"></a>
## 阶段 7：完成

1. 运行最终证据计数：`python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list`
2. 存档完整的调查目录。
3. 如果确认遭到入侵：
   - 列出即时缓解措施（轮换凭据、锁定依赖哈希、通知受影响用户）
   - 确定受影响的版本/包
   - 注明披露义务（如果是公开包：与包注册表协调）
4. 向用户展示最终的 `investigation-report.md`。

---

<a id="ethical-use-guidelines"></a>
## 道德使用指南

此技能设计用于**防御性安全调查**——保护开源软件免受供应链攻击。不得用于：

- **骚扰或跟踪**贡献者或维护者
- **人肉搜索**——将 GitHub 活动与真实身份关联以用于恶意目的
- **商业情报**——未经授权调查专有或内部仓库
- **虚假指控**——未经验证证据而发布调查结果（参见反幻觉护栏）
调查应遵循**最小入侵**原则：仅收集验证或推翻假设所必需的证据。发布结果时，请遵循负责任的披露实践，并在公开披露前与受影响的维护者协调。

如果调查发现确实存在入侵，请遵循协调漏洞披露流程：
1. 首先私下通知仓库维护者
2. 给予合理的修复时间（通常为 90 天）
3. 如果已发布的包受到影响，请与包注册表（npm、PyPI 等）协调
4. 在适当时提交 CVE

---

<a id="api-rate-limiting"></a>
## API 速率限制

GitHub REST API 会强制执行速率限制，如果不加以管理，可能会中断大型调查。

**已认证请求**：5,000/小时（需要 `GITHUB_TOKEN` 环境变量或 `gh` CLI 认证）
**未认证请求**：60/小时（无法用于调查）

**最佳实践**：
- 始终进行认证：`export GITHUB_TOKEN=ghp_...` 或使用 `gh` CLI（自动认证）
- 使用条件请求（`If-None-Match` / `If-Modified-Since` 标头）以避免对未更改数据消耗配额
- 对于分页端点，按顺序获取所有页面——不要对同一端点进行并行请求
- 检查 `X-RateLimit-Remaining` 标头；如果低于 100，则暂停直到 `X-RateLimit-Reset` 时间戳
- BigQuery 有自己的配额（免费层 10 TiB/天）——始终先进行试运行
- Wayback Machine CDX API：没有正式速率限制，但请保持礼貌（最大 1-2 请求/秒）
如果在调查过程中遇到速率限制，请将部分结果记录到证据存储中，并在报告中注明该限制。

---

<a id="reference-materials"></a>
## 参考资料

- [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md) — BigQuery 查询、CDX API、12 种事件类型
- [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md) — IOC 分类、证据来源类型、观察类型
- [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md) — 恢复已删除的提交、PR、议题
- [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md) — 针对每种攻击类型的预构建假设模板
- [evidence-store.py](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/scripts/evidence-store.py) — 用于管理证据 JSON 存储的命令行工具
- [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) — 结构化报告模板
