---
title: "稀疏自编码器训练"
sidebar_label: "稀疏自编码器训练"
description: "提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 稀疏自编码器训练 {#sparse-autoencoder-training}

提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征。在发现可解释特征、分析叠加或研究语言模型中的单语义表示时使用。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/saelens` 安装 |
| 路径 | `optional-skills/mlops/saelens` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `sae-lens>=6.0.0`, `transformer-lens>=2.0.0`, `torch>=2.0.0` |
| 标签 | `稀疏自编码器`, `SAE`, `机制可解释性`, `特征发现`, `叠加` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# SAELens：用于机制可解释性的稀疏自编码器 {#saelens-sparse-autoencoders-for-mechanistic-interpretability}

SAELens 是训练和分析稀疏自编码器（SAE）的主要库——这是一种将多语义神经网络激活分解为稀疏、可解释特征的技术。基于 Anthropic 在单语义性方面的开创性研究。

**GitHub**：[jbloomAus/SAELens](https://github.com/jbloomAus/SAELens)（1100+ 星标）

## 问题：多语义性与叠加 {#the-problem-polysemanticity-superposition}

神经网络中的单个神经元是**多语义的**——它们在多个语义不同的上下文中激活。这是因为模型使用**叠加**来表示比神经元数量更多的特征，这使得可解释性变得困难。

**SAE 解决了这个问题**，通过将密集激活分解为稀疏、单语义的特征——通常对于任何给定输入，只有少量特征激活，并且每个特征对应一个可解释的概念。

## 何时使用 SAELens {#when-to-use-saelens}

**在以下情况下使用 SAELens：**
- 发现模型激活中的可解释特征
- 理解模型学到了哪些概念
- 研究叠加和特征几何
- 执行基于特征的引导或消融
- 分析与安全相关的特征（欺骗、偏见、有害内容）

**考虑替代方案的情况：**
- 你需要基本的激活分析 → 直接使用 **TransformerLens**
- 你需要因果干预实验 → 使用 **pyvene** 或 **TransformerLens**
- 你需要生产环境引导 → 考虑直接激活工程

## 安装 {#installation}

```bash
pip install sae-lens
```

要求：Python 3.10+，transformer-lens>=2.0.0

## 核心概念 {#core-concepts}

### SAE 学习什么 {#what-saes-learn}

SAE 通过稀疏瓶颈训练来重建模型激活：

```
输入激活 → 编码器 → 稀疏特征 → 解码器 → 重建激活
    (d_model)       ↓        (d_sae >> d_model)    ↓         (d_model)
                 稀疏性                     重建
                 惩罚                       损失
```
**损失函数**：`MSE(原始, 重构) + L1系数 × L1(特征)`

### 关键验证（Anthropic 研究） {#key-validation-anthropic-research}

在《迈向单语义性》中，人类评估者发现 **70% 的 SAE 特征真正可解释**。发现的特征包括：
- DNA 序列、法律语言、HTTP 请求
- 希伯来语文本、营养声明、代码语法
- 情感、命名实体、语法结构

## 工作流 1：加载和分析预训练 SAE {#workflow-1-loading-and-analyzing-pre-trained-saes}

### 分步指南 {#step-by-step}

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
print(f"活跃特征数：{(sae_features > 0).sum()}")

# 4. 找出每个位置的前几个特征
for pos in range(tokens.shape[1]):
    top_features = sae_features[0, pos].topk(5)
    token = model.to_str_tokens(tokens[0, pos:pos+1])[0]
    print(f"Token '{token}'：特征 {top_features.indices.tolist()}")

# 5. 重构激活值
reconstructed = sae.decode(sae_features)
reconstruction_error = (activations - reconstructed).norm()
```

### 可用的预训练 SAE {#available-pre-trained-saes}

| 发布版本 | 模型 | 层 |
|---------|-------|--------|
| `gpt2-small-res-jb` | GPT-2 Small | 多个残差流 |
| `gemma-2b-res` | Gemma 2B | 残差流 |
| HuggingFace 上的各种版本 | 搜索标签 `saelens` | 多种 |

### 检查清单 {#checklist}
- [ ] 使用 TransformerLens 加载模型
- [ ] 加载目标层对应的 SAE
- [ ] 将激活值编码为稀疏特征
- [ ] 识别每个 token 激活最强的特征
- [ ] 验证重构质量

## 工作流 2：训练自定义 SAE {#workflow-2-training-a-custom-sae}

<a id="step-by-step"></a>
### 分步指南

```python
from sae_lens import SAE, LanguageModelSAERunnerConfig, SAETrainingRunner

# 1. 配置训练参数
cfg = LanguageModelSAERunnerConfig(
    # 模型
    model_name="gpt2-small",
    hook_name="blocks.8.hook_resid_pre",
    hook_layer=8,
    d_in=768,  # 模型维度

    # SAE 架构
    architecture="standard",  # 或 "gated", "topk"
    d_sae=768 * 8,  # 扩展因子为 8
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
print(f"L0（平均活跃特征数）：{trainer.metrics['l0']}")
print(f"CE 损失恢复率：{trainer.metrics['ce_loss_score']}")
```
### 关键超参数 {#key-hyperparameters}

| 参数 | 典型值 | 效果 |
|-----------|---------------|--------|
| `d_sae` | 4-16× d_model | 更多特征，更高容量 |
| `l1_coefficient` | 5e-5 到 1e-4 | 值越大 = 越稀疏，但精度越低 |
| `lr` | 1e-4 到 1e-3 | 标准优化器学习率 |
| `l1_warm_up_steps` | 500-2000 | 防止早期特征死亡 |

### 评估指标 {#evaluation-metrics}

| 指标 | 目标值 | 含义 |
|--------|--------|--------|
| **L0** | 50-200 | 每个 token 平均激活的特征数 |
| **CE Loss Score** | 80-95% | 恢复的交叉熵与原始交叉熵之比 |
| **Dead Features** | &lt;5% | 从未激活的特征比例 |
| **Explained Variance** | >90% | 重建质量 |

### 检查清单 {#checklist}
- [ ] 选择目标层和钩子点
- [ ] 设置扩展因子（d_sae = 4-16× d_model）
- [ ] 调整 L1 系数以达到期望的稀疏度
- [ ] 启用 L1 预热以防止特征死亡
- [ ] 训练期间监控指标（W&B）
- [ ] 验证 L0 和 CE Loss 恢复情况
- [ ] 检查死亡特征比例

## 工作流 3：特征分析与引导 {#workflow-3-feature-analysis-and-steering}

### 分析单个特征 {#analyzing-individual-features}

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

# 查找激活特定特征的文本
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

### 特征引导 {#feature-steering}

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

### 特征归因 {#feature-attribution}

```python
# 哪些特征对特定输出影响最大？
tokens = model.to_tokens("The capital of France is")
_, cache = model.run_with_cache(tokens)

# 获取最后一个位置的特征
features = sae.encode(cache["resid_pre", 8])[0, -1]  # [d_sae]

# 计算每个特征的对数几率归因
# 特征贡献 = 特征激活值 × 解码器权重 × 反嵌入权重
W_dec = sae.W_dec  # [d_sae, d_model]
W_U = model.W_U    # [d_model, vocab]

# 对 "Paris" 对数几率的贡献
paris_token = model.to_single_token(" Paris")
feature_contributions = features * (W_dec @ W_U[:, paris_token])

top_features = feature_contributions.topk(10)
print("预测 'Paris' 的 top 特征：")
for idx, val in zip(top_features.indices, top_features.values):
    print(f"  特征 {idx.item()}: {val.item():.3f}")
```
## 常见问题与解决方案 {#common-issues-solutions}

### 问题：死亡特征比例过高 {#issue-high-dead-feature-ratio}
```python
# 错误：没有预热，特征过早死亡
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,
    l1_warm_up_steps=0,  # 不好！
)

# 正确：对 L1 惩罚进行预热
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=8e-5,
    l1_warm_up_steps=1000,  # 逐步增加
    use_ghost_grads=True,   # 复活死亡特征
)
```

### 问题：重建效果差（CE 恢复率低） {#issue-poor-reconstruction-low-ce-recovery}
```python
# 降低稀疏性惩罚
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=5e-5,  # 越低 = 重建效果越好
    d_sae=768 * 16,       # 更大容量
)
```

### 问题：特征不可解释 {#issue-features-not-interpretable}
```python
# 增加稀疏性（更高的 L1）
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,  # 越高 = 越稀疏，越可解释
)
# 或者使用 TopK 架构
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn_kwargs={"k": 50},  # 恰好 50 个活跃特征
)
```

### 问题：训练期间内存错误 {#issue-memory-errors-during-training}
```python
cfg = LanguageModelSAERunnerConfig(
    train_batch_size_tokens=2048,  # 减小批次大小
    store_batch_size_prompts=4,    # 缓冲区中更少的提示
    n_batches_in_buffer=8,         # 更小的激活缓冲区
)
```

## 与 Neuronpedia 集成 {#integration-with-neuronpedia}

在 [neuronpedia.org](https://neuronpedia.org) 浏览预训练的 SAE 特征：

```python
# 特征通过 SAE ID 索引
# 示例：gpt2-small 第 8 层特征 1234
# → neuronpedia.org/gpt2-small/8-res-jb/1234
```

## 关键类参考 {#key-classes-reference}

| 类 | 用途 |
|-------|---------|
| `SAE` | 稀疏自编码器模型 |
| `LanguageModelSAERunnerConfig` | 训练配置 |
| `SAETrainingRunner` | 训练循环管理器 |
| `ActivationsStore` | 激活收集与批处理 |
| `HookedSAETransformer` | TransformerLens + SAE 集成 |

## 参考文档 {#reference-documentation}

有关详细的 API 文档、教程和高级用法，请参见 `references/` 文件夹：

| 文件 | 内容 |
|------|----------|
| [references/README.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/README.md) | 概述与快速入门指南 |
| [references/api.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/api.md) | SAE、TrainingSAE、配置的完整 API 参考 |
| [references/tutorials.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/saelens/references/tutorials.md) | 训练、分析、引导的逐步教程 |

## 外部资源 {#external-resources}

### 教程 {#tutorials}
- [基本加载与分析](https://github.com/jbloomAus/SAELens/blob/main/tutorials/basic_loading_and_analysing.ipynb)
- [训练稀疏自编码器](https://github.com/jbloomAus/SAELens/blob/main/tutorials/training_a_sparse_autoencoder.ipynb)
- [ARENA SAE 课程](https://www.lesswrong.com/posts/LnHowHgmrMbWtpkxx/intro-to-superposition-and-sparse-autoencoders-colab)

### 论文 {#papers}
- [迈向单语义性](https://transformer-circuits.pub/2023/monosemantic-features) - Anthropic (2023)
- [扩展单语义性](https://transformer-circuits.pub/2024/scaling-monosemanticity/) - Anthropic (2024)
- [稀疏自编码器发现高度可解释的特征](https://arxiv.org/abs/2309.08600) - Cunningham 等人 (ICLR 2024)
### 官方文档 {#official-documentation}
- [SAELens 文档](https://jbloomaus.github.io/SAELens/)
- [Neuronpedia](https://neuronpedia.org) - 特征浏览器

## SAE 架构 {#sae-architectures}

| 架构 | 描述 | 使用场景 |
|------|------|----------|
| **Standard** | ReLU + L1 惩罚项 | 通用目的 |
| **Gated** | 学习到的门控机制 | 更好的稀疏性控制 |
| **TopK** | 恰好 K 个活跃特征 | 一致的稀疏性 |

```python
# TopK SAE (exactly 50 features active)
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn="topk",
    activation_fn_kwargs={"k": 50},
)
```
