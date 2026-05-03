---
title: "研究论文写作 — 为 NeurIPS/ICML/ICLR 撰写机器学习论文：从设计到投稿"
sidebar_label: "研究论文写作"
description: "为 NeurIPS/ICML/ICLR 撰写机器学习论文：从设计到投稿"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 研究论文写作 {#research-paper-writing}

为 NeurIPS/ICML/ICLR 撰写机器学习论文：从设计到投稿。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/research-paper-writing` |
| 版本 | `1.1.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `semanticscholar`, `arxiv`, `habanero`, `requests`, `scipy`, `numpy`, `matplotlib`, `SciencePlots` |
| 平台 | linux, macos |
| 标签 | `研究`, `论文写作`, `实验`, `机器学习`, `人工智能`, `NeurIPS`, `ICML`, `ICLR`, `ACL`, `AAAI`, `COLM`, `LaTeX`, `引用`, `统计分析` |
| 相关技能 | [`arxiv`](/user-guide/skills/bundled/research/research-arxiv), `ml-paper-writing`, [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`plan`](/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 研究论文写作流程 {#research-paper-writing-pipeline}

端到端流程，用于生成面向 **NeurIPS、ICML、ICLR、ACL、AAAI 和 COLM** 的可投稿机器学习/人工智能研究论文。该技能涵盖完整的研究生命周期：实验设计、执行、监控、分析、论文写作、审阅、修改和投稿。
这**不是一条线性流水线**——而是一个迭代循环。结果会触发新的实验，评审会触发新的分析。Agent 必须处理这些反馈回路。

<!-- ascii-guard-ignore -->
<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────────┐
│                    研究论文流水线                            │
│                                                             │
│  阶段 0: 项目设置 ──► 阶段 1: 文献综述                      │
│       │                          │                          │
│       ▼                          ▼                          │
│  阶段 2: 实验设计        阶段 5: 论文草稿 ◄──┐              │
│       │                    撰写              │              │
│       │                          │           │              │
│       ▼                          ▼           │              │
│  阶段 3: 执行与          阶段 6: 自我评审     │              │
│       监控                    与修订 ────────┘              │
│       │                          │                          │
│       ▼                          ▼                          │
│  阶段 4: 分析 ─────► 阶段 7: 提交                          │
│       (反馈至阶段 2 或 5)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->
<!-- ascii-guard-ignore-end -->

---

## 何时使用此技能 {#when-to-use-this-skill}

在以下场景使用此技能：
- **从现有代码库或想法开始撰写一篇新的研究论文**
- **设计并运行实验**以支持论文中的主张
- **撰写或修改**研究论文的任何章节
- **准备向特定会议或研讨会提交论文**
- **回应评审意见**，补充额外实验或进行修订
- **在不同会议格式之间转换论文**
- **撰写非实证论文**——理论、综述、基准或立场论文（参见[实证 ML 之外的论文类型](#paper-types-beyond-empirical-ml)）
- **为 NLP、HCI 或对齐研究设计人工评估**
- **准备录用后的交付物**——海报、演讲、代码发布
## 核心理念 {#core-philosophy}

1. **主动出击。** 交付完整的草稿，而不是问题。科学家们都很忙——给出他们可以回应的具体内容，然后迭代。
2. **绝不捏造引用。** AI 生成的引用错误率约 40%。始终通过编程方式获取。将无法验证的引用标记为 `[CITATION NEEDED]`。
3. **论文是一个故事，而不是实验的集合。** 每篇论文都需要用一句话陈述一个清晰的贡献。如果做不到，说明论文还没准备好。
4. **实验服务于主张。** 每个实验必须明确说明它支持哪个主张。永远不要运行与论文叙事无关的实验。
5. **尽早提交，频繁提交。** 每完成一批实验、每更新一次论文草稿——都要用描述性的提交信息提交。Git 日志就是实验历史。

### 主动性与协作 {#proactivity-and-collaboration}

**默认：主动出击。先起草，带着草稿提问。**

| 信心等级 | 行动 |
|---------|------|
| **高**（仓库清晰，贡献明确） | 撰写完整草稿，交付，根据反馈迭代 |
| **中**（存在一些模糊之处） | 撰写带有标记不确定性的草稿，继续推进 |
| **低**（主要未知项） | 通过 `clarify` 提出 1-2 个针对性问题，然后起草 |

| 章节 | 自主起草？ | 在草稿中标记 |
|------|-----------|-------------|
| 摘要 | 是 | "将贡献表述为 X —— 如有需要请调整" |
| 引言 | 是 | "强调了问题 Y —— 如果错了请纠正" |
| 方法 | 是 | "包含了细节 A、B、C —— 请补充遗漏部分" |
| 实验 | 是 | "突出了结果 1、2、3 —— 如有需要请重新排序" |
| 相关工作 | 是 | "引用了论文 X、Y、Z —— 请补充我遗漏的" |
**仅当以下情况时输入此块**：目标会议不明确、存在多个矛盾的框架、结果似乎不完整、明确要求先进行审查。

---

## 阶段 0：项目设置 {#phase-0-project-setup}

**目标**：建立工作区，理解现有工作，明确贡献点。

### 步骤 0.1：探索仓库 {#step-0-1-explore-the-repository}

```bash
# 了解项目结构
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

查找：
- `README.md` — 项目概览和声明
- `results/`、`outputs/`、`experiments/` — 现有发现
- `configs/` — 实验设置
- `.bib` 文件 — 现有引用
- 草稿文档或笔记

### 步骤 0.2：组织工作区 {#step-0-2-organize-the-workspace}

建立一致的工作区结构：

```
workspace/
  paper/               # LaTeX 源码、图表、编译后的 PDF
  experiments/         # 实验运行脚本
  code/                # 核心方法实现
  results/             # 原始实验结果（自动生成）
  tasks/               # 任务/基准定义
  human_eval/          # 人工评估材料（如果需要）
```

### 步骤 0.3：设置版本控制 {#step-0-3-set-up-version-control}

```bash
git init  # 如果尚未初始化
git remote add origin <repo-url>
git checkout -b paper-draft  # 或 main
```

**Git 纪律**：每完成一批实验，都要用描述性信息提交。例如：
```
Add Monte Carlo constrained results (5 runs, Sonnet 4.6, policy memo task)
Add Haiku baseline comparison: autoreason vs refinement baselines at cheap model tier
```
### 步骤 0.4：明确贡献点 {#step-0-4-identify-the-contribution}

在动笔之前，先理清：
- **是什么**：这篇论文贡献了什么核心内容？
- **为什么**：有哪些证据支撑它？
- **所以呢**：读者为什么要在意？

> 向科学家提议：“根据我的理解，主要贡献是：[一句话]。关键结果显示 [Y]。这是您想要的表述框架吗？”

### 步骤 0.5：创建待办清单 {#step-0-5-create-a-todo-list}

使用 `todo` 工具创建结构化的项目计划：

```
研究论文待办清单：
- [ ] 定义一句话贡献
- [ ] 文献综述（相关工作 + 基线方法）
- [ ] 设计核心实验
- [ ] 运行实验
- [ ] 分析结果
- [ ] 撰写初稿
- [ ] 自我审查（模拟审稿人）
- [ ] 根据审查意见修改
- [ ] 投稿准备
```

在整个项目过程中持续更新此清单。它作为跨会话的持久状态。

### 步骤 0.6：估算计算预算 {#step-0-6-estimate-compute-budget}

在运行实验之前，估算总成本和时间：

```
计算预算检查清单：
- [ ] API 成本：（模型每 token 价格）×（每次运行预估 token 数）×（运行次数）
- [ ] GPU 时长：（每个实验耗时）×（实验数量）×（随机种子数）
- [ ] 人工评估成本：（标注人员数）×（小时数）×（时薪）
- [ ] 总预算上限和应急储备（为重新运行增加 30-50%）
```

在实验运行过程中跟踪实际花费：
```python
# 简单的成本跟踪器模式
import json, os
from datetime import datetime

COST_LOG = "results/cost_log.jsonl"

def log_cost(experiment: str, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "experiment": experiment,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }
    with open(COST_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```
**当预算紧张时**：在全面展开实验之前，先运行试点实验（1-2个随机种子，部分任务）。使用较便宜的模型调试流水线，然后在最终运行时切换到目标模型。

### 步骤 0.7：多作者协作 {#step-0-7-multi-author-coordination}

大多数论文有3-10位作者。尽早建立工作流程：

| 工作流程 | 工具 | 使用场景 |
|----------|------|----------|
| **Overleaf** | 基于浏览器 | 多位作者同时编辑，无Git经验 |
| **Git + LaTeX** | 使用 `git` 并配合 `.gitignore` 忽略辅助文件 | 技术团队，需要基于分支的审阅 |
| **Overleaf + Git 同步** | Overleaf 高级版 | 两者兼得——实时协作与版本历史 |

**章节所有权**：将每个章节分配给一位主要作者。其他人可以评论但不直接编辑。防止合并冲突和风格不一致。

```
作者协作检查清单：
- [ ] 确定章节所有权（谁写什么）
- [ ] 设置共享工作空间（Overleaf 或 Git 仓库）
- [ ] 在任何人开始写作之前，约定符号规范
- [ ] 安排内部审阅轮次（不要等到最后）
- [ ] 指定一人负责最终格式整理
- [ ] 在创建图表之前，约定图表风格（颜色、字体、大小）
```

**尽早约定的 LaTeX 规范**：
- `\method{}` 宏用于统一的方法命名
- 引用风格：`\citet{}` 与 `\citep{}` 的用法
- 数学符号：向量用小写粗体，矩阵用大写粗体等
- 英式英语 vs 美式英语拼写

---

## 第一阶段：文献综述 {#phase-1-literature-review}
**目标**：查找相关工作，确定基线方法，收集引用。

### 步骤 1.1：确定种子论文 {#step-1-1-identify-seed-papers}

从代码库中已引用的论文开始：

```bash
# 通过终端：
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

### 步骤 1.2：搜索相关工作 {#step-1-2-search-for-related-work}

**加载 `arxiv` 技能**以进行结构化论文发现：`skill_view("arxiv")`。它提供 arXiv REST API 搜索、Semantic Scholar 引用图谱、作者简介以及 BibTeX 生成。

使用 `web_search` 进行广泛发现，使用 `web_extract` 获取特定论文：

```
# 通过 web_search：
web_search("[主要技术] + [应用领域] site:arxiv.org")
web_search("[基线方法] 比较 ICML NeurIPS 2024")

# 通过 web_extract（针对特定论文）：
web_extract("https://arxiv.org/abs/2303.17651")
```

其他可尝试的搜索查询：

```
搜索查询：
- "[主要技术] + [应用领域]"
- "[基线方法] 比较"
- "[问题名称] 最新进展"
- 现有引用中的作者姓名
```

**推荐**：安装 **Exa MCP** 以进行实时学术搜索：
```bash
claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"
```

### 步骤 1.2b：深化搜索（先广度，后深度） {#step-1-2b-deepen-the-search-breadth-first-then-depth}

一次扁平搜索（一轮查询）通常会遗漏重要的相关工作。采用受深度研究流程启发的迭代式**先广度后深度**模式：

```
迭代式文献搜索：

第 1 轮（广度）：4-6 个并行查询，覆盖不同角度
  - "[方法] + [领域]"
  - "[问题名称] 最新进展 2024 2025"
  - "[基线方法] 比较"
  - "[替代方法] vs [你的方法]"
  → 收集论文，提取关键概念和术语

第 2 轮（深度）：根据第 1 轮的学习生成后续查询
  - 第 1 轮论文中发现的新术语
  - 第 1 轮最相关结果引用的论文
  - 需要调查的矛盾发现
  → 收集论文，识别剩余空白

第 3 轮（针对性）：填补特定空白
  - 第 1-2 轮中识别出的缺失基线
  - 同期工作（最近 6 个月，同一问题）
  - 关键负面结果或失败方法
  → 当新查询返回的论文大部分已见过时停止
```
**何时停止**：如果某一轮返回的论文中已有超过80%在你的收藏中，则搜索已饱和。通常2-3轮即可。对于综述论文，预计需要4-5轮。

**针对基于Agent的工作流**：通过 `delegate_task` 并行委派每一轮的查询。收集结果，去重，然后根据综合学习成果生成下一轮的查询。

### 步骤 1.3：验证每条引用 {#step-1-3-verify-every-citation}

**绝不要凭记忆生成 BibTeX。始终通过编程方式获取。**

对于每条引用，遵循强制性的5步流程：

```
引用验证（每条引用必须执行）：
1. 搜索 → 使用特定关键词查询 Semantic Scholar 或 Exa MCP
2. 验证 → 确认论文存在于2个以上来源（Semantic Scholar + arXiv/CrossRef）
3. 获取 → 通过 DOI 内容协商获取 BibTeX（编程方式，而非凭记忆）
4. 确认 → 验证你引用的主张确实出现在论文中
5. 添加 → 将验证后的 BibTeX 添加到参考文献列表
如果任何步骤失败 → 标记为 [CITATION NEEDED]，通知科学家
```

```python
# 通过 DOI 获取 BibTeX
import requests

def doi_to_bibtex(doi: str) -> str:
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text
```

如果你无法验证某条引用：

```latex
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: 验证此引用是否存在
```

**始终告知科学家**：“我已将 [X] 条引用标记为占位符，需要验证。”
参见 [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md) 获取完整的 API 文档和 `CitationManager` 类。

### 步骤 1.4：组织相关工作 {#step-1-4-organize-related-work}

按方法论对论文进行分组，而不是逐篇罗列：

**好的做法**：“一条工作线使用 X 的假设 [参考文献]，而我们使用 Y 的假设，因为……”
**不好的做法**：“Smith 等人提出了 X。Jones 等人提出了 Y。我们结合了二者。”

---

## 阶段 2：实验设计 {#phase-2-experiment-design}

**目标**：设计直接支撑论文主张的实验。每个实验必须回答一个具体问题。

### 步骤 2.1：将主张映射到实验 {#step-2-1-map-claims-to-experiments}

创建明确的映射表：

| 主张 | 实验 | 预期证据 |
|-------|-----------|-------------------|
| “我们的方法优于基线” | 主要对比（表 1） | 胜率、统计显著性 |
| “对于较弱模型，效果更明显” | 模型规模研究 | 单调提升曲线 |
| “收敛需要范围约束” | 有约束 vs 无约束 | 收敛速度对比 |

**规则**：如果某个实验没有对应任何主张，就不要运行它。

### 步骤 2.2：设计基线 {#step-2-2-design-baselines}

强大的基线是区分被接收论文和被拒论文的关键。审稿人会问：“他们和 X 对比了吗？”

标准基线类别：
- **朴素基线**：最简单的方法
- **强基线**：已知的最佳现有方法
- **消融基线**：你的方法去掉一个组件
- **计算量匹配基线**：相同的计算预算，不同的分配方式
### 步骤 2.3：定义评估协议 {#step-2-3-define-evaluation-protocol}

在运行任何实验之前，请明确以下内容：
- **指标**：你测量的内容，以及方向符号（越高越好/越低越好）
- **聚合方式**：如何将多次运行/任务的结果合并
- **统计检验**：使用哪些检验来确立显著性
- **样本量**：运行次数/问题数/任务数

### 步骤 2.4：编写实验脚本 {#step-2-4-write-experiment-scripts}

参考以下成功研究流程中的模式：

**增量保存** — 每一步都保存结果，以便崩溃后恢复：
```python
# 每个问题/任务后保存
result_path = f"results/{task}/{strategy}/result.json"
if os.path.exists(result_path):
    continue  # 跳过已完成的工作
# ... 运行实验 ...
with open(result_path, 'w') as f:
    json.dump(result, f, indent=2)
```

**产物保留** — 保存所有中间输出：
```
results/<实验名称>/
  <任务>/
    <策略>/
      final_output.md          # 最终结果
      history.json             # 完整轨迹
      pass_01/                 # 每次迭代的产物
        version_a.md
        version_b.md
        critic.md
```

**关注点分离** — 将生成、评估和可视化分开：
```
run_experiment.py              # 核心实验运行器
run_baselines.py               # 基线对比
run_comparison_judge.py        # 盲评
analyze_results.py             # 统计分析
make_charts.py                 # 可视化
```

完整的设计模式、定时监控和错误恢复，请参见 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md)。
### 步骤 2.5：设计人工评估（如适用） {#step-2-5-design-human-evaluation-if-applicable}

许多 NLP、HCI 和对齐论文需要人工评估作为主要或补充证据。请在运行自动化实验之前设计好这一环节——人工评估通常需要更长的准备时间（机构审查委员会批准、标注员招募）。

**何时需要人工评估：**
- 自动化指标无法捕捉你关心的方面（流畅度、有用性、安全性）
- 你的贡献涉及面向人的品质（可读性、偏好、信任）
- NLP 会议（ACL、EMNLP）的审稿人期望生成任务有人工评估

**关键设计决策：**

| 决策 | 选项 | 指导建议 |
|----------|---------|----------|
| **标注员类型** | 专家、众包工人、最终用户 | 与你的主张要求相匹配 |
| **评分尺度** | 李克特量表（1-5）、两两比较、排序 | 对于大语言模型输出，两两比较比李克特量表更可靠 |
| **样本量** | 每位标注员及总项目数 | 功效分析或至少 100 个项目，3 名以上标注员 |
| **一致性指标** | Cohen's kappa、Krippendorff's alpha、ICC | 标注员超过 2 人时使用 Krippendorff's alpha；同时报告原始一致性 |
| **平台** | Prolific、MTurk、内部团队 | Prolific 保证质量；MTurk 适合大规模；内部团队适合领域专业知识 |

**标注指南检查清单：**
```
- [ ] 清晰的任务描述并附有示例（好的和坏的）
- [ ] 模糊案例的决策标准
- [ ] 每个类别至少 2 个已完成的示例
- [ ] 注意力检查/黄金标准项目（占总量的 10-15%）
- [ ] 资格任务或筛选轮次
- [ ] 每个项目的预估时间和公平报酬（>= 当地最低工资）
- [ ] 如果机构要求，进行机构审查委员会/伦理审查
```
**报告要求**（审稿人会检查以下所有项）：
- 标注者人数及其资质
- 标注者间一致性（需注明具体指标和数值）
- 报酬详情（金额、预估时薪）
- 标注界面描述或截图（附录）
- 总标注时长

完整指南（含人工评估数据的统计检验、众包质量控制模式及IRB指导）请参见 [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)。

---

## 阶段 3：实验执行与监控 {#phase-3-experiment-execution-monitoring}

**目标**：可靠地运行实验，监控进度，从失败中恢复。

### 步骤 3.1：启动实验 {#step-3-1-launch-experiments}

对于长时间运行的实验，使用 `nohup`：

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!  # 记录进程ID
```

**并行执行**：可同时运行相互独立的实验，但需注意 API 速率限制。在同一 API 上同时运行 4 个以上实验会拖慢每个实验的速度。

### 步骤 3.2：设置监控（Cron 模式） {#step-3-2-set-up-monitoring-cron-pattern}

对于长时间运行的实验，设置定期状态检查。Cron 提示应遵循以下模板：

```
监控提示模板：
1. 检查进程是否仍在运行：ps aux | grep <模式>
2. 读取日志最后 30 行：tail -30 <日志文件>
3. 检查是否已有完成的结果：ls <结果目录>
4. 如果存在结果，读取并报告：cat <结果文件>
5. 如果全部完成，提交：git add -A && git commit -m "<描述性消息>" && git push
6. 以结构化格式报告（表格形式呈现关键指标）
7. 回答本次实验的关键分析问题
```
**静默模式**：如果自上次检查以来没有任何变化，请回复 `[SILENT]` 以抑制对用户的通知。仅在出现新消息时进行报告。

### 步骤 3.3：处理失败 {#step-3-3-handle-failures}

常见的失败模式及恢复方法：

| 失败类型 | 检测方式 | 恢复方法 |
|---------|----------|-----------|
| API 速率限制 / 额度耗尽 | 日志中出现 402/429 错误 | 等待，然后重新运行（脚本会跳过已完成的工作） |
| 进程崩溃 | PID 消失，结果不完整 | 从上一个检查点重新运行 |
| 难题超时 | 进程卡住，日志无进展 | 终止并跳过，在结果中注明 |
| 错误的模型 ID | 引用模型名称时出错 | 修正 ID 并重新运行 |

**关键**：脚本应始终检查现有结果并跳过已完成的工作。这使得重新运行既安全又高效。

### 步骤 3.4：提交完成的结果 {#step-3-4-commit-completed-results}

每批实验完成后：

```bash
git add -A
git commit -m "添加 <实验名称>：<一行关键发现>"
git push
```

### 步骤 3.5：维护实验日志 {#step-3-5-maintain-an-experiment-journal}

Git 提交记录了发生了什么，但并未记录**探索树**——即根据所学内容决定下一步尝试什么的决策过程。维护一个结构化的实验日志来捕获这个树：

```json
// experiment_journal.jsonl — 每次实验尝试追加一条记录
{
  "id": "exp_003",
  "parent": "exp_001",
  "timestamp": "2025-05-10T14:30:00Z",
  "hypothesis": "添加作用域约束将修复 exp_001 中的收敛失败问题",
  "plan": "使用 max_tokens=2000 和固定结构模板重新运行 autoreason",
  "config": {"model": "haiku", "strategy": "autoreason", "max_tokens": 2000},
  "status": "completed",
  "result_path": "results/exp_003/",
  "key_metrics": {"win_rate": 0.85, "convergence_rounds": 3},
  "analysis": "作用域约束修复了收敛问题。胜率从 0.42 跃升至 0.85。",
  "next_steps": ["在 Sonnet 上尝试相同约束", "测试不使用结构模板"],
  "figures": ["figures/exp003_convergence.pdf"]
}
```
**为什么用日志（journal），而不是只用 git？** Git 跟踪文件变更。日志跟踪的是推理过程：为什么尝试 X，学到了什么，这对下一步实验意味着什么。写论文时，这个树状结构对“方法”部分（“我们观察到 X，这促使我们尝试 Y”）和诚实的失败报告来说非常宝贵。

**选择最佳路径**：当日志显示一个分支树（exp_001 → exp_002a, exp_002b, exp_003）时，找出最能支撑论文主张的路径。将死胡同分支记录在附录中，作为消融实验或负面结果。

**每个实验的快照代码**：每次运行后复制实验脚本：
```bash
cp experiment.py results/exp_003/experiment_snapshot.py
```
这样即使后续代码发生更改，也能精确复现。

---

## 阶段 4：结果分析 {#phase-4-result-analysis}

**目标**：提取发现，计算统计量，识别故事主线。

### 步骤 4.1：汇总结果 {#step-4-1-aggregate-results}

编写分析脚本，完成以下任务：
1. 加载一个批次中的所有结果文件
2. 计算每个任务和聚合指标
3. 生成汇总表格

```python
# 标准分析模式
import json, os
from pathlib import Path

results = {}
for result_file in Path("results/").rglob("result.json"):
    data = json.loads(result_file.read_text())
    strategy = result_file.parent.name
    task = result_file.parent.parent.name
    results.setdefault(strategy, {})[task] = data

# 计算聚合指标
for strategy, tasks in results.items():
    scores = [t["score"] for t in tasks.values()]
    print(f"{strategy}: mean={np.mean(scores):.1f}, std={np.std(scores):.1f}")
```
### 步骤 4.2：统计显著性 {#step-4-2-statistical-significance}

始终计算：
- **误差线**：标准差或标准误，需指明具体使用哪一种
- **置信区间**：关键结果给出 95% 置信区间
- **成对检验**：使用 McNemar 检验比较两种方法
- **效应量**：使用 Cohen's d 或 h 衡量实际显著性

McNemar 检验、自助法置信区间和 Cohen's h 的完整实现，请参见 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md)。

### 步骤 4.3：确定故事主线 {#step-4-3-identify-the-story}

分析之后，明确回答以下问题：
1. **主要发现是什么？** 用一句话概括。
2. **什么让你感到意外？** 出乎意料的结果往往能成就最好的论文。
3. **哪些实验失败了？** 失败的实验往往信息量最大。如实报告失败反而能增强论文的可信度。
4. **还需要哪些后续实验？** 结果通常会引出新的问题。

#### 处理负面或无效结果 {#handling-negative-or-null-results}

当你的假设错误或结果不明确时，你有三种选择：

| 情况 | 应对策略 | 适合的会议/期刊 |
|-----------|--------|-----------|
| 假设错误，但**原因**有信息量 | 围绕原因分析来组织论文 | NeurIPS、ICML（如果分析足够严谨） |
| 方法未超越基线，但**揭示了新东西** | 将贡献重新定义为理解/分析 | ICLR（重视理解类工作）、workshop 论文 |
| 针对流行观点得到干净的负面结果 | 写出来——领域需要知道 | NeurIPS Datasets & Benchmarks、TMLR、workshops |
| 结果不明确，没有清晰的故事 | 转向——换不同的实验或重新组织 | 不要硬凑一篇不存在的论文 |
**如何撰写负面结果论文：**
- 以社区普遍认知为引，说明为何检验该认知至关重要
- 描述严谨的方法论（必须无懈可击——审稿人会更加严格地审查）
- 用统计证据清晰呈现零结果
- 分析预期结果**为何**未能出现
- 讨论对该领域的影响

**明确欢迎负面结果的会议/期刊**：NeurIPS（数据集与基准测试轨道）、TMLR、ML可复现性挑战赛、各大会议的工作坊。部分工作坊专门征集负面结果。

### 步骤 4.4：创建图表与表格 {#step-4-4-create-figures-and-tables}

**图表**：
- 所有绘图使用矢量图形（PDF）：`plt.savefig('fig.pdf')`
- 色盲友好调色板（Okabe-Ito 或 Paul Tol）
- 自包含图注——读者无需阅读正文即可理解
- 图中不包含标题——图注承担此功能

**表格**：
- 使用 `booktabs` LaTeX 宏包
- 每个指标的最佳值加粗
- 包含方向符号（越高越好/越低越好）
- 统一小数精度

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

### 步骤 4.5：决定：继续实验还是开始写作？ {#step-4-5-decide-more-experiments-or-write}

| 情况 | 行动 |
|-----------|--------|
| 核心主张得到支持，结果显著 | 进入阶段 5（写作） |
| 结果不明确，需要更多数据 | 返回阶段 2（设计） |
| 意外发现提示新方向 | 返回阶段 2（设计） |
| 缺少审稿人会要求的消融实验 | 先运行该实验，再进入阶段 5 |
| 所有实验已完成但部分失败 | 记录失败，进入阶段 5 |
### 步骤 4.6：撰写实验日志（连接实验与论文的桥梁） {#step-4-6-write-the-experiment-log-bridge-to-writeup}

在开始撰写论文之前，创建一个结构化的实验日志，将实验结果与文字叙述连接起来。这是连接实验与论文之间最重要的纽带——没有它，写作 Agent 就必须从原始结果文件中重新推导出整个故事。

**创建 `experiment_log.md`**，结构如下：

```markdown
# 实验日志

## 贡献（一句话概括）
[论文的核心主张]

## 已完成的实验

### 实验 1：[名称]
- **验证的论点**：[该实验支持论文中的哪个论点]
- **实验设置**：[模型、数据集、配置、运行次数]
- **关键结果**：[一句话概括，包含具体数字]
- **结果文件**：results/exp1/final_info.json
- **生成的图表**：figures/exp1_comparison.pdf
- **意外发现**：[任何出乎意料的结果]

### 实验 2：[名称]
...

## 图表
| 文件名 | 描述 | 所属章节 |
|----------|-------------|---------------------------|
| figures/main_comparison.pdf | 在基准测试 X 上比较所有方法的柱状图 | 结果，图 2 |
| figures/ablation.pdf | 移除组件 A、B、C 的消融实验 | 结果，图 3 |
...

## 失败的实验（如实记录）
- [尝试了什么，失败的原因，以及它告诉了我们什么]

## 待解决的问题
- [实验结果提出的、论文需要解答的任何问题]
```

**为什么这很重要**：在起草论文时，Agent（或一个委派的子 Agent）可以加载 `experiment_log.md` 以及 LaTeX 模板，并基于实际结果生成初稿。如果没有这个桥梁，写作 Agent 就必须解析原始的 JSON/CSV 文件并推断故事脉络——这通常是导致数字被幻觉或误报的常见原因。
**Git discipline**: 将这份日志与它所描述的结果一起提交。

---

## 迭代优化：策略选择 {#iterative-refinement-strategy-selection}

此流程中的任何输出——论文草稿、实验脚本、分析——都可以进行迭代优化。自推理研究为每种优化策略何时有效、何时失效提供了经验证据。请使用本节来选择合适的方法。

### 快速决策表 {#quick-decision-table}

| 你的情况 | 策略 | 原因 |
|---------------|----------|-----|
| 中端模型 + 约束性任务 | **自推理** | 最佳适用点。生成与评估之间的差距最大。基线方法会主动破坏弱模型的输出。 |
| 中端模型 + 开放性任务 | **自推理**（添加范围约束） | 添加固定事实、结构或可交付成果来限定改进空间。 |
| 前沿模型 + 约束性任务 | **自推理** | 即使在前沿模型上，也能在 2/3 的约束性任务中胜出。 |
| 前沿模型 + 无约束任务 | **批评与修订** 或 **单次生成** | 自推理排名最后。模型自身评估能力足够好。 |
| 具体技术任务（系统设计） | **批评与修订** | 直接的“发现-修复”循环更高效。 |
| 模板填充任务（一种正确结构） | **单次生成** 或 **保守策略** | 决策空间极小。迭代不会增加价值。 |
| 带测试用例的代码 | **自推理（代码变体）** | 在修复前对*失败原因*进行结构化分析。恢复率 62% 对比 43%。 |
| 非常弱的模型（Llama 8B 级别） | **单次生成** | 模型太弱，无法生成多样化的候选方案。应投资于生成质量。 |
### 生成-评估差距 {#the-generation-evaluation-gap}

**核心洞察**：Autoreason 的价值取决于模型的生成能力与自我评估能力之间的差距。

<!-- ascii-guard-ignore -->
```
模型层级           │ 生成能力 │ 自我评估 │ 差距    │ Autoreason 价值
──────────────────┼──────────┼─────────┼────────┼─────────────────
弱（Llama 8B）     │ 差       │ 差      │ 小      │ 无 — 无法生成多样化的候选
中（Haiku 3.5）    │ 尚可     │ 差      │ 大      │ 最大 — 42/42 完美 Borda
中（Gemini Flash） │ 尚可     │ 中等    │ 较大    │ 高 — 赢得 2/3
强（Sonnet 4）     │ 好       │ 尚可    │ 中等    │ 中等 — 赢得 3/5
前沿（S4.6）       │ 优秀     │ 好      │ 小      │ 仅在约束条件下有效
```
<!-- ascii-guard-ignore-end -->

这种差距是结构性的，而非暂时的。随着成本下降，今天的前沿模型会成为明天的中端模型。最佳点会移动，但永远不会消失。

### Autoreason 循环（总结） {#autoreason-loop-summary}

每一轮由全新、独立的 Agent 生成三个候选：

1. **批评者** → 找出当前方案 A 中的问题（不提供修复）
2. **作者 B** → 基于批评意见修改 A
3. **合成者** → 合并 A 和 B（随机化标签）
4. **评审团** → 3 个盲审 CoT 评审员通过 Borda 计数对 A、B、AB 进行排名
5. **收敛** → A 连续获胜 k=2 轮 → 结束

**关键参数：**
- k=2 收敛（k=1 过早，k=3 成本过高且无质量提升）
- 始终使用 CoT 评审员（收敛速度提升 3 倍）
- 作者温度 0.8，评审员温度 0.3
- 保守平局决胜：当前方案获胜
- 每个角色都是全新 Agent，无共享上下文
### 应用于论文草稿 {#applying-to-paper-drafts}

在通过自动推理（autoreason）对论文本身进行精炼时：
- **向评审者提供真实数据**：实际的实验数据、结果 JSON、统计输出。没有这些，模型会幻觉出虚假的消融实验和伪造的置信区间。
- **至少使用 3 个有效评审者**：一个损坏的评审解析器不会增加噪声——它会完全阻止达成均衡。
- **限定修订范围**：“解决这些具体弱点”，而不是“改进论文”。

### 失败模式 {#failure-modes}

| 失败类型 | 检测方法 | 修复方式 |
|---------|-----------|---------|
| 无法收敛（A 从未获胜） | 在 20+ 轮中 A 获胜 &lt;15% | 为任务添加范围约束 |
| 综合漂移 | 字数无限制增长 | 约束结构和交付物 |
| 退化至低于单次生成 | 基线得分高于迭代输出 | 切换为单次生成；模型可能太弱 |
| 过拟合（代码） | 公开测试通过率高，私有测试通过率低 | 使用结构化分析，而不仅仅是测试反馈 |
| 评审者损坏 | 解析失败导致评审小组少于 3 人 | 在继续之前修复解析器 |

完整提示词、Borda 评分细节、模型选择指南、范围约束设计模式以及计算预算参考，请参见 [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md)。

---

## 阶段 5：论文撰写 {#phase-5-paper-drafting}

**目标**：撰写一篇完整的、可发表的论文。

### 大型项目的上下文管理 {#context-management-for-large-projects}
一个包含 50 多个实验文件、多个结果目录和大量文献笔记的论文项目，很容易超出 Agent 的上下文窗口。请主动管理：

**每个起草任务应加载到上下文中的内容：**

| 起草任务 | 加载到上下文 | 不要加载 |
|---------------|------------------|-------------|
| 撰写引言 | `experiment_log.md`、贡献声明、5-10 篇最相关的论文摘要 | 原始结果 JSON、完整的实验脚本、所有文献笔记 |
| 撰写方法 | 实验配置、伪代码、架构描述 | 原始日志、其他实验的结果 |
| 撰写结果 | `experiment_log.md`、结果汇总表、图表列表 | 完整的分析脚本、中间数据 |
| 撰写相关工作 | 整理好的引用笔记（步骤 1.4 的输出）、.bib 文件 | 实验文件、原始 PDF |
| 修订阶段 | 完整的论文草稿、具体的审稿人意见 | 其他所有内容 |

**原则：**
- **`experiment_log.md` 是主要的上下文桥梁** — 它汇总了写作所需的一切，无需加载原始数据文件（参见步骤 4.6）
- **委托任务时，一次只加载一个章节的上下文**。负责起草方法的子 Agent 不需要文献综述笔记。
- **进行摘要，不要包含原始文件。** 对于 200 行的结果 JSON，加载一个 10 行的汇总表。对于 50 页的相关论文，加载 5 句摘要 + 你关于其相关性的 2 行笔记。
- **对于非常大的项目**：创建一个包含预压缩摘要的 `context/` 目录：
  ```
  context/
    contribution.md          # 1 句话
    experiment_summary.md    # 关键结果表（来自 experiment_log.md）
    literature_map.md        # 整理好的引用笔记
    figure_inventory.md      # 带描述的图表列表
  ```
### 叙事原则 {#the-narrative-principle}

**最关键的一点**：你的论文不是实验的堆砌——它是一个有清晰贡献、有证据支撑的故事。

每一篇成功的机器学习论文都围绕 Neel Nanda 所说的“叙事”展开：一个简短、严谨、基于证据的技术故事，并给出读者关心的结论。

**三大支柱（必须在引言结束时清晰呈现）：**

| 支柱 | 描述 | 检验标准 |
|------|------|----------|
| **是什么** | 1-3 个具体的新颖主张 | 你能用一句话说清楚吗？ |
| **为什么** | 严谨的实证证据 | 实验能否区分你的假设与其他可能性？ |
| **所以呢** | 读者为什么要在意 | 这能否关联到社区公认的问题？ |

**如果你无法用一句话说清自己的贡献，那你还未真正拥有一篇论文。**

### 本指南的参考来源 {#the-sources-behind-this-guidance}

本技能综合了多位在顶级会议大量发表论文的研究者的写作理念。写作理念层最初由 [Orchestra Research](https://github.com/orchestra-research) 以 `ml-paper-writing` 技能的形式整理。

| 来源 | 关键贡献 | 链接 |
|------|----------|------|
| **Neel Nanda**（Google DeepMind） | 叙事原则，是什么/为什么/所以呢框架 | [如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) |
| **Sebastian Farquhar**（DeepMind） | 五句话摘要公式 | [如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| **Gopen & Swan** | 读者期望的七项原则 | [科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| **Zachary Lipton** | 用词选择，消除模糊表述 | [科学写作启发式](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| **Jacob Steinhardt**（加州大学伯克利分校） | 精确性，术语一致性 | [写作技巧](https://bounded-regret.ghost.io/) |
| **Ethan Perez**（Anthropic） | 微观层面的清晰度技巧 | [轻松论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/) |
| **Andrej Karpathy** | 聚焦单一贡献 | 各类讲座 |
**如需深入了解以上任何内容，请参阅：**
- [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) — 包含示例的完整说明
- [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) — 完整参考文献

### 时间分配 {#time-allocation}

在以下各部分上花费**大致相等**的时间：
1. 摘要
2. 引言
3. 图表
4. 其余所有内容的总和

**为什么？** 大多数审稿人在读到你的方法之前就已经形成了判断。读者阅读论文的顺序是：标题 → 摘要 → 引言 → 图表 → 可能才到其余部分。

### 写作流程 {#writing-workflow}

```
论文写作检查清单：
- [ ] 步骤 1：定义一句话贡献
- [ ] 步骤 2：起草图 1（核心思想或最令人信服的结果）
- [ ] 步骤 3：起草摘要（5 句公式）
- [ ] 步骤 4：起草引言（最多 1-1.5 页）
- [ ] 步骤 5：起草方法
- [ ] 步骤 6：起草实验与结果
- [ ] 步骤 7：起草相关工作
- [ ] 步骤 8：起草结论与讨论
- [ ] 步骤 9：起草局限性（所有会议/期刊均要求）
- [ ] 步骤 10：规划附录（证明、额外实验、细节）
- [ ] 步骤 11：完成论文检查清单
- [ ] 步骤 12：最终审阅
```

### 两遍精炼模式 {#two-pass-refinement-pattern}

在使用 AI Agent 起草时，采用**两遍**方法（在 SakanaAI 的 AI-Scientist 流程中已被证明有效）：

**第一遍 — 逐节写作 + 立即精炼：**
对于每个章节，先写出完整草稿，然后在同一上下文中立即进行精炼。这样可以在章节内容还新鲜时，抓住局部问题（清晰度、流畅性、完整性）。
**Pass 2 — 全局精炼（结合全文上下文）：**  
在所有章节草稿完成后，带着对整篇论文的认知重新审视每个章节。这能发现跨章节问题：冗余、术语不一致、叙事流畅性，以及某个章节承诺了但其他章节未兑现的缺口。

```
第二轮精炼提示（按章节）：
"Review the [SECTION] in the context of the complete paper.
- Does it fit with the rest of the paper? Are there redundancies with other sections?
- Is terminology consistent with Introduction and Methods?
- Can anything be cut without weakening the message?
- Does the narrative flow from the previous section and into the next?
Make minimal, targeted edits. Do not rewrite from scratch."
```

### LaTeX 错误检查清单 {#latex-error-checklist}

将以下检查清单附加到每个精炼提示后。这些是 LLM 编写 LaTeX 时最常见的错误：

```
LaTeX 质量检查清单（每次编辑后验证）：
- [ ] 无未闭合的数学符号（$ 符号成对出现）
- [ ] 仅引用存在的图表（\ref 与 \label 匹配）
- [ ] 无捏造的引用（\cite 与 .bib 中的条目匹配）
- [ ] 每个 \begin{env} 都有对应的 \end{env}（尤其是 figure、table、algorithm）
- [ ] 无 HTML 污染（例如 </end{figure}> 而非 \end{figure}）
- [ ] 数学模式外无未转义的下划线（文本中使用 \_）
- [ ] 无重复的 \label 定义
- [ ] 无重复的章节标题
- [ ] 文本中的数字与实际实验结果一致
- [ ] 所有图表都有标题和标签
- [ ] 无导致 overfull hbox 警告的过长行
```
### 步骤 5.0：标题 {#step-5-0-title}

标题是论文中被阅读最多的元素。它决定了是否有人会点击进入摘要。

**好的标题**：
- 陈述贡献或发现："Autoreason: When Iterative LLM Refinement Works and Why It Fails"
- 突出令人惊讶的结果："Scaling Data-Constrained Language Models"（暗示你可以做到）
- 命名方法 + 其作用："DPO: Direct Preference Optimization of Language Models"

**不好的标题**：
- 过于通用："An Approach to Improving Language Model Outputs"
- 过长：超过约 15 个单词的任何标题
- 仅含术语："Asymptotic Convergence of Iterative Stochastic Policy Refinement"（这是给谁看的？）

**规则**：
- 如果有方法名称，请包含在内（便于引用）
- 包含 1-2 个审稿人会搜索的关键词
- 除非两部分都有意义，否则避免使用冒号
- 测试：审稿人仅凭标题就能知道领域和贡献吗？

### 步骤 5.1：摘要（五句话公式） {#step-5-1-abstract-5-sentence-formula}

来自 Sebastian Farquhar（DeepMind）：

```
1. 你实现了什么："We introduce...", "We prove...", "We demonstrate..."
2. 为什么这很难且重要
3. 你如何做到（包含专业关键词以便被发现）
4. 你有什么证据
5. 你最引人注目的数字/结果
```

**删除**像"Large language models have achieved remarkable success..."这样的通用开头。

### 步骤 5.2：图 1 {#step-5-2-figure-1}

图 1 是大多数读者（在摘要之后）看的第二样东西。在写引言之前先草拟它——这会迫使你理清核心想法。
| 图1类型 | 使用时机 | 示例 |
|---------------|-------------|---------|
| **方法图** | 新架构或新流程 | 展示你系统的TikZ流程图 |
| **结果预告图** | 一个令人信服的结果就能说明全部 | 柱状图：“我们的 vs 基线”，差距明显 |
| **问题说明图** | 问题本身不直观 | 修复前后对比，展示你解决的失败模式 |
| **概念图** | 抽象贡献需要视觉支撑 | 方法属性的2x2矩阵 |

**规则**：图1必须在不阅读任何文字的情况下就能理解。仅凭图注就应传达核心思想。有目的地使用颜色——不要只是为了装饰。

### 步骤5.3：引言（最多1-1.5页） {#step-5-3-introduction-1-1-5-pages-max}

必须包含：
- 清晰的问题陈述
- 简要的方法概述
- 2-4条贡献列表（双栏格式下每条最多1-2行）
- 方法部分应在第2-3页开始

### 步骤5.4：方法 {#step-5-4-methods}

确保可复现：
- 概念性大纲或伪代码
- 列出所有超参数
- 提供足以复现的架构细节
- 呈现最终设计决策；消融实验放在实验部分

### 步骤5.5：实验与结果 {#step-5-5-experiments-results}

对于每个实验，明确说明：
- **它支持什么主张**
- 如何与主要贡献关联
- 观察要点：“蓝线显示X，这证明了Y”

要求：
- 误差棒及其方法说明（标准差 vs 标准误差）
- 超参数搜索范围
- 计算基础设施（GPU型号、总时长）
- 随机种子设置方法
### 步骤 5.6：相关工作 {#step-5-6-related-work}

按方法论组织，不要逐篇罗列论文。广泛引用——审稿人很可能就是相关论文的作者。

### 步骤 5.7：局限性（必填） {#step-5-7-limitations-required}

所有重要会议都要求这一部分。坦诚有助于：
- 审稿人被要求不因诚实的局限性说明而扣分
- 先指出弱点，提前规避批评
- 解释为什么这些局限性不会削弱核心主张

### 步骤 5.8：结论与讨论 {#step-5-8-conclusion-discussion}

**结论**（必填，0.5–1 页）：
- 用一句话重新陈述贡献（措辞与摘要不同）
- 总结关键发现（2–3 句话，不要列清单）
- 意义：这对领域意味着什么？
- 未来工作：2–3 个具体的下一步（不要模糊地说“我们把 X 留给未来工作”）

**讨论**（可选，有时与结论合并）：
- 超出直接结果的更广泛影响
- 与其他子领域的联系
- 对方法何时有效、何时无效的诚实评估
- 实际部署方面的考虑

**不要**在结论中引入新的结果或主张。

### 步骤 5.9：附录策略 {#step-5-9-appendix-strategy}

所有主要会议对附录页数没有限制，附录对可复现性至关重要。结构如下：

| 附录章节 | 内容 |
|---------|------|
| **证明与推导** | 正文中过长的完整证明。正文可陈述定理并注明“证明见附录 A”。 |
| **额外实验** | 消融实验、缩放曲线、按数据集细分、超参数敏感性 |
| **实现细节** | 完整的超参数表、训练细节、硬件规格、随机种子 |
| **数据集文档** | 数据收集过程、标注指南、许可信息、预处理 |
| **提示与模板** | 使用的确切提示（针对基于 LLM 的方法）、评估模板 |
| **人工评估** | 标注界面截图、给标注者的说明、IRB 详情 |
| **额外图表** | 按任务细分、轨迹可视化、失败案例示例 |
**规则**：
- 主论文必须独立成篇——审稿人无需阅读附录
- 切勿将关键证据仅放在附录中
- 交叉引用时写明："完整结果见表5（附录B）"，而非仅仅"见附录"
- 使用 `\appendix` 命令，然后使用 `\section{A: 证明}` 等

### 页面预算管理 {#page-budget-management}

当超出页面限制时：

| 缩减策略 | 节省页数 | 风险 |
|-------------|-------|------|
| 将证明移入附录 | 0.5-2 页 | 低——标准做法 |
| 压缩相关工作 | 0.5-1 页 | 中——可能遗漏关键引用 |
| 使用子图合并表格 | 0.25-0.5 页 | 低——通常可提高可读性 |
| 谨慎使用 `\vspace{-Xpt}` | 0.1-0.3 页 | 用量少则风险低，明显则风险高 |
| 删除定性示例 | 0.5-1 页 | 中——审稿人喜欢示例 |
| 缩小图片尺寸 | 0.25-0.5 页 | 高——图片必须保持可读性 |

**不要**：减小字号、修改页边距、删除必要章节（局限性、更广泛影响），或在正文中使用 `\small`/`\footnotesize`。

### 步骤 5.10：伦理与更广泛影响声明 {#step-5-10-ethics-broader-impact-statement}

大多数会议现在要求或强烈鼓励提供伦理/更广泛影响声明。这不是套话——审稿人会认真阅读，并可能指出伦理问题，从而导致直接拒稿。

**需要包含的内容：**

| 组成部分 | 内容 | 要求方 |
|-----------|---------|-------------|
| **积极的社会影响** | 你的工作如何惠及社会 | NeurIPS, ICML |
| **潜在的负面影响** | 滥用风险、双重用途问题、失败模式 | NeurIPS, ICML |
| **公平性与偏见** | 你的方法/数据是否存在已知偏见？ | 所有会议（隐含要求） |
| **环境影响** | 大规模训练的计算碳足迹 | ICML, 以及越来越多的 NeurIPS |
| **隐私** | 你的工作是否使用或支持处理个人数据？ | ACL, NeurIPS |
| **LLM 声明** | 是否在写作或实验中使用 AI？ | ICLR（强制）, ACL |
**撰写声明：**

```latex
\section*{更广泛影响声明}
% NeurIPS/ICML：在结论之后，不计入页数限制

% 1. 积极应用（1-2句话）
本工作实现了[具体应用]，可能使[具体群体]受益。

% 2. 风险与缓解措施（1-3句话，要具体）
[方法/模型]可能被滥用于[具体风险]。我们通过[具体缓解措施，例如仅发布大于特定大小的模型权重、包含安全过滤器、记录故障模式]来缓解这一风险。

% 3. 影响声明的局限性（1句话）
我们的评估仅限于[特定领域]；更广泛的部署需要[具体的额外工作]。
```

**常见错误：**
- 写“我们看不出任何负面影响”（几乎从不真实——审稿人不信任这种说法）
- 模糊表述：“这可能被滥用”但没有说明如何被滥用
- 忽略大规模工作的计算成本
- 忘记在要求披露LLM使用的会议中说明LLM的使用情况

**计算碳足迹**（针对训练密集型论文）：
```python
# 使用 ML CO2 Impact 工具方法估算
gpu_hours = 1000  # 总 GPU 小时数
gpu_tdp_watts = 400  # 例如 A100 = 400W
pue = 1.1  # 电能利用效率（数据中心开销）
carbon_intensity = 0.429  # kg CO2/kWh（美国平均值；因地区而异）

energy_kwh = (gpu_hours * gpu_tdp_watts * pue) / 1000
carbon_kg = energy_kwh * carbon_intensity
print(f"能量：{energy_kwh:.0f} kWh，碳：{carbon_kg:.0f} kg CO2eq")
```

### 第 5.11 步：数据表与模型卡（如适用） {#step-5-11-datasheets-model-cards-if-applicable}
如果您的论文介绍了**新数据集**或**发布模型**，请包含结构化文档。审稿人越来越期望这一点，NeurIPS 数据集与基准（Datasets & Benchmarks）赛道也要求这样做。

**数据集数据表**（Datasheets for Datasets, Gebru et al., 2021）——包含在附录中：

```
数据集文档（附录）：
- 动机：为什么创建这个数据集？它支持什么任务？
- 组成：实例是什么？有多少？数据类型？
- 收集：数据是如何收集的？来源是什么？
- 预处理：应用了哪些清洗/过滤？
- 分发：数据集如何分发？使用什么许可证？
- 维护：谁维护它？如何报告问题？
- 伦理考量：包含个人数据？获得同意了吗？
  潜在的危害？已知的偏见？
```

**模型卡**（Model Cards, Mitchell et al., 2019）——对于模型发布，包含在附录中：

```
模型卡（附录）：
- 模型详情：架构、训练数据、训练流程
- 预期用途：主要用例，超出范围的使用
- 评估指标：基准测试的评估指标和结果
- 伦理考量：已知偏见，公平性评估
- 局限性：已知的失败模式，模型表现不佳的领域
```

### 写作风格 {#writing-style}

**句子层面的清晰度（Gopen & Swan 的 7 条原则）：**

| 原则 | 规则 |
|-----------|------|
| 主语-动词邻近 | 主语和动词保持靠近 |
| 强调位置 | 将重点放在句子末尾 |
| 话题位置 | 先给出上下文，后放新信息 |
| 旧信息在前，新信息在后 | 熟悉信息 → 不熟悉信息 |
| 一个单元，一个功能 | 每个段落围绕一个要点 |
| 动词表达动作 | 使用动词，而非名词化 |
| 先上下文，后新内容 | 呈现之前先设定背景 |
**单词选择（Lipton, Steinhardt）：**
- 具体化：用“准确率”而非“性能”
- 避免模糊：除非确实不确定，否则去掉“可能”
- 全文术语保持一致
- 避免渐进式词汇：用“开发”，不用“组合”

**完整写作指南及示例**：参见 [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md)

### 使用 LaTeX 模板 {#using-latex-templates}

**始终先复制整个模板目录，然后在其中进行写作。**

```
模板设置检查清单：
- [ ] 步骤 1：将整个模板目录复制到新项目
- [ ] 步骤 2：验证模板原样编译通过（在修改之前）
- [ ] 步骤 3：阅读模板的示例内容，了解结构
- [ ] 步骤 4：逐节替换示例内容
- [ ] 步骤 5：使用模板宏（检查导言区中的 \newcommand 定义）
- [ ] 步骤 6：最后再清理模板残留内容
```

**步骤 1：复制完整模板**

```bash
cp -r templates/neurips2025/ ~/papers/my-paper/
cd ~/papers/my-paper/
ls -la  # 应看到：main.tex, neurips.sty, Makefile 等
```

复制整个目录，而不仅仅是 .tex 文件。模板包含样式文件（.sty）、参考文献样式（.bst）、示例内容和 Makefile。

**步骤 2：先验证模板能编译**

在进行任何修改之前：
```bash
latexmk -pdf main.tex
# 或手动：pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

如果未修改的模板无法编译，请先解决该问题（通常是缺少 TeX 包——通过 `tlmgr install &lt;package&gt;` 安装）。
**步骤 3：保留模板内容作为参考**

不要立即删除示例内容。将其注释掉，并作为格式参考使用：
```latex
% 模板示例（保留作为参考）：
% \begin{figure}[t]
%   \centering
%   \includegraphics[width=0.8\linewidth]{example-image}
%   \caption{模板展示了标题样式}
% \end{figure}

% 你的实际图片：
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{your-figure.pdf}
  \caption{你的标题，遵循相同样式。}
\end{figure}
```

**步骤 4：逐节替换内容**

按顺序系统地进行：标题/作者 → 摘要 → 引言 → 方法 → 实验 → 相关工作 → 结论 → 参考文献 → 附录。每完成一节后编译一次。

**步骤 5：使用模板宏**

```latex
\newcommand{\method}{YourMethodName}  % 统一的方法命名
\newcommand{\eg}{e.g.,\xspace}        % 正确的缩写
\newcommand{\ie}{i.e.,\xspace}
```

### 模板常见陷阱 {#template-pitfalls}

| 陷阱 | 问题 | 解决方案 |
|------|------|----------|
| 只复制 `.tex` 文件 | 缺少 `.sty`，无法编译 | 复制整个目录 |
| 修改 `.sty` 文件 | 破坏会议格式 | 永远不要编辑样式文件 |
| 随意添加宏包 | 冲突，破坏模板 | 只在必要时添加 |
| 过早删除模板内容 | 丢失格式参考 | 保留为注释直到完成 |
| 不频繁编译 | 错误累积 | 每完成一节后编译 |
| 使用栅格 PNG 作为图片 | 论文中模糊 | 始终通过 `savefig('fig.pdf')` 使用矢量 PDF |
### 快速模板参考 {#quick-template-reference}

| 会议 | 主文件 | 样式文件 | 页数限制 |
|------------|-----------|------------|------------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 9 页 |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 8 页 |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 9 页 |
| ACL 2025 | `acl_latex.tex` | `acl.sty` | 8 页（长文） |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 7 页 |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 9 页 |

**通用规则**：双盲评审，参考文献不计入页数，附录不限页数，必须使用 LaTeX。

模板位于 `templates/` 目录下。编译环境设置（VS Code、命令行、Overleaf、其他 IDE）请参见 [templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md)。

### 表格与图表 {#tables-and-figures}

**表格** — 使用 `booktabs` 实现专业排版：

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
方法 & 准确率 $\uparrow$ & 延迟 $\downarrow$ \\
\midrule
基线 & 85.2 & 45ms \\
\textbf{我们的方法} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

规则：
- 每个指标的最佳值加粗
- 包含方向符号（$\uparrow$ 越高越好，$\downarrow$ 越低越好）
- 数值列右对齐
- 小数精度保持一致

**图表**：
- **矢量图**（PDF、EPS）用于所有图表和示意图 — `plt.savefig('fig.pdf')`
- **位图**（PNG 600 DPI）仅用于照片
- **色盲友好调色板**（Okabe-Ito 或 Paul Tol）
- 验证**灰度可读性**（8% 的男性存在色觉缺陷）
- **图表内不包含标题** — 图注承担此功能
- **图注自包含** — 读者无需阅读正文即可理解
### 会议转投 {#conference-resubmission}

如需在不同会议之间转换格式，请参见第 7 阶段（投稿准备）——其中涵盖了完整的转换流程、页面变更表格以及被拒后的指导。

### 专业 LaTeX 导言区 {#professional-latex-preamble}

为任何论文添加以下宏包，即可获得专业品质。它们与所有主流会议样式文件兼容：

```latex
% --- 专业宏包（在会议样式文件之后添加）---

% 排版
\usepackage{microtype}              % 微排版改进（突出、扩展）
                                     % 让文字明显更精致——始终包含

% 表格
\usepackage{booktabs}               % 专业表格线（\toprule, \midrule, \bottomrule）
\usepackage{siunitx}                % 统一的数字格式、小数点对齐
                                     % 用法：\num{12345} → 12,345；\SI{3.5}{GHz} → 3.5 GHz
                                     % 表格对齐：S 列类型用于小数点对齐的数字

% 图片
\usepackage{graphicx}               % 包含图片（\includegraphics）
\usepackage{subcaption}             % 子图，带 (a)、(b)、(c) 标签
                                     % 用法：\begin{subfigure}{0.48\textwidth} ... \end{subfigure}

% 图表与算法
\usepackage{tikz}                   % 可编程矢量图
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc, fit, backgrounds}
\usepackage[ruled,vlined]{algorithm2e}  % 专业伪代码
                                     % 替代方案：如果模板已包含，则使用 \usepackage{algorithmicx}

% 交叉引用
\usepackage{cleveref}               % 智能引用：\cref{fig:x} → "图 1"
                                     % 必须在 hyperref 之后加载
                                     % 处理：图、表、章节、公式、算法

% 数学（通常由会议 .sty 包含，但请确认）
\usepackage{amsmath,amssymb}        % AMS 数学环境与符号
\usepackage{mathtools}              % 扩展 amsmath（dcases, coloneqq 等）

% 颜色（用于图片和图表）
\usepackage{xcolor}                 % 颜色管理
% Okabe-Ito 色盲友好调色板：
\definecolor{okblue}{HTML}{0072B2}
\definecolor{okorange}{HTML}{E69F00}
\definecolor{okgreen}{HTML}{009E73}
\definecolor{okred}{HTML}{D55E00}
\definecolor{okpurple}{HTML}{CC79A7}
\definecolor{okcyan}{HTML}{56B4E9}
\definecolor{okyellow}{HTML}{F0E442}
```
**注意：**
- `microtype` 是对视觉质量影响最大的单一宏包。它会在亚像素级别调整字符间距。请始终包含它。
- `siunitx` 通过 `S` 列类型处理表格中的小数点对齐——无需手动调整间距。
- `cleveref` 必须在 `hyperref` **之后**加载。大多数会议 `.sty` 文件会加载 hyperref，因此请将 cleveref 放在最后。
- 检查会议模板是否已加载了这些宏包（尤其是 `algorithm`、`amsmath`、`graphicx`）。不要重复加载。

### siunitx 表格对齐 {#siunitx-table-alignment}

`siunitx` 能显著提升数字密集型表格的可读性：

```latex
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1] S[table-format=2.1]}
\toprule
Method & {Accuracy $\uparrow$} & {F1 $\uparrow$} & {Latency (ms) $\downarrow$} \\
\midrule
Baseline         & 85.2  & 83.7  & 45.3 \\
Ablation (no X)  & 87.1  & 85.4  & 42.1 \\
\textbf{Ours}    & \textbf{92.1} & \textbf{90.8} & \textbf{38.7} \\
\bottomrule
\end{tabular}
```

`S` 列类型会自动按小数点对齐。用 `{}` 包裹的表头会跳过对齐。

### 子图 {#subfigures}

并排图的常用模式：

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_a.pdf}
    \caption{Results on Dataset A.}
    \label{fig:results-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_b.pdf}
    \caption{Results on Dataset B.}
    \label{fig:results-b}
  \end{subfigure}
  \caption{Comparison of our method across two datasets. (a) shows the scaling
  behavior and (b) shows the ablation results. Both use 5 random seeds.}
  \label{fig:results}
\end{figure}
```
使用 `\cref{fig:results}` → "图1"，`\cref{fig:results-a}` → "图1a"。

### 使用 algorithm2e 的伪代码 {#pseudocode-with-algorithm2e}

```latex
\begin{algorithm}[t]
\caption{Iterative Refinement with Judge Panel}
\label{alg:method}
\KwIn{Task $T$, model $M$, judges $J_1 \ldots J_n$, convergence threshold $k$}
\KwOut{Final output $A^*$}
$A \gets M(T)$ \tcp*{Initial generation}
$\text{streak} \gets 0$\;
\While{$\text{streak} < k$}{
  $C \gets \text{Critic}(A, T)$ \tcp*{Identify weaknesses}
  $B \gets M(T, C)$ \tcp*{Revised version addressing critique}
  $AB \gets \text{Synthesize}(A, B)$ \tcp*{Merge best elements}
  \ForEach{judge $J_i$}{
    $\text{rank}_i \gets J_i(\text{shuffle}(A, B, AB))$ \tcp*{Blind ranking}
  }
  $\text{winner} \gets \text{BordaCount}(\text{ranks})$\;
  \eIf{$\text{winner} = A$}{
    $\text{streak} \gets \text{streak} + 1$\;
  }{
    $A \gets \text{winner}$; $\text{streak} \gets 0$\;
  }
}
\Return{$A$}\;
\end{algorithm}
```

### TikZ 图表模式 {#tikz-diagram-patterns}

TikZ 是机器学习论文中方法图的标准。常见模式：

**流水线/流程图**（机器学习论文中最常见）：

```latex
\begin{figure}[t]
\centering
\begin{tikzpicture}[
  node distance=1.8cm,
  box/.style={rectangle, draw, rounded corners, minimum height=1cm, 
              minimum width=2cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
]
  \node[box, fill=okcyan!20] (input) {Input\\$x$};
  \node[box, fill=okblue!20, right of=input] (encoder) {Encoder\\$f_\theta$};
  \node[box, fill=okgreen!20, right of=encoder] (latent) {Latent\\$z$};
  \node[box, fill=okorange!20, right of=latent] (decoder) {Decoder\\$g_\phi$};
  \node[box, fill=okred!20, right of=decoder] (output) {Output\\$\hat{x}$};
  
  \draw[arrow] (input) -- (encoder);
  \draw[arrow] (encoder) -- (latent);
  \draw[arrow] (latent) -- (decoder);
  \draw[arrow] (decoder) -- (output);
\end{tikzpicture}
\caption{Architecture overview. The encoder maps input $x$ to latent 
representation $z$, which the decoder reconstructs.}
\label{fig:architecture}
\end{figure}
```
**比较/矩阵图**（用于展示方法变体）：

```latex
\begin{tikzpicture}[
  cell/.style={rectangle, draw, minimum width=2.5cm, minimum height=1cm, 
               align=center, font=\small},
  header/.style={cell, fill=gray!20, font=\small\bfseries},
]
  % 表头
  \node[header] at (0, 0) {方法};
  \node[header] at (3, 0) {收敛？};
  \node[header] at (6, 0) {质量？};
  % 行
  \node[cell] at (0, -1) {单次通过};
  \node[cell, fill=okgreen!15] at (3, -1) {N/A};
  \node[cell, fill=okorange!15] at (6, -1) {基线};
  \node[cell] at (0, -2) {批评+修订};
  \node[cell, fill=okred!15] at (3, -2) {否};
  \node[cell, fill=okred!15] at (6, -2) {退化};
  \node[cell] at (0, -3) {我们的方法};
  \node[cell, fill=okgreen!15] at (3, -3) {是（$k$=2）};
  \node[cell, fill=okgreen!15] at (6, -3) {提升};
\end{tikzpicture}
```

**迭代循环图**（用于带反馈的方法）：

```latex
\begin{tikzpicture}[
  node distance=2cm,
  box/.style={rectangle, draw, rounded corners, minimum height=0.8cm, 
              minimum width=1.8cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
  label/.style={font=\scriptsize, midway, above},
]
  \node[box, fill=okblue!20] (gen) {生成器};
  \node[box, fill=okred!20, right=2.5cm of gen] (critic) {批评器};
  \node[box, fill=okgreen!20, below=1.5cm of $(gen)!0.5!(critic)$] (judge) {评判小组};
  
  \draw[arrow] (gen) -- node[label] {输出 $A$} (critic);
  \draw[arrow] (critic) -- node[label, right] {批评 $C$} (judge);
  \draw[arrow] (judge) -| node[label, left, pos=0.3] {胜者} (gen);
\end{tikzpicture}
```
### 使用 latexdiff 进行修订追踪 {#latexdiff-for-revision-tracking}

对 rebuttal 阶段至关重要——可生成标记了版本间变更的 PDF：

```bash
# 安装
# macOS: brew install latexdiff（或随 TeX Live 自带）
# Linux: sudo apt install latexdiff

# 生成差异文件
latexdiff paper_v1.tex paper_v2.tex > paper_diff.tex
pdflatex paper_diff.tex

# 对于多文件项目（使用了 \input{} 或 \include{}）
latexdiff --flatten paper_v1.tex paper_v2.tex > paper_diff.tex
```

这会生成一个 PDF，其中删除内容以红色删除线显示，新增内容以蓝色显示——这是 rebuttal 补充材料的标准格式。

### 使用 SciencePlots 美化 matplotlib 图表 {#scienceplots-for-matplotlib}

安装并使用，可生成出版级质量的图表：

```bash
pip install SciencePlots
```

```python
import matplotlib.pyplot as plt
import scienceplots  # 注册样式

# 使用科学样式（类似 IEEE，简洁）
with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # 单栏宽度
    ax.plot(x, y, label='Ours', color='#0072B2')
    ax.plot(x, y2, label='Baseline', color='#D55E00', linestyle='--')
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Accuracy')
    ax.legend()
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')

# 可用样式：'science', 'ieee', 'nature', 'science+ieee'
# 如果生成图表的机器未安装 LaTeX，请添加 'no-latex'
```

**标准图表尺寸**（双栏格式）：
- 单栏：`figsize=(3.5, 2.5)` —— 适合一栏宽度
- 双栏：`figsize=(7.0, 3.0)` —— 跨两栏
- 方形：`figsize=(3.5, 3.5)` —— 用于热力图、混淆矩阵
---

## 第六阶段：自我审阅与修订 {#phase-6-self-review-revision}

**目标**：模拟投稿前的审阅流程，尽早发现薄弱环节。

### 步骤 6.1：模拟审阅（集成模式） {#step-6-1-simulate-reviews-ensemble-pattern}

从多个视角生成审阅意见。自动化研究管线（尤其是 SakanaAI 的 AI-Scientist）的关键洞见是：**使用元审稿人的集成审阅，比单次审阅能产生更校准的反馈。**

**第一步：生成 N 份独立审阅**（N=3-5）

使用不同的模型或温度设置。每位审稿人只看到论文，看不到其他审阅意见。**默认偏向负面**——LLM 在评估中普遍存在正向偏差。

```
你是一位 [会议/期刊] 的专家审稿人。你批判且严谨。
如果论文存在弱点，或者你对某个主张不确定，请明确标记出来，
并在评分中反映出来。不要给予怀疑的好处。

请根据官方审稿指南审阅这篇论文。评估以下方面：

1. 可靠性（主张是否有充分支持？基线是否公平且强有力？）
2. 清晰度（论文是否写得好？专家能否复现？）
3. 重要性（对社区是否有意义？）
4. 原创性（是否有新见解，而不仅仅是增量组合？）

请以结构化的 JSON 格式提供你的审阅意见：
{
  "summary": "2-3 句摘要",
  "strengths": ["优势 1", "优势 2", ...],
  "weaknesses": ["弱点 1（最关键）", "弱点 2", ...],
  "questions": ["向作者提问 1", ...],
  "missing_references": ["应引用的论文", ...],
  "soundness": 1-4,
  "presentation": 1-4,
  "contribution": 1-4,
  "overall": 1-10,
  "confidence": 1-5
}
```
**Step 2: 元评审（领域主席聚合）**

将所有 N 份评审反馈提交给一位元评审人：

```
你是 [VENUE] 的领域主席。你收到了对一篇论文的 [N] 份独立评审。
你的任务是：

1. 识别评审人之间的共识优势和劣势
2. 通过直接检查论文来解决分歧
3. 生成代表综合判断的元评审
4. 使用所有评审的平均数值分数

保持保守态度：如果评审人对于某个弱点是否严重存在分歧，则将之视为严重问题，直到作者解决它为止。

评审：
[review_1]
[review_2]
...
```

**Step 3: 反思循环**（可选，2-3 轮）

每位评审人在看到元评审后，可以优化自己的评审。使用提前终止哨兵机制：如果评审人回复“I am done”（无变更），则停止迭代。

**评审的模型选择**：即使你用一个较便宜的模型写了论文，评审时最好也用当前可用的最强模型。评审模型应与写作模型独立选择。

**少样本校准**：如果可行，提供 1-2 篇来自目标会议的真实已发表评审作为示例。这会显著改善分数校准。参见 [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) 获取示例评审。

### Step 6.1b: 视觉评审通道（VLM） {#step-6-1b-visual-review-pass-vlm}

纯文本评审会漏掉一整类问题：图表质量、排版问题、视觉一致性。如果你有支持视觉理解的模型，对已编译的 PDF 运行一次独立的**视觉评审**：
```
你正在审阅这份研究论文PDF的视觉呈现效果。
请检查：
1. 图表质量：绘图是否清晰可读？标签是否清晰？颜色是否可区分？
2. 图表与标题对应：每个标题是否准确描述了对应的图表？
3. 布局问题：孤立的章节标题、尴尬的分页、图表远离其引用位置
4. 表格格式：列对齐、小数精度一致、最佳结果加粗
5. 视觉一致性：所有图表使用相同的配色方案、一致的字体大小
6. 灰度可读性：如果以黑白打印，图表是否仍能理解？

对于每个问题，请指明页码和具体位置。
```

这能捕捉到纯文本审阅无法发现的问题：轴标签难以辨认的绘图、距离首次引用位置3页的图表、图2和图5之间不一致的配色方案，或者明显超出列宽的表格。

### 步骤 6.1c：声明验证环节 {#step-6-1c-claim-verification-pass}

在模拟审阅之后，运行一个独立的验证环节。这能捕捉到审阅者可能遗漏的事实性错误：

```
声明验证协议：
1. 从论文中提取每一个事实性声明（数字、比较、趋势）
2. 对于每个声明，追溯其支持的具体实验/结果
3. 验证论文中的数字是否与实际结果文件一致
4. 标记任何无法追溯来源的声明为 [VERIFY]
```

对于基于Agent的工作流：将验证委托给一个**全新的 sub-agent**，该 sub-agent 仅接收论文文本和原始结果文件。全新的上下文可以防止确认偏差——验证者不会“记住”结果应该是什么。
### 步骤 6.2：对反馈进行优先级排序 {#step-6-2-prioritize-feedback}

收集完审阅意见后，进行分类：

| 优先级 | 操作 |
|--------|------|
| **严重**（技术缺陷、缺少基线） | 必须修复。可能需要新实验 → 返回阶段 2 |
| **高**（清晰度问题、缺少消融实验） | 应在本次修订中修复 |
| **中**（次要写作问题、额外实验） | 时间允许则修复 |
| **低**（风格偏好、无关建议） | 记录为未来工作 |

### 步骤 6.3：修订周期 {#step-6-3-revision-cycle}

针对每个严重/高优先级问题：
1. 确定受影响的特定章节
2. 起草修复方案
3. 验证修复不会破坏其他论断
4. 更新论文
5. 再次对照审稿人的意见进行核查

### 步骤 6.4：撰写反驳信 {#step-6-4-rebuttal-writing}

在回应实际审稿意见时（投稿后），反驳信是一项与修订截然不同的技能：

**格式**：逐点回应。针对每位审稿人的每条意见：
```
> R1-W1: "论文缺少与方法 X 的对比。"

我们感谢审稿人的建议。我们已在表 3（修订版）中添加了与方法 X 的对比。
我们的方法在 [指标] 上比 X 高出 3.2 个百分点（p<0.05）。我们注意到 X 需要
我们两倍的计算预算。
```

**规则**：
- 回应每一条意见——审稿人会注意到你是否跳过某条
- 用最强的回应开头
- 简洁直接——审稿人需要阅读数十份反驳信
- 如果在反驳期间进行了实验，请包含新的结果
- 即使面对薄弱批评，也切勿表现出防御性或轻蔑态度
- 使用 `latexdiff` 生成标记了修改的 PDF（参见专业 LaTeX 工具章节）
- 感谢审稿人提出具体、可操作的反馈（而非泛泛的赞美）
**不要这样做**：没有证据就说“我们不敢苟同”。不解释就说“这不在范围内”。只回应优点而忽略缺点。

### 步骤 6.5：论文演进追踪 {#step-6-5-paper-evolution-tracking}

在关键里程碑保存快照：
```
paper/
  paper.tex                    # 当前工作版本
  paper_v1_first_draft.tex     # 第一版完整草稿
  paper_v2_post_review.tex     # 模拟审稿后版本
  paper_v3_pre_submission.tex  # 提交前最终版
  paper_v4_camera_ready.tex    # 接收后最终版
```

---

## 阶段 7：提交准备 {#phase-7-submission-preparation}

**目标**：最终检查、格式调整与提交。

### 步骤 7.1：会议检查清单 {#step-7-1-conference-checklist}

每个会议都有强制检查清单。请仔细完成——不完整的检查清单可能导致直接拒稿。

参见 [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) 了解：
- NeurIPS 16 项论文检查清单
- ICML 更广泛影响 + 可复现性
- ICLR LLM 披露政策
- ACL 强制性局限性说明部分
- 通用提交前检查清单

### 步骤 7.2：匿名化检查清单 {#step-7-2-anonymization-checklist}

双盲审稿意味着审稿人无法知道论文作者是谁。请检查以下所有项：

```
匿名化检查清单：
- [ ] PDF 中没有任何作者姓名或所属机构
- [ ] 没有致谢部分（接收后再添加）
- [ ] 自引用使用第三人称：“Smith 等人 [1] 表明……”而不是“我们之前表明 [1]……”
- [ ] 没有指向个人仓库的 GitHub/GitLab 链接
- [ ] 代码链接使用 Anonymous GitHub (https://anonymous.4open.science/)
- [ ] 图片中没有机构标志或标识符
- [ ] 文件元数据不包含作者姓名（检查 PDF 属性）
- [ ] 没有“我们之前的工作”或“在我们之前的论文中”这样的措辞
- [ ] 数据集名称不暴露机构（必要时重命名）
- [ ] 补充材料不包含可识别信息
```
**常见错误**：补充代码中可见的 Git 提交信息、来自机构工具的水印图片、前序草稿遗留的致谢、匿名期前发布的 arXiv 预印本。

### 步骤 7.3：格式验证 {#step-7-3-formatting-verification}

```
提交前格式检查：
- [ ] 页数限制（参考文献和附录除外）
- [ ] 所有图片为矢量图（PDF）或高分辨率位图（600 DPI PNG）
- [ ] 所有图片在灰度模式下可读
- [ ] 所有表格使用 booktabs
- [ ] 参考文献正确编译（引用中无 "?"）
- [ ] 关键区域无 overfull hboxes
- [ ] 附录清晰标注并分离
- [ ] 必需章节已包含（局限性、更广泛影响等）
```

### 步骤 7.4：编译前验证 {#step-7-4-pre-compilation-validation}

在尝试 `pdflatex` **之前**运行这些自动化检查。在此处捕获错误比调试编译器输出更快。

```bash
# 1. Lint with chktex (catches common LaTeX mistakes)
# Suppress noisy warnings: -n2 (sentence end), -n24 (parens), -n13 (intersentence), -n1 (command terminated)
chktex main.tex -q -n2 -n24 -n13 -n1

# 2. Verify all citations exist in .bib
# Extract \cite{...} from .tex, check each against .bib
python3 -c "
import re
tex = open('main.tex').read()
bib = open('references.bib').read()
cites = set(re.findall(r'\\\\cite[tp]?{([^}]+)}', tex))
for cite_group in cites:
    for cite in cite_group.split(','):
        cite = cite.strip()
        if cite and cite not in bib:
            print(f'WARNING: \\\\cite{{{cite}}} not found in references.bib')
"

# 3. Verify all referenced figures exist on disk
python3 -c "
import re, os
tex = open('main.tex').read()
figs = re.findall(r'\\\\includegraphics(?:\[.*?\])?{([^}]+)}', tex)
for fig in figs:
    if not os.path.exists(fig):
        print(f'WARNING: Figure file not found: {fig}')
"

# 4. Check for duplicate \label definitions
python3 -c "
import re
from collections import Counter
tex = open('main.tex').read()
labels = re.findall(r'\\\\label{([^}]+)}', tex)
dupes = {k: v for k, v in Counter(labels).items() if v > 1}
for label, count in dupes.items():
    print(f'WARNING: Duplicate label: {label} (appears {count} times)')
"
```
在继续之前，请先修复所有警告。对于基于 Agent 的工作流：将 chktex 的输出反馈给 Agent，并指示其进行最小化修复。

### 步骤 7.5：最终编译 {#step-7-5-final-compilation}

```bash
# 清理构建
rm -f *.aux *.bbl *.blg *.log *.out *.pdf
latexmk -pdf main.tex

# 或手动编译（三次 pdflatex + bibtex 处理交叉引用）
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# 确认输出文件存在且有内容
ls -la main.pdf
```

**如果编译失败**：解析 `.log` 文件，找到第一个错误。常见修复方法：
- "Undefined control sequence" → 缺少宏包或命令名拼写错误
- "Missing $ inserted" → 数学符号出现在数学模式之外
- "File not found" → 图片路径错误或缺少 .sty 文件
- "Citation undefined" → .bib 条目缺失或未运行 bibtex

### 步骤 7.6：会议特定要求 {#step-7-6-conference-specific-requirements}

| 会议 | 特殊要求 |
|-------|---------------------|
| **NeurIPS** | 附录中需包含论文清单，若被接收则需提供通俗摘要 |
| **ICML** | 需包含更广泛影响声明（位于结论之后，不计入字数限制） |
| **ICLR** | 需披露是否使用大语言模型，并签署互审协议 |
| **ACL** | 必须包含局限性章节，以及负责任 NLP 清单 |
| **AAAI** | 严格遵循样式文件——不得做任何修改 |
| **COLM** | 需为语言模型社区阐述贡献 |

### 步骤 7.7：会议转投与格式转换 {#step-7-7-conference-resubmission-format-conversion}

在不同会议之间转投时，**切勿在不同模板之间复制 LaTeX 导言区**：
```bash
# 1. 从目标模板开始全新准备
cp -r templates/icml2026/ new_submission/

# 2. 仅复制内容部分（非前言）
#    - 摘要文本、章节内容、图表、表格、参考文献条目

# 3. 根据页数限制调整
# 4. 添加特定会议要求的章节
# 5. 更新参考文献
```

| 从 → 到 | 页数变化 | 关键调整 |
|-----------|-------------|-----------------|
| NeurIPS → ICML | 9 → 8 | 删减1页，增加 Broader Impact |
| ICML → ICLR | 8 → 9 | 扩展实验，增加 LLM 披露声明 |
| NeurIPS → ACL | 9 → 8 | 按 NLP 惯例重构，增加 Limitations |
| ICLR → AAAI | 9 → 7 | 大幅删减，严格遵循格式要求 |
| 任意 → COLM | 不定 → 9 | 重新聚焦于语言模型方向 |

删减页数时：将证明移至附录，压缩相关工作，合并表格，使用子图。
扩展页数时：增加消融实验，扩展局限性，补充更多基线，添加定性示例。

**被拒后**：在新版本中回应审稿人的意见，但不要包含“修改说明”章节或引用之前的投稿（盲审）。

### 步骤 7.8：最终版准备（录用后） {#step-7-8-camera-ready-preparation-post-acceptance}

录用后，准备最终版：

```
最终版检查清单：
- [ ] 去匿名化：添加作者姓名、单位、邮箱地址
- [ ] 添加致谢章节（基金资助、计算资源、有帮助的审稿人）
- [ ] 添加公开代码/数据链接（真实 GitHub 仓库，非匿名）
- [ ] 处理元审稿人要求的强制性修改
- [ ] 切换模板至最终版模式（如适用——例如 AAAI 的 \anon → \camera）
- [ ] 按会议要求添加版权声明
- [ ] 更新文中所有“匿名”占位符
- [ ] 确认最终 PDF 编译无误
- [ ] 检查最终版页数限制（有时与投稿时不同）
- [ ] 将补充材料（代码、数据、附录）上传至会议系统
```
### 步骤 7.9：arXiv 与预印本策略 {#step-7-9-arxiv-preprint-strategy}

在机器学习领域，将论文发布到 arXiv 是标准做法，但需要考虑时机和匿名性等重要因素。

**时机决策树：**

| 情况 | 建议 |
|-----------|---------------|
| 投稿至双盲会议（NeurIPS、ICML、ACL） | 在投稿截止日期**之后**再发布到 arXiv，而不是之前。提前发布在技术上可能违反匿名政策，尽管执行力度因会议而异。 |
| 投稿至 ICLR | ICLR 明确允许在投稿前发布 arXiv 版本。但不要在投稿本身中放入作者姓名。 |
| 论文已在 arXiv 上，投稿至新会议 | 大多数会议可以接受。审稿期间**不要**更新 arXiv 版本，加入引用审稿意见的修改。 |
| 研讨会论文 | 随时可以发布 arXiv——研讨会通常不是双盲的。 |
| 希望确立优先权 | 如果担心被抢先，立即发布——但接受匿名性方面的权衡。 |

**arXiv 类别选择**（机器学习/人工智能论文）：

| 类别 | 代码 | 最适合 |
|----------|------|----------|
| 机器学习 | `cs.LG` | 通用机器学习方法 |
| 计算与语言 | `cs.CL` | 自然语言处理、语言模型 |
| 人工智能 | `cs.AI` | 推理、规划、Agent |
| 计算机视觉 | `cs.CV` | 视觉模型 |
| 信息检索 | `cs.IR` | 搜索、推荐 |

**列出主类别 + 1-2 个交叉列表类别。** 类别越多 = 可见性越高，但只交叉列表到真正相关的类别。

**版本策略：**
- **v1**：初始提交（与会议投稿版本一致）
- **v2**：接收后，加入最终定稿修正（在摘要中添加“已接收于 [会议名称]”）
- 审稿期间不要发布 v2 版本，尤其是包含明显回应审稿人意见的修改。
```bash
# 检查你的论文标题在 arXiv 上是否已被占用
# （在选定标题之前）
pip install arxiv
python -c "
import arxiv
results = list(arxiv.Search(query='ti:\"你的确切标题\"', max_results=5).results())
print(f'找到 {len(results)} 个匹配结果')
for r in results: print(f'  {r.title} ({r.published.year})')
"
```

### 步骤 7.10：研究代码打包 {#step-7-10-research-code-packaging}

发布干净、可运行的代码能显著提升引用量和审稿人信任度。请将代码与最终提交版本一同打包。

**仓库结构：**

```
your-method/
  README.md              # 环境搭建、使用说明、复现指南
  requirements.txt       # 或使用 environment.yml（conda 环境）
  setup.py               # 用于 pip 可安装的包
  LICENSE                # 研究推荐使用 MIT 或 Apache 2.0 许可证
  configs/               # 实验配置
  src/                   # 核心方法实现
  scripts/               # 训练、评估、分析脚本
    train.py
    evaluate.py
    reproduce_table1.sh  # 每个主要结果对应一个脚本
  data/                  # 小规模数据或下载脚本
    download_data.sh
  results/               # 用于验证的预期输出
```

**研究代码的 README 模板：**

```markdown
# [论文标题]

"[论文标题]" 的官方实现（会议/期刊年份）。

## 环境搭建
[搭建环境的具体命令]

## 复现
复现表 1：`bash scripts/reproduce_table1.sh`
复现图 2：`python scripts/make_figure2.py`

## 引用
[BibTeX 条目]
```
**预发布检查清单：**
```
- [ ] 从干净的克隆中运行代码（在全新机器或 Docker 上测试）
- [ ] 所有依赖项固定到特定版本
- [ ] 没有硬编码的绝对路径
- [ ] 仓库中没有 API 密钥、凭据或个人数据
- [ ] README 涵盖设置、复现和引用
- [ ] LICENSE 文件存在（MIT 或 Apache 2.0 以获得最大复用性）
- [ ] 结果在预期方差内可复现
- [ ] .gitignore 排除数据文件、检查点、日志
```

**用于投稿的匿名代码**（录用前）：
```bash
# 使用 Anonymous GitHub 进行双盲评审
# https://anonymous.4open.science/
# 上传你的仓库 → 获取匿名 URL → 放入论文中
```

---

## 阶段 8：录用后交付物 {#phase-8-post-acceptance-deliverables}

**目标**：通过演示材料和社区互动，最大化已录用论文的影响力。

### 步骤 8.1：会议海报 {#step-8-1-conference-poster}

大多数会议要求海报展示环节。海报设计原则：

| 元素 | 指南 |
|------|------|
| **尺寸** | 查看会场要求（通常为 24"x36" 或 A0 纵向/横向） |
| **内容** | 标题、作者、一句话贡献、方法图、2-3 个关键结果、结论 |
| **阅读顺序** | 左上到右下（Z 字形）或列式 |
| **文字** | 标题在 3 米处可读，正文在 1 米处可读。不要整段文字——仅用要点。 |
| **图表** | 复用论文中的图表，使用更高分辨率。放大关键结果。 |

**工具**：LaTeX（`beamerposter` 包）、PowerPoint/Keynote、Figma、Canva。

**制作**：在会议前 2 周以上下单。布质海报更轻便，便于携带。许多会议现在也支持虚拟/数字海报。
### 步骤 8.2：会议口头报告 / 亮点报告 {#step-8-2-conference-talk-spotlight}

如果获得口头或亮点展示机会：

| 报告类型 | 时长 | 内容 |
|-----------|----------|---------|
| **亮点报告** | 5 分钟 | 问题、方法、一个关键结果。排练到恰好 5 分钟。 |
| **口头报告** | 15-20 分钟 | 完整故事：问题、方法、关键结果、消融实验、局限性。 |
| **研讨会报告** | 10-15 分钟 | 根据研讨会听众调整——可能需要更多背景介绍。 |

**幻灯片设计规则：**
- 每页只讲一个想法
- 尽量减少文字——细节靠说，不要投在屏幕上
- 对关键图表做动画，逐步构建理解
- 在结尾放一张“要点总结”幻灯片（一句话概括贡献）
- 准备备用幻灯片，应对可能被问到的问题

### 步骤 8.3：博客文章 / 社交媒体 {#step-8-3-blog-post-social-media}

一篇通俗易懂的总结能显著提升影响力：

- **Twitter/X 帖子串**：5-8 条推文。用结果开头，而不是方法。包含图 1 和关键结果图。
- **博客文章**：800-1500 字。面向机器学习从业者，而非审稿人。省略形式化内容，强调直觉和实际意义。
- **项目页面**：包含摘要、图表、演示、代码链接、BibTeX 的 HTML 页面。使用 GitHub Pages。

**发布时间**：论文出现在会议论文集或 arXiv 定稿后的 1-2 天内发布。

---

## 研讨会与短文 {#workshop-short-papers}

研讨会论文和短文（例如 ACL 短文、Findings 论文）遵循相同的流程，但有不同的限制和期望。

### 研讨会论文 {#workshop-papers}

| 属性 | 研讨会 | 主会 |
|----------|----------|-----------------|
| **页数限制** | 4-6 页（通常） | 7-9 页 |
| **审稿标准** | 完整性要求较低 | 必须完整、彻底 |
| **审稿流程** | 通常为单盲或轻度审稿 | 双盲、严格 |
| **看重什么** | 有趣的想法、初步结果、立场文章 | 完整的实证故事，有强基线 |
| **arXiv** | 随时可发布 | 时机重要（参见 arXiv 策略） |
| **贡献门槛** | 新颖方向、有趣的负面结果、进行中的工作 | 有强证据的重大进展 |
**何时投稿 workshop：**
- 早期想法，希望在完整论文前获得反馈
- 负面结果，不值得写 8 页以上
- 针对热点话题的立场文章或观点
- 复现研究或可重复性报告

### ACL 短文与 Findings {#acl-short-papers-findings}

ACL 会议有明确的投稿类型：

| 类型 | 页数 | 预期内容 |
|------|------|----------|
| **长文** | 8 | 完整研究，强基线，消融实验 |
| **短文** | 4 | 聚焦贡献：一个清晰观点并附证据 |
| **Findings** | 8 | 扎实的工作，但略低于主会标准 |

**短文策略**：选择一个主张并充分支持。不要试图将长文压缩到 4 页——写一篇不同且更聚焦的论文。

---

## 经验 ML 之外的论文类型 {#paper-types-beyond-empirical-ml}

上述主要流程针对经验 ML 论文。其他论文类型需要不同的结构和证据标准。关于每种类型的详细指导，请参见 [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。

### 理论论文 {#theory-papers}

**结构**：引言 → 预备知识（定义、符号）→ 主要结果（定理）→ 证明草图 → 讨论 → 完整证明（附录）

**与经验论文的主要区别：**
- 贡献是定理、界或不可能性结果——而非实验数据
- 方法部分替换为“预备知识”和“主要结果”
- 证明是证据，而非实验（不过理论的经验验证也受欢迎）
- 正文中放证明草图，附录中放完整证明是标准做法
- 实验部分可选，但如果能验证理论预测，则能增强论文
**证明写作原则：**
- 形式化陈述定理，明确所有假设
- 在正式证明前提供直观理解（“关键洞察是……”）
- 证明梗概应在 0.5–1 页内传达主要思想
- 使用 `\begin{proof}...\end{proof}` 环境
- 对假设进行编号，并在定理中引用：“在假设 1–3 下，……”

### 综述 / 教程论文 {#survey-tutorial-papers}

**结构**：引言 → 分类法 / 组织方式 → 详细覆盖 → 开放问题 → 结论

**关键区别：**
- 贡献在于组织、综合和识别开放问题——而非新方法
- 必须在范围内全面（审稿人会检查是否遗漏参考文献）
- 需要清晰的分类法或组织框架
- 价值来自单个论文未建立的作品之间的联系
- 最佳发表场所：TMLR（综述轨道）、JMLR、Foundations and Trends in ML、ACM Computing Surveys

### 基准论文 {#benchmark-papers}

**结构**：引言 → 任务定义 → 数据集构建 → 基线评估 → 分析 → 预期用途与局限性

**关键区别：**
- 贡献在于基准本身——它必须填补真正的评估空白
- 数据集文档是强制性的，而非可选的（参见 Datasheets，步骤 5.11）
- 必须证明基准具有挑战性（基线未饱和）
- 必须证明基准测量了你声称要测量的内容（构念效度）
- 最佳发表场所：NeurIPS Datasets & Benchmarks 轨道、ACL（资源论文）、LREC-COLING
### 立场论文 {#position-papers}

**结构**：引言 → 背景 → 论点/论证 → 支撑证据 → 反驳观点 → 影响

**关键区别**：
- 贡献在于提出论点，而非呈现结果
- 必须认真对待反驳观点
- 证据可以是经验性的、理论性的或逻辑分析
- 最佳发表场所：ICML（立场轨道）、研讨会、TMLR

---

## Hermes Agent 集成 {#hermes-agent-integration}

本技能专为 Hermes Agent 设计。它利用 Hermes 的工具、委派、调度和记忆功能，覆盖完整的研究生命周期。

### 相关技能 {#related-skills}

将本技能与其他 Hermes 技能组合，用于特定阶段：

| 技能 | 使用时机 | 加载方式 |
|-------|-------------|-------------|
| **arxiv** | 阶段 1（文献综述）：搜索 arXiv、生成 BibTeX、通过 Semantic Scholar 查找相关论文 | `skill_view("arxiv")` |
| **subagent-driven-development** | 阶段 5（草稿撰写）：并行撰写章节，并经过两阶段审查（先检查规范符合性，再检查质量） | `skill_view("subagent-driven-development")` |
| **plan** | 阶段 0（准备）：在执行前创建结构化计划。写入 `.hermes/plans/` | `skill_view("plan")` |
| **qmd** | 阶段 1（文献）：通过混合 BM25+向量搜索，检索本地知识库（笔记、转录稿、文档） | 安装：`skill_manage("install", "qmd")` |
| **diagramming** | 阶段 4-5：创建基于 Excalidraw 的图形和架构图 | `skill_view("diagramming")` |
| **data-science** | 阶段 4（分析）：使用 Jupyter 实时内核进行交互式分析和可视化 | `skill_view("data-science")` |
**此技能已取代 `ml-paper-writing`** — 它包含了 ml-paper-writing 的全部内容，并新增了完整的实验/分析流程和自动推理方法。

### Hermes 工具参考 {#hermes-tools-reference}

| 工具 | 在此流程中的用途 |
|------|----------------------|
| **`terminal`** | LaTeX 编译（`latexmk -pdf`）、Git 操作、启动实验（`nohup python run.py &`）、进程检查 |
| **`process`** | 后台实验管理：`process("start", ...)`、`process("poll", pid)`、`process("log", pid)`、`process("kill", pid)` |
| **`execute_code`** | 运行 Python 进行引用验证、统计分析、数据聚合。通过 RPC 拥有工具访问权限。 |
| **`read_file`** / **`write_file`** / **`patch`** | 论文编辑、实验脚本、结果文件。使用 `patch` 对大型 .tex 文件进行针对性编辑。 |
| **`web_search`** | 文献发现：`web_search("transformer attention mechanism 2024")` |
| **`web_extract`** | 获取论文内容，验证引用：`web_extract("https://arxiv.org/abs/2303.17651")` |
| **`delegate_task`** | **并行章节起草** — 为每个章节生成独立的子 Agent。也用于并发引用验证。 |
| **`todo`** | 跨会话的主要状态跟踪器。每次阶段转换后更新。 |
| **`memory`** | 跨会话持久化关键决策：贡献框架、投稿场所、审稿人反馈。 |
| **`cronjob`** | 安排实验监控、截止日期倒计时、自动 arXiv 检查。 |
| **`clarify`** | 在遇到阻碍时向用户提出针对性问题（投稿场所、贡献框架）。 |
| **`send_message`** | 实验完成或草稿就绪时通知用户，即使用户不在聊天中。 |
### 工具使用模式 {#tool-usage-patterns}

**实验监控**（最常见）：
```
terminal("ps aux | grep <pattern>")
→ terminal("tail -30 <logfile>")
→ terminal("ls results/")
→ execute_code("分析结果 JSON，计算指标")
→ terminal("git add -A && git commit -m '<描述性消息>' && git push")
→ send_message("实验完成：<摘要>")
```

**并行章节起草**（使用委托）：
```
delegate_task("根据这些实验脚本和配置起草方法部分。内容包括：伪代码、所有超参数、足以复现的架构细节。使用 neurips2025 模板约定以 LaTeX 编写。")

delegate_task("起草相关工作部分。使用 web_search 和 web_extract 查找论文。通过 Semantic Scholar 验证每条引用。按方法论分组。")

delegate_task("起草实验部分。读取 results/ 中的所有结果文件。说明每个实验支持哪个主张。包含误差线和显著性。")
```

每个委托任务作为一个**全新的子 Agent** 运行，不共享上下文——在提示中提供所有必要信息。收集输出并进行整合。

**引用验证**（使用 execute_code）：
```python
# 在 execute_code 中：
from semanticscholar import SemanticScholar
import requests

sch = SemanticScholar()
results = sch.search_paper("attention mechanism transformers", limit=5)
for paper in results:
    doi = paper.externalIds.get('DOI', 'N/A')
    if doi != 'N/A':
        bibtex = requests.get(f"https://doi.org/{doi}", 
                              headers={"Accept": "application/x-bibtex"}).text
        print(bibtex)
```
### 使用 `memory` 和 `todo` 进行状态管理 {#state-management-with-memory-and-todo}

**`memory` 工具** — 持久化关键决策（限制：MEMORY.md 约 2200 字符）：

```
memory("add", "Paper: autoreason. Venue: NeurIPS 2025 (9 pages). 
  Contribution: structured refinement works when generation-evaluation gap is wide.
  Key results: Haiku 42/42, Sonnet 3/5, S4.6 constrained 2/3.
  Status: Phase 5 — drafting Methods section.")
```

在重大决策或阶段转换后更新 memory。该信息会在会话之间持久保存。

**`todo` 工具** — 跟踪细粒度进度：

```
todo("add", "Design constrained task experiments for Sonnet 4.6")
todo("add", "Run Haiku baseline comparison")
todo("add", "Draft Methods section")
todo("update", id=3, status="in_progress")
todo("update", id=1, status="completed")
```

**会话启动协议：**
```
1. todo("list")                           # 检查当前任务列表
2. memory("read")                         # 回忆关键决策
3. terminal("git log --oneline -10")      # 检查最近提交
4. terminal("ps aux | grep python")       # 检查正在运行的实验
5. terminal("ls results/ | tail -20")     # 检查新结果
6. 向用户报告状态，请求下一步方向
```

### 使用 `cronjob` 进行定时监控 {#cron-monitoring-with-cronjob}

使用 `cronjob` 工具安排定期实验检查：

```
cronjob("create", {
  "schedule": "*/30 * * * *",  # 每30分钟
  "prompt": "Check experiment status:
    1. ps aux | grep run_experiment
    2. tail -30 logs/experiment_haiku.log
    3. ls results/haiku_baselines/
    4. If complete: read results, compute Borda scores, 
       git add -A && git commit -m 'Add Haiku results' && git push
    5. Report: table of results, key finding, next step
    6. If nothing changed: respond with [SILENT]"
})
```
**[SILENT] 协议**：如果自上次检查以来没有任何变化，请仅回复 `[SILENT]`。这会抑制向用户发送通知。仅在存在值得了解的真正变化时才进行报告。

**截止日期跟踪**：
```
cronjob("create", {
  "schedule": "0 9 * * *",  # Daily at 9am
  "prompt": "NeurIPS 2025 deadline: May 22. Today is {date}. 
    Days remaining: {compute}. 
    Check todo list — are we on track? 
    If <7 days: warn user about remaining tasks."
})
```

### 通信模式 {#communication-patterns}

**何时通知用户**（通过 `send_message` 或直接回复）：
- 实验批次完成（附带结果表格）
- 出现需要决策的意外发现或失败
- 草稿章节准备就绪可供审阅
- 截止日期临近且任务未完成

**何时不通知**：
- 实验仍在运行，没有新结果 → `[SILENT]`
- 例行监控，无变化 → `[SILENT]`
- 不需要关注的中间步骤

**报告格式** — 始终包含结构化数据：
```
## Experiment: <name>
Status: Complete / Running / Failed

| Task | Method A | Method B | Method C |
|------|---------|---------|---------|
| Task 1 | 85.2 | 82.1 | **89.4** |

Key finding: <one sentence>
Next step: <what happens next>
```

### 需要人工输入的决策点 {#decision-points-requiring-human-input}

当确实遇到阻碍时，使用 `clarify` 提出针对性问题：

| 决策 | 何时询问 |
|----------|-------------|
| 目标会议 | 开始写论文前（影响页数限制、框架） |
| 贡献框架 | 存在多个合理框架时 |
| 实验优先级 | 待办列表中的实验超出时间允许范围时 |
| 提交就绪状态 | 最终提交前 |
**请勿询问**（主动决策，做出选择，标记问题）：
- 措辞选择、章节排序
- 具体突出哪些结果
- 引用完整性（根据已有内容起草，标注缺失）

---

## 审稿人评估标准 {#reviewer-evaluation-criteria}

了解审稿人的关注点有助于聚焦精力：

| 标准 | 审稿人检查内容 |
|-----------|----------------|
| **质量** | 技术可靠性、论点有充分依据、基线公平 |
| **清晰度** | 写作清晰、专家可复现、符号一致 |
| **重要性** | 社区影响力、推动认知进步 |
| **原创性** | 新见解（不要求必须是新方法） |

**评分（NeurIPS 6 分制）：**
- 6：强烈接收 — 开创性、无瑕疵
- 5：接收 — 技术扎实、影响力高
- 4：边缘接收 — 扎实但评估有限
- 3：边缘拒稿 — 缺点大于优点
- 2：拒稿 — 技术缺陷
- 1：强烈拒稿 — 已知结果或伦理问题

详细指南、常见问题及反驳策略请参见 [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md)。

---

## 常见问题与解决方案 {#common-issues-and-solutions}

| 问题 | 解决方案 |
|-------|----------|
| 摘要过于泛泛 | 如果第一句话可以套用在任何机器学习论文上，就删掉它。从你的具体贡献开始。 |
| 引言超过 1.5 页 | 将背景拆分到相关工作部分。把贡献要点前置。 |
| 实验缺乏明确主张 | 在每个实验前添加："本实验测试 [具体主张] 是否成立……" |
| 审稿人认为论文难以理解 | 增加路标指引，使用一致的术语，让图表标题自包含。 |
| 缺少统计显著性 | 添加误差线、运行次数、统计检验、置信区间。 |
| 实验范围失控 | 每个实验必须对应一个具体主张。砍掉不对应的实验。 |
| 论文被拒，需要重新提交 | 参见阶段 7 的会议重新投稿。回应审稿人意见时不要提及之前的审稿。 |
| 缺少更广泛影响声明 | 参见步骤 5.10。大多数会议要求此项。"没有负面影响"几乎不可信。 |
| 人工评估被认为薄弱 | 参见步骤 2.5 和 [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)。报告一致性指标、标注者详情、报酬。 |
| 审稿人质疑可复现性 | 发布代码（步骤 7.9），记录所有超参数，包含随机种子和计算细节。 |
| 理论论文缺乏直觉 | 在正式证明之前，用通俗语言添加证明草图。参见 [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。 |
| 结果为负/无效 | 参见阶段 4.3 关于处理负结果的内容。考虑投稿 workshop、TMLR，或重新框架化为分析性论文。 |
---

## 参考文档 {#reference-documents}

| 文档 | 内容 |
|----------|----------|
| [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) | Gopen & Swan 7 原则、Perez 微技巧、Lipton 用词选择、Steinhardt 精确性、图表设计 |
| [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md) | 引用 API、Python 代码、CitationManager 类、BibTeX 管理 |
| [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) | NeurIPS 16 项、ICML、ICLR、ACL 要求、通用投稿前检查清单 |
| [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) | 评审标准、评分、常见问题、反驳模板 |
| [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) | 所有写作指南、会议指南、API 的完整参考文献 |
| [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md) | 实验设计模式、评估协议、监控、错误恢复 |
| [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md) | Autoreason 循环、策略选择、模型指南、提示词、范围约束、Borda 评分 |
| [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md) | 人工评估设计、标注指南、一致性指标、众包质量控制、IRB 指导 |
| [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md) | 理论论文（证明写作、定理结构）、综述论文、基准论文、立场论文 |
### LaTeX 模板 {#latex-templates}

`templates/` 目录下的模板适用于：**NeurIPS 2025**、**ICML 2026**、**ICLR 2026**、**ACL**、**AAAI 2026**、**COLM 2025**。

编译说明请参见 [templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md)。

### 关键外部资源 {#key-external-sources}

**写作理念：**
- [Neel Nanda：如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar：如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen & Swan：科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton：科学写作的启发式方法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez：轻松论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/)

**API：** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**会议：** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)
