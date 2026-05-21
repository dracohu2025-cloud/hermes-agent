---
title: "Slime RL 训练 — 提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导"
sidebar_label: "Slime RL 训练"
description: "提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="slime-rl-training"></a>
# Slime RL 训练

提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导。适用于训练 GLM 模型、实现自定义数据生成工作流，或需要紧密集成 Megatron-LM 以实现强化学习扩展的场景。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/slime` 安装 |
| 路径 | `optional-skills/mlops/slime` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `sglang-router>=0.2.3`、`ray`、`torch>=2.0.0`、`transformers>=4.40.0` |
| 平台 | linux、macos |
| 标签 | `强化学习`、`Megatron-LM`、`SGLang`、`GRPO`、`后训练`、`GLM` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::
<a id="slime-llm-post-training-framework-for-rl-scaling"></a>
# slime: 面向 RL 扩展的 LLM 后训练框架

slime 是清华大学 THUDM 团队开发的 LLM 后训练框架，为 GLM-4.5、GLM-4.6 和 GLM-4.7 提供支持。它将用于训练的 Megatron-LM 与用于高吞吐量 rollout 生成的 SGLang 连接起来。

<a id="when-to-use-slime"></a>
## 何时使用 slime

**在以下情况下选择 slime：**
- 需要 Megatron-LM 原生训练与 SGLang 推理
- 需要灵活的数据缓冲区实现自定义数据生成工作流
- 训练 GLM、Qwen3、DeepSeek V3 或 Llama 3 模型
- 需要研究级框架且具备生产环境支持（Z.ai）

**在以下情况下考虑其他方案：**
- 需要企业级稳定性功能 → 使用 **miles**
- 需要灵活的后端切换 → 使用 **verl**
- 需要 PyTorch 原生抽象 → 使用 **torchforge**

<a id="key-features"></a>
## 主要特性

- **训练**：Megatron-LM，支持完整并行（TP、PP、DP、SP）
- **Rollout**：基于 SGLang 的高吞吐量生成，带路由器
- **数据缓冲区**：灵活的提示管理和样本存储
- **模型**：GLM-4.x、Qwen3、DeepSeek V3/R1、Llama 3
<a id="architecture-overview"></a>
## 架构概览

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────┐
│                    Data Buffer                          │
│ - Prompt 初始化与管理                                   │
│ - 自定义数据生成与过滤                                  │
│ - Rollout 样本存储                                     │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
┌─────────────▼───────────┐ ┌─────────────▼───────────────┐
│ 训练（Megatron-LM）     │ │ Rollout（SGLang + Router）  │
│ - Actor 模型训练        │ │ - 响应生成                  │
│ - Critic（可选）        │ │ - 奖励/验证器输出           │
│ - 权重同步到 Rollout    │ │ - 多轮对话支持              │
└─────────────────────────┘ └─────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

<a id="installation"></a>
## 安装

```bash
# Recommended: Docker
docker pull slimerl/slime:latest
docker run --rm --gpus all --ipc=host --shm-size=16g \
  -it slimerl/slime:latest /bin/bash

# Inside container
cd /root/slime && pip install -e . --no-deps
```
<a id="from-source"></a>
### From Source

```bash
git clone https://github.com/THUDM/slime.git
cd slime
pip install -r requirements.txt
pip install -e .
```

<a id="quick-start-grpo-training"></a>
## Quick Start: GRPO Training

```bash
# Source model configuration
source scripts/models/qwen3-4B.sh

# Launch training
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 4 \
    --rollout-num-gpus 4 \
    --advantage-estimator grpo \
    --use-kl-loss --kl-loss-coef 0.001 \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --prompt-data /path/to/data.jsonl \
    ${MODEL_ARGS[@]} ${CKPT_ARGS[@]}
```

---

<a id="workflow-1-standard-grpo-training"></a>
## Workflow 1: Standard GRPO Training

Use this workflow for training reasoning models with group-relative advantages.

<a id="prerequisites-checklist"></a>
### Prerequisites Checklist
- [ ] Docker environment or Megatron-LM + SGLang installed
- [ ] Model checkpoint (HuggingFace or Megatron format)
- [ ] Training data in JSONL format

<a id="step-1-prepare-data"></a>
### Step 1: Prepare Data

```python
# data.jsonl format
{"prompt": "What is 2 + 2?", "label": "4"}
{"prompt": "Solve: 3x = 12", "label": "x = 4"}
```
或者使用聊天格式：

```python
{
    "prompt": [
        {"role": "system", "content": "你是一位数学导师。"},
        {"role": "user", "content": "15 + 27 等于多少？"}
    ],
    "label": "42"
}
```

<a id="step-2-configure-model"></a>
### 步骤 2：配置模型

选择一个预配置的模型脚本：

```bash
# 列出可用模型
ls scripts/models/
# glm4-9B.sh, qwen3-4B.sh, qwen3-30B-A3B.sh, deepseek-v3.sh, llama3-8B.sh, ...

# 加载你的模型
source scripts/models/qwen3-4B.sh
```

<a id="step-3-launch-training"></a>
### 步骤 3：启动训练

```bash
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --advantage-estimator grpo \
    --use-kl-loss \
    --kl-loss-coef 0.001 \
    --prompt-data /path/to/train.jsonl \
    --input-key prompt \
    --label-key label \
    --apply-chat-template \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --save-interval 100 \
    --eval-interval 50 \
    ${MODEL_ARGS[@]}
```

<a id="step-4-monitor-training"></a>
### 步骤 4：监控训练
- [ ] 检查 TensorBoard：`tensorboard --logdir outputs/`
- [ ] 验证奖励曲线是否在上升
- [ ] 监控各节点的 GPU 利用率

## 工作流 3：多轮 Agent 训练

使用此工作流来训练带有工具调用或多步推理的 Agent。

### 前置条件
- [ ] 用于多轮逻辑的自定义生成函数
- [ ] 工具/环境接口

### 第 1 步：定义自定义生成函数

```python
# custom_generate.py
async def custom_generate(args, samples, evaluation=False):
    """带工具调用的多轮生成。"""
    for sample in samples:
        conversation = sample.prompt

        for turn in range(args.max_turns):
            # 生成响应
            response = await generate_single(conversation)

            # 检查工具调用
            tool_call = extract_tool_call(response)
            if tool_call:
                tool_result = execute_tool(tool_call)
                conversation.append({"role": "assistant", "content": response})
                conversation.append({"role": "tool", "content": tool_result})
            else:
                break

        sample.response = response
        sample.reward = compute_reward(sample)

    return samples
```
<a id="step-2-launch-with-custom-function"></a>
### 步骤 2：使用自定义函数启动

```bash
python train.py \
    --custom-generate-function-path custom_generate.py \
    --max-turns 5 \
    --prompt-data /path/to/agent_data.jsonl \
    ${MODEL_ARGS[@]}
```

完整的多轮搜索示例请参见 `examples/search-r1/`。

---

<a id="configuration-reference"></a>
## 配置参考

<a id="three-argument-categories"></a>
### 三类参数

slime 使用三种类型的参数：

**1. Megatron 参数**（直接传递）：
```bash
--tensor-model-parallel-size 2
--pipeline-model-parallel-size 1
--num-layers 32
--hidden-size 4096
```

**2. SGLang 参数**（以 `--sglang-` 为前缀）：
```bash
--sglang-mem-fraction-static 0.8
--sglang-context-length 8192
--sglang-log-level INFO
```

**3. slime 参数**：
```bash
# 资源分配
--actor-num-nodes 1
--actor-num-gpus-per-node 8
--rollout-num-gpus 8
--colocate  # 训练/推理共享 GPU

# 数据
--prompt-data /path/to/data.jsonl
--input-key prompt
--label-key label

# 训练循环
--num-rollout 3000
--rollout-batch-size 32
--n-samples-per-prompt 8
--global-batch-size 256

# 算法
--advantage-estimator grpo  # 或：gspo, ppo, reinforce_plus_plus
--use-kl-loss
--kl-loss-coef 0.001
```
<a id="key-constraints"></a>
### 关键约束

```
rollout_batch_size × n_samples_per_prompt = global_batch_size × num_steps_per_rollout
```

示例：32 × 8 = 256 × 1

---

<a id="data-buffer-system"></a>
## 数据缓冲区系统

slime 的数据缓冲区支持灵活的数据管理：

<a id="basic-data-source"></a>
### 基本数据源

```python
class RolloutDataSource:
    def get_samples(self, num_samples):
        """Fetch prompts from dataset."""
        return self.dataset.sample(num_samples)

    def add_samples(self, samples):
        """Called after generation (no-op by default)."""
        pass
```

<a id="buffered-data-source-off-policy"></a>
### 缓冲数据源（Off-Policy）

```python
class RolloutDataSourceWithBuffer(RolloutDataSource):
    def __init__(self):
        self.buffer = []

    def add_samples(self, samples):
        """Store generated samples for reuse."""
        self.buffer.extend(samples)

    def buffer_filter(self, args, buffer, num_samples):
        """Custom selection logic (prioritized, stratified, etc.)."""
        return select_best(buffer, num_samples)
```

---

<a id="common-issues-and-solutions"></a>
## 常见问题与解决方案
<a id="issue-sglang-engine-crash"></a>
### 问题：SGLang 引擎崩溃

**症状**：推理引擎在训练过程中挂掉

**解决方案**：
```bash
# 启用容错机制
--use-fault-tolerance

# 增加内存分配
--sglang-mem-fraction-static 0.85

# 减少批量大小
--rollout-batch-size 16
```

<a id="issue-weight-sync-timeout"></a>
### 问题：权重同步超时

**症状**：训练在 rollout 后卡住

**解决方案**：
```bash
# 增加同步间隔
--update-weights-interval 5

# 使用同址模式（无网络传输）
--colocate
```

<a id="issue-oom-during-training"></a>
### 问题：训练过程中 OOM

**症状**：反向传播时 CUDA 内存不足

**解决方案**：
```bash
# 启用梯度检查点
--recompute-activations

# 减少微批量大小
--micro-batch-size 1

# 启用序列并行
--sequence-parallel
```

<a id="issue-slow-data-loading"></a>
### 问题：数据加载缓慢

**症状**：GPU 在数据获取期间空闲

**解决方案**：
```bash
# 增加数据加载进程数
--num-data-workers 4

# 使用流式数据集
--streaming-data
```

---

<a id="supported-models"></a>
## 支持的模型

| 模型系列      | 配置                         |
|---------------|------------------------------|
| GLM           | GLM-4.5, GLM-4.6, GLM-4.7, GLM-Z1-9B |
| Qwen          | Qwen3 (4B, 8B, 30B-A3B), Qwen3-MoE, Qwen2.5 |
| DeepSeek      | V3, V3.1, R1                 |
| Llama         | Llama 3 (8B, 70B)            |
| 其他          | Kimi K2, Moonlight-16B       |
每个模型在 `scripts/models/` 目录下都有预先配置好的脚本。

---

<a id="advanced-topics"></a>
## 高级主题

<a id="co-location-mode"></a>
### 共置模式

在训练和推理之间共享 GPU 以减少内存占用：

```bash
python train.py \
    --colocate \
    --actor-num-gpus-per-node 8 \
    --sglang-mem-fraction-static 0.4 \
    ${MODEL_ARGS[@]}
```

<a id="custom-reward-model"></a>
### 自定义奖励模型

```python
# custom_rm.py
class CustomRewardModel:
    def __init__(self, model_path):
        self.model = load_model(model_path)

    def compute_reward(self, prompts, responses):
        inputs = self.tokenize(prompts, responses)
        scores = self.model(inputs)
        return scores.tolist()
```

```bash
--custom-rm-path custom_rm.py
```

<a id="evaluation-multi-task"></a>
### 多任务评估

```bash
--eval-prompt-data aime /path/to/aime.jsonl \
--eval-prompt-data gsm8k /path/to/gsm8k.jsonl \
--n-samples-per-eval-prompt 16
```

---

<a id="resources"></a>
## 资源

- **文档**：https://thudm.github.io/slime/
- **GitHub**：https://github.com/THUDM/slime
- **博客**：https://lmsys.org/blog/2025-07-09-slime/
- **示例**：请参阅 `examples/` 目录，包含 14 个以上的实践示例
