---
title: "Serving Llms Vllm — vLLM：高吞吐量 LLM 服务，OpenAI API，量化"
sidebar_label: "Serving Llms Vllm"
description: "vLLM：高吞吐量 LLM 服务，OpenAI API，量化"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="serving-llms-vllm"></a>
# Serving Llms Vllm

vLLM：高吞吐量 LLM 服务，OpenAI API，量化。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/vllm` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `vllm`, `torch`, `transformers` |
| 平台 | linux, macos |
| 标签 | `vLLM`, `Inference Serving`, `PagedAttention`, `Continuous Batching`, `High Throughput`, `Production`, `OpenAI API`, `Quantization`, `Tensor Parallelism` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 agent 在技能激活时看到的指令。
:::

<a id="vllm-high-performance-llm-serving"></a>
# vLLM - 高性能 LLM 服务

<a id="when-to-use"></a>
## 何时使用

在部署生产级 LLM API、优化推理延迟/吞吐量，或在 GPU 内存有限的情况下服务模型时使用。支持 OpenAI 兼容端点、量化（GPTQ/AWQ/FP8）和张量并行。

<a id="quick-start"></a>
## 快速开始

vLLM 通过 PagedAttention（基于块的 KV 缓存）和连续批处理（混合预填充/解码请求）实现了比标准 Transformers 高 24 倍的吞吐量。

**安装**：
```bash
pip install vllm
```

**基本离线推理**：
```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, max_tokens=256)

outputs = llm.generate(["Explain quantum computing"], sampling)
print(outputs[0].outputs[0].text)
```

**OpenAI 兼容服务器**：
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

<a id="common-workflows"></a>
## 常见工作流

<a id="workflow-1-production-api-deployment"></a>
### 工作流 1：生产级 API 部署

复制此清单并跟踪进度：

```
部署进度：
- [ ] 步骤 1：配置服务器设置
- [ ] 步骤 2：使用有限流量测试
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

# 生产环境，带缓存和指标
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```
**步骤 2：用有限流量进行测试**

在生产环境前运行负载测试：

```bash
# 安装负载测试工具
pip install locust

# 创建包含示例请求的 test_load.py
# 运行：locust -f test_load.py --host http://localhost:8000
```

验证 TTFT（首 token 生成时间）&lt; 500ms，吞吐量 > 100 req/sec。

**步骤 3：启用监控**

vLLM 在 9090 端口暴露 Prometheus 指标：

```bash
curl http://localhost:9090/metrics | grep vllm
```

需要监控的关键指标：
- `vllm:time_to_first_token_seconds` - 延迟
- `vllm:num_requests_running` - 活跃请求数
- `vllm:gpu_cache_usage_perc` - KV 缓存利用率

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
- TTFT &lt; 500ms（针对短提示）
- 吞吐量 > 目标 req/sec
- GPU 利用率 > 80%
- 日志中没有 OOM 错误

<a id="workflow-2-offline-batch-inference"></a>
### 工作流程 2：离线批量推理

用于处理大数据集，无需服务器开销。

复制以下检查清单：

```
Batch Processing:
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

vLLM 会自动合并请求以提高效率：

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

<a id="workflow-3-quantized-model-serving"></a>
### 工作流程 3：量化模型服务

在有限的 GPU 内存中适配大型模型。

```
Quantization Setup:
- [ ] 步骤 1：选择量化方法
- [ ] 步骤 2：找到或创建量化模型
- [ ] 步骤 3：使用量化标志启动
- [ ] 步骤 4：验证精度
```

**步骤 1：选择量化方法**

- **AWQ**：最适合 70B 模型，精度损失最小
- **GPTQ**：广泛模型支持，压缩效果好
- **FP8**：在 H100 GPU 上速度最快
**步骤 2：查找或创建量化模型**

使用 HuggingFace 上的预量化模型：

```bash
# 搜索 AWQ 模型
# 示例：TheBloke/Llama-2-70B-AWQ
```

**步骤 3：使用量化标志启动**

```bash
# 使用预量化模型
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95

# 结果：70B 模型约占用 40GB 显存
```

**步骤 4：验证精度**

测试输出是否符合预期质量：

```python
# 对比量化与非量化模型的响应
# 确认任务特定性能没有变化
```

<a id="when-to-use-vs-alternatives"></a>
## 何时使用 vs 替代方案

**使用 vLLM 的场景：**
- 部署生产级 LLM API（100+ 请求/秒）
- 提供与 OpenAI 兼容的接口
- GPU 内存有限但需要大模型
- 多用户应用（聊天机器人、助手）
- 需要低延迟与高吞吐量

**改用替代方案：**
- **llama.cpp**：CPU/边缘推理，单用户
- **HuggingFace transformers**：研究、原型设计、一次性生成
- **TensorRT-LLM**：仅限 NVIDIA，追求极致性能
- **Text-Generation-Inference**：已在 HuggingFace 生态系统中

<a id="common-issues"></a>
## 常见问题

**问题：加载模型时内存不足**

降低内存使用：
```bash
vllm serve MODEL \
  --gpu-memory-utilization 0.7 \
  --max-model-len 4096
```

或使用量化：
```bash
vllm serve MODEL --quantization awq
```

**问题：首个 token 生成慢（TTFT > 1 秒）**

为重复提示启用前缀缓存：
```bash
vllm serve MODEL --enable-prefix-caching
```

对于长提示，启用分块预填充：
```bash
vllm serve MODEL --enable-chunked-prefill
```

**问题：模型未找到错误**

对自定义模型使用 `--trust-remote-code`：
```bash
vllm serve MODEL --trust-remote-code
```

**问题：吞吐量低（&lt;50 请求/秒）**

增加并发序列数：
```bash
vllm serve MODEL --max-num-seqs 512
```

用 `nvidia-smi` 检查 GPU 利用率——应大于 80%。

**问题：推理速度比预期慢**

确保张量并行使用 2 的幂次 GPU：
```bash
vllm serve MODEL --tensor-parallel-size 4  # 不要用 3
```

启用推测解码以加快生成：
```bash
vllm serve MODEL --speculative-model DRAFT_MODEL
```

<a id="advanced-topics"></a>
## 高级主题

**服务部署模式**：参见 [references/server-deployment.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/server-deployment.md) 了解 Docker、Kubernetes 和负载均衡配置。

**性能优化**：参见 [references/optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/optimization.md) 了解 PagedAttention 调优、连续批处理细节和基准测试结果。

**量化指南**：参见 [references/quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/quantization.md) 了解 AWQ/GPTQ/FP8 配置、模型准备和精度比较。

**故障排除**：参见 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/troubleshooting.md) 获取详细错误信息、调试步骤和性能诊断。
<a id="hardware-requirements"></a>
## 硬件要求

- **小模型（7B-13B）**：1x A10（24GB）或 A100（40GB）
- **中等模型（30B-40B）**：2x A100（40GB），需张量并行
- **大模型（70B+）**：4x A100（40GB）或 2x A100（80GB），建议使用 AWQ/GPTQ

支持的平台：NVIDIA（主要）、AMD ROCm、Intel GPU、TPU

<a id="resources"></a>
## 资源

- 官方文档：https://docs.vllm.ai
- GitHub：https://github.com/vllm-project/vllm
- 论文："Efficient Memory Management for Large Language Model Serving with PagedAttention"（SOSP 2023）
- 社区：https://discuss.vllm.ai
