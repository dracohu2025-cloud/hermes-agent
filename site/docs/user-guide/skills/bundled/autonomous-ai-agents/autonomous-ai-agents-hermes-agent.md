---
title: "Hermes Agent — 配置、扩展或贡献 Hermes Agent"
sidebar_label: "Hermes Agent"
description: "配置、扩展或贡献 Hermes Agent"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hermes Agent {#hermes-agent}

配置、扩展或贡献 Hermes Agent。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/hermes-agent` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `hermes`、`setup`、`configuration`、`multi-agent`、`spawning`、`cli`、`gateway`、`development` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code)、[`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex)、[`opencode`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="hermes-agent"></a>
# Hermes Agent

Hermes Agent 是 Nous Research 开发的开源 AI Agent 框架，可在终端、消息平台和 IDE 中运行。它与 Claude Code（Anthropic）、Codex（OpenAI）和 OpenClaw 属于同一类别——即通过工具调用与系统交互的自主编码和任务执行 Agent。Hermes 支持任何 LLM 提供商（OpenRouter、Anthropic、OpenAI、DeepSeek、本地模型等 15 种以上），并可在 Linux、macOS 和 WSL 上运行。
Hermes 的不同之处：

- **通过技能自我改进** — Hermes 通过将可复用的流程保存为技能来从经验中学习。当它解决复杂问题、发现工作流或收到纠正时，可以将该知识持久化为技能文档，并在未来的会话中加载。技能随时间积累，使 agent 更擅长处理你的特定任务和环境。
- **跨会话持久记忆** — 记住你是谁、你的偏好、环境细节以及学到的经验。可插拔的记忆后端（内置、Honcho、Mem0 等）让你选择记忆的工作方式。
- **多平台网关** — 同一个 agent 可在 Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Email 以及 10 多个其他平台上运行，且拥有完整的工具访问权限，而不仅仅是聊天。
- **提供商无关** — 在工作流中随时切换模型和提供商，无需更改其他任何内容。凭据池自动在多个 API 密钥之间轮换。
- **配置档案** — 运行多个独立的 Hermes 实例，每个实例拥有隔离的配置、会话、技能和记忆。
- **可扩展** — 插件、MCP 服务器、自定义工具、Webhook 触发器、Cron 调度以及完整的 Python 生态系统。

人们使用 Hermes 进行软件开发、研究、系统管理、数据分析、内容创作、家庭自动化，以及任何其他受益于具有持久上下文和完整系统访问权限的 AI agent 的场景。

**本技能帮助你高效使用 Hermes Agent** — 包括设置、配置功能、生成额外的 agent 实例、排查问题、找到正确的命令和设置，以及在需要扩展或贡献时理解系统的工作原理。
**文档:** https://hermes-agent.nousresearch.com/docs/

## 快速开始 {#quick-start}

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 交互式聊天（默认）
hermes

# 单次查询
hermes chat -q "法国的首都是哪里？"

# 设置向导
hermes setup

# 切换模型/提供商
hermes model

# 健康检查
hermes doctor
```

---

## CLI 参考 {#cli-reference}

### 全局标志 {#global-flags}

```
hermes [flags] [command]

  --version, -V             显示版本
  --resume, -r SESSION      通过 ID 或标题恢复会话
  --continue, -c [NAME]     按名称恢复，或恢复最近的会话
  --worktree, -w            隔离的 git 工作树模式（并行 Agents）
  --skills, -s SKILL        预加载技能（逗号分隔或重复使用）
  --profile, -p NAME        使用指定的配置文件
  --yolo                    跳过危险命令确认
  --pass-session-id         在系统提示中包含会话 ID
```

无子命令时默认执行 `chat`。

### 聊天 {#chat}

```
hermes chat [flags]
  -q, --query TEXT          单次查询，非交互模式
  -m, --model MODEL         模型（例如 anthropic/claude-sonnet-4）
  -t, --toolsets LIST       逗号分隔的工具集
  --provider PROVIDER       强制指定提供商（openrouter, anthropic, nous 等）
  -v, --verbose             详细输出
  -Q, --quiet               隐藏横幅、旋转动画、工具预览
  --checkpoints             启用文件系统检查点（/rollback）
  --source TAG              会话来源标签（默认：cli）
```
### 配置 {#configuration}

```
hermes setup [section]      交互式向导（model|terminal|gateway|tools|agent）
hermes model                交互式模型/提供商选择器
hermes config               查看当前配置
hermes config edit          在 $EDITOR 中打开 config.yaml
hermes config set KEY VAL   设置配置项
hermes config path          打印 config.yaml 路径
hermes config env-path      打印 .env 路径
hermes config check         检查缺失/过时的配置
hermes config migrate       用新选项更新配置
hermes login [--provider P] OAuth 登录（nous, openai-codex）
hermes logout               清除已存储的认证信息
hermes doctor [--fix]       检查依赖和配置
hermes status [--all]       显示组件状态
```

### 工具与技能 {#tools-skills}

```
hermes tools                交互式工具启用/禁用（curses 界面）
hermes tools list           显示所有工具及其状态
hermes tools enable NAME    启用某个工具集
hermes tools disable NAME   禁用某个工具集

hermes skills list          列出已安装的技能
hermes skills search QUERY  在技能中心搜索
hermes skills install ID    安装技能（ID 可以是中心标识符，也可以是直接的 https://…/SKILL.md 链接；当 frontmatter 没有名称时，使用 --name 覆盖）
hermes skills inspect ID    预览但不安装
hermes skills config        按平台启用/禁用技能
hermes skills check         检查更新
hermes skills update        更新过时的技能
hermes skills uninstall N   移除中心技能
hermes skills publish PATH  发布到注册表
hermes skills browse        浏览所有可用技能
hermes skills tap add REPO  添加 GitHub 仓库作为技能来源
```
### MCP 服务器 {#mcp-servers}

```
hermes mcp serve            以 MCP 服务器模式运行 Hermes
hermes mcp add NAME         添加 MCP 服务器（--url 或 --command）
hermes mcp remove NAME      移除 MCP 服务器
hermes mcp list             列出已配置的服务器
hermes mcp test NAME        测试连接
hermes mcp configure NAME   切换工具选择
```

### 网关（消息平台） {#gateway-messaging-platforms}

```
hermes gateway run          启动网关（前台）
hermes gateway install      安装为后台服务
hermes gateway start/stop   控制服务启停
hermes gateway restart      重启服务
hermes gateway status       查看状态
hermes gateway setup        配置平台
```

支持平台：Telegram、Discord、Slack、WhatsApp、Signal、Email、SMS、Matrix、Mattermost、Home Assistant、钉钉、飞书、企业微信、BlueBubbles（iMessage）、微信、API 服务器、Webhooks。Open WebUI 通过 API 服务器适配器连接。

平台文档：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### 会话 {#sessions}

```
hermes sessions list        列出最近会话
hermes sessions browse      交互式选择器
hermes sessions export OUT  导出为 JSONL
hermes sessions rename ID T 重命名会话
hermes sessions delete ID   删除会话
hermes sessions prune       清理旧会话（--older-than N 天）
hermes sessions stats       会话存储统计
```

### 定时任务 {#cron-jobs}

```
hermes cron list            列出任务（--all 显示已禁用的）
hermes cron create SCHED    创建：'30m'、'every 2h'、'0 9 * * *'
hermes cron edit ID         编辑调度、提示词、投递方式
hermes cron pause/resume ID 控制任务状态
hermes cron run ID          在下一个触发点执行
hermes cron remove ID       删除任务
hermes cron status          调度器状态
```
### Webhooks {#webhooks}

```
hermes webhook subscribe N  在 /webhooks/<name> 创建路由
hermes webhook list         列出订阅
hermes webhook remove NAME  移除订阅
hermes webhook test NAME    发送测试 POST 请求
```

### 配置文件 {#profiles}

```
hermes profile list         列出所有配置文件
hermes profile create NAME  创建（--clone、--clone-all、--clone-from）
hermes profile use NAME     设置默认配置
hermes profile delete NAME  删除配置文件
hermes profile show NAME    显示详细信息
hermes profile alias NAME   管理包装脚本
hermes profile rename A B   重命名配置文件
hermes profile export NAME  导出为 tar.gz
hermes profile import FILE  从归档文件导入
```

### 凭据池 {#credential-pools}

```
hermes auth add             交互式凭据向导
hermes auth list [PROVIDER] 列出池化凭据
hermes auth remove P INDEX  按提供方和索引移除
hermes auth reset PROVIDER  清除耗尽状态
```

### 其他 {#other}

```
hermes insights [--days N]  使用分析
hermes update               更新到最新版本
hermes pairing list/approve/revoke  私信授权
hermes plugins list/install/remove  插件管理
hermes honcho setup/status  Honcho 记忆集成（需要 honcho 插件）
hermes memory setup/status/off  记忆提供方配置
hermes completion bash|zsh  Shell 补全
hermes acp                  ACP 服务器（IDE 集成）
hermes claw migrate         从 OpenClaw 迁移
hermes uninstall            卸载 Hermes
```

---

## 斜杠命令（会话内） {#slash-commands-in-session}

--- END DOCUMENT CHUNK ---
在交互式聊天会话期间输入这些命令。

### 会话控制 {#session-control}
```
/new (/reset)        全新会话
/clear               清屏 + 全新会话（CLI）
/retry               重新发送上一条消息
/undo                移除上一次对话
/title [名称]        为会话命名
/compress            手动压缩上下文
/stop                终止后台进程
/rollback [N]        恢复文件系统检查点
/background <提示词> 在后台运行提示词
/queue <提示词>      排队等待下一轮
/resume [名称]       恢复一个已命名的会话
```

### 配置 {#configuration}
```
/config              显示配置（CLI）
/model [名称]        显示或更改模型
/personality [名称]  设置个性
/reasoning [级别]    设置推理级别（none|minimal|low|medium|high|xhigh|show|hide）
/verbose             循环切换：关闭 → 新 → 全部 → 详细
/voice [on|off|tts]  语音模式
/yolo                切换审批绕过
/skin [名称]         更改主题（CLI）
/statusbar           切换状态栏（CLI）
```

### 工具与技能 {#tools-skills}
```
/tools               管理工具（CLI）
/toolsets            列出工具集（CLI）
/skills              搜索/安装技能（CLI）
/skill <名称>        将技能加载到会话中
/cron                管理定时任务（CLI）
/reload-mcp          重新加载 MCP 服务器
/plugins             列出插件（CLI）
```

### 网关 {#gateway}
```
/approve             批准待处理的命令（网关）
/deny                拒绝待处理的命令（网关）
/restart             重启网关（网关）
/sethome             将当前聊天设为首页频道（网关）
/update              将 Hermes 更新到最新版本（网关）
/platforms (/gateway) 显示平台连接状态（网关）
```
### 实用工具 {#utility}
```
/branch (/fork)      分支当前会话
/fast                切换优先级/快速处理
/browser             打开 CDP 浏览器连接
/history             显示对话历史（CLI）
/save                将对话保存到文件（CLI）
/paste               附加剪贴板图片（CLI）
/image               附加本地图片文件（CLI）
```

### 信息 {#info}
```
/help                显示命令
/commands [page]     浏览所有命令（网关）
/usage               令牌用量
/insights [days]     用量分析
/status              会话信息（网关）
/profile             当前配置文件信息
```

### 退出 {#exit}
```
/quit (/exit, /q)    退出 CLI
```

---

## 关键路径与配置 {#key-paths-config}

```
~/.hermes/config.yaml       主配置文件
~/.hermes/.env               API 密钥与机密
$HERMES_HOME/skills/         已安装的技能
~/.hermes/sessions/          会话记录
~/.hermes/logs/              网关与错误日志
~/.hermes/auth.json          OAuth 令牌与凭据池
~/.hermes/hermes-agent/      源代码（如果通过 git 安装）
```

配置文件使用 `~/.hermes/profiles/&lt;name&gt;/` 目录，布局相同。

### 配置项 {#config-sections}

使用 `hermes config edit` 或 `hermes config set section.key value` 进行编辑。

| 配置段 | 键选项 |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |
完整配置参考：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### 提供商 {#providers}

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
| Alibaba / DashScope | API 密钥 | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API 密钥 | `XIAOMI_API_KEY` |
| Kilo Code | API 密钥 | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API 密钥 | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API 密钥 | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API 密钥 | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| 自定义端点 | 配置 | `model.base_url` + `model.api_key` 在 config.yaml 中 |
| GitHub Copilot ACP | 外部 | `COPILOT_CLI_PATH` 或 Copilot CLI |

完整提供商文档：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 工具集 {#toolsets}

通过 `hermes tools`（交互式）或 `hermes tools enable/disable NAME` 启用/禁用。
| 工具集 | 提供的能力 |
|---------|-----------|
| `web` | 网页搜索与内容提取 |
| `browser` | 浏览器自动化（Browserbase、Camofox 或本地 Chromium） |
| `terminal` | Shell 命令与进程管理 |
| `file` | 文件读写/搜索/补丁 |
| `code_execution` | 沙箱化 Python 执行 |
| `vision` | 图像分析 |
| `image_gen` | AI 图像生成 |
| `tts` | 文本转语音 |
| `skills` | 技能浏览与管理 |
| `memory` | 跨会话持久化记忆 |
| `session_search` | 搜索历史对话 |
| `delegation` | 子 Agent 任务委派 |
| `cronjob` | 定时任务管理 |
| `clarify` | 向用户提问以澄清需求 |
| `messaging` | 跨平台消息发送 |
| `search` | 仅网页搜索（`web` 的子集） |
| `todo` | 会话内任务规划与跟踪 |
| `rl` | 强化学习工具（默认关闭） |
| `moa` | Agent 混合（默认关闭） |
| `homeassistant` | 智能家居控制（默认关闭） |

工具变更在 `/reset`（新会话）后生效。它们不会在对话中途生效，以保持提示缓存。

---

## 安全与隐私开关 {#security-privacy-toggles}

常见问题：“为什么 Hermes 对我的输出/工具调用/命令做了 X？”——以及修改它们的具体命令。其中大部分需要新会话（在聊天中输入 `/reset`，或启动新的 `hermes` 调用），因为这些设置只在启动时读取一次。

### 工具输出中的密钥脱敏 {#secret-redaction-in-tool-output}

密钥脱敏**默认关闭**——工具输出（终端 stdout、`read_file`、网页内容、子 Agent 摘要等）原样通过。如果用户希望 Hermes 在将内容送入对话上下文和日志之前自动屏蔽看起来像 API 密钥、令牌和密钥的字符串：
```bash
hermes config set security.redact_secrets true       # 全局启用
```

**需要重启。** `security.redact_secrets` 在导入时快照——在会话中途切换（例如通过工具调用执行 `export HERMES_REDACT_SECRETS=true`）不会对当前运行进程生效。请告知用户在终端中运行 `hermes config set security.redact_secrets true`，然后启动新会话。这是有意为之——防止 LLM 在任务进行中自行翻转开关。

再次禁用：
```bash
hermes config set security.redact_secrets false
```

### 网关消息中的 PII 脱敏 {#pii-redaction-in-gateway-messages}

与机密脱敏分开。启用后，网关会在上下文到达模型之前对用户 ID 进行哈希处理，并从会话上下文中去除电话号码：

```bash
hermes config set privacy.redact_pii true    # 启用
hermes config set privacy.redact_pii false   # 禁用（默认）
```

### 命令审批提示 {#command-approval-prompts}

默认情况下（`approvals.mode: manual`），Hermes 会在运行被标记为破坏性的 shell 命令（`rm -rf`、`git reset --hard` 等）之前提示用户。模式包括：

- `manual` — 始终提示（默认）
- `smart` — 使用辅助 LLM 自动批准低风险命令，高风险时提示
- `off` — 跳过所有审批提示（等同于 `--yolo`）

```bash
hermes config set approvals.mode smart       # 推荐的折中方案
hermes config set approvals.mode off         # 绕过所有检查（不推荐）
```

无需修改配置即可单次绕过：
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`
注意：YOLO / `approvals.mode: off` 并不会关闭秘密内容编辑功能。两者是独立的。

### Shell 钩子允许列表 {#shell-hooks-allowlist}

某些 shell 钩子集成需要显式加入允许列表后才能触发。通过 `~/.hermes/shell-hooks-allowlist.json` 管理——当钩子首次尝试运行时，会交互式地提示用户进行设置。

### 禁用 Web/浏览器/图像生成工具 {#disabling-the-web-browser-image-gen-tools}

若要让模型完全远离网络或媒体工具，请打开 `hermes tools` 并按平台切换开关。更改将在下次会话（`/reset`）时生效。请参阅上方的“工具与技能”部分。

---

## 语音与转录 {#voice-transcription}

### STT（语音 → 文本） {#stt-voice-text}

来自消息平台的语音消息会自动转录。

提供商优先级（自动检测）：
1. **本地 faster-whisper** — 免费，无需 API 密钥：`pip install faster-whisper`
2. **Groq Whisper** — 免费套餐：设置 `GROQ_API_KEY`
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

### TTS（文本 → 语音） {#tts-text-voice}

| 提供商 | 环境变量 | 免费？ |
|----------|---------|-------|
| Edge TTS | 无 | 是（默认） |
| ElevenLabs | `ELEVENLABS_API_KEY` | 免费套餐 |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | 付费 |
| MiniMax | `MINIMAX_API_KEY` | 付费 |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | 付费 |
| NeuTTS（本地） | 无（`pip install neutts[all]` + `espeak-ng`） | 免费 |

语音命令：`/voice on`（语音对语音）、`/voice tts`（始终语音）、`/voice off`。
---

## 生成额外的 Hermes 实例 {#spawning-additional-hermes-instances}

将额外的 Hermes 进程作为完全独立的子进程运行——独立的会话、工具和环境。

### 何时使用此功能 vs delegate_task {#when-to-use-this-vs-delegatetask}

| | `delegate_task` | 生成 `hermes` 进程 |
|-|-----------------|--------------------------|
| 隔离性 | 独立对话，共享进程 | 完全独立的进程 |
| 持续时间 | 分钟级（受父循环限制） | 小时/天级 |
| 工具访问 | 父工具的子集 | 完全工具访问权限 |
| 交互性 | 否 | 是（PTY 模式） |
| 使用场景 | 快速并行子任务 | 长时间自主任务 |

### 一次性模式 {#one-shot-mode}

```
terminal(command="hermes chat -q '研究 GRPO 论文并将摘要写入 ~/research/grpo.md'", timeout=300)

# 长时间任务的背景运行：
terminal(command="hermes chat -q '为 ~/myapp 设置 CI/CD'", background=true)
```

### 交互式 PTY 模式（通过 tmux） {#interactive-pty-mode-via-tmux}

Hermes 使用 prompt_toolkit，这需要一个真实的终端。使用 tmux 进行交互式生成：

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
### 多 Agent 协调 {#multi-agent-coordination}

```
# Agent A：后端
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend '构建用户管理 REST API' Enter", timeout=15)

# Agent B：前端
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend '构建用户管理 React 仪表盘' Enter", timeout=15)

# 检查进度，在它们之间传递上下文
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend '这是来自后端 Agent 的 API 模式：...' Enter", timeout=5)
```

### 会话恢复 {#session-resume}

```
# 恢复最近的会话
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# 恢复指定会话
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### 提示 {#tips}

- **对于快速子任务，优先使用 `delegate_task`** — 比启动完整进程的开销更小
- **在生成编辑代码的 Agent 时，使用 `-w`（工作树模式）** — 可防止 git 冲突
- **为一次性模式设置超时时间** — 复杂任务可能需要 5-10 分钟
- **使用 `hermes chat -q` 实现“发后即忘”** — 无需 PTY
- **使用 tmux 进行交互式会话** — 原始 PTY 模式在 prompt_toolkit 中存在 `\r` 与 `\n` 的问题
- **对于定时任务，使用 `cronjob` 工具而不是启动 Agent** — 可处理投递和重试
---

## 故障排除 {#troubleshooting}

### 语音无法使用 {#voice-not-working}
1. 检查 `stt.enabled: true` 是否在 config.yaml 中已设置
2. 验证提供商：`pip install faster-whisper` 或设置 API 密钥
3. 在网关中：`/restart`。在 CLI 中：退出并重新启动。

### 工具不可用 {#tool-not-available}
1. `hermes tools` — 检查工具集是否已为你的平台启用
2. 某些工具需要环境变量（检查 `.env`）
3. 启用工具后执行 `/reset`

### 模型/提供商问题 {#model-provider-issues}
1. `hermes doctor` — 检查配置和依赖项
2. `hermes login` — 重新认证 OAuth 提供商
3. 检查 `.env` 中是否有正确的 API 密钥
4. **Copilot 403**：`gh auth login` 生成的令牌**不**适用于 Copilot API。你必须通过 `hermes model` → GitHub Copilot 使用 Copilot 专用的 OAuth 设备代码流程。

### 更改未生效 {#changes-not-taking-effect}
- **工具/技能：** `/reset` 会使用更新后的工具集启动新会话
- **配置更改：** 在网关中：`/restart`。在 CLI 中：退出并重新启动。
- **代码更改：** 重启 CLI 或网关进程

### 技能未显示 {#skills-not-showing}
1. `hermes skills list` — 验证是否已安装
2. `hermes skills config` — 检查平台启用状态
3. 显式加载：`/skill name` 或 `hermes -s name`

### 网关问题 {#gateway-issues}
首先检查日志：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见网关问题：
- **SSH 登出后网关停止运行**：启用 linger：`sudo loginctl enable-linger $USER`
- **WSL2 关闭后网关停止运行**：WSL2 需要在 `/etc/wsl.conf` 中设置 `systemd=true` 才能使 systemd 服务正常工作。否则，网关会回退到 `nohup`（会话关闭时停止）。
- **网关崩溃循环**：重置失败状态：`systemctl --user reset-failed hermes-gateway`
### 平台特定问题 {#platform-specific-issues}
- **Discord 机器人静默无响应**：必须在 Bot → 特权网关意图（Privileged Gateway Intents）中启用**消息内容意图（Message Content Intent）**。
- **Slack 机器人仅能在私信中工作**：必须订阅 `message.channels` 事件。否则机器人会忽略公开频道。
- **Windows HTTP 400 "No models provided"**：配置文件编码问题（BOM）。请确保 `config.yaml` 以 UTF-8 无 BOM 格式保存。

### 辅助模型不工作 {#auxiliary-models-not-working}
如果 `auxiliary`（辅助）任务（视觉、压缩、会话搜索）静默失败，`auto` 提供者将无法找到后端。请设置 `OPENROUTER_API_KEY` 或 `GOOGLE_API_KEY`，或者显式配置每个辅助任务的提供者：
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## 查找内容 {#where-to-find-things}

| 查找内容... | 位置 |
|----------------|----------|
| 配置选项 | `hermes config edit` 或 [配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| 可用工具 | `hermes tools list` 或 [工具参考](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| 斜杠命令 | 会话中输入 `/help` 或 [斜杠命令参考](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| 技能目录 | `hermes skills browse` 或 [技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| 提供者设置 | `hermes model` 或 [提供者指南](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| 平台设置 | `hermes gateway setup` 或 [消息文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP 服务器 | `hermes mcp list` 或 [MCP 指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| 配置文件 | `hermes profile list` 或 [配置文件文档](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| 定时任务 | `hermes cron list` 或 [Cron 文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| 记忆 | `hermes memory status` 或 [记忆文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| 环境变量 | `hermes config env-path` 或 [环境变量参考](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI 命令 | `hermes --help` 或 [CLI 参考](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| 网关日志 | `~/.hermes/logs/gateway.log` |
| 会话文件 | `~/.hermes/sessions/` 或 `hermes sessions browse` |
| 源代码 | `~/.hermes/hermes-agent/` |
---

## 贡献者快速参考 {#contributor-quick-reference}

面向偶尔贡献者和 PR 作者。完整开发者文档：https://hermes-agent.nousresearch.com/docs/developer-guide/

### 项目结构 {#project-layout}

<!-- ascii-guard-ignore -->
```
hermes-agent/
├── run_agent.py          # AIAgent — 核心对话循环
├── model_tools.py        # 工具发现与调度
├── toolsets.py           # 工具集定义
├── cli.py                # 交互式 CLI（HermesCLI）
├── hermes_state.py       # SQLite 会话存储
├── agent/                # 提示构建器、上下文压缩、记忆、模型路由、凭证池、技能调度
├── hermes_cli/           # CLI 子命令、配置、设置、命令
│   ├── commands.py       # 斜杠命令注册表（CommandDef）
│   ├── config.py         # DEFAULT_CONFIG、环境变量定义
│   └── main.py           # CLI 入口和 argparse
├── tools/                # 每个工具一个文件
│   └── registry.py       # 中央工具注册表
├── gateway/              # 消息网关
│   └── platforms/        # 平台适配器（telegram、discord 等）
├── cron/                 # 任务调度器
├── tests/                # 约 3000 个 pytest 测试
└── website/              # Docusaurus 文档站点
```
<!-- ascii-guard-ignore-end -->

配置：`~/.hermes/config.yaml`（设置），`~/.hermes/.env`（API 密钥）。

### 添加工具（3 个文件） {#adding-a-tool-3-files}

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

自动发现：任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入——无需手动添加列表。

所有处理程序必须返回 JSON 字符串。使用 `get_hermes_home()` 获取路径，切勿硬编码 `~/.hermes`。

### 添加斜杠命令 {#adding-a-slash-command}

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加 `CommandDef`
2. 在 `cli.py` → `process_command()` 中添加处理程序
3. （可选）在 `gateway/run.py` 中添加网关处理程序

所有消费者（帮助文本、自动补全、Telegram 菜单、Slack 映射）都会自动从中央注册表中派生。

### Agent 循环（高层级） {#agent-loop-high-level}

```
run_conversation():
  1. 构建系统提示
  2. 当迭代次数 < max 时循环：
     a. 调用 LLM（OpenAI 格式消息 + 工具模式）
     b. 如果有 tool_calls → 通过 handle_function_call() 分发每个调用 → 追加结果 → 继续
     c. 如果有文本响应 → 返回
  3. 接近 token 限制时自动触发上下文压缩
```

### 测试 {#testing}

```bash
python -m pytest tests/ -o 'addopts=' -q   # 完整测试套件
python -m pytest tests/tools/ -q            # 特定区域
```

- 测试会自动将 `HERMES_HOME` 重定向到临时目录——绝不会触及真实的 `~/.hermes/`
- 推送任何更改前运行完整测试套件
- 使用 `-o 'addopts='` 清除任何内置的 pytest 标志

### 提交约定 {#commit-conventions}

```
type: 简洁的主题行

可选正文。
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

### 关键规则 {#key-rules}

- **切勿破坏提示缓存**——不要在对话中途更改上下文、工具或系统提示
- **消息角色交替**——不能连续出现两条 assistant 或两条 user 消息
- 对所有路径使用 `hermes_constants` 中的 `get_hermes_home()`（配置文件安全）
- 配置值放在 `config.yaml` 中，密钥放在 `.env` 中
- 新工具需要 `check_fn`，以便仅在满足要求时出现
