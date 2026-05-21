---
title: "Hermes Agent — 配置、扩展或贡献 Hermes Agent"
sidebar_label: "Hermes Agent"
description: "配置、扩展或贡献 Hermes Agent"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="hermes-agent"></a>
# Hermes Agent

配置、扩展或贡献 Hermes Agent。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内嵌（默认安装） |
| 路径 | `skills/autonomous-ai-agents/hermes-agent` |
| 版本 | `2.1.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `hermes`, `setup`, `configuration`, `multi-agent`, `spawning`, `cli`, `gateway`, `development` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`opencode`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其作为指令来执行。
:::

# Hermes Agent

Hermes Agent 是由 Nous Research 开发的开源 AI Agent 框架，可在终端、即时通讯平台及 IDE 中运行。它属于与 Claude Code（Anthropic）、Codex（OpenAI）和 OpenClaw 同类的自主编程与任务执行 Agent，通过工具调用与系统交互。Hermes 支持任何 LLM 提供商（OpenRouter、Anthropic、OpenAI、DeepSeek、本地模型等 15 种以上），并可在 Linux、macOS 和 WSL 上运行。

Hermes 的与众不同之处：

- **通过技能实现自我改进** — Hermes 能将可复用的流程保存为技能，从而从经验中学习。当它解决复杂问题、发现工作流程或收到修正时，可将该知识持久化为技能文档，并在后续会话中加载。技能会随时间积累，让 Agent 更擅长你的特定任务和环境。
- **跨会话的持久记忆** — 能记住你是谁、你的偏好、环境细节以及学到的教训。可插拔的记忆后端（内置、Honcho、Mem0 等）让你自由选择记忆的工作方式。
- **多平台网关** — 同一个 Agent 可运行在 Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Email 等 10 多个平台上，且能完整使用工具，而不仅仅是聊天。
- **提供商无关** — 可中途切换模型和提供商，无需更改任何其他配置。凭据池会自动轮换多个 API 密钥。
- **配置文件** — 可运行多个独立的 Hermes 实例，每个实例拥有独立的配置、会话、技能和记忆。
- **可扩展** — 支持插件、MCP 服务器、自定义工具、Webhook 触发器、定时任务以及整个 Python 生态系统。

人们使用 Hermes 进行软件开发、研究、系统管理、数据分析、内容创作、家庭自动化，以及任何其他需要具备持久上下文和完整系统访问权限的 AI Agent 的场景。

**此技能可帮助你高效使用 Hermes Agent** — 包括设置、配置功能、生成更多 Agent 实例、排查问题、查找合适的命令和设置，以及在你需要扩展或贡献时理解系统的工作原理。
**文档：** https://hermes-agent.nousresearch.com/docs/

<a id="quick-start"></a>
## 快速开始

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 交互式聊天（默认）
hermes

# 单次查询
hermes chat -q "What is the capital of France?"

# 设置向导
hermes setup

# 更改模型/提供商
hermes model

# 健康检查
hermes doctor
```

---

<a id="cli-reference"></a>
## CLI 参考

<a id="global-flags"></a>
### 全局标志

```
hermes [flags] [command]

  --version, -V             显示版本
  --resume, -r SESSION      按ID或标题恢复会话
  --continue, -c [NAME]     按名称恢复，或恢复最近会话
  --worktree, -w            隔离的git worktree模式（并行Agents）
  --skills, -s SKILL        预加载技能（逗号分隔或重复使用）
  --profile, -p NAME        使用指定配置
  --yolo                    跳过危险命令审批
  --pass-session-id         在系统提示中包含会话ID
```

无子命令时默认使用 `chat`。

<a id="chat"></a>
### Chat

```
hermes chat [flags]
  -q, --query TEXT          单次查询，非交互模式
  -m, --model MODEL         模型（例如 anthropic/claude-sonnet-4）
  -t, --toolsets LIST       逗号分隔的工具集
  --provider PROVIDER       强制指定提供商（openrouter、anthropic、nous 等）
  -v, --verbose             详细输出
  -Q, --quiet               隐藏横幅、旋转动画、工具预览
  --checkpoints             启用文件系统检查点（/rollback）
  --source TAG              会话来源标签（默认：cli）
```

<a id="configuration"></a>
### 配置

```
hermes setup [section]      交互式向导（model|terminal|gateway|tools|agent）
hermes model                交互式模型/提供商选择器
hermes config               查看当前配置
hermes config edit          用 $EDITOR 打开 config.yaml
hermes config set KEY VAL   设置配置值
hermes config path          打印 config.yaml 路径
hermes config env-path      打印 .env 路径
hermes config check         检查缺失/过期的配置
hermes config migrate       用新选项更新配置
hermes login [--provider P] OAuth 登录（nous、openai-codex）
hermes logout               清除存储的认证信息
hermes doctor [--fix]       检查依赖和配置
hermes status [--all]       显示组件状态
```

<a id="tools-skills"></a>
### 工具与技能

```
hermes tools                交互式工具启用/禁用（curses UI）
hermes tools list           显示所有工具及其状态
hermes tools enable NAME    启用工具集
hermes tools disable NAME   禁用工具集

hermes skills list          列出已安装的技能
hermes skills search QUERY  搜索技能中心
hermes skills install ID    安装技能（ID 可以是中心标识符，也可以是直接的 https://…/SKILL.md URL；如果 frontmatter 中没有名称，可以通过 --name 覆盖）
hermes skills inspect ID    预览而不安装
hermes skills config        按平台启用/禁用技能
hermes skills check         检查更新
hermes skills update        更新过时的技能
hermes skills uninstall N   移除中心技能
hermes skills publish PATH  发布到注册表
hermes skills browse        浏览所有可用技能
hermes skills tap add REPO  添加 GitHub 仓库作为技能源
```
<a id="mcp-servers"></a>
### MCP 服务器

```
hermes mcp serve            以MCP服务器模式运行Hermes
hermes mcp add NAME         添加一个MCP服务器 (--url 或 --command)
hermes mcp remove NAME      移除一个MCP服务器
hermes mcp list             列出已配置的服务器
hermes mcp test NAME        测试连接
hermes mcp configure NAME   切换工具选择
```

<a id="gateway-messaging-platforms"></a>
### 网关（消息平台）

```
hermes gateway run          以前台模式启动网关
hermes gateway install      安装为后台服务
hermes gateway start/stop   控制服务
hermes gateway restart      重启服务
hermes gateway status       检查状态
hermes gateway setup        配置平台
```

支持的平台：Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks。Open WebUI 通过 API Server 适配器连接。

平台文档：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

<a id="sessions"></a>
### 会话

```
hermes sessions list        列出最近会话
hermes sessions browse      交互式选择器
hermes sessions export OUT  导出为 JSONL
hermes sessions rename ID T 重命名会话
hermes sessions delete ID   删除会话
hermes sessions prune       清理旧会话 (--older-than N 天)
hermes sessions stats       会话存储统计
```

<a id="cron-jobs"></a>
### 定时任务

```
hermes cron list            列出任务 (--all 显示已禁用的)
hermes cron create SCHED    创建: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         编辑计划、提示、投递方式
hermes cron pause/resume ID 控制任务状态
hermes cron run ID          在下一个触发点执行
hermes cron remove ID       删除任务
hermes cron status          调度器状态
```

<a id="webhooks"></a>
### Webhook

```
hermes webhook subscribe N  在 /webhooks/<name> 创建路由
hermes webhook list         列出订阅
hermes webhook remove NAME  移除订阅
hermes webhook test NAME    发送测试 POST 请求
```

<a id="profiles"></a>
### 配置文件

```
hermes profile list         列出所有配置文件
hermes profile create NAME  创建 (--clone, --clone-all, --clone-from)
hermes profile use NAME     设置固定默认值
hermes profile delete NAME  删除配置文件
hermes profile show NAME    显示详情
hermes profile alias NAME   管理包装脚本
hermes profile rename A B   重命名配置文件
hermes profile export NAME  导出为 tar.gz
hermes profile import FILE  从存档导入
```

<a id="credential-pools"></a>
### 凭据池

```
hermes auth add             交互式凭据向导
hermes auth list [PROVIDER] 列出池化凭据
hermes auth remove P INDEX  按提供者和索引移除
hermes auth reset PROVIDER  清除耗尽状态
```

<a id="other"></a>
### 其他

```
hermes insights [--days N]  使用分析
hermes update               更新到最新版本
hermes pairing list/approve/revoke  私信授权
hermes plugins list/install/remove  插件管理
hermes honcho setup/status  Honcho 记忆集成 (需要 honcho 插件)
hermes memory setup/status/off  记忆提供者配置
hermes completion bash|zsh  Shell 自动补全
hermes acp                  ACP 服务器 (IDE 集成)
hermes claw migrate         从 OpenClaw 迁移
hermes uninstall            卸载 Hermes
```
---

<a id="slash-commands-in-session"></a>
## 斜杠命令（会话内）

在交互式聊天会话中输入这些命令。新命令会频繁添加；如果下面内容看起来过时了，请在会话中运行 `/help` 查看权威列表，或参阅[实时斜杠命令参考](https://hermes-agent.nousresearch.com/docs/reference/slash-commands)。命令注册表位于 `hermes_cli/commands.py` — 所有消费者（自动补全、Telegram 菜单、Slack 映射、`/help`）都由此派生。

<a id="session-control"></a>
### 会话控制
```
/new (/reset)        新建会话
/clear               清屏 + 新建会话（CLI）
/retry               重新发送最后一条消息
/undo                移除上一次对话
/title [name]        命名会话
/compress            手动压缩上下文
/stop                终止后台进程
/rollback [N]        恢复文件系统检查点
/snapshot [sub]      创建或恢复 Hermes 配置/状态的状态快照（CLI）
/background <prompt> 在后台运行提示
/queue <prompt>      排队等待下一轮
/steer <prompt>      在下一个工具调用之后注入一条消息，不中断当前流程
/agents (/tasks)     显示活跃的 Agent 和正在运行的任务
/resume [name]       恢复指定名称的会话
/goal [text|sub]     设置一个长期目标，Hermes 会在多轮对话中持续努力直到达成
                     （子命令：status, pause, resume, clear）
/redraw              强制重绘整个 UI（CLI）
```

<a id="configuration"></a>
### 配置
```
/config              显示配置（CLI）
/model [name]        显示或切换模型
/personality [name]  设置人格
/reasoning [level]   设置推理级别（none|minimal|low|medium|high|xhigh|show|hide）
/verbose             循环切换：off → new → all → verbose
/voice [on|off|tts]  语音模式
/yolo                切换绕过审批
/busy [sub]          控制 Hermes 正在工作时 Enter 键的行为（CLI）
                     （子命令：queue, steer, interrupt, status）
/indicator [style]   选择 TUI 繁忙指示器样式（CLI）
                     （样式：kaomoji, emoji, unicode, ascii）
/footer [on|off]     在最终回复中切换网关运行时元数据页脚
/skin [name]         切换主题（CLI）
/statusbar           切换状态栏（CLI）
```

<a id="tools-skills"></a>
### 工具与技能
```
/tools               管理工具（CLI）
/toolsets            列出工具集（CLI）
/skills              搜索/安装技能（CLI）
/skill <name>        将技能加载到会话中
/reload-skills       重新扫描 ~/.hermes/skills/ 以发现新增或移除的技能
/reload              重新加载 .env 变量到当前运行的会话（CLI）
/reload-mcp          重新加载 MCP 服务器
/cron                管理 cron 任务（CLI）
/curator [sub]       后台技能维护（status, run, pin, archive, …）
/kanban [sub]        多资料协作看板（tasks, links, comments）
/plugins             列出插件（CLI）
```

<a id="gateway"></a>
### 网关
```
/approve             批准待处理的命令（网关）
/deny                拒绝待处理的命令（网关）
/restart             重启网关（网关）
/sethome             将当前聊天设为首页频道（网关）
/update              更新 Hermes 到最新版本（网关）
/topic [sub]         启用或检查 Telegram 私聊话题会话（网关）
/platforms (/gateway) 显示平台连接状态（网关）
```
<a id="utility"></a>
### 实用工具
```
/branch (/fork)      分支当前会话
/fast               切换优先级/快速处理
/browser            打开 CDP 浏览器连接
/history            显示对话历史（CLI）
/save               将对话保存到文件（CLI）
/copy [N]           复制上一条助手回复到剪贴板（CLI）
/paste              附加剪贴板图片（CLI）
/image              附加本地图片文件（CLI）
```

<a id="info"></a>
### 信息
```
/help               显示命令
/commands [page]    浏览所有命令（网关）
/usage              Token 用量
/insights [days]    使用分析
/gquota             显示 Google Gemini Code Assist 配额用量（CLI）
/status             会话信息（网关）
/profile            当前配置文件信息
/debug              上传调试报告（系统信息 + 日志）并获取可分享链接
```

<a id="exit"></a>
### 退出
```
/quit (/exit, /q)   退出 CLI
```

---

<a id="key-paths-config"></a>
## 关键路径与配置

```
~/.hermes/config.yaml       主配置
~/.hermes/.env              API 密钥与机密
$HERMES_HOME/skills/        已安装技能
~/.hermes/sessions/         会话记录
~/.hermes/logs/             网关与错误日志
~/.hermes/auth.json         OAuth 令牌与凭据池
~/.hermes/hermes-agent/     源代码（如果通过 git 安装）
```

配置文件使用 `~/.hermes/profiles/&lt;name&gt;/` 目录，布局相同。

<a id="config-sections"></a>
### 配置段

使用 `hermes config edit` 或 `hermes config set section.key value` 进行编辑。

| 段 | 键选项 |
|---------|-------------|
| `model` | `default`、`provider`、`base_url`、`api_key`、`context_length` |
| `agent` | `max_turns` (90)、`tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal)、`cwd`、`timeout` (180) |
| `compression` | `enabled`、`threshold` (0.50)、`target_ratio` (0.20) |
| `display` | `skin`、`tool_progress`、`show_reasoning`、`show_cost` |
| `stt` | `enabled`、`provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`、`user_profile_enabled`、`provider` |
| `security` | `tirith_enabled`、`website_blocklist` |
| `delegation` | `model`、`provider`、`base_url`、`api_key`、`max_iterations` (50)、`reasoning_effort` |
| `checkpoints` | `enabled`、`max_snapshots` (50) |

完整配置参考：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

<a id="providers"></a>
### 提供商

支持 20+ 个提供商。通过 `hermes model` 或 `hermes setup` 设置。

| 提供商 | 认证方式 | 密钥环境变量 |
|----------|------|-------------|
| OpenRouter | API 密钥 | `OPENROUTER_API_KEY` |
| Anthropic | API 密钥 | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | 令牌 | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API 密钥 | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` |
| DeepSeek | API 密钥 | `DEEPSEEK_API_KEY` |
| xAI / Grok | API 密钥 | `XAI_API_KEY` |
| Hugging Face | 令牌 | `HF_TOKEN` |
| Z.AI / GLM | API 密钥 | `GLM_API_KEY` |
| MiniMax | API 密钥 | `MINIMAX_API_KEY` |
| MiniMax CN | API 密钥 | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API 密钥 | `KIMI_API_KEY` |
| 阿里云 / DashScope | API 密钥 | `DASHSCOPE_API_KEY` |
| 小米 MiMo | API 密钥 | `XIAOMI_API_KEY` |
| Kilo Code | API 密钥 | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API 密钥 | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API 密钥 | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API 密钥 | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| 自定义端点 | 配置 | 在 config.yaml 中设置 `model.base_url` + `model.api_key` |
| GitHub Copilot ACP | 外部 | `COPILOT_CLI_PATH` 或 Copilot CLI |
完整的 provider 文档：https://hermes-agent.nousresearch.com/docs/integrations/providers

<a id="toolsets"></a>
### 工具集

通过 `hermes tools`（交互式）或 `hermes tools enable/disable NAME` 启用/禁用。

| 工具集 | 功能 |
|---------|-----------------|
| `web` | 网络搜索和内容提取 |
| `search` | 仅网络搜索（`web` 的子集） |
| `browser` | 浏览器自动化（Browserbase、Camofox 或本地 Chromium） |
| `terminal` | Shell 命令和进程管理 |
| `file` | 文件读写/搜索/修补 |
| `code_execution` | 沙盒化 Python 执行 |
| `vision` | 图像分析 |
| `image_gen` | AI 图像生成 |
| `video` | 视频分析和生成 |
| `tts` | 文本转语音 |
| `skills` | 技能浏览和管理 |
| `memory` | 持久化跨会话记忆 |
| `session_search` | 搜索历史对话 |
| `delegation` | 子 Agent 任务委派 |
| `cronjob` | 计划任务管理 |
| `clarify` | 向用户提问澄清 |
| `messaging` | 跨平台消息发送 |
| `todo` | 会话内任务规划与跟踪 |
| `kanban` | 多 Agent 工作队列工具（仅限于分派给工作器） |
| `debugging` | 额外的内省/调试工具（默认关闭） |
| `safe` | 最小化、低风险工具集，适用于锁定会话 |
| `spotify` | Spotify 播放和播放列表控制 |
| `homeassistant` | 智能家居控制（默认关闭） |
| `discord` | Discord 集成工具 |
| `discord_admin` | Discord 管理员/管理工具 |
| `feishu_doc` | 飞书文档工具 |
| `feishu_drive` | 飞书云盘工具 |
| `yuanbao` | 元宝集成工具 |
| `rl` | 强化学习工具（默认关闭） |
| `moa` | Agent 混合（默认关闭） |

完整枚举位于 `toolsets.py` 中的 `TOOLSETS` 字典；`_HERMES_CORE_TOOLS` 是大多数平台继承的默认套件。

工具变更在 `/reset`（新会话）后生效。它们**不会**在对话中途应用，以保持提示缓存。

---

<a id="security-privacy-toggles"></a>
## 安全与隐私开关

常见问题："为什么 Hermes 对我的输出/工具调用/命令做了 X？" 的开关 — 以及更改它们的确切命令。这些大多需要全新会话（在聊天中输入 `/reset`，或启动新的 `hermes` 执行），因为它们只在启动时读取一次。

<a id="secret-redaction-in-tool-output"></a>
### 工具输出中的密钥脱敏

密钥脱敏**默认关闭** — 工具输出（终端 stdout、`read_file`、网页内容、子 Agent 摘要等）原样通过。如果用户希望 Hermes 在进入对话上下文和日志之前自动掩码看起来像 API 密钥、令牌和秘密的字符串：

```bash
hermes config set security.redact_secrets true       # 全局启用
```

**需要重启。** `security.redact_secrets` 在导入时快照 — 在会话中途切换它（例如通过工具调用执行 `export HERMES_REDACT_SECRETS=true`）**不会**对当前运行进程生效。请告知用户在终端中运行 `hermes config set security.redact_secrets true`，然后启动新会话。这是有意为之 — 它可以防止 LLM 在任务中自行翻转开关。
再次禁用：
```bash
hermes config set security.redact_secrets false
```

<a id="pii-redaction-in-gateway-messages"></a>
### 网关消息中的 PII 脱敏

与秘密脱敏分开。启用后，网关会在会话上下文到达模型之前，对用户 ID 进行哈希处理，并从上下文中移除手机号码：

```bash
hermes config set privacy.redact_pii true    # 启用
hermes config set privacy.redact_pii false   # 禁用（默认）
```

<a id="command-approval-prompts"></a>
### 命令审批提示

默认情况下（`approvals.mode: manual`），Hermes 在运行被标记为破坏性的 shell 命令（如 `rm -rf`、`git reset --hard` 等）之前会提示用户。模式有：

- `manual` — 始终提示（默认）
- `smart` — 使用辅助 LLM 自动批准低风险命令，高风险则提示
- `off` — 跳过所有审批提示（相当于 `--yolo`）

```bash
hermes config set approvals.mode smart       # 推荐折中方案
hermes config set approvals.mode off         # 绕过所有提示（不推荐）
```

无需修改配置即可在单次调用中绕过：
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

注意：YOLO 模式 / `approvals.mode: off` 不会关闭秘密脱敏。它们是独立的。

<a id="shell-hooks-allowlist"></a>
### Shell 钩子允许列表

某些 shell 钩子集成需要显式加入允许列表后才能触发。通过 `~/.hermes/shell-hooks-allowlist.json` 管理——钩子首次尝试运行时，会以交互方式提示用户。

<a id="disabling-the-web-browser-image-gen-tools"></a>
### 禁用网络/浏览器/图片生成工具

要让模型完全远离网络或媒体工具，打开 `hermes tools` 并按平台切换。下次会话（`/reset`）时生效。请参阅上面的“工具与技能”部分。

---

<a id="voice-transcription"></a>
## 语音与转录

<a id="stt-voice-text"></a>
### STT（语音 → 文本）

来自消息平台的语音消息会自动转录。

提供者优先级（自动检测）：
1. **本地 faster-whisper** — 免费，无需 API 密钥：`pip install faster-whisper`
2. **Groq Whisper** — 免费层级：设置 `GROQ_API_KEY`
3. **OpenAI Whisper** — 付费：设置 `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — 设置 `MISTRAL_API_KEY`

配置：
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

<a id="tts-text-voice"></a>
### TTS（文本 → 语音）

| 提供者 | 环境变量 | 免费？ |
|--------|---------|--------|
| Edge TTS | 无 | 是（默认） |
| ElevenLabs | `ELEVENLABS_API_KEY` | 有免费层级 |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | 付费 |
| MiniMax | `MINIMAX_API_KEY` | 付费 |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | 付费 |
| NeuTTS (本地) | 无（`pip install neutts[all]` + `espeak-ng`） | 免费 |

语音命令：`/voice on`（语音到语音）、`/voice tts`（始终语音）、`/voice off`。

---

<a id="spawning-additional-hermes-instances"></a>
## 派生额外的 Hermes 实例

将额外的 Hermes 进程作为完全独立的子进程运行——独立的会话、工具和环境。

<a id="when-to-use-this-vs-delegatetask"></a>
### 何时使用此方式 vs `delegate_task`

| | `delegate_task` | 派生 `hermes` 进程 |
|-|-----------------|-------------------|
| 隔离性 | 独立对话，共享进程 | 完全独立进程 |
| 持续时间 | 分钟级（受父循环限制） | 小时/天级 |
| 工具访问 | 父进程工具的子集 | 完整工具访问 |
| 交互性 | 否 | 是（PTY 模式） |
| 使用场景 | 快速的并行子任务 | 长期自主任务 |
<a id="one-shot-mode"></a>
### 单次模式

```
terminal(command="hermes chat -q '研究 GRPO 论文并将摘要写入 ~/research/grpo.md'", timeout=300)

# 长时间任务的背景说明：
terminal(command="hermes chat -q '为 ~/myapp 设置 CI/CD'", background=true)
```

<a id="interactive-pty-mode-via-tmux"></a>
### 交互式 PTY 模式（通过 tmux）

Hermes 使用 prompt_toolkit，它需要一个真正的终端。使用 tmux 进行交互式生成：

```
# 启动
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# 等待启动，然后发送消息
terminal(command="sleep 8 && tmux send-keys -t agent1 '构建一个 FastAPI 认证服务' Enter", timeout=15)

# 读取输出
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# 发送后续指令
terminal(command="tmux send-keys -t agent1 '添加限流中间件' Enter", timeout=5)

# 退出
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

<a id="multi-agent-coordination"></a>
### 多 Agent 协调

```
# Agent A：后端
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend '为用户管理构建 REST API' Enter", timeout=15)

# Agent B：前端
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend '为用户管理构建 React 仪表盘' Enter", timeout=15)

# 检查进度，在它们之间传递上下文
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend '这是来自后端 Agent 的 API 模式：...' Enter", timeout=5)
```

<a id="session-resume"></a>
### 会话恢复

```
# 恢复最近的会话
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# 恢复特定会话
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

<a id="tips"></a>
### 提示

- **对于快速子任务，优先使用 `delegate_task`** — 比生成完整进程的开销更小
- **在生成编辑代码的 Agent 时使用 `-w`（工作树模式）** — 防止 git 冲突
- **为单次模式设置超时** — 复杂任务可能需要 5-10 分钟
- **使用 `hermes chat -q` 进行“发后即忘”操作** — 不需要 PTY
- **使用 tmux 进行交互式会话** — 原始 PTY 模式在 prompt_toolkit 中存在 `\r` 与 `\n` 的问题
- **对于定时任务**，使用 `cronjob` 工具而不是生成进程 — 它处理交付和重试

---

<a id="durable-background-systems"></a>
## 持久化与后台系统

四个系统与主对话循环并行运行。此处为快速参考；完整的开发者说明位于 `AGENTS.md`，面向用户的文档位于 `website/docs/user-guide/features/`。

<a id="delegation-delegatetask"></a>
### 委派（`delegate_task`）

同步子 Agent 生成 — 父 Agent 等待子 Agent 的摘要后再继续自己的循环。隔离的上下文 + 终端会话。

- **单个：** `delegate_task(goal, context, toolsets)`。
- **批量：** `delegate_task(tasks=[{goal, ...}, ...])` 并行运行子任务，上限由 `delegation.max_concurrent_children`（默认 3）控制。
- **角色：** `leaf`（默认；不能再次委派）与 `orchestrator`（可以生成自己的工作进程，受 `delegation.max_spawn_depth` 限制）。
- **非持久化。** 如果父进程被中断，子进程也会被取消。对于需要超越当前轮次的工作，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。
配置：`config.yaml` 中的 `delegation.*`。

<a id="cron-scheduled-jobs"></a>
### Cron（定时任务）

持久化调度器 — `cron/jobs.py` + `cron/scheduler.py`。通过 `cronjob` 工具、`hermes cron` CLI（`list`、`add`、`edit`、`pause`、`resume`、`run`、`remove`）或 `/cron` 斜杠命令来驱动。

- **调度方式：** 持续时间（`"30m"`、`"2h"`）、"every" 短语（`"every monday 9am"`）、5 字段 cron（`"0 9 * * *"`）或 ISO 时间戳。
- **每个任务的控制参数：** `skills`、`model`/`provider` 覆盖、`script`（预运行数据收集；`no_agent=True` 使脚本成为整个任务）、`context_from`（将任务 A 的输出链入任务 B）、`workdir`（在特定目录中运行，并加载该目录的 `AGENTS.md` / `CLAUDE.md`）、多平台交付。
- **不变约束：** 每次运行硬性中断 3 分钟；`.tick.lock` 文件防止跨进程重复 tick；cron 会话默认传递 `skip_memory=True`；cron 交付以页眉/页脚框架呈现，而不是镜像到目标网关会话（保持角色交替不变）。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

<a id="curator-skill-lifecycle"></a>
### Curator（技能生命周期）

用于 Agent 创建的技能的背景维护。跟踪使用情况，将闲置技能标记为陈旧，将陈旧的技能归档，保留预运行的 tar.gz 备份以便不会丢失任何内容。

- **CLI：** `hermes curator &lt;verb&gt;` — `status`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`prune`、`backup`、`rollback`。
- **斜杠命令：** `/curator &lt;subcommand&gt;` 镜像 CLI。
- **作用范围：** 仅处理 `created_by: "agent"` 来源的技能。捆绑安装和从 Hub 安装的技能被排除在外。**从不删除** — 最大的破坏性操作是归档。固定的技能不受任何自动转换和 LLM 审查。
- **遥测：** 辅助文件 `~/.hermes/skills/.usage.json` 保存每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state`、`pinned`。

配置：`curator.*`（`enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*`）。
用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

<a id="kanban-multi-agent-work-queue"></a>
### Kanban（多 Agent 工作队列）

持久化 SQLite 板，用于多配置文件/多工作者协作。用户通过 `hermes kanban &lt;verb&gt;` 驱动；调度器生成的工作者会看到一个由 `HERMES_KANBAN_TASK` 控制的专注的 `kanban_*` 工具集；编排器配置文件可以选择加入更广泛的 `kanban` 工具集。正常会话仍然没有 `kanban_*` 模式痕迹，除非配置了。

- **CLI 动词（常用）：** `init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`。不常用：`watch`、`stats`、`runs`、`log`、`dispatch`、`daemon`、`gc`。
- **工作者/编排器工具集：** `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`；显式启用了 `kanban` 工具集（在调度器生成的任务之外）的配置文件还可以获得 `kanban_list` 和 `kanban_unblock` 用于看板路由。
- **调度器** 默认在网关内运行（`kanban.dispatch_in_gateway: true`）— 回收过期的声明、提升就绪的任务、原子性地声明、生成分配的配置文件。在配置的 `kanban.failure_limit` 次连续非成功尝试后自动阻塞任务（默认：2）。
- **隔离：** 看板是硬边界（工作者在环境变量中得到 `HERMES_KANBAN_BOARD`）；租户是看板内的一个软命名空间，用于工作空间路径和内存键隔离。
User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

<a id="windows-specific-quirks"></a>
## Windows 特有怪癖

Hermes 在 Windows 上原生运行（PowerShell、cmd、Windows Terminal、git-bash mintty、VS Code 集成终端）。大部分功能开箱即用，但 Win32 和 POSIX 之间的一些差异曾让我们吃过亏——在这里记录你遇到的每一个，这样下一个人（或下一次会话）就不必从头重新发现它们。

<a id="input-keybindings"></a>
### 输入 / 快捷键

**Alt+Enter 不会插入换行。** Windows Terminal 在终端层拦截 Alt+Enter 以切换全屏——按键事件永远到达不了 prompt_toolkit。请改用 **Ctrl+Enter**。Windows Terminal 将 Ctrl+Enter 作为 LF（`c-j`）传递，与普通 Enter（`c-m` / CR）不同；CLI 仅在 `win32` 上将 `c-j` 绑定为换行插入（参见 `cli.py` 中的 `_bind_prompt_submit_keys` 以及仅适用于 Windows 的 `c-j` 绑定）。副作用：在 Windows 上，原始的 Ctrl+J 按键也会插入换行——不可避免，因为 Windows Terminal 在 Win32 控制台 API 层将 Ctrl+Enter 和 Ctrl+J 折叠为相同的键码。Windows 上不存在与 Ctrl+J 冲突的绑定，所以这是一个无害的副作用。

mintty / git-bash 行为相同（Alt+Enter 全屏），除非你在“选项→按键”中禁用 Alt+Fn 快捷键。更简单的方法是直接使用 Ctrl+Enter。

**诊断快捷键。** 运行 `python scripts/keystroke_diagnostic.py`（仓库根目录）可以查看 prompt_toolkit 在当前终端中如何识别每个按键。解答诸如“Shift+Enter 是否作为独立按键传递？”（几乎从不——大多数终端将其折叠为普通 Enter）或“我的终端对 Ctrl+Enter 发送了什么字节序列？”这类问题。正是通过这种方式才确认了 Ctrl+Enter 等于 `c-j` 这个事实。

<a id="config-files"></a>
### 配置 / 文件

**首次运行时出现 HTTP 400 "No models provided"。** `config.yaml` 保存时带有 UTF-8 BOM（Windows 应用写入时常见）。请重新保存为无 BOM 的 UTF-8。`hermes config edit` 写入时不带 BOM；在记事本中手动编辑通常是罪魁祸首。

<a id="executecode-sandbox"></a>
### `execute_code` / 沙盒

**来自沙盒子进程的 WinError 10106**（"无法加载或初始化请求的服务提供商"）——它无法创建 `AF_INET` 套接字，因此回环 TCP RPC 回退在 `connect()` 之前就失败了。根本原因通常**不是**损坏的 Winsock LSP；而是 Hermes 自身的环境清理器从子进程环境中丢弃了 `SYSTEMROOT` / `WINDIR` / `COMSPEC`。Python 的 `socket` 模块需要 `SYSTEMROOT` 来定位 `mswsock.dll`。通过 `tools/code_execution_tool.py` 中的 `_WINDOWS_ESSENTIAL_ENV_VARS` 白名单修复。如果你仍然遇到此问题，可以在 `execute_code` 块内部打印 `os.environ` 以确认 `SYSTEMROOT` 是否已设置。完整诊断方案请见 `references/execute-code-sandbox-env-windows.md`。

<a id="testing-contributing"></a>
### 测试 / 贡献

**`scripts/run_tests.sh` 在 Windows 上不能直接使用**——它寻找 POSIX 虚拟环境布局（`.venv/bin/activate`）。Hermes 安装的虚拟环境位于 `venv/Scripts/`，里面也没有 pip 或 pytest（为减小安装体积而被剥离）。解决方法：将 `pytest + pytest-xdist + pyyaml` 安装到系统 Python 3.11 的用户站点中，然后直接通过设置 `PYTHONPATH` 来调用 pytest：
```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

使用 `-n 0`，而不是 `-n 4`——`pyproject.toml` 中的默认 `addopts` 已经包含了 `-n`，并且包装器的 CI 一致性保证不适用于非 POSIX 系统。

**仅限 POSIX 的测试需要跳过保护。** 代码库中已有的常见标记：
- 符号链接——Windows 上需要提升权限
- `0o600` 文件模式——NTFS 默认不强制 POSIX 模式位
- `signal.SIGALRM`——仅 Unix（参见 `tests/conftest.py::_enforce_test_timeout`）
- Winsock / Windows 特定的回归问题——`@pytest.mark.skipif(sys.platform != "win32", ...)`

使用现有的跳过模式风格（`sys.platform == "win32"` 或 `sys.platform.startswith("win")`），以保持与套件其余部分一致。

<a id="path-filesystem"></a>
### 路径 / 文件系统

**行尾。** Git 可能会警告 `LF will be replaced by CRLF the next time Git touches it`。这是表面问题——仓库的 `.gitattributes` 会进行规范化。不要让编辑器自动将已提交的 POSIX 换行文件转换为 CRLF。

**正斜杠几乎在任何地方都有效。** `C:/Users/...` 被所有 Hermes 工具和大多数 Windows API 接受。在代码和日志中优先使用正斜杠——避免在 bash 中对反斜杠进行 shell 转义。

---

<a id="troubleshooting"></a>
## 故障排除

<a id="voice-not-working"></a>
### 语音无法工作
1. 检查 config.yaml 中的 `stt.enabled: true`
2. 验证提供商：`pip install faster-whisper` 或设置 API 密钥
3. 在网关中：`/restart`。在 CLI 中：退出并重新启动。

<a id="tool-not-available"></a>
### 工具不可用
1. `hermes tools`——检查工具集是否已为你的平台启用
2. 某些工具需要环境变量（检查 `.env`）
3. 启用工具后执行 `/reset`

<a id="model-provider-issues"></a>
### 模型/提供商问题
1. `hermes doctor`——检查配置和依赖项
2. `hermes login`——重新认证 OAuth 提供商
3. 检查 `.env` 是否包含正确的 API 密钥
4. **Copilot 403**：`gh auth login` 令牌不适用于 Copilot API。你必须通过 `hermes model` → GitHub Copilot 使用 Copilot 特定的 OAuth 设备代码流程。

<a id="changes-not-taking-effect"></a>
### 更改未生效
- **工具/技能：** `/reset` 使用更新的工具集启动新会话
- **配置更改：** 在网关中：`/restart`。在 CLI 中：退出并重新启动。
- **代码更改：** 重启 CLI 或网关进程

<a id="skills-not-showing"></a>
### 技能未显示
1. `hermes skills list`——验证是否已安装
2. `hermes skills config`——检查平台启用状态
3. 显式加载：`/skill name` 或 `hermes -s name`

<a id="gateway-issues"></a>
### 网关问题
首先检查日志：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见的网关问题：
- **SSH 注销时网关终止**：启用 linger：`sudo loginctl enable-linger $USER`
- **WSL2 关闭时网关终止**：WSL2 需要在 `/etc/wsl.conf` 中设置 `systemd=true` 才能使 systemd 服务正常工作。没有它，网关会回退到 `nohup`（会话关闭时终止）。
- **网关崩溃循环**：重置失败状态：`systemctl --user reset-failed hermes-gateway`

<a id="platform-specific-issues"></a>
### 平台特定问题
- **Discord 机器人静默**：必须在 Bot → Privileged Gateway Intents 中启用 **Message Content Intent**。
- **Slack 机器人仅在 DM 中工作**：必须订阅 `message.channels` 事件。没有它，机器人会忽略公共频道。
- **Windows 特定问题**（`Alt+Enter` 换行、WinError 10106、UTF-8 BOM 配置、测试套件、行尾）：请参阅上面的专用 **Windows 特定怪癖** 部分。
<a id="auxiliary-models-not-working"></a>
### 辅助模型不工作
如果 `auxiliary` 任务（视觉、压缩）静默失败，`auto` 提供商找不到后端。请设置 `OPENROUTER_API_KEY` 或 `GOOGLE_API_KEY`，或者显式配置每个辅助任务的提供商：
```bash
hermes config set auxiliary.vision.provider <你的提供商>
hermes config set auxiliary.vision.model <模型名称>
```

---

<a id="where-to-find-things"></a>
## 从哪找到这些

| 寻找什么... | 位置 |
|-------------|------|
| 配置选项 | `hermes config edit` 或 [配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| 可用工具 | `hermes tools list` 或 [工具参考](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| 斜杠命令 | 会话中的 `/help` 或 [斜杠命令参考](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| 技能目录 | `hermes skills browse` 或 [技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| 提供商设置 | `hermes model` 或 [提供商指南](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| 平台设置 | `hermes gateway setup` 或 [消息文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP 服务器 | `hermes mcp list` 或 [MCP 指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| 配置文件 | `hermes profile list` 或 [配置文件文档](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron 任务 | `hermes cron list` 或 [Cron 文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| 记忆 | `hermes memory status` 或 [记忆文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| 环境变量 | `hermes config env-path` 或 [环境变量参考](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI 命令 | `hermes --help` 或 [CLI 参考](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| 网关日志 | `~/.hermes/logs/gateway.log` |
| 会话文件 | `~/.hermes/sessions/` 或 `hermes sessions browse` |
| 源代码 | `~/.hermes/hermes-agent/` |

---

<a id="contributor-quick-reference"></a>
## 贡献者快速参考

适用于偶尔的贡献者和 PR 作者。完整开发者文档：https://hermes-agent.nousresearch.com/docs/developer-guide/

<a id="project-layout"></a>
### 项目结构

<!-- ascii-guard-ignore -->
```
hermes-agent/
├── run_agent.py          # AIAgent — 核心对话循环
├── model_tools.py        # 工具发现与分发
├── toolsets.py           # 工具集定义
├── cli.py                # 交互式 CLI（HermesCLI）
├── hermes_state.py       # SQLite 会话存储
├── agent/                # 提示构建、上下文压缩、记忆、模型路由、凭据池、技能分发
├── hermes_cli/           # CLI 子命令、配置、设置、命令
│   ├── commands.py       # 斜杠命令注册表（CommandDef）
│   ├── config.py         # DEFAULT_CONFIG、环境变量定义
│   └── main.py           # CLI 入口和 argparse
├── tools/                # 每个工具一个文件
│   └── registry.py       # 中央工具注册表
├── gateway/              # 消息网关
│   └── platforms/        # 平台适配器（telegram、discord 等）
├── cron/                 # 作业调度器
├── tests/                # 约 3000 个 pytest 测试
└── website/              # Docusaurus 文档站点
```
<!-- ascii-guard-ignore-end -->
配置：`~/.hermes/config.yaml`（设置），`~/.hermes/.env`（API 密钥）。

<a id="adding-a-tool-3-files"></a>
### 添加工具（3 个文件）

**1. 创建 `tools/your_tool.py`：**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 添加到 `toolsets.py`** → `_HERMES_CORE_TOOLS` 列表。

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入——无需手动列表。

所有处理程序必须返回 JSON 字符串。使用 `get_hermes_home()` 获取路径，切勿硬编码 `~/.hermes`。

<a id="adding-a-slash-command"></a>
### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加 `CommandDef`
2. 在 `cli.py` → `process_command()` 中添加处理程序
3. （可选）在 `gateway/run.py` 中添加网关处理程序

所有消费者（帮助文本、自动补全、Telegram 菜单、Slack 映射）都会自动从中央注册表中派生。

<a id="agent-loop-high-level"></a>
### Agent 循环（高级）

```
run_conversation():
  1. 构建系统提示
  2. 当迭代次数 < 最大值时循环：
     a. 调用 LLM（OpenAI 格式消息 + 工具模式）
     b. 如果有 tool_calls → 通过 handle_function_call() 分发每个调用 → 追加结果 → 继续
     c. 如果有文本响应 → 返回
  3. 接近令牌限制时自动触发上下文压缩
```

<a id="testing"></a>
### 测试

```bash
python -m pytest tests/ -o 'addopts=' -q   # 完整测试套件
python -m pytest tests/tools/ -q            # 特定区域
```

- 测试会自动将 `HERMES_HOME` 重定向到临时目录——绝不会触及真实的 `~/.hermes/`
- 推送任何更改前请运行完整测试套件
- 使用 `-o 'addopts='` 清除任何内置的 pytest 标志

**Windows 贡献者：** `scripts/run_tests.sh` 目前会查找 POSIX 虚拟环境（`.venv/bin/activate` / `venv/bin/activate`），在 Windows 上会报错，因为 Windows 的布局是 `venv/Scripts/activate` + `python.exe`。Hermes 安装在 `venv/Scripts/` 的虚拟环境也没有 `pip` 或 `pytest`——为了减小最终用户安装包大小，它被精简了。解决方法：将 pytest + pytest-xdist + pyyaml 安装到系统 Python 3.11 的用户站点目录（`/c/Program Files/Python311/python -m pip install --user pytest pytest-xdist pyyaml`），然后直接运行测试：

```bash
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/tools/test_foo.py -v --tb=short -n 0
```

使用 `-n 0`（而不是 `-n 4`），因为 `pyproject.toml` 的默认 `addopts` 已经包含了 `-n`，并且包装器的 CI 一致性逻辑不适用于非 POSIX 环境。

**跨平台测试保护：** 使用仅 POSIX 系统调用的测试需要跳过标记。代码库中已有的常见情况：
- 创建符号链接 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`（参见 `tests/cron/test_cron_script.py`）
- POSIX 文件模式（0o600 等）→ `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")`（参见 `tests/hermes_cli/test_auth_toctou_file_modes.py`）
- `signal.SIGALRM` → 仅 Unix（参见 `tests/conftest.py::_enforce_test_timeout`）
- 实时 Winsock / Windows 特定回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`
**仅通过 `sys.platform` 打猴子补丁是不够的**，如果被测代码还调用了 `platform.system()` / `platform.release()` / `platform.mac_ver()`。这些函数会独立重新读取真实操作系统信息，因此在 Windows 机器上设置 `sys.platform = "linux"` 的测试仍然会看到 `platform.system() == "Windows"` 并进入 Windows 分支。需要同时修补这三个：

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

可参考 `tests/agent/test_prompt_builder.py::TestEnvironmentHints` 中的完整示例。

<a id="extending-the-system-prompt-s-execution-environment-block"></a>
### 扩展系统提示语的执行环境块

关于宿主操作系统、用户 home 目录、当前工作目录、终端后端和 shell（Windows 下是 bash 还是 PowerShell）的实际情况指导信息，由 `agent/prompt_builder.py::build_environment_hints()` 函数生成。WSL 提示和后端探测逻辑也在此处。约定如下：

- **本地终端后端** → 输出宿主信息（OS、`$HOME`、cwd）+ Windows 特定说明（主机名 ≠ 用户名，`terminal` 使用 bash 而非 PowerShell）。
- **远程终端后端**（属于 `_REMOTE_TERMINAL_BACKENDS`：`docker, singularity, modal, daytona, ssh, vercel_sandbox, managed_modal`）→ **抑制**全部宿主信息，仅描述后端。通过 `tools.environments.get_environment(...).execute(...)` 在后端内部实时执行 `uname`/`whoami`/`pwd` 探测，结果按进程缓存在 `_BACKEND_PROBE_CACHE` 中，若探测超时则使用静态后备值。
- **编写提示语的关键事实**：当 `TERMINAL_ENV != "local"` 时，*每个*文件工具（`read_file`、`write_file`、`patch`、`search_files`）都在后端容器内运行，而非宿主上。此时系统提示语绝不能描述宿主——Agent 无法触及它。

完整设计说明、具体输出的字符串以及测试陷阱：
`references/prompt-builder-environment-hints.md`。

**重构安全模式（POSIX 等价守卫）：** 当你将内联逻辑提取到添加 Windows/平台特定行为的辅助函数中时，在测试文件中保留一个 `_legacy_&lt;name&gt;` 旧版 oracle 函数（即原代码的逐字拷贝），然后通过参数化差异对比。示例：`tests/tools/test_code_execution_windows_env.py::TestPosixEquivalence`。这确保了 POSIX 行为逐位不变，任何未来的偏离都会以清晰的差异对比大声失败。

<a id="commit-conventions"></a>
### 提交约定

```
type: concise subject line

Optional body.
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

<a id="key-rules"></a>
### 关键规则

- **永远不要破坏提示缓存** — 不要在对话中途更改上下文、工具或系统提示语
- **消息角色交替** — 不能连续两条 assistant 消息或连续两条 user 消息
- 所有路径使用 `hermes_constants` 中的 `get_hermes_home()`（配置文件安全）
- 配置值放入 `config.yaml`，密钥放入 `.env`
- 新工具需要 `check_fn`，以便仅在满足要求时才出现
