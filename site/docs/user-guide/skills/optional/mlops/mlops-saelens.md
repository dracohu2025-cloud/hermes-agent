---
title: "稀疏自编码器训练"
sidebar_label: "稀疏自编码器训练"
description: "提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指南，将神经网络激活分解为可解释的特征"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="sparse-autoencoder-training"></a>
# 稀疏自编码器训练

提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指南，将神经网络激活分解为可解释的特征。在发现可解释特征、分析叠加或研究语言模型中的单一语义表示时使用。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/saelens` 安装 |
| 路径 | `optional-skills/mlops/saelens` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `sae-lens>=6.0.0`, `transformer-lens>=2.0.0`, `torch>=2.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `稀疏自编码器`, `SAE`, `机制可解释性`, `特征发现`, `叠加` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。即技能激活后 Agent 所看到的指令。
:::

<a id="saelens-sparse-autoencoders-for-mechanistic-interpretability"></a>
# SAELens：用于机制可解释性的稀疏自编码器

SAELens 是训练和分析稀疏自编码器（SAE）的主要库——这是一种将多语义神经网络激活分解为稀疏、可解释特征的技术。基于 Anthropic 在单一语义性方面的开创性研究。

**GitHub**：[jbloomAus/SAELens](https://github.com/jbloomAus/SAELens)（1100+ 星标）

<a id="the-problem-polysemanticity-superposition"></a>
## 问题：多语义性与叠加

神经网络中的单个神经元是**多语义的**——它们会在多个语义不同的上下文中激活。这是因为模型利用**叠加**来表示比神经元数量更多的特征，这使得可解释性变得困难。

**SAE 解决了这个问题**，它将稠密激活分解为稀疏、单一语义的特征——通常对于任何给定输入，只有少量特征被激活，且每个特征对应一个可解释的概念。

<a id="when-to-use-saelens"></a>
## 何时使用 SAELens

**在以下场景使用 SAELens：**
- 发现模型激活中的可解释特征
- 理解模型学到的概念
- 研究叠加和特征几何
- 执行基于特征的引导或消融
- 分析与安全相关的特征（欺骗、偏见、有害内容）

**在以下场景考虑替代方案：**
- 需要基本的激活分析 → 直接使用 **TransformerLens**
- 进行因果干预实验 → 使用 **pyvene** 或 **TransformerLens**
- 需要生产级引导 → 考虑直接激活工程

<a id="installation"></a>
## 安装

```bash
pip install sae-lens
```

要求：Python 3.10+、transformer-lens>=2.0.0

<a id="core-concepts"></a>
## 核心概念

<a id="what-saes-learn"></a>
### SAE 学到了什么

SAE 通过稀疏瓶颈来训练重建模型激活：

```
输入激活 → 编码器 → 稀疏特征 → 解码器 → 重建激活
 (d_model)       ↓       (d_sae >> d_model)    ↓       (d_model)
              稀疏性惩罚                  重建损失
```
**Loss Function**: `MSE(original, reconstructed) + L1_coefficient × L1(features)`

<a id="key-validation-anthropic-research"></a>
### 关键验证（Anthropic Research）

在《Towards Monosemanticity》中，人类评估者发现 **70% 的 SAE 特征确实可解释**。发现的特征包括：
- DNA 序列、法律语言、HTTP 请求
- 希伯来文本、营养声明、代码语法
- 情感、命名实体、语法结构

<a id="workflow-1-loading-and-analyzing-pre-trained-saes"></a>
## Workflow 1: 加载并分析预训练 SAE

<a id="step-by-step"></a>
### 分步操作

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE

# 1. 加载模型和预训练 SAE
model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

# 2. 获取模型激活值
tokens = model.to_tokens("The capital of France is Paris")
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]  # [batch, pos, d_model]

# 3. 编码为 SAE 特征
sae_features = sae.encode(activations)  # [batch, pos, d_sae]
print(f"激活的特征数量: {(sae_features > 0).sum()}")

# 4. 找出每个位置的最强特征
for pos in range(tokens.shape[1]):
    top_features = sae_features[0, pos].topk(5)
    token = model.to_str_tokens(tokens[0, pos:pos+1])[0]
    print(f"Token '{token}': features {top_features.indices.tolist()}")

# 5. 重建激活值
reconstructed = sae.decode(sae_features)
reconstruction_error = (activations - reconstructed).norm()
```

<a id="available-pre-trained-saes"></a>
### 可用的预训练 SAE

| Release | Model | Layers |
|---------|-------|--------|
| `gpt2-small-res-jb` | GPT-2 Small | 多个残差流 |
| `gemma-2b-res` | Gemma 2B | 残差流 |
| HuggingFace 上的其他模型 | 搜索标签 `saelens` | 多种 |

<a id="checklist"></a>
### 检查清单
- [ ] 使用 TransformerLens 加载模型
- [ ] 加载与目标层匹配的 SAE
- [ ] 将激活值编码为稀疏特征
- [ ] 识别每个 token 的最强激活特征
- [ ] 验证重建质量

<a id="workflow-2-training-a-custom-sae"></a>
## Workflow 2: 训练自定义 SAE

### 分步操作

```python
from sae_lens import SAE, LanguageModelSAERunnerConfig, SAETrainingRunner

# 1. 配置训练
cfg = LanguageModelSAERunnerConfig(
    # 模型
    model_name="gpt2-small",
    hook_name="blocks.8.hook_resid_pre",
    hook_layer=8,
    d_in=768,  # 模型维度

    # SAE 架构
    architecture="standard",  # 或 "gated", "topk"
    d_sae=768 * 8,  # 扩展因子 8
    activation_fn="relu",

    # 训练
    lr=4e-4,
    l1_coefficient=8e-5,  # 稀疏性惩罚
    l1_warm_up_steps=1000,
    train_batch_size_tokens=4096,
    training_tokens=100_000_000,

    # 数据
    dataset_path="monology/pile-uncopyrighted",
    context_size=128,

    # 日志
    log_to_wandb=True,
    wandb_project="sae-training",

    # 检查点
    checkpoint_path="checkpoints",
    n_checkpoints=5,
)

# 2. 训练
trainer = SAETrainingRunner(cfg)
sae = trainer.run()

# 3. 评估
print(f"L0（平均激活特征数）: {trainer.metrics['l0']}")
print(f"CE Loss Recovered: {trainer.metrics['ce_loss_score']}")
```
<a id="key-hyperparameters"></a>
### 关键超参数

| 参数 | 典型值 | 效果 |
|-----------|---------------|--------|
| `d_sae` | 4-16× d_model | 更多特征，更高容量 |
| `l1_coefficient` | 5e-5 至 1e-4 | 值越大越稀疏，但精度下降 |
| `lr` | 1e-4 至 1e-3 | 标准优化器学习率 |
| `l1_warm_up_steps` | 500-2000 | 防止早期特征死亡 |

<a id="evaluation-metrics"></a>
### 评估指标

| 指标 | 目标值 | 含义 |
|--------|--------|------|
| **L0** | 50-200 | 每个 token 的平均激活特征数 |
| **CE Loss Score** | 80-95% | 恢复的交叉熵与原始交叉熵之比 |
| **Dead Features** | &lt;5% | 从未激活的特征占比 |
| **Explained Variance** | >90% | 重建质量 |

<a id="checklist"></a>
### 检查清单
- [ ] 选择目标层和钩子点
- [ ] 设置扩展系数（d_sae = 4-16× d_model）
- [ ] 调整 L1 系数以达到期望的稀疏度
- [ ] 启用 L1 warm-up 以防止特征死亡
- [ ] 训练期间监控指标（W&B）
- [ ] 验证 L0 和 CE Loss 恢复情况
- [ ] 检查死亡特征比例

<a id="workflow-3-feature-analysis-and-steering"></a>
## 工作流 3：特征分析与引导

<a id="analyzing-individual-features"></a>
### 分析单个特征

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE
import torch

model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae, _, _ = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

# 找出什么会激活特定特征
feature_idx = 1234
test_texts = [
    "The scientist conducted an experiment",
    "I love chocolate cake",
    "The code compiles successfully",
    "Paris is beautiful in spring",
]

for text in test_texts:
    tokens = model.to_tokens(text)
    _, cache = model.run_with_cache(tokens)
    features = sae.encode(cache["resid_pre", 8])
    activation = features[0, :, feature_idx].max().item()
    print(f"{activation:.3f}: {text}")
```

<a id="feature-steering"></a>
### 特征引导

```python
def steer_with_feature(model, sae, prompt, feature_idx, strength=5.0):
    """将 SAE 特征方向添加到残差流中。"""
    tokens = model.to_tokens(prompt)

    # 从解码器获取特征方向
    feature_direction = sae.W_dec[feature_idx]  # [d_model]

    def steering_hook(activation, hook):
        # 在所有位置添加缩放后的特征方向
        activation += strength * feature_direction
        return activation

    # 使用引导进行生成
    output = model.generate(
        tokens,
        max_new_tokens=50,
        fwd_hooks=[("blocks.8.hook_resid_pre", steering_hook)]
    )
    return model.to_string(output[0])
```

<a id="feature-attribution"></a>
### 特征归因

```python
# 哪些特征对特定输出影响最大？
tokens = model.to_tokens("The capital of France is")
_, cache = model.run_with_cache(tokens)

# 获取最后一个位置的特征
features = sae.encode(cache["resid_pre", 8])[0, -1]  # [d_sae]

# 获取每个特征的 logit 归因
# 特征贡献 = 特征激活值 × 解码器权重 × 反嵌入
W_dec = sae.W_dec  # [d_sae, d_model]
W_U = model.W_U    # [d_model, vocab]

# 对 "Paris" 这个 logit 的贡献
paris_token = model.to_single_token(" Paris")
feature_contributions = features * (W_dec @ W_U[:, paris_token])

top_features = feature_contributions.topk(10)
print("预测 'Paris' 的 top 特征：")
for idx, val in zip(top_features.indices, top_features.values):
    print(f"  特征 {idx.item()}: {val.item():.3f}")
```
<a id="common-issues-solutions"></a>
## 常见问题与解决方案

<a id="issue-high-dead-feature-ratio"></a>
### 问题：无效特征比例过高
```python
# 错误：无预热，特征过早失效
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,
    l1_warm_up_steps=0,  # 不好！
)

# 正确：对 L1 惩罚进行预热
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=8e-5,
    l1_warm_up_steps=1000,  # 逐步增大
    use_ghost_grads=True,   # 复活无效特征
)
```

<a id="issue-poor-reconstruction-low-ce-recovery"></a>
### 问题：重建效果差（CE 恢复率低）
```python
# 降低稀疏惩罚
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=5e-5,  # 数值越低，重建效果越好
    d_sae=768 * 16,       # 容量更大
)
```

<a id="issue-features-not-interpretable"></a>
### 问题：特征不可解释
```python
# 增大稀疏度（更高的 L1）
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,  # 数值越高，特征越稀疏、越可解释
)
# 或者使用 TopK 架构
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn_kwargs={"k": 50},  # 恰好激活 50 个特征
)
```

<a id="issue-memory-errors-during-training"></a>
### 问题：训练期间内存错误
```python
cfg = LanguageModelSAERunnerConfig(
    train_batch_size_tokens=2048,  # 减小批处理大小
    store_batch_size_prompts=4,    # 缓冲区中提示数量减少
    n_batches_in_buffer=8,         # 缩小激活缓冲区
)
```

<a id="integration-with-neuronpedia"></a>
## 与 Neuronpedia 集成

在 [neuronpedia.org](https://neuronpedia.org) 浏览预训练的 SAE 特征：

```python
# 特征按 SAE ID 索引
# 示例：gpt2-small 第 8 层特征 1234
# → neuronpedia.org/gpt2-small/8-res-jb/1234
```

<a id="key-classes-reference"></a>
## 关键类参考

| 类 | 用途 |
|-------|---------|
| `SAE` | 稀疏自编码器模型 |
| `LanguageModelSAERunnerConfig` | 训练配置 |
| `SAETrainingRunner` | 训练循环管理器 |
| `ActivationsStore` | 激活收集与批处理 |
| `HookedSAETransformer` | TransformerLens + SAE 集成 |

<a id="reference-documentation"></a>
## 参考文档

有关详细 API 文档、教程和高级用法，请参见 `references/` 文件夹：

| 文件 | 内容 |
|------|----------|
| [references/README.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/README.md) | 概览与快速入门指南 |
| [references/api.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/api.md) | SAE、TrainingSAE、配置的完整 API 参考 |
| [references/tutorials.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/tutorials.md) | 涉及训练、分析和特征操控的逐步教程 |

<a id="external-resources"></a>
## 外部资源

<a id="tutorials"></a>
### 教程
- [基础加载与分析](https://github.com/jbloomAus/SAELens/blob/main/tutorials/basic_loading_and_analysing.ipynb)
- [训练稀疏自编码器](https://github.com/jbloomAus/SAELens/blob/main/tutorials/training_a_sparse_autoencoder.ipynb)
- [ARENA SAE 课程](https://www.lesswrong.com/posts/LnHowHgmrMbWtpkxx/intro-to-superposition-and-sparse-autoencoders-colab)

<a id="papers"></a>
### 论文
- [迈向单语义性](https://transformer-circuits.pub/2023/monosemantic-features) — Anthropic（2023）
- [规模化单语义性](https://transformer-circuits.pub/2024/scaling-monosemanticity/) — Anthropic（2024）
- [稀疏自编码器发现高度可解释的特征](https://arxiv.org/abs/2309.08600) — Cunningham 等（ICLR 2024）
<a id="official-documentation"></a>
### 官方文档
- [SAELens 文档](https://jbloomaus.github.io/SAELens/)
- [Neuronpedia](https://neuronpedia.org) - 特征浏览器

<a id="sae-architectures"></a>
## SAE 架构

| 架构 | 描述 | 用途 |
|--------------|-------------|----------|
| **Standard** | ReLU + L1 惩罚 | 通用目的 |
| **Gated** | 学习门控机制 | 更好的稀疏性控制 |
| **TopK** | 恰好 K 个活跃特征 | 一致的稀疏性 |

```python
# TopK SAE（恰好 50 个特征活跃）
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn="topk",
    activation_fn_kwargs={"k": 50},
)
```
