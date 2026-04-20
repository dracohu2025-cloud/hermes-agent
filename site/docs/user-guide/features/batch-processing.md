---
sidebar_position: 12
title: "批量处理"
description: "大规模生成 Agent 轨迹 — 并行处理、检查点机制及工具集分布"
---

# 批量处理 {#batch-processing}

批量处理功能允许你并行运行 Hermes Agent 来处理成百上千个提示词（prompt），从而生成结构化的轨迹数据。这主要用于**训练数据生成**——即生成带有工具使用统计信息的 ShareGPT 格式轨迹，这些数据可用于微调或评估。

## 概览 {#overview}

批量运行器（`batch_runner.py`）会处理一个 JSONL 格式的提示词数据集，让每个提示词都通过一个具备工具访问权限的完整 Agent 会话进行处理。每个提示词都有其独立的运行环境。输出结果为结构化的轨迹数据，包含完整的对话历史、工具调用统计信息以及推理覆盖率指标。

## 快速开始 {#quick-start}

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

# 列出可用的工具集分布
python batch_runner.py --list_distributions
```

## 数据集格式 {#dataset-format}

输入数据集是一个 JSONL 文件（每行一个 JSON 对象）。每个条目必须包含一个 `prompt` 字段：

```jsonl
{"prompt": "Write a Python function that finds the longest palindromic substring"}
{"prompt": "Create a REST API endpoint for user authentication using Flask"}
{"prompt": "Debug this error: TypeError: cannot unpack non-iterable NoneType object"}
```

条目还可以选择性包含：
- `image` 或 `docker_image`：用于此提示词沙盒的容器镜像（适用于 Docker、Modal 和 Singularity 后端）
- `cwd`：任务终端会话的工作目录覆盖设置

## 配置选项 {#configuration-options}

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--dataset_file` | (必填) | JSONL 数据集路径 |
| `--batch_size` | (必填) | 每个批次的提示词数量 |
| `--run_name` | (必填) | 本次运行的名称（用于输出目录和检查点） |
| `--distribution` | `"default"` | 用于采样的工具集分布 |
| `--model` | `claude-sonnet-4.6` | 使用的模型 |
| `--base_url` | `https://openrouter.ai/api/v1` | API 基础 URL |
| `--api_key` | (环境变量) | 模型的 API 密钥 |
| `--max_turns` | `10` | 每个提示词的最大工具调用迭代次数 |
| `--num_workers` | `4` | 并行工作进程数 |
| `--resume` | `false` | 从检查点恢复 |
| `--verbose` | `false` | 启用详细日志记录 |
| `--max_samples` | all | 仅处理数据集中的前 N 个样本 |
| `--max_tokens` | 模型默认值 | 模型响应的最大 token 数 |

### 提供商路由 (OpenRouter) {#provider-routing-openrouter}

| 参数 | 描述 |
|-----------|-------------|
| `--providers_allowed` | 允许的提供商列表（逗号分隔，例如 `"anthropic,openai"`） |
| `--providers_ignored` | 忽略的提供商列表（逗号分隔，例如 `"together,deepinfra"`） |
| `--providers_order` | 首选提供商顺序（逗号分隔） |
| `--provider_sort` | 按 `"price"`（价格）、`"throughput"`（吞吐量）或 `"latency"`（延迟）排序 |

### 推理控制 {#reasoning-control}

| 参数 | 描述 |
|-----------|-------------|
| `--reasoning_effort` | 推理努力程度：`none`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| `--reasoning_disabled` | 完全禁用推理/思考 token |

### 高级选项 {#advanced-options}

| 参数 | 描述 |
|-----------|-------------|
| `--ephemeral_system_prompt` | 执行期间使用但不会保存到轨迹中的系统提示词 |
| `--log_prefix_chars` | 日志预览中显示的字符数（默认：100） |
| `--prefill_messages_file` | 包含用于少样本引导（few-shot priming）的预填充消息的 JSON 文件路径 |

## 工具集分布 {#toolset-distributions}

每个提示词都会从一个**分布（distribution）**中随机采样一组工具集。这确保了训练数据涵盖了多样的工具组合。使用 `--list_distributions` 查看所有可用的分布。

在当前的实现中，分布会为**每个单独的工具集**分配一个概率。采样器会独立地对每个工具集进行投掷，然后确保至少启用一个工具集。这与手动编写的预构建组合表有所不同。

## 输出格式 {#output-format}

所有输出都存放在 `data/<run_name>/` 中：

```text
data/my_run/
├── trajectories.jsonl    # 合并后的最终输出（所有批次已合并）
├── batch_0.jsonl         # 单个批次结果
├── batch_1.jsonl
├── ...
├── checkpoint.json       # 恢复检查点
└── statistics.json       # 汇总的工具使用统计信息
```

### 轨迹格式 {#trajectory-format}

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

`conversations` 字段使用类似 ShareGPT 的格式，包含 `from` 和 `value` 字段。工具统计信息已标准化，包含所有可能的工具并以零作为默认值，确保条目间架构一致，从而兼容 HuggingFace 数据集。

## 检查点机制 {#checkpointing}

批量运行器具有强大的检查点机制以实现容错：

- **检查点文件：** 在每个批次完成后保存，跟踪哪些提示词索引已完成
- **基于内容的恢复：** 使用 `--resume` 时，运行器会扫描现有的批次文件，并根据实际文本内容（而非仅索引）匹配已完成的提示词，即使数据集顺序发生变化也能实现恢复
- **失败的提示词：** 只有成功完成的提示词才会被标记为已完成——失败的提示词将在恢复时重试
- **批次合并：** 完成后，所有批次文件（包括之前运行产生的）都会合并为一个 `trajectories.jsonl`

### 恢复机制的工作原理 {#how-resume-works}

1. 扫描所有 `batch_*.jsonl` 文件以查找已完成的提示词（通过内容匹配）
2. 过滤数据集以排除已完成的提示词
3. 对剩余的提示词重新分批
4. 仅处理剩余的提示词
5. 将所有批次文件（旧文件 + 新文件）合并为最终输出

## 质量过滤 {#quality-filtering}

批量运行器应用了自动质量过滤：

- **无推理过滤：** 丢弃那些没有任何助手轮次包含推理（没有 `<REASONING_SCRATCHPAD>` 或原生思考 token）的样本
- **损坏条目过滤：** 在最终合并期间，过滤掉包含幻觉工具名称（不在有效工具列表中）的条目
- **推理统计：** 跟踪整个运行过程中包含/不包含推理的轮次百分比

## 统计信息 {#statistics}

完成后，运行器会打印全面的统计信息：

- **工具使用：** 每个工具的调用次数、成功/失败率
- **推理覆盖率：** 包含推理的助手轮次百分比
- **丢弃的样本：** 因缺乏推理而被过滤的样本数量
- **持续时间：** 总处理时间

统计信息也会保存到 `statistics.json` 中，以便进行程序化分析。

## 使用场景 {#use-cases}

### 训练数据生成 {#training-data-generation}

生成多样的工具使用轨迹以进行微调：

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

### 模型评估 {#model-evaluation}

评估模型在标准化提示词下使用工具的表现：

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### 每个提示词的容器镜像 {#per-prompt-container-images}
对于需要特定环境的基准测试，每个 prompt 都可以指定其专属的容器镜像：

```jsonl
{"prompt": "Install numpy and compute eigenvalues of a 3x3 matrix", "image": "python:3.11-slim"}
{"prompt": "Compile this Rust program and run it", "image": "rust:1.75"}
{"prompt": "Set up a Node.js Express server", "image": "node:20-alpine", "cwd": "/app"}
```

批量运行程序（batch runner）会在执行每个 prompt 之前验证 Docker 镜像是否可访问。
