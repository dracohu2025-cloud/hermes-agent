---
title: "Tensorrt Llm — 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
sidebar_label: "Tensorrt Llm"
description: "使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="tensorrt-llm"></a>
# Tensorrt Llm

使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。适用于在 NVIDIA GPU（A100/H100）上进行生产部署，当你需要比 PyTorch 快 10-100 倍的推理速度，或者需要为模型提供量化（FP8/INT4）、动态批处理和多 GPU 扩展支持时。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/tensorrt-llm` 安装 |
| 路径 | `optional-skills/mlops/tensorrt-llm` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `tensorrt-llm`, `torch` |
| 平台 | linux, macos |
| 标签 | `推理服务`, `TensorRT-LLM`, `NVIDIA`, `推理优化`, `高吞吐量`, `低延迟`, `生产环境`, `FP8`, `INT4`, `动态批处理`, `多GPU` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# TensorRT-LLM

NVIDIA 的开源库，用于在 NVIDIA GPU 上以最先进的性能优化 LLM 推理。

<a id="when-to-use-tensorrt-llm"></a>
## 何时使用 TensorRT-LLM

**在以下情况下使用 TensorRT-LLM：**
- 在 NVIDIA GPU（A100、H100、GB200）上部署
- 需要最大吞吐量（Llama 3 上每秒超过 24,000 个 token）
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

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
# Docker（推荐）
docker pull nvidia/tensorrt_llm:latest

# pip 安装
pip install tensorrt_llm==1.2.0rc3

# 需要 CUDA 13.0.0、TensorRT 10.13.2、Python 3.10-3.12
```

<a id="basic-inference"></a>
### 基本推理

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

<a id="serving-with-trtllm-serve"></a>
### 使用 trtllm-serve 提供服务

```bash
# 启动服务器（自动下载和编译模型）
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --tp_size 4 \              # 张量并行（4 个 GPU）
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
<a id="key-features"></a>
## 关键特性

<a id="performance-optimizations"></a>
### 性能优化
- **In-flight batching**：在生成过程中动态批处理
- **Paged KV cache**：高效的内存管理
- **Flash Attention**：优化后的注意力核函数
- **Quantization**：FP8、INT4、FP4，实现 2-4 倍的推理加速
- **CUDA graphs**：降低核函数启动开销

<a id="parallelism"></a>
### 并行能力
- **Tensor parallelism (TP)**：跨 GPU 拆分模型
- **Pipeline parallelism (PP)**：按层分布
- **Expert parallelism**：用于 Mixture-of-Experts 模型
- **Multi-node**：扩展到单机之外

<a id="advanced-features"></a>
### 高级特性
- **Speculative decoding**：通过草稿模型实现更快的生成
- **LoRA serving**：高效的多适配器部署
- **Disaggregated serving**：分离预填充和生成阶段

<a id="common-patterns"></a>
## 常用模式

<a id="quantized-model-fp8"></a>
### 量化模型 (FP8)

```python
from tensorrt_llm import LLM

# Load FP8 quantized model (2× faster, 50% memory)
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    dtype="fp8",
    max_num_tokens=8192
)

# Inference same as before
outputs = llm.generate(["Summarize this article..."])
```

<a id="multi-gpu-deployment"></a>
### 多 GPU 部署

```python
# Tensor parallelism across 8 GPUs
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=8,
    dtype="fp8"
)
```

<a id="batch-inference"></a>
### 批量推理

```python
# Process 100 prompts efficiently
prompts = [f"Question {i}: ..." for i in range(100)]

outputs = llm.generate(
    prompts,
    sampling_params=SamplingParams(max_tokens=200)
)

# Automatic in-flight batching for maximum throughput
```

<a id="performance-benchmarks"></a>
## 性能基准

**Meta Llama 3-8B**（H100 GPU）：
- 吞吐量：24,000 tokens/sec
- 延迟：~10ms per token
- 对比 PyTorch：**100 倍加速**

**Llama 3-70B**（8× A100 80GB）：
- FP8 量化：比 FP16 快 2 倍
- 内存：FP8 减少 50%

<a id="supported-models"></a>
## 支持的模型

- **LLaMA 系列**：Llama 2, Llama 3, CodeLlama
- **GPT 系列**：GPT-2, GPT-J, GPT-NeoX
- **Qwen**：Qwen, Qwen2, QwQ
- **DeepSeek**：DeepSeek-V2, DeepSeek-V3
- **Mixtral**：Mixtral-8x7B, Mixtral-8x22B
- **视觉模型**：LLaVA, Phi-3-vision
- HuggingFace 上的 **100+ 模型**

<a id="references"></a>
## 参考文档

- **[优化指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/optimization.md)** – 量化、批处理、KV cache 调优
- **[多 GPU 设置](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/multi-gpu.md)** – 张量/流水线并行、多节点
- **[部署指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/serving.md)** – 生产部署、监控、自动扩缩容

<a id="resources"></a>
## 资源链接

- **文档**：https://nvidia.github.io/TensorRT-LLM/
- **GitHub**：https://github.com/NVIDIA/TensorRT-LLM
- **模型库**：https://huggingface.co/models?library=tensorrt_llm
