---
title: "Obliteratus — OBLITERATUS: 消除大语言模型的拒绝行为（均值差异法）"
sidebar_label: "Obliteratus"
description: "OBLITERATUS: 消除大语言模型的拒绝行为（均值差异法）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="obliteratus"></a>
# Obliteratus

OBLITERATUS: 消除大语言模型的拒绝行为（均值差异法）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/obliteratus` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 依赖项 | `obliteratus`, `torch`, `transformers`, `bitsandbytes`, `accelerate`, `safetensors` |
| 支持平台 | linux, macos |
| 标签 | `Abliteration`, `Uncensoring`, `Refusal-Removal`, `LLM`, `Weight-Projection`, `SVD`, `Mechanistic-Interpretability`, `HuggingFace`, `Model-Surgery` |
| 相关技能 | `vllm`, `gguf`, [`huggingface-tokenizers`](/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="obliteratus-skill"></a>
# OBLITERATUS 技能

<a id="what-s-inside"></a>
## 内部包含什么

9 个 CLI 方法、28 个分析模块、横跨 5 个计算层级的 116 个模型预设、锦标赛评估以及遥测驱动的推荐。

无需重新训练或微调，即可从开放权重的大语言模型中移除拒绝行为（护栏）。它利用机制可解释性技术——包括均值差异法、SVD、白化 SVD、LEACE 概念擦除、SAE 分解、贝叶斯核投影等——来识别并精确地从模型权重中切除拒绝方向，同时保留推理能力。

**许可证警告：** OBLITERATUS 采用 AGPL-3.0 许可证。切勿将其作为 Python 库导入。始终通过 CLI（`obliteratus` 命令）或子进程调用。这可以保持 Hermes Agent 的 MIT 许可证纯净。

<a id="video-guide"></a>
## 视频指南

Hermes Agent 使用 OBLITERATUS 消除 Gemma 拒绝行为的完整演示：
https://www.youtube.com/watch?v=8fG9BrNTeHs（"OBLITERATUS: 一个 AI Agent 移除了 Gemma 4 的安全护栏"）

当用户希望在亲自运行之前对整个工作流程有一个直观了解时，这个视频会很有用。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

在以下情况下触发：
- 用户想要“解除审查”或“消除”一个大语言模型
- 用户询问如何移除模型的拒绝/护栏行为
- 用户想要创建 Llama、Qwen、Mistral 等模型的未审查版本
- 用户提到“拒绝行为移除”、“消除”、“权重投影”
- 用户想要分析模型的拒绝机制是如何工作的
- 用户引用了 OBLITERATUS、abliterator 或拒绝方向

<a id="step-1-installation"></a>
## 第一步：安装

检查是否已安装：
```bash
obliteratus --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

如果未安装，从 GitHub 克隆并安装：
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
pip install -e .
# 如需 Gradio 网页界面支持：
# pip install -e ".[spaces]"
```

**重要提示：** 安装前需征得用户确认。这会拉取约 5-10GB 的依赖项（PyTorch、Transformers、bitsandbytes 等）。

<a id="step-2-check-hardware"></a>
## 第二步：检查硬件
在开始之前，先检查可用的 GPU：

```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('TIER: tiny (models under 1B)')
    elif vram < 8: print('TIER: small (models 1-4B)')
    elif vram < 16: print('TIER: medium (models 4-9B with 4bit quant)')
    elif vram < 32: print('TIER: large (models 8-32B with 4bit quant)')
    else: print('TIER: frontier (models 32B+)')
else:
    print('NO GPU - only tiny models (under 1B) on CPU')
"
```

<a id="vram-requirements-with-4-bit-quantization"></a>
### VRAM 需求（使用 4-bit 量化）

| VRAM     | 最大模型大小 | 示例模型                            |
|:---------|:-------------|:-----------------------------------|
| 仅 CPU   | ~1B 参数     | GPT-2, TinyLlama, SmolLM           |
| 4-8 GB   | ~4B 参数     | Qwen2.5-1.5B, Phi-3.5 mini, Llama 3.2 3B |
| 8-16 GB  | ~9B 参数     | Llama 3.1 8B, Mistral 7B, Gemma 2 9B      |
| 24 GB    | ~32B 参数    | Qwen3-32B, Llama 3.1 70B（紧张）, Command-R |
| 48 GB+   | ~72B+ 参数   | Qwen2.5-72B, DeepSeek-R1             |
| 多 GPU   | 200B+ 参数   | Llama 3.1 405B, DeepSeek-V3 (685B MoE) |

<a id="step-3-browse-available-models-get-recommendations"></a>
## 第 3 步：浏览可用模型并获取推荐

```bash
# 按计算层级浏览模型
obliteratus models --tier medium

# 获取特定模型的架构信息
obliteratus info <model_name>

# 获取基于遥测数据的最佳方法及参数推荐
obliteratus recommend <model_name>
obliteratus recommend <model_name> --insights  # 全局跨架构排名
```

<a id="step-4-choose-a-method"></a>
## 第 4 步：选择方法

<a id="method-selection-guide"></a>
### 方法选择指南
**默认 / 大多数情况推荐使用 `advanced`。** 它采用多方向 SVD 结合保范投影，经过充分测试。

| 情况                           | 推荐方法     | 理由                                       |
|:-------------------------------|:-------------|:-------------------------------------------|
| 默认 / 大多数模型               | `advanced`   | 多方向 SVD，保范，可靠                      |
| 快速测试 / 原型开发              | `basic`      | 快速、简单，足以评估效果                     |
| 密集模型（Llama, Mistral）      | `advanced`   | 多方向，保范                                |
| MoE 模型（DeepSeek, Mixtral）   | `nuclear`    | 专家粒度，处理 MoE 复杂性                    |
| 推理模型（R1 蒸馏版）            | `surgical`   | 考虑 CoT，保留思维链                        |
| 持续顽固拒绝回答                | `aggressive` | 白化 SVD + 头部分手术 + 越狱                |
| 希望可逆的改动                  | 使用转向向量（参见分析章节）|
| 追求极致质量，不介意时间         | `optimized`  | 贝叶斯搜索最佳参数                          |
| 实验性自动检测                  | `informed`   | 自动检测对齐类型——实验性，不一定总是优于 `advanced` |
<a id="9-cli-methods"></a>
### 9 种 CLI 方法
- **basic** — 通过均值差异实现单一拒绝方向。速度快（8B 模型约 5-10 分钟）。
- **advanced**（默认，推荐）— 多 SVD 方向、保范投影、2 次精炼迭代。速度中等（约 10-20 分钟）。
- **aggressive** — 白化 SVD + 越狱对比 + 注意力头手术。导致连贯性受损的风险较高。
- **spectral_cascade** — DCT 频域分解。研究/新颖方法。
- **informed** — 在 abliteration 过程中运行分析以自动配置。实验性 — 比 advanced 慢且可预测性较低。
- **surgical** — SAE 特征 + 神经元掩码 + 头手术 + 逐专家处理。非常慢（约 1-2 小时）。最适合推理模型。
- **optimized** — 贝叶斯超参数搜索（Optuna TPE）。运行时间最长，但能找到最优参数。
- **inverted** — 翻转拒绝方向。模型变得主动愿意。
- **nuclear** — 针对顽固 MoE 模型的最大力度组合。专家粒度。

<a id="direction-extraction-methods-direction-method-flag"></a>
### 方向提取方法（--direction-method 标志）
- **diff_means**（默认）— 拒绝/顺从激活之间的简单均值差异。鲁棒。
- **svd** — 多方向 SVD 提取。更适合复杂对齐。
- **leace** — LEACE（通过闭式估计进行线性擦除）。最优线性擦除。

<a id="4-python-api-only-methods"></a>
### 4 种仅限 Python API 的方法
（CLI 不可用 — 需要 Python 导入，这违反了 AGPL 边界。仅当用户明确希望在其自己的 AGPL 项目中将 OBLITERATUS 作为库使用时才提及。）
- failspy, gabliteration, heretic, rdo

<a id="step-5-run-abliteration"></a>
## 第 5 步：运行 Abliteration

<a id="standard-usage"></a>
### 标准用法
```bash
# 默认方法（advanced）— 推荐用于大多数模型
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models

# 使用 4 位量化（节省 VRAM）
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models

# 大型模型（70B+）— 保守默认值
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

<a id="fine-tuning-parameters"></a>
### 微调参数
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # 选择加入遥测以支持社区研究
```

<a id="key-flags"></a>
### 关键标志
| 标志 | 描述 | 默认值 |
|:-----|:------------|:--------|
| `--method` | Abliteration 方法 | advanced |
| `--direction-method` | 方向提取 | diff_means |
| `--n-directions` | 拒绝方向数量（1-32） | 取决于方法 |
| `--refinement-passes` | 迭代次数（1-5） | 2 |
| `--regularization` | 正则化强度（0.0-1.0） | 0.1 |
| `--quantization` | 以 4bit 或 8bit 加载 | 无（全精度） |
| `--large-model` | 针对 120B+ 模型的保守默认值 | false |
| `--output-dir` | 保存 abliterated 模型的目录 | ./obliterated_model |
| `--contribute` | 共享匿名结果以支持研究 | false |
| `--verify-sample-size` | 用于拒绝检查的测试提示数量 | 20 |
| `--dtype` | 模型数据类型（float16, bfloat16） | auto |
<a id="other-execution-modes"></a>
### 其他执行模式
```bash
# 交互式引导模式（硬件 → 模型 → 预设）
obliteratus interactive

# Web UI（Gradio）
obliteratus ui --port 7860

# 从 YAML 配置运行完整消融研究
obliteratus run config.yaml --preset quick

# 锦标赛：所有方法相互对抗
obliteratus tourney <model_name>
```

<a id="step-6-verify-results"></a>
## 步骤 6：验证结果

消融后，检查输出指标：

| 指标 | 良好值 | 警告 |
|:-------|:-----------|:--------|
| 拒绝率 | < 5%（理想情况下 ~0%） | > 10% 表示拒绝仍存在 |
| 困惑度变化 | < 10% 增加 | > 15% 表示连贯性受损 |
| KL 散度 | < 0.1 | > 0.5 表示显著分布偏移 |
| 连贯性 | 高 / 通过定性检查 | 响应质量下降、重复 |

<a id="if-refusals-persist-10"></a>
### 如果拒绝率仍高（> 10%）
1. 尝试使用 `aggressive` 方法
2. 增加 `--n-directions`（例如 8 或 16）
3. 添加 `--refinement-passes 3`
4. 尝试使用 `--direction-method svd` 替代 diff_means

<a id="if-coherence-is-damaged-perplexity-15-increase"></a>
### 如果连贯性受损（困惑度增加 > 15%）
1. 减少 `--n-directions`（尝试 2）
2. 增加 `--regularization`（尝试 0.3）
3. 将 `--refinement-passes` 减少到 1
4. 尝试使用 `basic` 方法（更温和）

<a id="step-7-use-the-abliterated-model"></a>
## 步骤 7：使用消融后的模型

输出是一个标准的 HuggingFace 模型目录。

```bash
# 使用 transformers 本地测试
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('How do I pick a lock?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# 上传到 HuggingFace Hub
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# 使用 vLLM 提供服务
vllm serve ./abliterated-models/<model>
```

<a id="cli-command-reference"></a>
## CLI 命令参考

| 命令 | 描述 |
|:--------|:------------|
| `obliteratus obliterate` | 主要消融命令 |
| `obliteratus info &lt;model&gt;` | 打印模型架构详细信息 |
| `obliteratus models --tier &lt;tier&gt;` | 按计算层级浏览精选模型 |
| `obliteratus recommend &lt;model&gt;` | 基于遥测数据的方法/参数建议 |
| `obliteratus interactive` | 引导式设置向导 |
| `obliteratus tourney &lt;model&gt;` | 锦标赛：所有方法正面交锋 |
| `obliteratus run &lt;config.yaml&gt;` | 从 YAML 执行消融研究 |
| `obliteratus strategies` | 列出所有注册的消融策略 |
| `obliteratus report &lt;results.json&gt;` | 重新生成可视化报告 |
| `obliteratus ui` | 启动 Gradio Web 界面 |
| `obliteratus aggregate` | 汇总社区遥测数据 |

<a id="analysis-modules"></a>
## 分析模块

OBLITERATUS 包含 28 个用于机制可解释性的分析模块。
请参阅 `skill_view(name="obliteratus", file_path="references/analysis-modules.md")` 获取完整参考。

<a id="quick-analysis-commands"></a>
### 快速分析命令
```bash
# 运行特定分析模块
obliteratus run analysis-config.yaml --preset quick

# 首先运行的关键模块：
# - alignment_imprint：指纹识别 DPO/RLHF/CAI/SFT 对齐方法
# - concept_geometry：单方向 vs 多面体锥
# - logit_lens：决定拒绝的层
# - anti_ouroboros：自我修复风险评分
# - causal_tracing：因果必要性组件
```
<a id="steering-vectors-reversible-alternative"></a>
### 引导向量（可逆替代方案）
无需永久修改权重，使用推理时向量引导：
```python
# 仅限 Python API — 用于用户自己的项目
from obliteratus.analysis.steering_vectors import SteeringVectorFactory, SteeringHookManager
```

<a id="ablation-strategies"></a>
## 消融策略

除了基于方向的消融（abliteration），OBLITERATUS 还包含结构性消融策略：
- **嵌入层消融** — 针对嵌入层组件
- **FFN 消融** — 移除前馈网络块
- **头剪枝** — 注意力头剪枝
- **层移除** — 完整层移除

列出所有可用策略：`obliteratus strategies`

<a id="evaluation"></a>
## 评估

OBLITERATUS 内置了评估工具：
- 拒绝率基准测试
- 困惑度对比（消融前后）
- LM Eval Harness 集成，用于学术基准测试
- 与竞品的直接对比
- 基线性能追踪

<a id="platform-support"></a>
## 平台支持

- **CUDA** — 完全支持（NVIDIA GPU）
- **Apple Silicon（MLX）** — 通过 MLX 后端支持
- **CPU** — 支持小模型（< 1B 参数）

<a id="yaml-config-templates"></a>
## YAML 配置模板

通过 `skill_view` 加载可复现运行的模板：
- `templates/abliteration-config.yaml` — 标准单模型配置
- `templates/analysis-study.yaml` — 消融前分析研究
- `templates/batch-abliteration.yaml` — 多模型批处理

<a id="telemetry"></a>
## 遥测

OBLITERATUS 可选择性地将匿名运行数据贡献给全球研究数据集。
使用 `--contribute` 标志启用。不收集任何个人数据——仅包含模型名称、方法、指标。

<a id="common-pitfalls"></a>
## 常见陷阱

1. **不要将 `informed` 设为默认** — 该方法是实验性的且速度较慢。对于可靠结果应使用 `advanced`。
2. **约 1B 以下的模型对消融反应不佳** — 它们的拒绝行为浅显且碎片化，难以提取清晰的方向。预期只能获得部分结果（仍有 20-40% 的拒绝）。3B 以上的模型具有更清晰的拒绝方向，反应会好得多（使用 `advanced` 通常可实现 0% 拒绝）。
3. **`aggressive` 可能让情况更糟** — 在小模型上会破坏连贯性，甚至提高拒绝率。仅在 3B 以上模型使用 `advanced` 后拒绝率仍高于 10% 时使用。
4. **始终检查困惑度** — 如果困惑度飙升超过 15%，说明模型已受损。请降低激进程度。
5. **MoE 模型需要特殊处理** — 对 Mixtral、DeepSeek-MoE 等模型使用 `nuclear` 方法。
6. **量化模型无法再次量化** — 先对全精度模型进行消融，然后再对输出进行量化。
7. **VRAM 估算为近似值** — 4-bit 量化有帮助，但峰值用量可能在提取过程中飙升。
8. **推理模型很敏感** — 对 R1 蒸馏模型使用 `surgical` 以保留思维链。
9. **检查 `obliteratus recommend`** — 遥测数据可能包含比默认值更优的参数。
10. **AGPL 许可证** — 切勿在 MIT/Apache 项目中 `import obliteratus`。仅限 CLI 调用。
11. **大模型（70B+）** — 始终使用 `--large-model` 标志以采用保守默认值。
12. **频谱认证显示 RED 很常见** — 即使实际拒绝率为 0%，频谱检查也常标记为“不完整”。应检查实际拒绝率，而非仅依赖频谱认证。
<a id="complementary-skills"></a>
## Complementary Skills

- **vllm** — 以高吞吐量服务 abliterated models
- **gguf** — 将 abliterated models 转换为适用于 llama.cpp 的 GGUF 格式
- **huggingface-tokenizers** — 处理模型分词器
