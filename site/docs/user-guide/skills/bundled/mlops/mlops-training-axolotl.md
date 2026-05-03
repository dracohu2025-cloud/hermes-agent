---
title: "Axolotl — Axolotl：YAML LLM 微调（LoRA、DPO、GRPO）"
sidebar_label: "Axolotl"
description: "Axolotl：YAML LLM 微调（LoRA、DPO、GRPO）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Axolotl {#axolotl}

Axolotl：YAML LLM 微调（LoRA、DPO、GRPO）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/training/axolotl` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `axolotl`、`torch`、`transformers`、`datasets`、`peft`、`accelerate`、`deepspeed` |
| 标签 | `Fine-Tuning`、`Axolotl`、`LLM`、`LoRA`、`QLoRA`、`DPO`、`KTO`、`ORPO`、`GRPO`、`YAML`、`HuggingFace`、`DeepSpeed`、`Multimodal` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Axolotl 技能 {#axolotl-skill}

## 内容概览 {#what-s-inside}

使用 Axolotl 微调 LLM 的专家指导——YAML 配置、100+ 模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持。

基于官方文档，提供 Axolotl 开发的全面帮助。

## 何时使用此技能 {#when-to-use-this-skill}

此技能应在以下情况触发：
- 使用 Axolotl 时
- 询问 Axolotl 功能或 API 时
- 实现 Axolotl 解决方案时
- 调试 Axolotl 代码时
- 学习 Axolotl 最佳实践时

## 快速参考 {#quick-reference}

### 常见模式 {#common-patterns}

**模式 1：** 要验证训练作业是否存在可接受的数据传输速度，运行 NCCL 测试有助于定位瓶颈，例如：

```
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

**模式 2：** 在 Axolotl yaml 中配置模型使用 FSDP。例如：

```
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

**模式 3：** `context_parallel_size` 应为 GPU 总数的除数。例如：

```
context_parallel_size
```

**模式 4：** 例如：- 使用 8 个 GPU 且无序列并行：每步处理 8 个不同批次 - 使用 8 个 GPU 且 `context_parallel_size=4`：每步仅处理 2 个不同批次（每个批次分布在 4 个 GPU 上） - 如果每个 GPU 的 `micro_batch_size` 为 2，则全局批次大小从 16 减少到 4

```
context_parallel_size=4
```

**模式 5：** 在配置中设置 `save_compressed: true` 可以压缩格式保存模型，这将：- 减少约 40% 的磁盘空间占用 - 保持与 vLLM 的兼容性以加速推理 - 保持与 llmcompressor 的兼容性以进一步优化（例如量化）

```
save_compressed: true
```

**模式 6：** 注意：不必将集成放在 `integrations` 文件夹中。它可以放在任何位置，只要它作为 Python 环境中的包安装即可。示例见此仓库：https://github.com/axolotl-ai-cloud/diff-transformer

```
integrations
```
**Pattern 7：** 处理单个样本和批量数据。  
- 单个样本：`sample['input_ids']` 是一个 `list[int]`  
- 批量数据：`sample['input_ids']` 是一个 `list[list[int]]`

```
utils.trainer.drop_long_seq(sample, sequence_len=2048, min_sequence_len=2)
```

### 示例代码模式 {#example-code-patterns}

**示例 1**（Python）：
```python
cli.cloud.modal_.ModalCloud(config, app=None)
```

**示例 2**（Python）：
```python
cli.cloud.modal_.run_cmd(cmd, run_folder, volumes=None)
```

**示例 3**（Python）：
```python
core.trainers.base.AxolotlTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

**示例 4**（Python）：
```python
core.trainers.base.AxolotlTrainer.log(logs, start_time=None)
```

**示例 5**（Python）：
```python
prompt_strategies.input_output.RawInputOutputPrompter()
```

## 参考文件 {#reference-files}

该技能在 `references/` 中包含了全面的文档：

- **api.md** - API 文档
- **dataset-formats.md** - 数据集格式文档
- **other.md** - 其他文档

当需要详细信息时，可使用 `view` 命令读取特定的参考文件。

## 使用此技能 {#working-with-this-skill}

### 对于初学者 {#for-beginners}
从 `getting_started` 或 `tutorials` 参考文件开始，了解基础概念。

### 对于特定功能 {#for-specific-features}
使用相应类别的参考文件（如 api、guides 等）获取详细信息。

### 对于代码示例 {#for-code-examples}
上面的快速参考章节包含了从官方文档中提取的常见模式。

## 资源 {#resources}

### references/ {#references}
从官方来源提取的结构化文档。这些文件包含：
- 详细说明
- 带有语言标注的代码示例
- 指向原始文档的链接
- 便于快速导航的目录

### scripts/ {#scripts}
在此添加辅助脚本，用于常见的自动化任务。

### assets/ {#assets}
在此添加模板、样板文件或示例项目。

## 说明 {#notes}

- 此技能是根据官方文档自动生成的
- 参考文件保留了源文档的结构和示例
- 代码示例包含语言检测功能，便于更好的语法高亮
- 快速参考模式从文档中的常见用法示例中提取

## 更新 {#updating}

要使用更新后的文档刷新此技能：
1. 使用相同配置重新运行爬虫
2. 技能将使用最新信息重新构建
