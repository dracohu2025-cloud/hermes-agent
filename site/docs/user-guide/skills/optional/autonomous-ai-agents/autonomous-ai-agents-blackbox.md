---
title: "Blackbox — 将编码任务委托给 Blackbox AI CLI Agent"
sidebar_label: "Blackbox"
description: "将编码任务委托给 Blackbox AI CLI Agent"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="blackbox"></a>
# Blackbox

将编码任务委托给 Blackbox AI CLI Agent。这是一个多模型 Agent，内置判断机制，能通过多个 LLM 执行任务并选出最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/blackbox` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/blackbox` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Blackbox`, `Multi-Agent`, `Judge`, `Multi-Model` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这即是在技能激活时 Agent 所看到指令。
:::

<a id="blackbox-cli"></a>
# Blackbox CLI

通过 Hermes 终端将编码任务委托给 [Blackbox AI](https://www.blackbox.ai/)。Blackbox 是一个多模型编码 Agent CLI，它可以将任务分派给多个 LLM（Claude、Codex、Gemini、Blackbox Pro），并使用判断机制选择最佳实现方案。

该 CLI 是[开源的](https://github.com/blackboxaicode/cli)（GPL-3.0，TypeScript，从 Gemini CLI 复刻而来），支持交互式会话、非交互式一次性任务、检查点、MCP 以及视觉模型切换。

<a id="prerequisites"></a>
## 前置要求

- 已安装 Node.js 20+
- 已安装 Blackbox CLI：`npm install -g @blackboxai/cli`
- 或从源码安装：
  ```
  git clone https://github.com/blackboxaicode/cli.git
  cd cli && npm install && npm install -g .
  ```
- 从 [app.blackbox.ai/dashboard](https://app.blackbox.ai/dashboard) 获取 API 密钥
- 配置：运行 `blackbox configure` 并输入你的 API 密钥
- 在终端调用中使用 `pty=true` —— Blackbox CLI 是一个交互式终端应用

<a id="one-shot-tasks"></a>
## 一次性任务

```
terminal(command="blackbox --prompt '为 Express API 添加带有刷新令牌的 JWT 认证'", workdir="/path/to/project", pty=true)
```

快速临时任务：
```
terminal(command="cd $(mktemp -d) && git init && blackbox --prompt '用 SQLite 构建一个待办事项 REST API'", pty=true)
```

<a id="background-mode-long-tasks"></a>
## 后台模式（长时间任务）

对于需要几分钟才能完成的任务，使用后台模式以便你监控进度：

```
# 在后台启动，使用 PTY
terminal(command="blackbox --prompt '重构认证模块以使用 OAuth 2.0'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Blackbox 提问，发送输入
process(action="submit", session_id="<id>", data="yes")

# 如果需要，终止进程
process(action="kill", session_id="<id>")
```
<a id="checkpoints-resume"></a>
## 检查点与恢复

Blackbox CLI 内置了检查点支持，可以暂停和恢复任务：

```
# 任务完成后，Blackbox 会显示一个检查点标签
# 通过后续任务恢复：
terminal(command="blackbox --resume-checkpoint 'task-abc123-2026-03-06' --prompt '现在给端点添加限流功能'", workdir="~/project", pty=true)
```

<a id="session-commands"></a>
## 会话命令

在交互式会话中，可以使用以下命令：

| 命令 | 作用 |
|---------|--------|
| `/compress` | 压缩对话历史以节省 token |
| `/clear` | 清除历史记录，重新开始 |
| `/stats` | 查看当前 token 使用量 |
| `Ctrl+C` | 取消当前操作 |

<a id="pr-reviews"></a>
## PR 审查

克隆到临时目录，避免修改工作树：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && blackbox --prompt '对照 main 分支审查这个 PR。检查是否存在 bug、安全问题和代码质量问题。'", pty=true)
```

<a id="parallel-work"></a>
## 并行工作

为独立任务启动多个 Blackbox 实例：

```
terminal(command="blackbox --prompt '修复登录 bug'", workdir="/tmp/issue-1", background=true, pty=true)
terminal(command="blackbox --prompt '为认证模块添加单元测试'", workdir="/tmp/issue-2", background=true, pty=true)

# 监控所有任务
process(action="list")
```

<a id="multi-model-mode"></a>
## 多模型模式

Blackbox 的独特功能是让多个模型运行同一个任务，并对结果进行评判。通过 `blackbox configure` 配置要使用的模型——选择多个提供商即可启用 Chairman/评判工作流，CLI 会评估不同模型的输出并选出最佳结果。

<a id="key-flags"></a>
## 关键标志

| 标志 | 作用 |
|------|--------|
| `--prompt "task"` | 非交互式一次性执行 |
| `--resume-checkpoint "tag"` | 从保存的检查点恢复 |
| `--yolo` | 自动批准所有操作和模型切换 |
| `blackbox session` | 启动交互式聊天会话 |
| `blackbox configure` | 更改设置、提供商、模型 |
| `blackbox info` | 显示系统信息 |

<a id="vision-support"></a>
## 视觉支持

Blackbox 会自动检测输入中的图像，并可切换到多模态分析。VLM 模式：
- `"once"` — 仅对当前查询切换模型
- `"session"` — 对整个会话切换模型
- `"persist"` — 保持当前模型（不切换）

<a id="token-limits"></a>
## Token 限制

通过 `.blackboxcli/settings.json` 控制 token 使用量：
```json
{
  "sessionTokenLimit": 32000
}
```

<a id="rules"></a>
## 规则

1. **始终使用 `pty=true`** — Blackbox CLI 是一个交互式终端应用，没有 PTY 会挂起
2. **使用 `workdir`** — 让 Agent 专注于正确的目录
3. **长时间任务使用后台模式** — 使用 `background=true` 并通过 `process` 工具监控
4. **不要干扰** — 使用 `poll`/`log` 监控，不要因为任务慢就终止会话
5. **报告结果** — 完成后，检查发生了什么变化，并为用户总结
6. **积分需要花钱** — Blackbox 使用基于积分的系统；多模型模式消耗积分更快
7. **检查前置条件** — 在尝试委派任务前，确认 `blackbox` CLI 已安装
