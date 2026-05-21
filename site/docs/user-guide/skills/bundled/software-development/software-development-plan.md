---
title: "Plan — Plan 模式：将 Markdown 计划写入"
sidebar_label: "Plan"
description: "Plan 模式：将 Markdown 计划写入"
---

{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="plan"></a>
# Plan

Plan 模式：将 Markdown 计划写入 .hermes/plans/，不执行。

<a id="skill-metadata"></a>
## Skill 元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/plan` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `planning`, `plan-mode`, `implementation`, `workflow` |
| 相关技能 | [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans)、[`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

<a id="plan-mode"></a>
# Plan 模式

当用户需要计划而不是执行时，请使用此技能。

<a id="core-behavior"></a>
## 核心行为

在当前回合，你只负责规划。

- 不要实现代码。
- 不要编辑除计划 Markdown 文件以外的项目文件。
- 不要运行会修改状态的终端命令、提交、推送或执行外部操作。
- 你可以使用只读命令/工具检查仓库或其他上下文（如果需要）。
- 你的交付成果是一个保存在当前工作空间 `.hermes/plans/` 目录下的 Markdown 计划。

<a id="output-requirements"></a>
## 输出要求

编写具体且可执行的 Markdown 计划。

在相关的情况下，包含：
- 目标
- 当前上下文 / 假设
- 建议方案
- 逐步计划
- 可能更改的文件
- 测试 / 验证
- 风险、权衡和未解决的问题

如果任务与代码相关，请包含确切的文件路径、可能的测试目标和验证步骤。

<a id="save-location"></a>
## 保存位置

使用 `write_file` 将计划保存到：
- `.hermes/plans/YYYY-MM-DD_HHMMSS-&lt;slug&gt;.md`

将其视为相对于当前工作目录 / 后端工作空间。Hermes 文件工具是后端感知的，因此使用此相对路径可以将计划保留在工作空间中（支持 local、docker、ssh、modal 和 daytona 后端）。

如果运行环境提供了特定的目标路径，请使用该确切路径。
如果没有，则自行在 `.hermes/plans/` 下创建一个合理的时间戳文件名。

<a id="interaction-style"></a>
## 交互风格

- 如果请求足够明确，直接编写计划。
- 如果 `/plan` 没有附带明确的指令，从当前对话上下文中推断任务。
- 如果确实描述不清，请提出一个简短的澄清问题，而不是猜测。
- 保存计划后，简要回复你计划的内容以及保存路径。
