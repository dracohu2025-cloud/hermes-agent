---
sidebar_position: 12
title: "批量处理 (Batch Processing)"
description: "大规模生成 Agent 轨迹 —— 并行处理、断点续传和工具集分布"
---

# 批量处理 (Batch Processing)

批量处理允许你针对成百上千个 prompt 并行运行 Hermes Agent，生成结构化的轨迹数据。这主要用于**训练数据生成** —— 产出带有工具使用统计信息的 ShareGPT 格式轨迹，可用于微调或评估。

## 概览

批量运行器 (`batch_runner.py`) 处理 JSONL 格式的 prompt 数据集，让每个 prompt 在带有工具访问权限的完整 Agent 会话中运行。每个 prompt 都有自己独立的隔离环境。输出结果是结构化的轨迹数据，包含完整的对话历史、工具调用统计和推理覆盖率指标。

## 快速开始

```bash
# 基础批量运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=4

# 恢复中断的运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --resume

# 列出可用的工具集分布 (toolset distributions)
python batch_runner.py --list_distributions
```

## 数据集格式

输入数据集是一个 JSONL 文件（每行一个 JSON 对象）。每个条目必须包含 `prompt` 字段：

```jsonl
{"prompt": "Write a Python function that finds the longest palindromic substring"}
{"prompt": "Create a REST API endpoint for user authentication using Flask"}
{"prompt": "Debug this error: TypeError: cannot unpack non-iterable NoneType object"}
```

条目可以包含以下可选字段：
- `image` 或 `docker_image`：用于该 prompt 沙箱的容器镜像（支持 Docker、Modal 和 Singularity 后端）
- `cwd`：覆盖该任务终端会话的工作目录

## 配置选项

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--dataset_file` | (必填) | JSONL 数据集路径 |
| `--batch_size` | (必填) | 每批次的 prompt 数量 |
| `--run_name` | (必填) | 本次运行的名称（用于输出目录和断点记录） |
| `--distribution` | `"default"` | 采样的工具集分布 |
| `--model` | `claude-sonnet-4.6` | 使用的模型 |
| `--base_url` | `https://openrouter.ai/api/v1` | API 基础 URL |
| `--api_key` | (环境变量) | 模型的 API 密钥 |
| `--max_turns` | `10` | 每个 prompt 的最大工具调用迭代次数 |
| `--num_workers` | `4` | 并行工作进程数 |
| `--resume` | `false` | 从断点恢复 |
| `--verbose` | `false` | 启用详细日志 |
| `--max_samples` | 全部 | 仅处理数据集中的前 N 个样本 |
| `--max_tokens` | 模型默认 | 模型单次响应的最大 token 数 |

### 供应商路由 (OpenRouter)

| 参数 | 描述 |
|-----------|-------------|
| `--providers_allowed` | 允许的供应商，逗号分隔（例如 `"anthropic,openai"`） |
| `--providers_ignored` | 忽略的供应商，逗号分隔（例如 `"together,deepinfra"`） |
| `--providers_order` | 优先的供应商顺序，逗号分隔 |
| `--provider_sort` | 排序方式：`"price"`（价格）、`"throughput"`（吞吐量）或 `"latency"`（延迟） |

### 推理控制 (Reasoning Control)

| 参数 | 描述 |
|-----------|-------------|
| `--reasoning_effort` | 推理强度：`xhigh`, `high`, `medium`, `low`, `minimal`, `none` |
| `--reasoning_disabled` | 完全禁用推理/思考 token |

### 高级选项

| 参数 | 描述 |
|-----------|-------------|
| `--ephemeral_system_prompt` | 执行期间使用但**不**保存到轨迹中的系统提示词 |
| `--log_prefix_chars` | 日志预览中显示的字符数（默认：100） |
| `--prefill_messages_file` | 包含用于 few-shot 引导的 prefill 消息的 JSON 文件路径 |

## 工具集分布 (Toolset Distributions)

每个 prompt 都会从一个**分布 (distribution)** 中随机采样一组工具集。这确保了训练数据能覆盖多样化的工具组合。使用 `--list_distributions` 可以查看所有可用分布。

在当前实现中，分布会为**每个单独的工具集**分配一个概率。采样器独立地对每个工具集进行随机选择，并确保至少有一个工具集被启用。这与手动编写的预设组合表不同。

## 输出格式

所有输出都保存在 `data/<run_name>/` 目录下：

```text
data/my_run/
├── trajectories.jsonl    # 最终合并的输出（合并所有批次）
├── batch_0.jsonl         # 单个批次的结果
├── batch_1.jsonl
├── ...
├── checkpoint.json       # 恢复断点的记录文件
└── statistics.json       # 聚合的工具使用统计
```

### 轨迹格式 (Trajectory Format)

`trajectories.jsonl` 中的每一行都是一个 JSON 对象：

```json
{
  "prompt_index": 42,
  "conversations": [
    {"from": "human", "value": "Write a function..."},
    {"from": "gpt", "value": "I'll create that function...",
     "tool_calls": [...]},
    {"from": "tool", "value": "..."},
    {"from": "gpt", "value": "Here's the completed function..."}
  ],
  "metadata": {
    "batch_num": 2,
    "timestamp": "2026-01-15T10:30:00",
    "model": "anthropic/claude-sonnet-4.6"
  },
  "completed": true,
  "partial": false,
  "api_calls": 3,
  "toolsets_used": ["terminal", "file"],
  "tool_stats": {
    "terminal": {"count": 2, "success": 2, "failure": 0},
    "read_file": {"count": 1, "success": 1, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0
  }
}
```

`conversations` 字段使用类似 ShareGPT 的格式，包含 `from` 和 `value` 字段。工具统计信息经过归一化处理，包含所有可能的工具（默认值为零），以确保与 HuggingFace 数据集的架构兼容。

## 断点续传 (Checkpointing)

批量运行器具有强大的断点续传机制以实现容错：

- **断点文件：** 每个批次完成后保存，记录哪些 prompt 索引已完成。
- **基于内容的恢复：** 使用 `--resume` 时，运行器会扫描现有的批次文件，并通过实际文本内容（而不只是索引）匹配已完成的 prompt。即使数据集顺序发生变化，也能实现恢复。
- **失败的 prompt：** 只有成功完成的 prompt 会被标记为已完成 —— 失败的 prompt 将在恢复运行时重试。
- **批次合并：** 完成后，所有批次文件（包括之前运行的文件）都会合并到单个 `trajectories.jsonl` 中。

### 恢复运行的工作原理

1. 扫描所有 `batch_*.jsonl` 文件以查找已完成的 prompt（通过内容匹配）。
2. 过滤数据集，排除已完成的 prompt。
3. 对剩余的 prompt 重新分批。
4. 仅处理剩余的 prompt。
5. 将所有批次文件（旧的和新的）合并到最终输出中。

## 质量过滤

批量运行器会自动应用质量过滤：

- **无推理过滤：** 如果 Assistant 的所有轮次都不包含推理内容（没有 `<REASONING_SCRATCHPAD>` 或原生的思考 token），该样本将被丢弃。
- **损坏条目过滤：** 在最终合并期间，会过滤掉包含幻觉工具名称（不在有效工具列表中）的条目。
- **推理统计：** 追踪整个运行过程中包含/不包含推理的轮次百分比。

## 统计信息

完成后，运行器会打印详细的统计信息：

- **工具使用：** 每个工具的调用次数、成功/失败率。
- **推理覆盖率：** 包含推理的 Assistant 轮次百分比。
- **丢弃样本：** 因缺乏推理而被过滤掉的样本数量。
- **耗时：** 总处理时间。

统计信息也会保存到 `statistics.json` 中以便进行程序化分析。

## 使用场景

### 训练数据生成

生成用于微调的多样化工具使用轨迹：

```bash
python batch_runner.py \
    --dataset_file=data/coding_prompts.jsonl \
    --batch_size=20 \
    --run_name=coding_v1 \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=8 \
    --distribution=default \
    --max_turns=15
```

### 模型评估

评估模型在标准化 prompt 下使用工具的能力：

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### 每个 Prompt 独立的容器镜像
对于需要特定环境的基准测试（benchmarks），每个 prompt 都可以指定自己的容器镜像：

```jsonl
{"prompt": "Install numpy and compute eigenvalues of a 3x3 matrix", "image": "python:3.11-slim"}
{"prompt": "Compile this Rust program and run it", "image": "rust:1.75"}
{"prompt": "Set up a Node.js Express server", "image": "node:20-alpine", "cwd": "/app"}
```

批处理运行器（batch runner）在运行每个 prompt 之前，会先验证 Docker 镜像是否可用。
