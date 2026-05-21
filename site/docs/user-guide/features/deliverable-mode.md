---
title: 交付模式（聊天中的制品）
sidebar_label: 交付模式
description: Agent 如何将生成的图表、PDF、电子表格及其他文件作为消息平台的原生附件进行投递。
---

<a id="deliverable-mode"></a>
# 交付模式

当 Hermes Agent 在消息网关（Slack、Discord、Telegram、WhatsApp、Signal 等）中运行时，它可以将生成的文件直接投递到聊天中——不是作为用户需要复制的路径，而是作为原生附件。

图表以内嵌图片形式显示。PDF 报告以文件下载形式出现。电子表格以 `.xlsx` 形式上传。Agent 无需编写 `MEDIA:` 标签或做任何特殊操作——它只需生成文件并在回复中提及文件的绝对路径。网关会从文本中提取该路径，将其从可见消息中移除，并以原生方式上传文件。

<a id="how-it-works"></a>
## 工作原理

三个部分协同工作：

1. **Agent 拥有生成文件的工具。** `execute_code` 用于通过 matplotlib 生成图表，`latex-pdf-report` 技能用于生成 PDF，`powerpoint` 技能用于演示文稿，`image_generate` 用于图片，`text_to_speech` 用于音频，等等。

2. **网关扫描 Agent 回复中的文件路径。** 任何以支持的扩展名结尾的绝对路径（`/tmp/...`）或 home 相对路径（`~/...`）都会被提取出来。代码块和内联代码中的路径会被忽略，因此代码示例永远不会被破坏。

3. **网关按文件类型分发。** 图片在平台支持的情况下内嵌显示；视频内嵌显示；音频路由到语音/音频附件；其他所有内容作为文件附件上传。

<a id="supported-file-extensions"></a>
## 支持的文件扩展名

| 类别 | 扩展名 | 投递方式 |
|---|---|---|
| 图片 | `.png .jpg .jpeg .gif .webp .bmp .tiff .svg` | 内嵌显示 |
| 视频 | `.mp4 .mov .avi .mkv .webm` | 内嵌显示（平台支持时） |
| 音频 | `.mp3 .wav .ogg .m4a .flac` | 语音/音频附件 |
| 文档 | `.pdf .docx .doc .odt .rtf .txt .md` | 文件上传 |
| 数据 | `.xlsx .xls .csv .tsv .json .xml .yaml .yml` | 文件上传 |
| 演示文稿 | `.pptx .ppt .odp` | 文件上传 |
| 压缩包 | `.zip .tar .gz .tgz .bz2 .7z` | 文件上传 |
| 网页 | `.html .htm` | 文件上传 |

`.py`、`.log` 及其他源代码文件扩展名被有意排除，这样 Agent 就不会自动投递任意源文件；如果你想向用户发送代码，请使用代码块。

<a id="encouraging-the-agent-to-produce-artifacts"></a>
## 鼓励 Agent 生成制品

Agent 默认不会主动生成制品——它需要知道这一点。有两种方式可以引导它：

**会话级别：** 明确要求（“把对比结果以图表形式发给我”、“将数据以 CSV 格式返回”），或者编写你自己的自定义指令/角色描述，使其在消息平台上倾向于制品风格的回复。

**项目级别：** 在 Agent 工作的项目中的 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` 中添加偏好，或者在你的全局自定义指令 `~/.hermes/config.yaml` 的 `agent.custom_instructions` 下添加。

Agent 需要使用的机制很简单：将文件渲染到绝对路径（例如 `/tmp/q3-revenue.png`），并在回复中以纯文本形式提及该路径。剩下的工作由网关完成。围栏代码块或反引号内的路径会被忽略，因此代码示例永远不会被破坏。
<a id="kanban-artifacts-ride-completion-notifications"></a>
## Kanban：制品伴随任务完成通知

如果你使用Hermes的看板多Agent工作流，工作节点可以在`kanban_complete`调用中附加制品文件：

```python
kanban_complete(
    summary="渲染了Q3收入图表与报告",
    artifacts=[
        "/tmp/q3-revenue.png",
        "/tmp/q3-report.pdf",
    ],
)
```

当网关通知器向订阅了该任务的Slack/Telegram等渠道的接收者发送"任务完成"消息时，它也会将每个制品作为该聊天平台的原生附件上传。人类用户可以在同一位置同时获得交付物和摘要。

如果通知器运行时磁盘上不存在相应文件，则会静默跳过。

<a id="connecting-more-services-with-mcp"></a>
## 通过MCP连接更多服务

除了制品交付管道之外，Agent还可以通过MCP（模型上下文协议）触及其他服务。MCP生态系统为大多数流行工具提供了社区服务器——按需安装即可：

| 服务 | 解锁的功能 |
|---|---|
| **Notion** | 读写Notion页面、数据库、查询工作空间 |
| **GitHub** | Issues、PRs、评论、仓库搜索（超越gh CLI） |
| **Linear** | 工单、项目、周期 |
| **Slack** | 跨工作空间搜索、读取其他频道 |
| **Gmail** | 收件箱分类、发送邮件、标签管理 |
| **Salesforce** | 线索、商机、账户数据 |
| **Snowflake / BigQuery** | 对数据仓库执行SQL |
| **Google Drive** | 文件搜索、内容、共享管理 |

通过`~/.hermes/config.yaml`中的`mcp_servers`部分安装MCP服务器。完整配置指南请参阅[MCP集成](./mcp.md)。

<a id="comparison-to-perplexity-computer-in-slack"></a>
## 与Perplexity Computer in Slack的对比

Perplexity Computer的Slack集成基于相同的思路：Agent生成交付物（图表、PDF、幻灯片）并将其作为原生附件发布回线程中。Hermes Agent的交付物模式在本地提供了相同的面向用户模式：

- 生成发生在用户自己的venv/sandbox中（无远程租户）。
- 文件通过相同的Slack `files.uploadV2` API进入聊天。
- 连接器广度通过MCP实现，而非由400个托管集成组成的精选目录——安装你实际使用的那些。

OAuth令牌保留在用户机器的`auth.json` / `.env`中。没有托管令牌存储。没有多租户microVM。最终结果相同。
