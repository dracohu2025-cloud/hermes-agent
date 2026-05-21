---
title: "Darwinian Evolver — 使用 Imbue 的进化循环来进化提示词/正则表达式/SQL/代码"
sidebar_label: "Darwinian Evolver"
description: "使用 Imbue 的进化循环来进化提示词/正则表达式/SQL/代码"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="darwinian-evolver"></a>
# Darwinian Evolver

使用 Imbue 的进化循环来进化提示词/正则表达式/SQL/代码。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/research/darwinian-evolver` 安装 |
| 路径 | `optional-skills/research/darwinian-evolver` |
| 版本 | `0.1.0` |
| 作者 | Bihruze (Asahi0x), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `evolution`, `optimization`, `prompt-engineering`, `research` |
| 相关技能 | [`arxiv`](/user-guide/skills/bundled/research/research-arxiv), [`jupyter-live-kernel`](/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
下面是 Hermes 在该技能被触发时加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

# Darwinian Evolver

运行 Imbue 的 [darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) —— 一个由 LLM 驱动的进化搜索循环 —— 以针对**适应度函数**优化**提示词、正则表达式、SQL 查询或小型代码片段**。

状态：对上游工具的轻薄封装。该技能会安装它，引导 Agent 编写一个 `Problem` 定义（organism + evaluator + mutator），并通过上游 CLI 或一个小型自定义 Python 驱动程序驱动循环。

**许可证：** 上游工具是 **AGPL-3.0**。该技能仅通过上游 CLI 或 `subprocess`/`uv run` 调用（纯粹的聚合）来调用它。请勿将上游类导入 Hermes 本身。

<a id="when-to-use"></a>
## 使用时机

- 用户说“优化这个提示词”、“进化一个用于 X 的正则表达式”、“自动改进这段代码/SQL”、“搜索更好的指令”。
- 你有一个评分器（精确匹配、正则通过率、单元测试、LLM 判断、运行时指标） 以及一个初始候选（organism）。如果没有评分器，请先停下来定义一个——这才是最困难的部分。
- 成本可接受：一次典型运行需要 50–500 次 LLM 调用。在 gpt-4o-mini 上只需几分钱；在 Claude Sonnet 上可能花费几美元。

**不要**在以下情况下使用：
- 优化目标可微分（请使用梯度下降 / DSPy）。
- 你只需要尝试 2–3 个变体——直接手动编写即可。
- 适应度信号纯粹是主观的，没有可衡量的标准。

<a id="prerequisites"></a>
## 先决条件

- Python ≥3.11
- `git`、`uv`（或 `pip`）
- 以下之一：`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY`

该技能附带了一个小型 `parrot_openrouter.py` 驱动程序，通过 OpenAI SDK 使用 `OPENROUTER_API_KEY`，因此 OpenRouter 上的任何模型都可以工作。上游 CLI 本身硬编码了 Anthropic，需要 `ANTHROPIC_API_KEY`。

<a id="install-one-time"></a>
## 安装（一次性）

通过 `terminal` 工具运行：

```bash
mkdir -p ~/.hermes/cache/darwinian-evolver && cd ~/.hermes/cache/darwinian-evolver
[ -d darwinian_evolver ] || git clone --depth 1 https://github.com/imbue-ai/darwinian_evolver.git
cd darwinian_evolver && uv sync
```
验证：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver \
  && uv run darwinian_evolver --help | head -5
```

<a id="quick-start-the-built-in-parrot-example"></a>
## 快速入门 — 内置的 Parrot 示例

小型冒烟测试（需要 `ANTHROPIC_API_KEY`）：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver
uv run darwinian_evolver parrot \
  --num_iterations 2 \
  --num_parents_per_iteration 2 \
  --mutator_concurrency 2 --evaluator_concurrency 2 \
  --output_dir /tmp/parrot_demo
```

输出：
- `/tmp/parrot_demo/snapshots/iteration_N.pkl` — 每轮迭代的 pickle 格式种群
- `/tmp/parrot_demo/&lt;jsonl&gt;` — 每轮迭代的 JSON 日志（路径会在末尾打印）

在浏览器中打开 `~/.hermes/cache/darwinian-evolver/darwinian_evolver/darwinian_evolver/lineage_visualizer.html` 并加载 JSON 日志，即可查看进化树。

<a id="quick-start-openrouter-driver-no-anthropic-key"></a>
## 快速入门 — OpenRouter 驱动（无需 Anthropic 密钥）

技能附带 `scripts/parrot_openrouter.py` — 与 parrot 问题相同，但 LLM 调用通过 OpenRouter，因此任何提供商都能工作。

```bash
# 无论技能安装在哪里：
SKILL_DIR=~/.hermes/skills/research/darwinian-evolver
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver

cd "$DE_DIR" && \
  EVOLVER_MODEL='openai/gpt-4o-mini' \
  uv run --with openai python "$SKILL_DIR/scripts/parrot_openrouter.py" \
    --num_iterations 3 --num_parents_per_iteration 2 \
    --output_dir /tmp/parrot_or
```

使用 `scripts/show_snapshot.py` 查看结果：

```bash
uv run --with openai python "$SKILL_DIR/scripts/show_snapshot.py" \
  /tmp/parrot_or/snapshots/iteration_3.pkl
```

预期输出：7 个按分数排序的进化提示模板，最佳得分在 0.6–0.8 左右（种子 `Say {{ phrase }}` 得分为 0.000）。

<a id="defining-a-custom-problem"></a>
## 定义自定义问题

技能附带 `templates/custom_problem_template.py` — 复制、编辑、运行。你需要定义三样东西：

1. **`Organism`** — 一个 Pydantic `BaseModel` 子类，保存正在进化的工件（`prompt_template: str`、`regex_pattern: str`、`sql_query: str`、`code_block: str` 等）。添加一个 `run(*args)` 方法来运行它。

2. **`Evaluator`** — `.evaluate(organism) -> EvaluationResult(score=..., trainable_failure_cases=[...], holdout_failure_cases=[...], is_viable=True)`。
   - **`score`** 在 `[0, 1]` 之间，数值越高越好。
   - **`trainable_failure_cases`** — 变异器看到的内容。包含足够的上下文（输入、期望、实际）供 LLM 诊断。
   - **`holdout_failure_cases`** — 不让变异器看到。用于检测过拟合。
   - **`is_viable=True`** — 除非 Organism 完全损坏（引发异常、返回 None 等），否则保持 `True`。一个得分为 0 的可行 Organism 是没问题的——它在父体选择时权重会降低。

3. **`Mutator`** — `.mutate(organism, failure_cases, learning_log_entries) -> list[Organism]`。
   通常做法：构建一个 LLM 提示，包含当前 Organism + 一个失败案例 + 要求提出修复方案；解析 LLM 的响应；返回一个新的 `Organism`。如果解析失败则返回 `[]` — 循环会处理这种情况。
然后编写一个驱动脚本，将 `Problem(initial_organism, evaluator, [mutators])` 接入 `EvolveProblemLoop`，并迭代执行 `loop.run(num_iterations=N)` —— 附带的 `scripts/parrot_openrouter.py` 可作为参考。

<a id="hyperparameters-that-actually-matter"></a>
## 真正重要的超参数

| 参数 | 默认值 | 何时调整 |
|---|---|---|
| `--num_iterations` | 5 | 当你信任评估器后，可提升至 10–20 |
| `--num_parents_per_iteration` | 4 | 为了低成本探索，可降至 2 |
| `--mutator_concurrency` | 10 | 为避免速率限制，可降至 2–4 |
| `--evaluator_concurrency` | 10 | 同理；评估器也会调用 LLM |
| `--batch_size` | 1 | 当你的 mutator 能处理多个失败时，可提升至 3–5 |
| `--verify_mutations` | 关闭 | 当 mutator 变得低效时开启（根据 Imbue 的经验，后续运行可节省 10 倍以上成本） |
| `--midpoint_score` | `p75` | 除非分数过于集中，否则保持默认 |
| `--sharpness` | 10 | 保持默认 |

<a id="pitfalls"></a>
## 常见陷阱

1. **`初始生物必须可存活`** —— 即使种子得分为 0，也要在 `EvaluationResult` 中设置 `is_viable=True`。循环会拒绝不可存活的生物，因为这意味着循环没有可进化的起点。
2. **提供者的内容过滤器会中断运行。** 基于 Azure 的 OpenRouter 模型会拒绝包含 "ignore previous instructions" 等短语的请求，并返回 HTTP 400。请将 LLM 调用包裹在 `try/except` 中，并返回 `f"&lt;LLM_ERROR: {e}&gt;"` —— 进化器会将该生物评分为 0 并继续运行。
3. **`loop.run()` 是一个生成器** —— 调用它不会立即执行任何操作，直到你开始迭代。请使用 `for snap in loop.run(num_iterations=N):`。
4. **快照是嵌套的 pickle 文件。** `iteration_N.pkl` 包含一个字典，其中包含 `population_snapshot`（更多 pickle 字节）。要解 pickle，你必须确保 `Organism` 类在与其被 pickle 时相同的点分路径下可导入。
5. **并发默认值过于激进。** 10/10 的并发设置会在大多数提供者上触发速率限制。建议从 2/2 开始。
6. **CLI 硬编码为 Anthropic。** `uv run darwinian_evolver &lt;problem&gt;` 会查找 `ANTHROPIC_API_KEY` 并使用 Claude Sonnet。要使用其他提供者，请编写类似 `parrot_openrouter.py` 的驱动脚本。
7. **AGPL 许可证。** 切勿在 Hermes 核心内部使用 `from darwinian_evolver import ...`。位于 `~/.hermes/skills/...` 下的自定义驱动脚本属于用户侧，没有问题。
8. **没有 PyPI 包。** `pip install darwinian-evolver` 会安装错误的内容。请始终从 GitHub 仓库安装。

<a id="verification"></a>
## 验证

安装并完成一次 parrot 运行后，以下命令返回退出码 0 即表示验证通过：

```bash
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver
ls "$DE_DIR/darwinian_evolver/lineage_visualizer.html" >/dev/null && \
cd "$DE_DIR" && uv run darwinian_evolver --help >/dev/null && \
echo "darwinian-evolver: OK"
```

<a id="references"></a>
## 参考资料

- [Imbue 研究文章](https://imbue.com/research/2026-02-27-darwinian-evolver/)
- [ARC-AGI-2 结果](https://imbue.com/research/2026-02-27-arc-agi-2-evolution/)
- [imbue-ai/darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) (AGPL-3.0)
- [Darwin Gödel Machines](https://arxiv.org/abs/2505.22954)
- [PromptBreeder](https://arxiv.org/abs/2309.16797)
