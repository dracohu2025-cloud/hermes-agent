---
title: "Tensorrt Llm — 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
sidebar_label: "Tensorrt Llm"
description: "使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Tensorrt Llm {#tensorrt-llm}

使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。适用于在 NVIDIA GPU（A100/H100）上进行生产部署，当你需要比 PyTorch 快 10-100 倍的推理速度，或者需要为量化模型（FP8/INT4）提供服务、支持动态批处理和多 GPU 扩展时。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/tensorrt-llm` 安装 |
| 路径 | `optional-skills/mlops/tensorrt-llm` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `tensorrt-llm`, `torch` |
| 标签 | `推理服务`, `TensorRT-LLM`, `NVIDIA`, `推理优化`, `高吞吐量`, `低延迟`, `生产环境`, `FP8`, `INT4`, `动态批处理`, `多 GPU` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="tensorrt-llm"></a>
# TensorRT-LLM

NVIDIA 的开源库，用于在 NVIDIA GPU 上以最先进的性能优化 LLM 推理。

## 何时使用 TensorRT-LLM {#when-to-use-tensorrt-llm}

**在以下情况下使用 TensorRT-LLM：**
- 在 NVIDIA GPU（A100、H100、GB200）上部署
- 需要最大吞吐量（Llama 3 上每秒 24,000+ tokens）
- 需要低延迟以满足实时应用需求
- 使用量化模型（FP8、INT4、FP4）
- 跨多个 GPU 或节点进行扩展

**在以下情况下改用 vLLM：**
- 需要更简单的设置和 Python 优先的 API
- 希望使用 PagedAttention 而无需 TensorRT 编译
- 使用 AMD GPU 或非 NVIDIA 硬件

**在以下情况下改用 llama.cpp：**
- 在 CPU 或 Apple Silicon 上部署
- 需要边缘部署且没有 NVIDIA GPU
- 希望使用更简单的 GGUF 量化格式

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
# Docker（推荐）
docker pull nvidia/tensorrt_llm:latest

# pip 安装
pip install tensorrt_llm==1.2.0rc3

# 需要 CUDA 13.0.0、TensorRT 10.13.2、Python 3.10-3.12
```

### 基本推理 {#basic-inference}

```python
from tensorrt_llm import LLM, SamplingParams

# 初始化模型
llm = LLM(model="meta-llama/Meta-Llama-3-8B")

# 配置采样参数
sampling_params = SamplingParams(
    max_tokens=100,
    temperature=0.7,
    top_p=0.9
)

# 生成
prompts = ["解释量子计算"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(output.text)
```

### 使用 trtllm-serve 提供服务 {#serving-with-trtllm-serve}

```bash
# 启动服务器（自动下载并编译模型）
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --tp_size 4 \              # 张量并行（4 块 GPU）
    --max_batch_size 256 \
    --max_num_tokens 4096

# 客户端请求
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "messages": [{"role": "user", "content": "你好！"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```
## 主要特性 {#key-features}

### 性能优化 {#performance-optimizations}
- **动态批处理（In-flight batching）**：生成过程中的动态批处理
- **分页 KV 缓存（Paged KV cache）**：高效的内存管理
- **Flash Attention**：优化的注意力核函数
- **量化（Quantization）**：FP8、INT4、FP4，推理速度提升 2-4 倍
- **CUDA graphs**：减少核函数启动开销

### 并行化 {#parallelism}
- **张量并行（Tensor parallelism, TP）**：将模型拆分到多个 GPU
- **流水线并行（Pipeline parallelism, PP）**：按层分布
- **专家并行（Expert parallelism）**：适用于混合专家模型
- **多节点（Multi-node）**：扩展到单机之外

### 高级特性 {#advanced-features}
- **推测解码（Speculative decoding）**：借助草稿模型实现更快的生成
- **LoRA 服务（LoRA serving）**：高效的多适配器部署
- **分离式服务（Disaggregated serving）**：将预填充和生成分离

## 常见模式 {#common-patterns}

### 量化模型（FP8） {#quantized-model-fp8}

```python
from tensorrt_llm import LLM

# 加载 FP8 量化模型（速度提升 2 倍，内存减少 50%）
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    dtype="fp8",
    max_num_tokens=8192
)

# 推理方式与之前相同
outputs = llm.generate(["Summarize this article..."])
```

### 多 GPU 部署 {#multi-gpu-deployment}

```python
# 在 8 个 GPU 上使用张量并行
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=8,
    dtype="fp8"
)
```

### 批量推理 {#batch-inference}

```python
# 高效处理 100 个提示
prompts = [f"Question {i}: ..." for i in range(100)]

outputs = llm.generate(
    prompts,
    sampling_params=SamplingParams(max_tokens=200)
)

# 自动动态批处理以实现最大吞吐量
```

## 性能基准测试 {#performance-benchmarks}

**Meta Llama 3-8B**（H100 GPU）：
- 吞吐量：24,000 tokens/秒
- 延迟：约 10ms 每 token
- 对比 PyTorch：**快 100 倍**

**Llama 3-70B**（8× A100 80GB）：
- FP8 量化：比 FP16 快 2 倍
- 内存：使用 FP8 减少 50%

## 支持的模型 {#supported-models}

- **LLaMA 系列**：Llama 2、Llama 3、CodeLlama
- **GPT 系列**：GPT-2、GPT-J、GPT-NeoX
- **Qwen**：Qwen、Qwen2、QwQ
- **DeepSeek**：DeepSeek-V2、DeepSeek-V3
- **Mixtral**：Mixtral-8x7B、Mixtral-8x22B
- **视觉模型**：LLaVA、Phi-3-vision
- HuggingFace 上 **100+ 个模型**

## 参考文档 {#references}

- **[优化指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/optimization.md)** - 量化、批处理、KV 缓存调优
- **[多 GPU 设置](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/multi-gpu.md)** - 张量/流水线并行、多节点
- **[服务指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/serving.md)** - 生产部署、监控、自动扩缩

## 资源 {#resources}

- **文档**：https://nvidia.github.io/TensorRT-LLM/
- **GitHub**：https://github.com/NVIDIA/TensorRT-LLM
- **模型**：https://huggingface.co/models?library=tensorrt_llm
