---
title: "Blackbox — 将编码任务委托给 Blackbox AI CLI Agent"
sidebar_label: "Blackbox"
description: "将编码任务委托给 Blackbox AI CLI Agent"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blackbox {#blackbox}

将编码任务委托给 Blackbox AI CLI Agent。这是一个多模型 Agent，内置评判机制，可通过多个 LLM 运行任务并选出最佳结果。需要安装 blackbox CLI 并拥有 Blackbox AI API 密钥。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/blackbox` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/blackbox` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 标签 | `Coding-Agent`, `Blackbox`, `Multi-Agent`, `Judge`, `Multi-Model` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Blackbox CLI {#blackbox-cli}

通过 Hermes 终端将编码任务委托给 [Blackbox AI](https://www.blackbox.ai/)。Blackbox 是一个多模型编码 Agent CLI，可将任务分发给多个 LLM（Claude、Codex、Gemini、Blackbox Pro），并使用评判机制选择最佳实现。

该 CLI 是[开源的](https://github.com/blackboxaicode/cli)（GPL-3.0，TypeScript，从 Gemini CLI 分支而来），支持交互式会话、非交互式一次性任务、检查点、MCP 以及视觉模型切换。

## 前提条件 {#prerequisites}

- 已安装 Node.js 20+
- 已安装 Blackbox CLI：`npm install -g @blackboxai/cli`
- 或从源码安装：
  ```
  git clone https://github.com/blackboxaicode/cli.git
  cd cli && npm install && npm install -g .
  ```
- 从 [app.blackbox.ai/dashboard](https://app.blackbox.ai/dashboard) 获取 API 密钥
- 配置：运行 `blackbox configure` 并输入你的 API 密钥
- 在终端调用中使用 `pty=true` — Blackbox CLI 是一个交互式终端应用

## 一次性任务 {#one-shot-tasks}

```
terminal(command="blackbox --prompt '为 Express API 添加带有刷新令牌的 JWT 认证'", workdir="/path/to/project", pty=true)
```

快速临时任务：
```
terminal(command="cd $(mktemp -d) && git init && blackbox --prompt '使用 SQLite 构建一个待办事项 REST API'", pty=true)
```

## 后台模式（长时间任务） {#background-mode-long-tasks}

对于需要几分钟的任务，使用后台模式以便监控进度：

```
# 在后台启动，使用 PTY
terminal(command="blackbox --prompt '将认证模块重构为使用 OAuth 2.0'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Blackbox 提问，发送输入
process(action="submit", session_id="<id>", data="yes")

# 如果需要，终止任务
process(action="kill", session_id="<id>")
```
## 检查点与恢复 {#checkpoints-resume}

Blackbox CLI 内置了检查点支持，可以暂停和恢复任务：

```
# 任务完成后，Blackbox 会显示一个检查点标签
# 通过后续任务恢复：
terminal(command="blackbox --resume-checkpoint 'task-abc123-2026-03-06' --prompt 'Now add rate limiting to the endpoints'", workdir="~/project", pty=true)
```

## 会话命令 {#session-commands}

在交互式会话中，可以使用以下命令：

| 命令 | 作用 |
|---------|--------|
| `/compress` | 压缩对话历史以节省 token |
| `/clear` | 清空历史，重新开始 |
| `/stats` | 查看当前 token 使用量 |
| `Ctrl+C` | 取消当前操作 |

## PR 审查 {#pr-reviews}

克隆到临时目录，避免修改工作树：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && blackbox --prompt 'Review this PR against main. Check for bugs, security issues, and code quality.'", pty=true)
```

## 并行任务 {#parallel-work}

为独立任务启动多个 Blackbox 实例：

```
terminal(command="blackbox --prompt 'Fix the login bug'", workdir="/tmp/issue-1", background=true, pty=true)
terminal(command="blackbox --prompt 'Add unit tests for auth'", workdir="/tmp/issue-2", background=true, pty=true)

# 监控所有任务
process(action="list")
```

## 多模型模式 {#multi-model-mode}

Blackbox 的独特功能是让多个模型运行同一任务并评判结果。通过 `blackbox configure` 配置要使用的模型——选择多个提供商即可启用 Chairman/judge 工作流，CLI 会评估不同模型的输出并选出最佳结果。

## 关键标志 {#key-flags}

| 标志 | 作用 |
|------|--------|
| `--prompt "task"` | 非交互式一次性执行 |
| `--resume-checkpoint "tag"` | 从保存的检查点恢复 |
| `--yolo` | 自动批准所有操作和模型切换 |
| `blackbox session` | 启动交互式聊天会话 |
| `blackbox configure` | 更改设置、提供商、模型 |
| `blackbox info` | 显示系统信息 |

## 视觉支持 {#vision-support}

Blackbox 会自动检测输入中的图像，并可切换到多模态分析。VLM 模式：
- `"once"` — 仅当前查询切换模型
- `"session"` — 整个会话切换
- `"persist"` — 保持当前模型（不切换）

## Token 限制 {#token-limits}

通过 `.blackboxcli/settings.json` 控制 token 使用量：
```json
{
  "sessionTokenLimit": 32000
}
```

## 规则 {#rules}

1. **始终使用 `pty=true`** — Blackbox CLI 是交互式终端应用，没有 PTY 会挂起
2. **使用 `workdir`** — 让 Agent 专注于正确的目录
3. **长时间任务使用后台** — 使用 `background=true` 并通过 `process` 工具监控
4. **不要干扰** — 使用 `poll`/`log` 监控，不要因为任务慢就终止会话
5. **报告结果** — 完成后检查变更并总结给用户
6. **积分需要花钱** — Blackbox 使用积分制；多模型模式消耗积分更快
7. **检查前提条件** — 在尝试委派之前，确认 `blackbox` CLI 已安装
