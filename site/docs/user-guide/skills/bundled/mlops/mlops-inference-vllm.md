---
title: "Serving Llms Vllm — vLLM: high-throughput LLM serving, OpenAI API, quantization"
sidebar_label: "Serving Llms Vllm"
description: "vLLM: high-throughput LLM serving, OpenAI API, quantization"
---

{/* 该页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 部署大语言模型 —— vLLM {#serving-llms-vllm}

vLLM：高吞吐量 LLM 服务，OpenAI API，量化。

## 技能元数据 {#skill-metadata}

|                      |                                                              |
| -------------------- | ------------------------------------------------------------ |
| 来源                 | 内置（默认安装）                                             |
| 路径                 | `skills/mlops/inference/vllm`                                |
| 版本                 | `1.0.0`                                                      |
| 作者                 | Orchestra Research                                           |
| 许可证               | MIT                                                          |
| 依赖                 | `vllm`, `torch`, `transformers`                              |
| 标签                 | `vLLM`, `Inference Serving`, `PagedAttention`, `Continuous Batching`, `High Throughput`, `Production`, `OpenAI API`, `Quantization`, `Tensor Parallelism` |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。Agent 在技能激活时看到的指令就是这部分内容。
:::

# vLLM —— 高性能大语言模型服务 {#vllm-high-performance-llm-serving}

## 何时使用 {#when-to-use}

在部署生产环境的 LLM API、优化推理延迟/吞吐量、或使用有限 GPU 内存运行模型时使用。支持兼容 OpenAI 的端点、量化（GPTQ/AWQ/FP8）以及张量并行。

## 快速开始 {#quick-start}

vLLM 通过 PagedAttention（基于块的 KV 缓存）和连续批处理（混合预填充/解码请求），实现了比标准 transformers 高 24 倍的吞吐量。

**安装**：
```bash
pip install vllm
```

**基础离线推理**：
```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, max_tokens=256)

outputs = llm.generate(["Explain quantum computing"], sampling)
print(outputs[0].outputs[0].text)
```

**兼容 OpenAI 的服务器**：
```bash
vllm serve meta-llama/Llama-3-8B-Instruct

# 使用 OpenAI SDK 查询
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
"
```

## 常见工作流 {#common-workflows}

### 工作流 1：生产环境 API 部署 {#workflow-1-production-api-deployment}

复制以下清单并跟踪进度：

```
部署进度：
- [ ] 步骤 1：配置服务器设置
- [ ] 步骤 2：使用少量流量测试
- [ ] 步骤 3：启用监控
- [ ] 步骤 4：部署到生产环境
- [ ] 步骤 5：验证性能指标
```

**步骤 1：配置服务器设置**

根据模型大小选择配置：

```bash
# 单 GPU 上的 7B-13B 模型
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000

# 使用张量并行的 30B-70B 模型
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000

# 带缓存和指标的生产环境版本
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```
**步骤 2：用少量流量进行测试**

在生产环境前运行负载测试：

```bash
# 安装负载测试工具
pip install locust

# 创建包含示例请求的 test_load.py
# 运行：locust -f test_load.py --host http://localhost:8000
```

验证 TTFT（首 token 延迟）< 500ms，吞吐量 > 100 req/sec。

**步骤 3：启用监控**

vLLM 在端口 9090 暴露 Prometheus 指标：

```bash
curl http://localhost:9090/metrics | grep vllm
```

需要监控的关键指标：
- `vllm:time_to_first_token_seconds` – 延迟
- `vllm:num_requests_running` – 活跃请求数
- `vllm:gpu_cache_usage_perc` – KV 缓存利用率

**步骤 4：部署到生产环境**

使用 Docker 实现一致的部署：

```bash
# 在 Docker 中运行 vLLM
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching
```

**步骤 5：验证性能指标**

检查部署是否达到目标：
- TTFT < 500ms（针对短提示）
- 吞吐量 > 目标 req/sec
- GPU 利用率 > 80%
- 日志中无 OOM 错误

### 工作流 2：离线批量推理 {#workflow-2-offline-batch-inference}

适用于处理大型数据集，无需服务器开销。

复制此检查清单：

```
批量处理：
- [ ] 步骤 1：准备输入数据
- [ ] 步骤 2：配置 LLM 引擎
- [ ] 步骤 3：运行批量推理
- [ ] 步骤 4：处理结果
```

**步骤 1：准备输入数据**

```python
# 从文件加载提示
prompts = []
with open("prompts.txt") as f:
    prompts = [line.strip() for line in f]

print(f"已加载 {len(prompts)} 条提示")
```

**步骤 2：配置 LLM 引擎**

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    tensor_parallel_size=2,  # 使用 2 块 GPU
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

sampling = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
    stop=["</s>", "\n\n"]
)
```

**步骤 3：运行批量推理**

vLLM 会自动对请求进行批处理以提高效率：

```python
# 一次调用处理所有提示
outputs = llm.generate(prompts, sampling)

# vLLM 内部处理批处理
# 无需手动拆分提示
```

**步骤 4：处理结果**

```python
# 提取生成的文本
results = []
for output in outputs:
    prompt = output.prompt
    generated = output.outputs[0].text
    results.append({
        "prompt": prompt,
        "generated": generated,
        "tokens": len(output.outputs[0].token_ids)
    })

# 保存到文件
import json
with open("results.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"已处理 {len(results)} 条提示")
```

### 工作流 3：量化模型服务 {#workflow-3-quantized-model-serving}

在有限的 GPU 内存中适配大型模型。

```
量化设置：
- [ ] 步骤 1：选择量化方法
- [ ] 步骤 2：查找或创建量化模型
- [ ] 步骤 3：使用量化标志启动
- [ ] 步骤 4：验证精度
```

**步骤 1：选择量化方法**

- **AWQ**：最适合 70B 模型，精度损失最小
- **GPTQ**：模型支持广泛，压缩效果好
- **FP8**：在 H100 GPU 上速度最快
**第 2 步：寻找或创建量化模型**

使用 HuggingFace 上预量化的模型：

```bash
# 搜索 AWQ 模型
# 示例：TheBloke/Llama-2-70B-AWQ
```

**第 3 步：启动时加上量化参数**

```bash
# 使用预量化模型
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95

# 结果：70B 模型约占用 40GB 显存
```

**第 4 步：验证精度**

测试输出是否符合预期质量：

```python
# 对比量化前后的响应
# 验证特定任务的性能没有变化
```

## 什么时候用 vLLM，什么时候用替代方案 {#when-to-use-vs-alternatives}

**使用 vLLM 的场景：**
- 部署生产级 LLM API（100+ 请求/秒）
- 提供与 OpenAI 兼容的端点
- 受限于 GPU 显存但仍需使用大模型
- 多用户应用（聊天机器人、助手）
- 需要低延迟和高吞吐量

**改用替代方案的场景：**
- **llama.cpp**：CPU/边缘推理，单用户
- **HuggingFace transformers**：研究、原型开发、单次生成
- **TensorRT-LLM**：仅限 NVIDIA，追求极致性能
- **Text-Generation-Inference**：已集成在 HuggingFace 生态中

## 常见问题 {#common-issues}

**问题：加载模型时内存不足**

减少内存占用：
```bash
vllm serve MODEL \
  --gpu-memory-utilization 0.7 \
  --max-model-len 4096
```

或使用量化：
```bash
vllm serve MODEL --quantization awq
```

**问题：首 Token 生成慢（TTFT > 1 秒）**

对重复提示启用前缀缓存：
```bash
vllm serve MODEL --enable-prefix-caching
```

对于长提示，启用分块预填充：
```bash
vllm serve MODEL --enable-chunked-prefill
```

**问题：找不到模型**

对自定义模型使用 `--trust-remote-code`：
```bash
vllm serve MODEL --trust-remote-code
```

**问题：吞吐量低（&lt;50 请求/秒）**

增加并发序列数：
```bash
vllm serve MODEL --max-num-seqs 512
```

用 `nvidia-smi` 检查 GPU 利用率——应 >80%。

**问题：推理速度慢于预期**

确认张量并行使用了 2 的幂次方 GPU 数量：
```bash
vllm serve MODEL --tensor-parallel-size 4  # 不要用3
```

启用推测解码以加快生成：
```bash
vllm serve MODEL --speculative-model DRAFT_MODEL
```

## 进阶主题 {#advanced-topics}

**服务器部署模式**：参见 [references/server-deployment.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/server-deployment.md) 了解 Docker、Kubernetes 和负载均衡配置。

**性能优化**：参见 [references/optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/optimization.md) 了解 PagedAttention 调优、连续批处理细节和基准测试结果。

**量化指南**：参见 [references/quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/quantization.md) 了解 AWQ/GPTQ/FP8 设置、模型准备和精度对比。

**故障排除**：参见 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/troubleshooting.md) 了解详细错误信息、调试步骤和性能诊断。
## 硬件要求 {#hardware-requirements}

- **小模型（7B-13B）**：1× A10（24GB）或 A100（40GB）
- **中等模型（30B-40B）**：2× A100（40GB），使用张量并行
- **大模型（70B+）**：4× A100（40GB）或 2× A100（80GB），使用 AWQ/GPTQ

支持的平台：NVIDIA（主要）、AMD ROCm、Intel GPU、TPU

## 资源 {#resources}

- 官方文档：https://docs.vllm.ai
- GitHub：https://github.com/vllm-project/vllm
- 论文：《Efficient Memory Management for Large Language Model Serving with PagedAttention》（SOSP 2023）
- 社区：https://discuss.vllm.ai
