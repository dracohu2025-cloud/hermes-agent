---
title: "Axolotl — Axolotl: YAML 大语言模型微调（LoRA、DPO、GRPO）"
sidebar_label: "Axolotl"
description: "Axolotl：YAML 大语言模型微调（LoRA、DPO、GRPO）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="axolotl"></a>
# Axolotl

Axolotl：YAML 大语言模型微调（LoRA、DPO、GRPO）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/axolotl` 安装 |
| 路径 | `optional-skills/mlops/training/axolotl` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `axolotl`、`torch`、`transformers`、`datasets`、`peft`、`accelerate`、`deepspeed` |
| 平台 | linux、macos |
| 标签 | `Fine-Tuning`、`Axolotl`、`LLM`、`LoRA`、`QLoRA`、`DPO`、`KTO`、`ORPO`、`GRPO`、`YAML`、`HuggingFace`、`DeepSpeed`、`Multimodal` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这就是 Agent 在技能激活时看到的指令。
:::

<a id="axolotl-skill"></a>
# Axolotl 技能

<a id="what-s-inside"></a>
## 包含内容

使用 Axolotl 微调大语言模型的专家指南——YAML 配置、100 多个模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持。

提供基于官方文档的综合 Axolotl 开发支持。

<a id="when-to-use-this-skill"></a>
## 何时使用该技能

以下情况应触发此技能：
- 正在使用 Axolotl
- 询问 Axolotl 的功能或 API
- 实现 Axolotl 解决方案
- 调试 Axolotl 代码
- 学习 Axolotl 最佳实践

<a id="quick-reference"></a>
## 快速参考

<a id="common-patterns"></a>
### 常见模式

**模式 1：** 要验证训练任务是否存在可接受的数据传输速度，运行 NCCL 测试可以帮助定位瓶颈，例如：

```
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

**模式 2：** 在 Axolotl 的 YAML 中配置模型使用 FSDP。例如：

```
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

**模式 3：** `context_parallel_size` 应该是总 GPU 数量的约数。例如：

```
context_parallel_size
```

**模式 4：** 例如：
- 使用 8 个 GPU，无序列并行：每步处理 8 个不同的批次
- 使用 8 个 GPU，`context_parallel_size=4`：每步仅处理 2 个不同的批次（每个批次跨 4 个 GPU 拆分）
- 如果每个 GPU 的 `micro_batch_size` 为 2，则全局 batch size 从 16 降至 4

```
context_parallel_size=4
```

**模式 5：** 在配置中设置 `save_compressed: true` 可以以压缩格式保存模型，这样会：
- 减少约 40% 的磁盘空间占用
- 保持与 vLLM 的兼容性以加速推理
- 保持与 llmcompressor 的兼容性以便进一步优化（例如量化）

```
save_compressed: true
```

**模式 6：** 注意：不必将集成放到 integrations 文件夹中。它可以放在任何位置，只要它在 Python 环境的某个包中安装即可。示例见此仓库：https://github.com/axolotl-ai-cloud/diff-transformer
```
integrations
```

**模式 7：** 处理单样本和批处理数据。  
- 单样本：`sample['input_ids']` 是 `list[int]` 类型  
- 批处理数据：`sample['input_ids']` 是 `list[list[int]]` 类型  

```
utils.trainer.drop_long_seq(sample, sequence_len=2048, min_sequence_len=2)
```

<a id="example-code-patterns"></a>
### 示例代码模式

**示例 1** (python):
```python
cli.cloud.modal_.ModalCloud(config, app=None)
```

**示例 2** (python):
```python
cli.cloud.modal_.run_cmd(cmd, run_folder, volumes=None)
```

**示例 3** (python):
```python
core.trainers.base.AxolotlTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

**示例 4** (python):
```python
core.trainers.base.AxolotlTrainer.log(logs, start_time=None)
```

**示例 5** (python):
```python
prompt_strategies.input_output.RawInputOutputPrompter()
```

<a id="reference-files"></a>
## 参考文件

本技能包含 `references/` 中全面的文档：

- **api.md** - API 文档
- **dataset-formats.md** - 数据集格式文档
- **other.md** - 其他文档

需要详细信息时，使用 `view` 命令阅读相应的参考文件。

<a id="working-with-this-skill"></a>
## 使用本技能

<a id="for-beginners"></a>
### 初学者
从 `getting_started` 或 `tutorials` 参考文件开始，了解基础概念。

<a id="for-specific-features"></a>
### 特定功能
使用相应的分类参考文件（如 `api`、`guides` 等）获取详细信息。

<a id="for-code-examples"></a>
### 代码示例
上方的快速参考部分包含从官方文档中提取的常见模式。

<a id="resources"></a>
## 资源

<a id="references"></a>
### references/
从官方来源提取的结构化文档。这些文件包含：
- 详细说明
- 带语言注释的代码示例
- 原始文档链接
- 便于快速导航的目录

<a id="scripts"></a>
### scripts/
在此添加辅助脚本，用于常见自动化任务。

<a id="assets"></a>
### assets/
在此添加模板、样板文件或示例项目。

<a id="notes"></a>
## 备注

- 本技能是从官方文档自动生成的
- 参考文件保留了源文档的结构和示例
- 代码示例包含语言检测以实现更好的语法高亮
- 快速参考模式是从文档中的常见使用示例提取的

<a id="updating"></a>
## 更新

如需使用更新后的文档刷新本技能：
1. 使用相同配置重新运行爬取器
2. 技能将使用最新信息重建
