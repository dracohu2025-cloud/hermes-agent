---
title: "计划 — 计划模式：将 Markdown 计划写入"
sidebar_label: "计划"
description: "计划模式：将 Markdown 计划写入"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 计划 {#plan}

计划模式：将 Markdown 计划写入 .hermes/plans/，不执行。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/plan` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `planning`, `plan-mode`, `implementation`, `workflow` |
| 相关技能 | [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# 计划模式 {#plan-mode}

当用户想要一个计划而不是执行时，使用此技能。

## 核心行为 {#core-behavior}

在此轮交互中，你仅负责规划。

- 不要实现代码。
- 不要编辑除计划 Markdown 文件以外的项目文件。
- 不要运行会改变状态的终端命令、提交、推送或执行外部操作。
- 必要时，你可以使用只读命令/工具检查仓库或其他上下文。
- 你的交付物是一个 Markdown 计划，保存在活动工作区下的 `.hermes/plans/` 目录中。

## 输出要求 {#output-requirements}

编写一个具体且可执行的 Markdown 计划。

在相关时，包含以下内容：
- 目标
- 当前上下文 / 假设
- 建议的方法
- 逐步计划
- 可能更改的文件
- 测试 / 验证
- 风险、权衡和未解决的问题

如果任务与代码相关，请包含确切的文件路径、可能的测试目标和验证步骤。

## 保存位置 {#save-location}

使用 `write_file` 将计划保存到：
- `.hermes/plans/YYYY-MM-DD_HHMMSS-&lt;slug&gt;.md`

将其视为相对于活动工作目录/后端工作区的路径。Hermes 文件工具是后端感知的，因此使用此相对路径可将计划与工作区一起保存在本地、docker、ssh、modal 和 daytona 后端上。

如果运行时提供了特定的目标路径，请使用该确切路径。
如果没有，则在 `.hermes/plans/` 下自行创建一个合理的时间戳文件名。

## 交互风格 {#interaction-style}

- 如果请求足够清晰，直接编写计划。
- 如果没有明确的指令伴随 `/plan`，则从当前对话上下文中推断任务。
- 如果确实描述不清，请提出一个简短的澄清问题，而不是猜测。
- 保存计划后，简要回复你计划了什么以及保存的路径。
