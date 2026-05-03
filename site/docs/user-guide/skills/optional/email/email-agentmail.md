---
title: "Agentmail — 通过 AgentMail 为 Agent 提供专属邮箱"
sidebar_label: "Agentmail"
description: "通过 AgentMail 为 Agent 提供专属邮箱"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Agentmail {#agentmail}

通过 AgentMail 为 Agent 提供专属邮箱。使用 Agent 拥有的邮箱地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理邮件。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/email/agentmail` 安装 |
| 路径 | `optional-skills/email/agentmail` |
| 版本 | `1.0.0` |
| 标签 | `email`, `communication`, `agentmail`, `mcp` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# AgentMail — Agent 拥有的邮箱 {#agentmail-agent-owned-email-inboxes}

## 前提条件 {#requirements}

- **AgentMail API 密钥**（必需）— 在 https://console.agentmail.to 注册（免费套餐：3 个邮箱，每月 3000 封邮件；付费套餐每月 20 美元起）
- Node.js 18+（用于 MCP 服务器）

## 何时使用 {#when-to-use}
当你需要以下功能时使用此技能：
- 为 Agent 提供专属邮箱地址
- 代表 Agent 自主发送邮件
- 接收和阅读收到的邮件
- 管理邮件线程和对话
- 通过邮件注册服务或进行身份验证
- 通过邮件与其他 Agent 或人类通信

此技能不用于读取用户的个人邮件（请使用 himalaya 或 Gmail 实现）。
AgentMail 为 Agent 提供自己的身份和邮箱。

## 设置 {#setup}

### 1. 获取 API 密钥 {#1-get-an-api-key}
- 前往 https://console.agentmail.to
- 创建账户并生成 API 密钥（以 `am_` 开头）

### 2. 配置 MCP 服务器 {#2-configure-mcp-server}
添加到 `~/.hermes/config.yaml`（粘贴你的实际密钥 — MCP 环境变量不会从 .env 展开）：
```yaml
mcp_servers:
  agentmail:
    command: "npx"
    args: ["-y", "agentmail-mcp"]
    env:
      AGENTMAIL_API_KEY: "am_your_key_here"
```

### 3. 重启 Hermes {#3-restart-hermes}
```bash
hermes
```
所有 11 个 AgentMail 工具现在会自动可用。

## 可用工具（通过 MCP） {#available-tools-via-mcp}

| 工具 | 描述 |
|------|------|
| `list_inboxes` | 列出所有 Agent 邮箱 |
| `get_inbox` | 获取特定邮箱的详细信息 |
| `create_inbox` | 创建新邮箱（获得一个真实的邮箱地址） |
| `delete_inbox` | 删除邮箱 |
| `list_threads` | 列出邮箱中的邮件线程 |
| `get_thread` | 获取特定邮件线程 |
| `send_message` | 发送新邮件 |
| `reply_to_message` | 回复现有邮件 |
| `forward_message` | 转发邮件 |
| `update_message` | 更新邮件标签/状态 |
| `get_attachment` | 下载邮件附件 |

## 操作步骤 {#procedure}

### 创建邮箱并发送邮件 {#create-an-inbox-and-send-an-email}
1. 创建专用邮箱：
   - 使用 `create_inbox` 并指定用户名（例如 `hermes-agent`）
   - Agent 获得地址：`hermes-agent@agentmail.to`
2. 发送邮件：
   - 使用 `send_message`，参数包括 `inbox_id`、`to`、`subject`、`text`
3. 检查回复：
   - 使用 `list_threads` 查看收到的对话
   - 使用 `get_thread` 阅读特定线程
### 检查收到的邮件 {#check-incoming-email}
1. 使用 `list_inboxes` 找到你的收件箱 ID
2. 使用 `list_threads` 配合收件箱 ID 查看会话
3. 使用 `get_thread` 读取一个会话及其消息

### 回复邮件 {#reply-to-an-email}
1. 使用 `get_thread` 获取会话
2. 使用 `reply_to_message` 配合消息 ID 和你的回复文本

## 示例工作流 {#example-workflows}

**注册服务：**
```
1. create_inbox (username: "signup-bot")
2. 使用收件箱地址在服务上注册
3. 使用 list_threads 检查验证邮件
4. 使用 get_thread 读取验证码
```

**Agent 向人类发起联系：**
```
1. create_inbox (username: "hermes-outreach")
2. send_message (to: user@example.com, subject: "Hello", text: "...")
3. 使用 list_threads 检查回复
```

## 注意事项 {#pitfalls}
- 免费版限制 3 个收件箱和每月 3,000 封邮件
- 免费版邮件来自 `@agentmail.to` 域名（付费计划可使用自定义域名）
- MCP 服务器需要 Node.js (18+) (`npx -y agentmail-mcp`)
- 必须安装 `mcp` Python 包：`pip install mcp`
- 实时入站邮件（webhooks）需要公网服务器——个人使用建议通过 cronjob 轮询 `list_threads`

## 验证 {#verification}
设置完成后，使用以下命令测试：
```
hermes --toolsets mcp -q "创建一个名为 test-agent 的 AgentMail 收件箱，并告诉我它的邮箱地址"
```
你应该会看到返回的新收件箱地址。

## 参考 {#references}
- AgentMail 文档：https://docs.agentmail.to/
- AgentMail 控制台：https://console.agentmail.to
- AgentMail MCP 仓库：https://github.com/agentmail-to/agentmail-mcp
- 定价：https://www.agentmail.to/pricing
