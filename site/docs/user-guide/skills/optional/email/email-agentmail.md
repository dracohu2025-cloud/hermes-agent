---
title: "Agentmail — 通过 AgentMail 为 Agent 提供专属邮件收件箱"
sidebar_label: "Agentmail"
description: "通过 AgentMail 为 Agent 提供专属邮件收件箱"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="agentmail"></a>
# Agentmail

通过 AgentMail 为 Agent 提供专属邮件收件箱。使用 Agent 拥有的邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理邮件。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/email/agentmail` 安装 |
| 路径 | `optional-skills/email/agentmail` |
| 版本 | `1.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `email`, `communication`, `agentmail`, `mcp` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="agentmail-agent-owned-email-inboxes"></a>
# AgentMail — Agent 拥有的邮件收件箱

<a id="requirements"></a>
## 前提条件

- **AgentMail API 密钥**（必需）— 在 https://console.agentmail.to 注册（免费套餐：3 个收件箱，每月 3000 封邮件；付费套餐从每月 20 美元起）
- Node.js 18+（用于 MCP 服务器）

<a id="when-to-use"></a>
## 何时使用
当你需要以下功能时，使用此技能：
- 为 Agent 提供其专属的邮件地址
- 代表 Agent 自主发送邮件
- 接收和阅读收到的邮件
- 管理邮件线程和对话
- 通过邮件注册服务或进行身份验证
- 通过邮件与其他 Agent 或人类通信

此技能不用于读取用户的个人邮件（请使用 himalaya 或 Gmail 实现该功能）。
AgentMail 为 Agent 提供其自己的身份和收件箱。

<a id="setup"></a>
## 设置

<a id="1-get-an-api-key"></a>
### 1. 获取 API 密钥
- 前往 https://console.agentmail.to
- 创建账户并生成 API 密钥（以 `am_` 开头）

<a id="2-configure-mcp-server"></a>
### 2. 配置 MCP 服务器
添加到 `~/.hermes/config.yaml`（粘贴你的实际密钥 — MCP 环境变量不会从 .env 展开）：
```yaml
mcp_servers:
  agentmail:
    command: "npx"
    args: ["-y", "agentmail-mcp"]
    env:
      AGENTMAIL_API_KEY: "am_your_key_here"
```

<a id="3-restart-hermes"></a>
### 3. 重启 Hermes
```bash
hermes
```
所有 11 个 AgentMail 工具现在会自动可用。

<a id="available-tools-via-mcp"></a>
## 可用工具（通过 MCP）

| 工具 | 描述 |
|------|------|
| `list_inboxes` | 列出所有 Agent 收件箱 |
| `get_inbox` | 获取特定收件箱的详细信息 |
| `create_inbox` | 创建新收件箱（获得一个真实的邮件地址） |
| `delete_inbox` | 删除收件箱 |
| `list_threads` | 列出收件箱中的邮件线程 |
| `get_thread` | 获取特定邮件线程 |
| `send_message` | 发送新邮件 |
| `reply_to_message` | 回复现有邮件 |
| `forward_message` | 转发邮件 |
| `update_message` | 更新邮件标签/状态 |
| `get_attachment` | 下载邮件附件 |

<a id="procedure"></a>
## 操作步骤

<a id="create-an-inbox-and-send-an-email"></a>
### 创建收件箱并发送邮件
1. 创建专属收件箱：
   - 使用 `create_inbox` 并指定用户名（例如 `hermes-agent`）
   - Agent 获得地址：`hermes-agent@agentmail.to`
2. 发送邮件：
   - 使用 `send_message` 并指定 `inbox_id`、`to`、`subject`、`text`
3. 检查回复：
   - 使用 `list_threads` 查看收到的对话
   - 使用 `get_thread` 阅读特定线程
<a id="check-incoming-email"></a>
### 检查收件箱
1. 使用 `list_inboxes` 找到你的收件箱 ID
2. 使用 `list_threads` 配合收件箱 ID 查看会话
3. 使用 `get_thread` 读取一个线程及其消息

<a id="reply-to-an-email"></a>
### 回复邮件
1. 使用 `get_thread` 获取线程
2. 使用 `reply_to_message` 配合消息 ID 和回复文本进行回复

<a id="example-workflows"></a>
## 示例工作流

**注册服务：**
```
1. create_inbox (username: "signup-bot")
2. 使用收件箱地址在服务上注册
3. list_threads 检查验证邮件
4. get_thread 读取验证码
```

**Agent 与用户的外联：**
```
1. create_inbox (username: "hermes-outreach")
2. send_message (to: user@example.com, subject: "Hello", text: "...")
3. list_threads 检查是否有回复
```

<a id="pitfalls"></a>
## 注意事项
- 免费套餐限制为 3 个收件箱和每月 3000 封邮件
- 免费套餐的邮件来自 `@agentmail.to` 域名（付费套餐可使用自定义域名）
- MCP 服务器需要 Node.js (18+)（`npx -y agentmail-mcp`）
- 必须安装 `mcp` Python 包：`pip install mcp`
- 实时接收邮件（webhooks）需要公网服务器——个人使用建议通过 cronjob 轮询 `list_threads`

<a id="verification"></a>
## 验证
配置完成后，用以下命令测试：
```
hermes --toolsets mcp -q "创建一个名为 test-agent 的 AgentMail 收件箱，并告诉我它的邮箱地址"
```
你应该会看到返回的新收件箱地址。

<a id="references"></a>
## 参考
- AgentMail 文档：https://docs.agentmail.to/
- AgentMail 控制台：https://console.agentmail.to
- AgentMail MCP 仓库：https://github.com/agentmail-to/agentmail-mcp
- 定价：https://www.agentmail.to/pricing
