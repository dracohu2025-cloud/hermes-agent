---
sidebar_position: 2
title: "环境变量"
description: "Hermes Agent 使用的所有环境变量的完整参考"
---

<a id="environment-variables-reference"></a>
# 环境变量参考

所有变量均放在 `~/.hermes/.env` 中。你也可以通过 `hermes config set 变量名 值` 来设置。

<a id="llm-providers"></a>
## LLM 提供商

| 变量名 | 说明 |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥（推荐使用，灵活性高） |
| `OPENROUTER_BASE_URL` | 覆盖兼容 OpenRouter 的基础 URL |
| `HERMES_OPENROUTER_CACHE` | 启用 OpenRouter 响应缓存（`1`/`true`/`yes`/`on`）。会覆盖 `config.yaml` 中的 `openrouter.response_cache`。参见 [响应缓存](https://openrouter.ai/docs/guides/features/response-caching)。 |
| `HERMES_OPENROUTER_CACHE_TTL` | 缓存 TTL，单位为秒（1-86400）。会覆盖 `config.yaml` 中的 `openrouter.response_cache_ttl`。 |
| `NOUS_BASE_URL` | 覆盖 Nous Portal 基础 URL（极少需要；仅用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 直接覆盖 Nous 推理端点 |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway API 密钥（[ai-gateway.vercel.sh](https://ai-gateway.vercel.sh)） |
| `AI_GATEWAY_BASE_URL` | 覆盖 AI Gateway 基础 URL（默认值：`https://ai-gateway.vercel.sh/v1`） |
| `OPENAI_API_KEY` | 用于自定义兼容 OpenAI 端点的 API 密钥（与 `OPENAI_BASE_URL` 配合使用） |
| `OPENAI_BASE_URL` | 自定义端点（VLLM、SGLang 等）的基础 URL |
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub token — 第一优先级（OAuth `gho_*` 或细粒度 PAT `github_pat_*`；经典 PAT `ghp_*` **不支持**） |
| `GH_TOKEN` | GitHub token — 第二优先级，用于 Copilot（`gh` CLI 也会使用） |
| `GITHUB_TOKEN` | GitHub token — 第三优先级，用于 Copilot |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot ACP CLI 二进制路径（默认值：`copilot`） |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND` 的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 Copilot ACP 参数（默认值：`--acp --stdio`） |
| `COPILOT_ACP_BASE_URL` | 覆盖 Copilot ACP 基础 URL |
| `GLM_API_KEY` | z.ai / 智谱 GLM API 密钥（[z.ai](https://z.ai)） |
| `ZAI_API_KEY` | `GLM_API_KEY` 的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY` 的别名 |
| `GLM_BASE_URL` | 覆盖 z.ai 基础 URL（默认值：`https://api.z.ai/api/paas/v4`） |
| `KIMI_API_KEY` | Kimi / Moonshot AI API 密钥（[moonshot.ai](https://platform.moonshot.ai)） |
| `KIMI_BASE_URL` | 覆盖 Kimi 基础 URL（默认值：`https://api.moonshot.ai/v1`） |
| `KIMI_CN_API_KEY` | Kimi / Moonshot 中国区 API 密钥（[moonshot.cn](https://platform.moonshot.cn)） |
| `ARCEEAI_API_KEY` | Arcee AI API 密钥（[chat.arcee.ai](https://chat.arcee.ai/)） |
| `ARCEE_BASE_URL` | 覆盖 Arcee 基础 URL（默认值：`https://api.arcee.ai/api/v1`） |
| `GMI_API_KEY` | GMI Cloud API 密钥（[gmicloud.ai](https://www.gmicloud.ai/)） |
| `GMI_BASE_URL` | 覆盖 GMI Cloud 基础 URL（默认值：`https://api.gmi-serving.com/v1`） |
| `MINIMAX_API_KEY` | MiniMax API 密钥 — 全球端点（[minimax.io](https://www.minimax.io)）。**`minimax-oauth` 不使用此变量**（OAuth 路径改用浏览器登录）。 |
| `MINIMAX_BASE_URL` | 覆盖 MiniMax 基础 URL（默认值：`https://api.minimax.io/anthropic` — Hermes 使用 MiniMax 兼容 Anthropic Messages 的端点）。**`minimax-oauth` 不使用此变量**。 |
| `MINIMAX_CN_API_KEY` | MiniMax API 密钥 — 中国区端点（[minimaxi.com](https://www.minimaxi.com)）。**`minimax-oauth` 不使用此变量**（OAuth 路径改用浏览器登录）。 |
| `MINIMAX_CN_BASE_URL` | 覆盖 MiniMax 中国区基础 URL（默认值：`https://api.minimaxi.com/anthropic`）。**`minimax-oauth` 不使用此变量**。 |
| `KILOCODE_API_KEY` | Kilo Code API 密钥（[kilo.ai](https://kilo.ai)） |
| `KILOCODE_BASE_URL` | 覆盖 Kilo Code 基础 URL（默认值：`https://api.kilo.ai/api/gateway`） |
| `XIAOMI_API_KEY` | 小米 MiMo API 密钥（[platform.xiaomimimo.com](https://platform.xiaomimimo.com)） |
| `XIAOMI_BASE_URL` | 覆盖小米 MiMo 基础 URL（默认值：`https://api.xiaomimimo.com/v1`） |
| `TOKENHUB_API_KEY` | 腾讯 TokenHub API 密钥（[tokenhub.tencentmaas.com](https://tokenhub.tencentmaas.com)） |
| `TOKENHUB_BASE_URL` | 覆盖腾讯 TokenHub 基础 URL（默认值：`https://tokenhub.tencentmaas.com/v1`） |
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI API 密钥（[ai.azure.com](https://ai.azure.com/)）。当 `model.auth_mode: entra_id` 时不需要。 |
| `AZURE_FOUNDRY_BASE_URL` | Microsoft Foundry 端点 URL（例如 `https://<资源>.openai.azure.com/openai/v1` 用于 OpenAI 风格，或 `https://<资源>.services.ai.azure.com/anthropic` 用于 Anthropic 风格） |
| `AZURE_ANTHROPIC_KEY` | 用于 `provider: anthropic` + `base_url` 指向 Microsoft Foundry Claude 部署的 Azure Anthropic API 密钥（当同时配置了 Anthropic 和 Azure Anthropic 时，作为 `ANTHROPIC_API_KEY` 的替代） |
| `AZURE_TENANT_ID` | Entra ID 租户 ID（服务主体流程；当 `model.auth_mode: entra_id` 时由 `azure-identity` 使用） |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载标识或用户分配的托管标识） |
| `AZURE_CLIENT_SECRET` | `EnvironmentCredential` 使用的服务主体密码 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（`AZURE_CLIENT_SECRET` 的替代） |
| `AZURE_FEDERATED_TOKEN_FILE` | 用于 AKS 工作负载标识 / OIDC 流程的联合令牌文件路径 |
| `AZURE_AUTHORITY_HOST` | 主权云权限覆盖（例如 Azure Government 使用 `https://login.microsoftonline.us`）。参见 [Azure Foundry 指南](/guides/azure-foundry#sovereign-clouds-government-china) |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | 用于应用服务、函数和容器应用的托管标识端点；VM 通常使用 IMDS 而不设置这些变量 |
| `HF_TOKEN` | Hugging Face 推理提供商的令牌（[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)） |
| `HF_BASE_URL` | 覆盖 Hugging Face 基础 URL（默认值：`https://router.huggingface.co/v1`） |
| `GOOGLE_API_KEY` | Google AI Studio API 密钥（[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)） |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY` 的别名 |
| `GEMINI_BASE_URL` | 覆盖 Google AI Studio 基础 URL |
| `HERMES_GEMINI_CLIENT_ID` | 用于 `google-gemini-cli` PKCE 登录的 OAuth 客户端 ID（可选；默认使用 Google 的公开 gemini-cli 客户端） |
| `HERMES_GEMINI_CLIENT_SECRET` | 用于 `google-gemini-cli` 的 OAuth 客户端密码（可选） |
| `HERMES_GEMINI_PROJECT_ID` | 付费 Gemini 层级的 GCP 项目 ID（免费层会自动配置） |
| `ANTHROPIC_API_KEY` | Anthropic Console API 密钥（[console.anthropic.com](https://console.anthropic.com/)） |
| `ANTHROPIC_TOKEN` | 手动或旧版 Anthropic OAuth/设置令牌覆盖 |
| `DASHSCOPE_API_KEY` | 通义千问（阿里云 DashScope）API 密钥，用于 Qwen 模型（[modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)） |
| `DASHSCOPE_BASE_URL` | 自定义 DashScope 基础 URL（默认值：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`；中国内地区域使用 `https://dashscope.aliyuncs.com/compatible-mode/v1`） |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于直接访问 DeepSeek（[platform.deepseek.com](https://platform.deepseek.com/api_keys)） |
| `DEEPSEEK_BASE_URL` | 自定义 DeepSeek API 基础 URL |
| `NOVITA_API_KEY` | NovitaAI API 密钥 — AI 原生云，提供模型 API、Agent 沙箱和 GPU 云（[novita.ai/settings/key-management](https://novita.ai/settings/key-management)） |
| `NOVITA_BASE_URL` | 覆盖 NovitaAI 基础 URL（默认值：`https://api.novita.ai/openai/v1`） |
| `NVIDIA_API_KEY` | NVIDIA NIM API 密钥 — Nemotron 和开放模型（[build.nvidia.com](https://build.nvidia.com)） |
| `NVIDIA_BASE_URL` | 覆盖 NVIDIA 基础 URL（默认值：`https://integrate.api.nvidia.com/v1`；对于本地 NIM 端点，设置为 `http://localhost:8000/v1`） |
| `STEPFUN_API_KEY` | StepFun API 密钥 — Step 系列模型（[platform.stepfun.com](https://platform.stepfun.com)） |
| `STEPFUN_BASE_URL` | 覆盖 StepFun 基础 URL（默认值：`https://api.stepfun.com/v1`） |
| `OLLAMA_API_KEY` | Ollama Cloud API 密钥 — 托管 Ollama 目录，无需本地 GPU（[ollama.com/settings/keys](https://ollama.com/settings/keys)） |
| `OLLAMA_BASE_URL` | 覆盖 Ollama Cloud 基础 URL（默认值：`https://ollama.com/v1`） |
| `XAI_API_KEY` | xAI (Grok) API 密钥，用于聊天 + TTS + 网络搜索（[console.x.ai](https://console.x.ai/)） |
| `XAI_BASE_URL` | 覆盖 xAI 基础 URL（默认值：`https://api.x.ai/v1`） |
| `MISTRAL_API_KEY` | Mistral API 密钥，用于 Voxtral TTS 和 Voxtral STT（[console.mistral.ai](https://console.mistral.ai)） |
| `AWS_REGION` | Bedrock 推理的 AWS 区域（例如 `us-east-1`、`eu-central-1`）。由 boto3 读取。 |
| `AWS_PROFILE` | Bedrock 认证的 AWS 命名配置文件（读取 `~/.aws/credentials`）。不设置则使用默认的 boto3 凭证链。 |
| `BEDROCK_BASE_URL` | 覆盖 Bedrock 运行时基础 URL（默认值：`https://bedrock-runtime.us-east-1.amazonaws.com`；通常不设置，而是使用 `AWS_REGION`） |
| `HERMES_QWEN_BASE_URL` | Qwen Portal 基础 URL 覆盖（默认值：`https://portal.qwen.ai/v1`） |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API 密钥 — 按需付费使用精选模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_ZEN_BASE_URL` | 覆盖 OpenCode Zen 基础 URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API 密钥 — 每月 10 美元订阅开放模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_GO_BASE_URL` | 覆盖 OpenCode Go 基础 URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 如果你手动导出，则显式覆盖 Claude Code 令牌 |
| `HERMES_MODEL` | 在进程级别覆盖模型名称（cron 调度器使用；正常使用推荐 `config.yaml`） |
| `VOICE_TOOLS_OPENAI_KEY` | 用于 OpenAI 语音转文本和文本转语音提供商的优先 OpenAI 密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给 `HERMES_LOCAL_STT_COMMAND` 或自动检测的本地 `whisper` CLI 回退的默认语言（默认值：`en`） |
| `HERMES_HOME` | 覆盖 Hermes 配置目录（默认值：`~/.hermes`）。同时限定网关 PID 文件和 systemd 服务名称的范围，因此多个安装可以同时运行 |
| `HERMES_GIT_BASH_PATH` | **仅限 Windows。** 覆盖终端工具使用的 `bash.exe` 发现路径。指向任何 bash — 完整 Git for Windows 安装、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序会自动将其设置为它提供的 PortableGit 路径。参见 [Windows（原生）指南](../user-guide/windows-native.md#how-hermes-runs-shell-commands-on-windows) |
| `HERMES_DISABLE_WINDOWS_UTF8` | **仅限 Windows。** 设置为 `1` 以禁用 UTF-8 stdio 垫片（`configure_windows_stdio()`）并回退到控制台的区域代码页。用于排查编码错误；在正常操作中很少需要正确设置 |
| `HERMES_KANBAN_HOME` | 覆盖共享的 Hermes 根目录，该目录锚定看板（数据库 + 工作空间 + 工作器日志）。回退到 `get_default_hermes_root()`（任何活动配置文件的父目录）。用于测试和特殊部署 |
| `HERMES_KANBAN_BOARD` | 锁定当前进程的活跃看板。优先级高于 `~/.hermes/kanban/current`；调度器会将其注入工作器子进程环境，因此工作器物理上无法看到其他看板的任务。默认值为 `default`。slug 验证：小写字母数字 + 连字符 + 下划线，1-64 个字符 |
| `HERMES_KANBAN_DB` | 直接锁定看板数据库文件路径（最高优先级；优先级高于 `HERMES_KANBAN_BOARD` 和 `HERMES_KANBAN_HOME`）。调度器会将其注入工作器子进程环境，因此配置文件工作器会收敛到调度器的看板 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 直接锁定看板工作空间根目录（工作空间的最高优先级；优先级高于 `HERMES_KANBAN_HOME`）。调度器会将其注入工作器子进程环境 |
| `HERMES_KANBAN_DISPATCH_IN_GATEWAY` | 运行时覆盖 `kanban.dispatch_in_gateway`。设置为 `0`、`false`、`no` 或 `off` 可阻止网关启动嵌入式看板调度器；任何其他非空值则启用它。当单独的调度器进程拥有看板时很有用。 |
<a id="provider-auth-oauth"></a>
## Provider Auth (OAuth)

对于 Anthropic 原生认证，Hermes 更喜欢使用 Claude Code 自己的凭证文件（如果存在），因为那些凭证可以自动刷新。**针对 Anthropic 的 OAuth 需要一个购买了额外使用额度的 Claude Max 计划**——Hermes 以 Claude Code 身份路由，仅消耗 Max 计划的额外/超额额度，而不是基本的 Max 额度，并且不适用于 Claude Pro。如果没有 Max + 额外额度，请改用 API 密钥。像 `ANTHROPIC_TOKEN` 这样的环境变量仍然可用作手动覆盖，但它们不再是 Claude Max 登录的首选方式。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_INFERENCE_PROVIDER` | 覆盖提供商选择：`auto`、`custom`、`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`huggingface`、`novita`、`gemini`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`（浏览器 OAuth 登录 —— 无需 API 密钥；请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)）、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`xai-oauth`（SuperGrok 订阅用户的浏览器 OAuth 登录 —— 无需 API 密钥；请参阅 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)）、`google-gemini-cli`、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`、`tencent-tokenhub`（默认值：`auto`） |
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 最小 Agent 密钥 TTL（重新生成前的时间），默认值：1800 = 30 分钟 |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭证/令牌流的 HTTP 超时时间 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 一个 JSON 文件的路径，该文件包含在 API 调用时注入的临时预填充消息 |
| `HERMES_TIMEZONE` | IANA 时区覆盖（例如 `America/New_York`） |

<a id="tool-apis"></a>
## Tool APIs

| 变量 | 描述 |
|----------|-------------|
| `PARALLEL_API_KEY` | AI 原生网络搜索 ([parallel.ai](https://parallel.ai/)) |
| `FIRECRAWL_API_KEY` | 网页抓取和云端浏览器 ([firecrawl.dev](https://firecrawl.dev/)) |
| `FIRECRAWL_API_URL` | 自定义 Firecrawl API 端点，用于自托管实例（可选） |
| `TAVILY_API_KEY` | Tavily API 密钥，用于 AI 原生网络搜索、提取和抓取 ([app.tavily.com](https://app.tavily.com/home)) |
| `SEARXNG_URL` | SearXNG 实例 URL，用于免费的自托管网络搜索 —— 无需 API 密钥 ([searxng.github.io](https://searxng.github.io/searxng/)) |
| `TAVILY_BASE_URL` | 覆盖 Tavily API 端点。适用于企业代理和自托管兼容 Tavily 的搜索后端。模式与 `GROQ_BASE_URL` 相同。 |
| `EXA_API_KEY` | Exa API 密钥，用于 AI 原生网络搜索和内容 ([exa.ai](https://exa.ai/)) |
| `BROWSERBASE_API_KEY` | 浏览器自动化 ([browserbase.com](https://browserbase.com/)) |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目 ID |
| `BROWSER_USE_API_KEY` | Browser Use 云端浏览器 API 密钥 ([browser-use.com](https://browser-use.com/)) |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl 浏览器会话 TTL（秒），默认值：300 |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools Protocol URL（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `CAMOFOX_URL` | Camofox 本地反检测浏览器 URL（默认值：`http://localhost:9377`） |
| `CAMOFOX_USER_ID` | 可选的由外部管理的 Camofox 用户 ID，用于共享可见会话 |
| `CAMOFOX_SESSION_KEY` | 可选的 Camofox 会话密钥，用于为 `CAMOFOX_USER_ID` 创建标签页时使用 |
| `CAMOFOX_ADOPT_EXISTING_TAB` | 设置为 `true` 以在创建新标签页之前重用现有的 Camofox 标签页 |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话不活动超时（秒） |
| `AGENT_BROWSER_ARGS` | 额外的 Chromium 启动标志（逗号或换行分隔）。当 Hermes 以 root 身份运行或在 AppArmor 限制的无特权用户命名空间（Ubuntu 23.10+、DGX Spark、许多容器镜像）下运行时，会自动注入 `--no-sandbox,--disable-dev-shm-usage`；仅当要覆盖或添加其他标志时才手动设置此变量。 |
| `FAL_KEY` | 图像生成 ([fal.ai](https://fal.ai/)) |
| `GROQ_API_KEY` | Groq Whisper STT API 密钥 ([groq.com](https://groq.com/)) |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级 TTS 语音 ([elevenlabs.io](https://elevenlabs.io/)) |
| `STT_GROQ_MODEL` | 覆盖 Groq STT 模型（默认值：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq 的 OpenAI 兼容 STT 端点 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI STT 模型（默认值：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的 STT 端点 |
| `GITHUB_TOKEN` | GitHub 令牌，用于 Skills Hub（更高的 API 速率限制、技能发布） |
| `HONCHO_API_KEY` | 跨会话用户建模 ([honcho.dev](https://honcho.dev/)) |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的基础 URL（默认值：Honcho 云端）。本地实例无需 API 密钥 |
| `HINDSIGHT_TIMEOUT` | Hindsight 记忆提供者 API 调用的超时时间（秒），默认值：`60`。如果您的 Hindsight 实例在 `/sync` 或 `on_session_switch` 期间响应缓慢且您在 `errors.log` 中看到超时，请增加此值。 |
| `SUPERMEMORY_API_KEY` | 带个人资料回忆和会话摄入的语义长期记忆 ([supermemory.ai](https://supermemory.ai)) |
| `DAYTONA_API_KEY` | Daytona 云端沙箱 ([daytona.io](https://daytona.io/)) |
| `VERCEL_TOKEN` | Vercel 沙箱访问令牌 ([vercel.com](https://vercel.com/)) |
| `VERCEL_PROJECT_ID` | Vercel 项目 ID（与 `VERCEL_TOKEN` 一起使用） |
| `VERCEL_TEAM_ID` | Vercel 团队 ID（与 `VERCEL_TOKEN` 一起使用） |
| `VERCEL_OIDC_TOKEN` | Vercel 短期 OIDC 令牌（仅限开发环境的替代方案） |
<a id="langfuse-observability"></a>
### Langfuse 可观测性

内置 [`observability/langfuse`](/user-guide/features/built-in-plugins#observabilitylangfuse) 插件所需的环境变量。在 `~/.hermes/.env` 中设置。必须先启用插件（`hermes plugins enable observability/langfuse`，或在 `hermes plugins` 中勾选）才能使这些变量生效。

| 变量名 | 说明 |
|----------|-------------|
| `HERMES_LANGFUSE_PUBLIC_KEY` | Langfuse 项目的公钥（`pk-lf-...`）。必填。 |
| `HERMES_LANGFUSE_SECRET_KEY` | Langfuse 项目的私钥（`sk-lf-...`）。必填。 |
| `HERMES_LANGFUSE_BASE_URL` | Langfuse 服务器 URL（默认：`https://cloud.langfuse.com`）。自部署时设置。 |
| `HERMES_LANGFUSE_ENV` | 追踪上的环境标签（`production`、`staging` 等） |
| `HERMES_LANGFUSE_RELEASE` | 追踪上的发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | SDK 采样率 0.0–1.0（默认：`1.0`） |
| `HERMES_LANGFUSE_MAX_CHARS` | 序列化 payload 的每个字段截断字符数（默认：`12000`） |
| `HERMES_LANGFUSE_DEBUG` | `true` 会启用详细的插件日志，输出到 `agent.log` |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | 标准 Langfuse SDK 变量名。当对应的 `HERMES_LANGFUSE_*` 变量未设置时，作为后备方案接受。 |

<a id="nous-tool-gateway"></a>
### Nous 工具网关

以下变量为付费 Nous 订阅用户或自部署网关，用于配置 [工具网关](/user-guide/features/tool-gateway)。大多数用户不需要设置这些——网关通过 `hermes model` 或 `hermes tools` 自动配置。

| 变量名 | 说明 |
|----------|-------------|
| `TOOL_GATEWAY_DOMAIN` | 工具网关路由的基础域名（默认：`nousresearch.com`） |
| `TOOL_GATEWAY_SCHEME` | 网关 URL 的 HTTP 或 HTTPS 协议（默认：`https`） |
| `TOOL_GATEWAY_USER_TOKEN` | 工具网关的认证令牌（通常从 Nous 认证自动填充） |
| `FIRECRAWL_GATEWAY_URL` | 专门用于覆盖 Firecrawl 网关端点的 URL |

<a id="terminal-backend"></a>
## 终端后端

| 变量名 | 说明 |
|----------|-------------|
| `TERMINAL_ENV` | 后端：`local`、`docker`、`ssh`、`singularity`、`modal`、`daytona`、`vercel_sandbox` |
| `HERMES_DOCKER_BINARY` | 覆盖 Hermes 调用的容器二进制文件（例如 `podman`、`/usr/local/bin/docker`）。未设置时，Hermes 自动在 `PATH` 中查找 `docker` 或 `podman`。当两者都已安装且你想使用非默认项，或者二进制文件不在 `PATH` 中时需要此变量。 |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像（默认：`nikolaik/python-nodejs:python3.11-nodejs20`） |
| `TERMINAL_DOCKER_FORWARD_ENV` | 要显式转发到 Docker 终端会话的环境变量名称的 JSON 数组。注意：技能声明的 `required_environment_variables` 会自动转发——你只需要为那些未被任何技能声明的变量设置此变量。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载（逗号分隔的 `host:container` 对） |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级可选：将启动时的当前工作目录挂载到 Docker 的 `/workspace`（`true`/`false`，默认：`false`） |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像或 `.sif` 路径 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙箱镜像 |
| `TERMINAL_VERCEL_RUNTIME` | Vercel Sandbox 运行时（`node24`、`node22`、`python3.13`） |
| `TERMINAL_TIMEOUT` | 命令超时时间（秒） |
| `TERMINAL_LIFETIME_SECONDS` | 终端会话的最大生存时间（秒） |
| `TERMINAL_CWD` | 终端会话的工作目录（仅限网关/cron；CLI 使用启动目录） |
| `SUDO_PASSWORD` | 启用 sudo 而不需要交互式提示 |
对于云沙箱后端，持久化是面向文件系统的。`TERMINAL_LIFETIME_SECONDS` 控制 Hermes 何时清理空闲终端会话，后续恢复时可能会重新创建沙箱，而不是保持原有的活跃进程运行。

<a id="ssh-backend"></a>
## SSH 后端

| 变量 | 描述 |
|------|------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH 用户名 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久化 Shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

<a id="container-resources-docker-singularity-modal-daytona"></a>
## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 描述 |
|------|------|
| `TERMINAL_CONTAINER_CPU` | CPU 核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存（MB，默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘（MB，默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 跨会话持久化容器文件系统（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 工作区和覆盖层的主机目录（默认：`~/.hermes/sandboxes/`） |

<a id="persistent-shell"></a>
## 持久化 Shell

| 变量 | 描述 |
|------|------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久化 Shell（默认：`true`）。也可通过 `config.yaml` 中的 `terminal.persistent_shell` 设置 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久化 Shell（默认：`false`） |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久化 Shell（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

<a id="messaging"></a>
## 消息通道

| 变量 | 描述 |
|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人令牌（来自 @BotFather） |
| `TELEGRAM_ALLOWED_USERS` | 允许使用机器人的用户 ID，英文逗号分隔（适用于私聊、群组和论坛） |
| `TELEGRAM_GROUP_ALLOWED_USERS` | 仅在群组/论坛中授权的发送者用户 ID，英文逗号分隔（不授予私聊权限）。以 `-` 开头的 Chat-ID 格式值仍会被当作聊天 ID 处理，以兼容 `#17686` 之前的配置，但会发出弃用警告。 |
| `TELEGRAM_GROUP_ALLOWED_CHATS` | 允许的群组/论坛聊天 ID，英文逗号分隔；其中的任何成员均被授权 |
| `TELEGRAM_HOME_CHANNEL` | 用于定时任务投递的默认 Telegram 聊天/频道 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram 主频道的显示名称 |
| `TELEGRAM_CRON_THREAD_ID` | 接收定时任务投递的论坛主题 ID；仅在定时任务时覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID`。在主题模式下使用，以便对定时消息的回复开启新会话，而非命中系统大厅（#24409）。 |
| `TELEGRAM_WEBHOOK_URL` | Webhook 模式的公共 HTTPS URL（启用 webhook 而非轮询） |
| `TELEGRAM_WEBHOOK_PORT` | Webhook 服务器的本地监听端口（默认：`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | Telegram 在每个更新中回传用于验证的密钥令牌。**每当设置 `TELEGRAM_WEBHOOK_URL` 时必填** —— 网关会在没有该值时拒绝启动（GHSA-3vpc-7q5r-276h）。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_REACTIONS` | 在处理消息时启用表情反应（默认：`false`） |
| `TELEGRAM_REQUIRE_MENTION` | 在 Telegram 群组中回复前要求显式触发。等同于 `config.yaml` 中的 `telegram.require_mention`。 |
| `TELEGRAM_MENTION_PATTERNS` | JSON 数组、换行分隔列表或英文逗号分隔的正则唤醒词模式列表，在 Telegram 群组提及门控启用时接受。等同于 `telegram.mention_patterns`。 |
| `TELEGRAM_EXCLUSIVE_BOT_MENTIONS` | 启用后，Telegram 群组中的显式 `@...bot` 提及只会路由到被提及的机器人用户名，之后再执行回复或唤醒词回退。默认：`true`。等同于 `telegram.exclusive_bot_mentions`。 |
| `TELEGRAM_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all`。与 Discord 模式匹配。 |
| `TELEGRAM_IGNORED_THREADS` | 机器人从不响应的 Telegram 论坛主题/线程 ID，英文逗号分隔 |
| `TELEGRAM_PROXY` | Telegram 连接的代理 URL —— 覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_BOT_TOKEN` | Discord 机器人令牌 |
| `DISCORD_ALLOWED_USERS` | 允许使用机器人的 Discord 用户 ID，英文逗号分隔 |
| `DISCORD_ALLOWED_ROLES` | 允许使用机器人的 Discord 角色 ID，英文逗号分隔（与 `DISCORD_ALLOWED_USERS` 是“或”关系）。自动启用 Members Intent。当管理团队人员变动时很有用——角色授权会自动传播。 |
| `DISCORD_ALLOWED_CHANNELS` | 允许的 Discord 频道 ID，英文逗号分隔。设置后，机器人只在这些频道中回复（如果允许私聊，则也包含私聊）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。 |
| `DISCORD_PROXY` | Discord 连接的代理 URL —— 覆盖 `HTTPS_PROXY`。支持 `http://`、`https://`、`socks5://` |
| `DISCORD_HOME_CHANNEL` | 用于定时任务投递的默认 Discord 频道 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord 主频道的显示名称 |
| `DISCORD_COMMAND_SYNC_POLICY` | Discord 斜杠命令启动同步策略：`safe`（差异调和）、`bulk`（传统 `tree.sync()`）或 `off` |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中回复前要求 @提及 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 不要求提及即可回复的频道 ID，英文逗号分隔 |
| `DISCORD_AUTO_THREAD` | 在支持时自动将长回复转为线程 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 当为 `true` 时，接受任意文件类型的附件（不仅限于内置的 PDF/文本/zip/office 允许列表）。未知类型会被缓存并作为本地路径提供给 Agent，使其能通过 `terminal` / `read_file` / `ffprobe` 检查。默认 `false`。 |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 网关会缓存的每个附件的最大字节数。默认 `33554432`（32 MiB）。设为 `0` 表示无上限（附件在写入时保留在内存中）。 |
| `DISCORD_REACTIONS` | 在处理消息时启用表情反应（默认：`true`） |
| `DISCORD_IGNORED_CHANNELS` | 机器人从不响应的频道 ID，英文逗号分隔 |
| `DISCORD_NO_THREAD_CHANNELS` | 机器人回复时不自动创建线程的频道 ID，英文逗号分隔 |
| `DISCORD_REPLY_TO_MODE` | 回复引用行为：`off`、`first`（默认）或 `all` |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 允许机器人 @`@everyone`/`@here`（默认：`false`）。请参见 [Mention Control](../user-guide/messaging/discord.md#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 允许机器人 @`@role` 提及（默认：`false`）。 |
| `DISCORD_ALLOW_MENTION_USERS` | 允许机器人 @个别 `@user` 提及（默认：`true`）。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 在回复其消息时 @提及原作者（默认：`true`）。 |
| `SLACK_BOT_TOKEN` | Slack 机器人令牌（`xoxb-...`） |
| `SLACK_APP_TOKEN` | Slack 应用级令牌（`xapp-...`，Socket 模式必需） |
| `SLACK_ALLOWED_USERS` | 允许的 Slack 用户 ID，英文逗号分隔 |
| `SLACK_HOME_CHANNEL` | 用于定时任务投递的默认 Slack 频道 |
| `SLACK_HOME_CHANNEL_NAME` | Slack 主频道的显示名称 |
| `GOOGLE_CHAT_PROJECT_ID` | 托管 Pub/Sub 主题的 GCP 项目（回退到 `GOOGLE_CLOUD_PROJECT`） |
| `GOOGLE_CHAT_SUBSCRIPTION_NAME` | Pub/Sub 订阅完整路径，格式 `projects/{proj}/subscriptions/{sub}`（旧别名：`GOOGLE_CHAT_SUBSCRIPTION`） |
| `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` | 服务账号 JSON 文件路径或内联 JSON（回退到 `GOOGLE_APPLICATION_CREDENTIALS`） |
| `GOOGLE_CHAT_ALLOWED_USERS` | 允许与机器人聊天的用户邮箱，英文逗号分隔 |
| `GOOGLE_CHAT_ALLOW_ALL_USERS` | 允许任何 Google Chat 用户触发机器人（仅用于开发） |
| `GOOGLE_CHAT_HOME_CHANNEL` | 用于定时任务投递的默认空间（例如 `spaces/AAAA...`） |
| `GOOGLE_CHAT_HOME_CHANNEL_NAME` | Google Chat 主空间的显示名称 |
| `GOOGLE_CHAT_MAX_MESSAGES` | Pub/Sub FlowControl 最大在途中消息数（默认：`1`） |
| `GOOGLE_CHAT_MAX_BYTES` | Pub/Sub FlowControl 最大在途中字节数（默认：`16777216`，16 MiB） |
| `GOOGLE_CHAT_BOOTSTRAP_SPACES` | 在启动时探测机器人自身 `users/{id}` 时额外探测的空间 ID，英文逗号分隔 |
| `GOOGLE_CHAT_DEBUG_RAW` | 设为任意值以在 DEBUG 级别记录脱敏后的 Pub/Sub 信封（仅调试用） |
| `WHATSAPP_ENABLED` | 启用 WhatsApp 桥接（`true`/`false`） |
| `WHATSAPP_MODE` | `bot`（独立号码）或 `self-chat`（给自己发消息） |
| `WHATSAPP_ALLOWED_USERS` | 允许的手机号，英文逗号分隔（含国家代码，不含 `+`），或 `*` 表示允许所有发送者 |
| `WHATSAPP_ALLOW_ALL_USERS` | 允许所有 WhatsApp 发送者，无需允许列表（`true`/`false`） |
| `WHATSAPP_DEBUG` | 记录桥接中的原始消息事件以进行故障排查（`true`/`false`） |
| `SIGNAL_HTTP_URL` | signal-cli 守护进程的 HTTP 端点（例如 `http://127.0.0.1:8080`） |
| `SIGNAL_ACCOUNT` | E.164 格式的机器人电话号码 |
| `SIGNAL_ALLOWED_USERS` | 允许的 E.164 手机号或 UUID，英文逗号分隔 |
| `SIGNAL_GROUP_ALLOWED_USERS` | 允许的群组 ID，英文逗号分隔，或 `*` 表示所有群组 |
| `SIGNAL_HOME_CHANNEL_NAME` | Signal 主频道的显示名称 |
| `SIGNAL_IGNORE_STORIES` | 忽略 Signal 故事/状态更新 |
| `SIGNAL_ALLOW_ALL_USERS` | 允许所有 Signal 用户，无需允许列表 |
| `TWILIO_ACCOUNT_SID` | Twilio 账户 SID（与电话技能共用） |
| `TWILIO_AUTH_TOKEN` | Twilio 认证令牌（与电话技能共用；也用于 webhook 签名验证） |
| `TWILIO_PHONE_NUMBER` | E.164 格式的 Twilio 电话号码（与电话技能共用） |
| `SMS_WEBHOOK_URL` | Twilio 签名验证的公共 URL —— 必须与 Twilio 控制台中的 webhook URL 一致（必需） |
| `SMS_WEBHOOK_PORT` | 入站短信的 Webhook 监听端口（默认：`8080`） |
| `SMS_WEBHOOK_HOST` | Webhook 绑定地址（默认：`0.0.0.0`） |
| `SMS_INSECURE_NO_SIGNATURE` | 设为 `true` 以禁用 Twilio 签名验证（仅用于本地开发 —— 不可用于生产环境） |
| `SMS_ALLOWED_USERS` | 允许聊天的 E.164 手机号，英文逗号分隔 |
| `SMS_ALLOW_ALL_USERS` | 允许所有短信发送者，无需允许列表 |
| `SMS_HOME_CHANNEL` | 用于定时任务/通知投递的手机号 |
| `SMS_HOME_CHANNEL_NAME` | SMS 主频道的显示名称 |
| `EMAIL_ADDRESS` | 邮件网关适配器的邮箱地址 |
| `EMAIL_PASSWORD` | 邮箱的密码或应用专用密码 |
| `EMAIL_IMAP_HOST` | 邮件适配器的 IMAP 主机名 |
| `EMAIL_IMAP_PORT` | IMAP 端口 |
| `EMAIL_SMTP_HOST` | 邮件适配器的 SMTP 主机名 |
| `EMAIL_SMTP_PORT` | SMTP 端口 |
| `EMAIL_ALLOWED_USERS` | 允许向机器人发消息的邮箱地址，英文逗号分隔 |
| `EMAIL_HOME_ADDRESS` | 主动邮件投递的默认收件人 |
| `EMAIL_HOME_ADDRESS_NAME` | 邮件主目标的显示名称 |
| `EMAIL_POLL_INTERVAL` | 邮件轮询间隔（秒） |
| `EMAIL_ALLOW_ALL_USERS` | 允许所有入站邮件发送者 |
| `DINGTALK_CLIENT_ID` | 来自开发者门户的钉钉机器人 AppKey（[open.dingtalk.com](https://open.dingtalk.com)） |
| `DINGTALK_CLIENT_SECRET` | 来自开发者门户的钉钉机器人 AppSecret |
| `DINGTALK_ALLOWED_USERS` | 允许向机器人发消息的钉钉用户 ID，英文逗号分隔 |
| `FEISHU_APP_ID` | 来自 [open.feishu.cn](https://open.feishu.cn/) 的飞书/Lark 机器人 App ID |
| `FEISHU_APP_SECRET` | 飞书/Lark 机器人 App Secret |
| `FEISHU_DOMAIN` | `feishu`（中国）或 `lark`（国际版）。默认：`feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket`（推荐）或 `webhook`。默认：`websocket` |
| `FEISHU_ENCRYPT_KEY` | Webhook 模式的可选加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | Webhook 模式的可选验证令牌 |
| `FEISHU_ALLOWED_USERS` | 允许向机器人发消息的飞书用户 ID，英文逗号分隔 |
| `FEISHU_ALLOW_BOTS` | `none`（默认）/ `mentions` / `all` —— 接受来自其他机器人的入站消息。请参见 [bot-to-bot messaging](../user-guide/messaging/feishu.md#bot-to-bot-messaging) |
| `FEISHU_REQUIRE_MENTION` | `true`（默认）/ `false` —— 群组消息是否必须 @提及机器人。可通过 `group_rules.&lt;chat_id&gt;.require_mention` 按聊天覆盖。 |
| `FEISHU_HOME_CHANNEL` | 用于定时任务投递和通知的飞书聊天 ID |
| `WECOM_BOT_ID` | 来自管理后台的企业微信 AI 机器人 ID |
| `WECOM_SECRET` | 企业微信 AI 机器人 secret |
| `WECOM_WEBSOCKET_URL` | 自定义 WebSocket URL（默认：`wss://openws.work.weixin.qq.com`） |
| `WECOM_ALLOWED_USERS` | 允许向机器人发消息的企业微信用户 ID，英文逗号分隔 |
| `WECOM_HOME_CHANNEL` | 用于定时任务投递和通知的企业微信聊天 ID |
| `WECOM_CALLBACK_CORP_ID` | 企业微信回调自建应用的 Corp ID |
| `WECOM_CALLBACK_CORP_SECRET` | 自建应用的 Corp Secret |
| `WECOM_CALLBACK_AGENT_ID` | 自建应用的 Agent ID |
| `WECOM_CALLBACK_TOKEN` | 回调验证令牌 |
| `WECOM_CALLBACK_ENCODING_AES_KEY` | 回调加密的 AES 密钥 |
| `WECOM_CALLBACK_HOST` | 回调服务器绑定地址（默认：`0.0.0.0`） |
| `WECOM_CALLBACK_PORT` | 回调服务器端口（默认：`8645`） |
| `WECOM_CALLBACK_ALLOWED_USERS` | 允许列表的用户 ID，英文逗号分隔 |
| `WECOM_CALLBACK_ALLOW_ALL_USERS` | 设为 `true` 以允许所有用户，无需允许列表 |
| `WEIXIN_ACCOUNT_ID` | 通过 iLink Bot API 二维码登录获得的微信账号 ID |
| `WEIXIN_TOKEN` | 通过 iLink Bot API 二维码登录获得的微信认证令牌 |
| `WEIXIN_BASE_URL` | 覆盖微信 iLink Bot API 基础 URL（默认：`https://ilinkai.weixin.qq.com`） |
| `WEIXIN_CDN_BASE_URL` | 覆盖微信媒体 CDN 基础 URL（默认：`https://novac2c.cdn.weixin.qq.com/c2c`） |
| `WEIXIN_DM_POLICY` | 私聊策略：`open`、`allowlist`、`pairing`、`disabled`（默认：`open`） |
| `WEIXIN_GROUP_POLICY` | 群消息策略：`open`、`allowlist`、`disabled`（默认：`disabled`） |
| `WEIXIN_ALLOWED_USERS` | 允许与机器人私聊的微信用户 ID，英文逗号分隔 |
| `WEIXIN_GROUP_ALLOWED_USERS` | 允许与机器人互动的微信**群聊 ID**（非成员用户 ID），英文逗号分隔。变量名是历史遗留的——它期望群组 ID。仅当 iLink 实际传递群组事件时生效；二维码登录的 iLink 机器人身份（`...@im.bot`）通常不会收到普通的微信群消息。 |
| `WEIXIN_HOME_CHANNEL` | 用于定时任务投递和通知的微信聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | 微信主频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | 允许所有微信用户，无需允许列表（`true`/`false`） |
| `BLUEBUBBLES_SERVER_URL` | BlueBubbles 服务器 URL（例如 `http://192.168.1.10:1234`） |
| `BLUEBUBBLES_PASSWORD` | BlueBubbles 服务器密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | Webhook 监听器绑定地址（默认：`127.0.0.1`） |
| `BLUEBUBBLES_WEBHOOK_PORT` | Webhook 监听器端口（默认：`8645`） |
| `BLUEBUBBLES_HOME_CHANNEL` | 用于定时任务/通知投递的电话/邮箱 |
| `BLUEBUBBLES_ALLOWED_USERS` | 已授权的用户，英文逗号分隔 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`） |
| `QQ_APP_ID` | 来自 [q.qq.com](https://q.qq.com) 的 QQ 机器人 App ID |
| `QQ_CLIENT_SECRET` | 来自 [q.qq.com](https://q.qq.com) 的 QQ 机器人 App Secret |
| `QQ_STT_API_KEY` | 外部 STT 回退提供商的 API 密钥（可选，当 QQ 内置 ASR 未返回文本时使用） |
| `QQ_STT_BASE_URL` | 外部 STT 提供商的基础 URL（可选） |
| `QQ_STT_MODEL` | 外部 STT 提供商的模型名称（可选） |
| `QQ_ALLOWED_USERS` | 允许向机器人发消息的 QQ 用户 openID，英文逗号分隔 |
| `QQ_GROUP_ALLOWED_USERS` | 允许群 @消息的 QQ 群组 ID，英文逗号分隔 |
| `QQ_ALLOW_ALL_USERS` | 允许所有用户（`true`/`false`，覆盖 `QQ_ALLOWED_USERS`） |
| `QQBOT_HOME_CHANNEL` | 用于定时任务投递和通知的 QQ 用户/群组 openID |
| `QQBOT_HOME_CHANNEL_NAME` | QQ 主频道的显示名称 |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机（设为 `sandbox.q.qq.com` 以通过沙箱网关路由；默认：`q.qq.com`） |
| `MATTERMOST_URL` | Mattermost 服务器 URL（例如 `https://mm.example.com`） |
| `MATTERMOST_TOKEN` | Mattermost 的机器人令牌或个人访问令牌 |
| `MATTERMOST_ALLOWED_USERS` | 允许向机器人发消息的 Mattermost 用户 ID，英文逗号分隔 |
| `MATTERMOST_HOME_CHANNEL` | 主动消息投递的频道 ID（定时任务、通知） |
| `MATTERMOST_REQUIRE_MENTION` | 在频道中要求 `@提及`（默认：`true`）。设为 `false` 以响应所有消息。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | 机器人无需 `@提及` 即可响应的频道 ID，英文逗号分隔 |
| `MATTERMOST_REPLY_MODE` | 回复样式：`thread`（线程回复）或 `off`（平面消息，默认） |
| `MATRIX_HOMESERVER` | Matrix 家庭服务器 URL（例如 `https://matrix.org`） |
| `MATRIX_ACCESS_TOKEN` | Matrix 访问令牌，用于机器人认证 |
| `MATRIX_USER_ID` | Matrix 用户 ID（例如 `@hermes:matrix.org`）—— 密码登录时必需，使用访问令牌时可选 |
| `MATRIX_PASSWORD` | Matrix 密码（替代访问令牌） |
| `MATRIX_ALLOWED_USERS` | 允许向机器人发消息的 Matrix 用户 ID，英文逗号分隔（例如 `@alice:matrix.org`） |
| `MATRIX_HOME_ROOM` | 主动消息投递的房间 ID（例如 `!abc123:matrix.org`） |
| `MATRIX_ENCRYPTION` | 启用端到端加密（`true`/`false`，默认：`false`） |
| `MATRIX_DEVICE_ID` | 稳定的 Matrix 设备 ID，用于在重启间保持 E2EE 持久性（例如 `HERMES_BOT`）。如果不设置，每次启动时 E2EE 密钥都会轮换，导致历史房间无法解密。 |
| `MATRIX_REACTIONS` | 在入站消息上启用处理生命周期表情反应（默认：`true`）。设为 `false` 以禁用。 |
| `MATRIX_REQUIRE_MENTION` | 在房间中要求 `@提及`（默认：`true`）。设为 `false` 以响应所有消息。 |
| `MATRIX_FREE_RESPONSE_ROOMS` | 机器人无需 `@提及` 即可响应的房间 ID，英文逗号分隔 |
| `MATRIX_AUTO_THREAD` | 自动为房间消息创建线程（默认：`true`） |
| `MATRIX_DM_MENTION_THREADS` | 当机器人在私聊中被 `@提及` 时创建线程（默认：`false`） |
| `MATRIX_RECOVERY_KEY` | 设备密钥轮换后用于交叉签名验证的恢复密钥。建议用于启用了交叉签名的 E2EE 设置。 |
| `HASS_TOKEN` | Home Assistant 长期访问令牌（启用 HA 平台 + 工具） |
| `HASS_URL` | Home Assistant URL（默认：`http://homeassistant.local:8123`） |
| `WEBHOOK_ENABLED` | 启用 Webhook 平台适配器（`true`/`false`） |
| `WEBHOOK_PORT` | 接收 Webhook 的 HTTP 服务器端口（默认：`8644`） |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥，用于 webhook 签名验证（当路由未指定自己的密钥时作为回退使用） |
| `API_SERVER_ENABLED` | 启用兼容 OpenAI 的 API 服务器（`true`/`false`）。与其他平台并行运行。 |
| `API_SERVER_KEY` | API 服务器认证的 Bearer 令牌。对于非回环绑定强制要求。 |
| `API_SERVER_CORS_ORIGINS` | 允许直接调用 API 服务器的浏览器来源，英文逗号分隔（例如 `http://localhost:3000,http://127.0.0.1:3000`）。默认：禁用。 |
| `API_SERVER_PORT` | API 服务器端口（默认：`8642`） |
| `API_SERVER_HOST` | API 服务器的主机/绑定地址（默认：`127.0.0.1`）。使用 `0.0.0.0` 以允许网络访问 —— 需要设置 `API_SERVER_KEY` 和窄的 `API_SERVER_CORS_ORIGINS` 白名单。 |
| `API_SERVER_MODEL_NAME` | 在 `/v1/models` 上发布的模型名称。默认为配置文件名称（默认配置文件为 `hermes-agent`）。多用户设置中很有用，例如 Open WebUI 等前端需要为每个连接使用不同的模型名称。 |
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL，用于转发消息（[代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)）。设置后，网关仅处理平台 I/O —— 所有 Agent 工作都委托给远程服务器。也可通过 `config.yaml` 中的 `gateway.proxy_url` 配置。 |
| `GATEWAY_PROXY_KEY` | 在代理模式下与远程 API 服务器认证的 Bearer 令牌。必须与远程主机上的 `API_SERVER_KEY` 匹配。 |
| `MESSAGING_CWD` | 消息模式下终端命令的工作目录（默认：`~`） |
| `GATEWAY_ALLOWED_USERS` | 跨所有平台允许的用户 ID，英文逗号分隔 |
| `GATEWAY_ALLOW_ALL_USERS` | 允许所有用户，无需允许列表（`true`/`false`，默认：`false`） |
<a id="microsoft-graph-teams-meetings"></a>
### Microsoft Graph (Teams 会议)

用于即将推出的 Teams 会议摘要管道的 Microsoft Graph REST 客户端的仅应用凭据。有关 Azure 门户操作指南和所需的确切 API 权限，请参阅[注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)。

| 变量 | 描述 |
|----------|-------------|
| `MSGRAPH_TENANT_ID` | Graph 应用注册的 Azure AD 租户 ID（目录 GUID）。 |
| `MSGRAPH_CLIENT_ID` | Azure 应用注册的应用程序（客户端）ID。 |
| `MSGRAPH_CLIENT_SECRET` | 应用注册的客户端机密值。存储在 `~/.hermes/.env` 中，权限设为 `chmod 600`；通过 Azure 门户定期轮换。 |
| `MSGRAPH_SCOPE` | 客户端凭据令牌请求的 OAuth2 范围（默认值：`https://graph.microsoft.com/.default`）。 |
| `MSGRAPH_AUTHORITY_URL` | Microsoft 标识平台颁发机构（默认值：`https://login.microsoftonline.com`）。仅在国家/主权云中覆盖（例如，GCC High 使用 `https://login.microsoftonline.us`）。 |

<a id="microsoft-graph-webhook-listener"></a>
### Microsoft Graph Webhook 监听器

用于 Graph 事件（Teams 会议、日历、聊天等）的入站更改通知监听器。有关设置和安全加固，请参阅 [Microsoft Graph Webhook 监听器](/user-guide/messaging/msgraph-webhook)。

| 变量 | 描述 |
|----------|-------------|
| `MSGRAPH_WEBHOOK_ENABLED` | 启用 `msgraph_webhook` 网关平台（`true`/`1`/`yes`）。 |
| `MSGRAPH_WEBHOOK_PORT` | 监听器绑定的端口（默认值：`8646`）。 |
| `MSGRAPH_WEBHOOK_CLIENT_STATE` | Graph 在每个通知中回显的共享密钥；与 `hmac.compare_digest` 进行比较。使用 `openssl rand -hex 32` 生成。 |
| `MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES` | 允许的 Graph 资源路径/模式的逗号分隔列表（例如 `communications/onlineMeetings,chats/*/messages`）。尾随 `*` 表示前缀匹配。空值表示接受所有。 |
| `MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS` | 允许向监听器发送 POST 请求的 CIDR 范围逗号分隔列表（例如 `52.96.0.0/14,52.104.0.0/14`）。空值表示允许所有（默认值）。在生产环境中应限制为 Microsoft Graph 发布的出口范围。 |

<a id="teams-meeting-summary-delivery"></a>
### Teams 会议摘要投递

仅在启用 [`teams_pipeline` 插件](/user-guide/messaging/msgraph-webhook)时使用。设置也可以在 `config.yaml` 的 `platforms.teams.extra` 下配置——当两者都设置时，环境变量优先。请参阅 [Microsoft Teams → 会议摘要投递](/user-guide/messaging/teams#meeting-summary-delivery-teams-meeting-pipeline)。

| 变量 | 描述 |
|----------|-------------|
| `TEAMS_DELIVERY_MODE` | `graph` 或 `incoming_webhook`。 |
| `TEAMS_INCOMING_WEBHOOK_URL` | Teams 生成的 webhook URL；当 `TEAMS_DELIVERY_MODE=incoming_webhook` 时需要。 |
| `TEAMS_GRAPH_ACCESS_TOKEN` | 预先获取的用于 Graph 投递的委派访问令牌。很少需要——当未设置时，写入器会回退到 `MSGRAPH_*` 应用凭据。 |
| `TEAMS_TEAM_ID` | 频道投递的目标团队 ID（`graph` 模式）。 |
| `TEAMS_CHANNEL_ID` | 目标频道 ID（与 `TEAMS_TEAM_ID` 配对使用）。 |
| `TEAMS_CHAT_ID` | 目标 1:1 或群聊 ID（`graph` 模式下替代团队+频道）。 |
<a id="line-messaging-api"></a>
### LINE Messaging API

由捆绑的 LINE 平台插件（`plugins/platforms/line/`）使用。完整配置请参见 [Messaging Gateway → LINE](/user-guide/messaging/line)。

| 变量名 | 描述 |
|----------|-------------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 来自 LINE Developers Console（Messaging API 标签页）的长期有效 channel access token。必填。 |
| `LINE_CHANNEL_SECRET` | Channel secret（Basic settings 标签页）；用于 HMAC-SHA256 Webhook 签名验证。必填。 |
| `LINE_HOST` | Webhook 绑定主机（默认值：`0.0.0.0`）。 |
| `LINE_PORT` | Webhook 绑定端口（默认值：`8646`）。 |
| `LINE_PUBLIC_URL` | 公开 HTTPS 基础 URL（例如 `https://my-tunnel.example.com`）。发送图片/音频/视频时必须填写——LINE 只接受可通过 HTTPS 访问的 URL。 |
| `LINE_ALLOWED_USERS` | 允许私聊机器人的用户 ID 列表（以 `U` 开头），用逗号分隔。 |
| `LINE_ALLOWED_GROUPS` | 机器人将响应的群组 ID 列表（以 `C` 开头），用逗号分隔。 |
| `LINE_ALLOWED_ROOMS` | 机器人将响应的房间 ID 列表（以 `R` 开头），用逗号分隔。 |
| `LINE_ALLOW_ALL_USERS` | 仅用于开发环境的逃生出口——接受任意来源。默认值：`false`。 |
| `LINE_HOME_CHANNEL` | 当 cron 任务设置 `deliver: line` 时的默认投递目标。 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 触发慢 LLM 模板按钮回传前的等待秒数（默认值：`45`）。设为 `0` 可禁用该功能，并始终使用 Push 回退。 |
| `LINE_PENDING_TEXT` | 与回传按钮一起显示的提示文字。 |
| `LINE_BUTTON_LABEL` | 回传按钮标签（默认值：`Get answer`）。 |
| `LINE_DELIVERED_TEXT` | 当用户再次点击已投递过的回传按钮时回复的内容（默认值：`Already replied ✅`）。 |
| `LINE_INTERRUPTED_TEXT` | 当用户点击因 `/stop` 而悬空的回传按钮时回复的内容（默认值：`Run was interrupted before completion.`）。 |

<a id="advanced-messaging-tuning"></a>
### 高级消息调优

针对各平台出站消息批处理器的高级调节开关。大多数用户无需触碰这些参数；默认值已兼顾各平台的速率限制，同时不会让用户感觉卡顿。

| 变量名 | 描述 |
|----------|-------------|
| `HERMES_TELEGRAM_TEXT_BATCH_DELAY_SECONDS` | 刷新 Telegram 文本队列前的等待窗口（默认值：`0.6`）。 |
| `HERMES_TELEGRAM_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 单条 Telegram 消息超长时，分割块之间的延迟（默认值：`2.0`）。 |
| `HERMES_TELEGRAM_MEDIA_BATCH_DELAY_SECONDS` | 刷新 Telegram 媒体队列前的等待窗口（默认值：`0.6`）。 |
| `HERMES_TELEGRAM_FOLLOWUP_GRACE_SECONDS` | Agent 完成后发送后续消息前的延迟，避免与最后一条流式输出块竞争。 |
| `HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT` / `_READ_TIMEOUT` / `_WRITE_TIMEOUT` / `_POOL_TIMEOUT` | 覆盖底层 `python-telegram-bot` 的 HTTP 超时设置（单位：秒）。 |
| `HERMES_TELEGRAM_HTTP_POOL_SIZE` | 与 Telegram API 的最大并发 HTTP 连接数。 |
| `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS` | 禁用 DNS 失败时硬编码的 Cloudflare 回退 IP（`true`/`false`）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 刷新 Discord 文本队列前的等待窗口（默认值：`0.6`）。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | Discord 消息超长时，分割块之间的延迟（默认值：`2.0`）。 |
| `HERMES_MATRIX_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | Matrix 平台上与 Telegram 批处理对应的调节参数。 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` / `_MAX_CHARS` / `_MAX_MESSAGES` | 飞书批处理调节——延迟、分割延迟、每消息最大字符数、每批最大消息数。 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 飞书媒体刷新延迟。 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 飞书 Webhook 去重缓存大小（默认值：`1024`）。 |
| `HERMES_WECOM_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | 企业微信批处理调节。 |
| `HERMES_VISION_DOWNLOAD_TIMEOUT` | 将图片交给视觉模型之前的下载超时时间（单位：秒，默认值：`30`）。 |
| `HERMES_RESTART_DRAIN_TIMEOUT` | 网关：在 `/restart` 操作中，等待正在运行的任务完成并排空的最长时间，超时后强制重启（默认值：`900`）。 |
| `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` | 网关启动时各平台连接的超时时间（单位：秒）。 |
| `HERMES_GATEWAY_BUSY_INPUT_MODE` | 网关繁忙时的默认输入行为：`queue`（排队）、`steer`（引导）或 `interrupt`（中断）。可通过 `/busy` 命令按对话覆盖。 |
| `HERMES_GATEWAY_BUSY_ACK_ENABLED` | 当用户发送输入且 Agent 正忙时，网关是否发送确认消息（⚡/⏳/⏩）（默认值：`true`）。设为 `false` 可完全取消这些消息——输入仍会正常排队、引导或中断，只是不会在聊天中回复。从 `config.yaml` 中的 `display.busy_ack_enabled` 继承而来。 |
| `HERMES_FILE_MUTATION_VERIFIER` | 启用每轮文件变更的验证脚注（默认值：`true`）。启用时，Hermes 会追加一条提示信息，列出本轮中执行失败的 `write_file` / `patch` 调用（未被后续成功写入覆盖的）。设为 `0`、`false`、`no` 或 `off` 可禁用。对应 `config.yaml` 中的 `display.file_mutation_verifier`；环境变量优先级更高。 |
| `HERMES_CRON_TIMEOUT` | Cron 任务中 Agent 运行的空闲超时时间（单位：秒，默认值：`600`）。Agent 在主动调用工具或接收流式令牌时可以无限运行——此超时只在空闲时触发。设为 `0` 表示无限制。 |
| `HERMES_CRON_SCRIPT_TIMEOUT` | Cron 任务关联的预运行脚本的超时时间（单位：秒，默认值：`120`）。若脚本需要更长执行时间（例如用于反机器人时序的随机延迟），可覆盖此值。也可通过 `config.yaml` 中的 `cron.script_timeout_seconds` 配置。 |
| `HERMES_CRON_MAX_PARALLEL` | 每个 tick 内并行运行的最大 cron 任务数（默认值：`4`）。 |
<a id="agent-behavior"></a>
## Agent 行为

| 变量 | 描述 |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | 每次对话的最大工具调用次数（默认：90） |
| `HERMES_INFERENCE_MODEL` | 在进程级别覆盖模型名称（优先级高于当前会话的 `config.yaml`）。也可通过 `-m`/`--model` 标志设置。 |
| `HERMES_YOLO_MODE` | 设置为 `1` 可跳过危险命令的批准提示。等同于 `--yolo`。 |
| `HERMES_ACCEPT_HOOKS` | 自动批准 `config.yaml` 中声明的任何未见过的 shell 钩子，无需 TTY 提示。等同于 `--accept-hooks` 或 `hooks_auto_accept: true`。 |
| `HERMES_IGNORE_USER_CONFIG` | 跳过 `~/.hermes/config.yaml` 并使用内置默认值（`.env` 中的凭据仍会加载）。等同于 `--ignore-user-config`。 |
| `HERMES_IGNORE_RULES` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能的自动注入。等同于 `--ignore-rules`。 |
| `HERMES_MD_NAMES` | 要自动注入的规则文件名列表，以逗号分隔（默认：`AGENTS.md,CLAUDE.md,.cursorrules,SOUL.md`）。 |
| `HERMES_TOOL_PROGRESS` | 用于工具进度显示的已弃用兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_TOOL_PROGRESS_MODE` | 用于工具进度模式的已弃用兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_HUMAN_DELAY_MODE` | 响应节奏：`off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | 自定义延迟范围最小值（毫秒） |
| `HERMES_HUMAN_DELAY_MAX_MS` | 自定义延迟范围最大值（毫秒） |
| `HERMES_QUIET` | 抑制非必要输出（`true`/`false`） |
| `CODEX_HOME` | 当启用 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime) 时，覆盖 Codex CLI 读取其配置和认证的目录（默认：`~/.codex`）。Hermes 的迁移功能会将受管理块写入 `&lt;CODEX_HOME&gt;/config.toml`。 |
| `HERMES_KANBAN_TASK` | 由看板调度器在生成工作进程时设置（任务 UUID）。工作进程和生成的 `hermes-tools` MCP 子进程会继承此变量，以便看板工具正确门控。请勿手动设置。 |
| `HERMES_API_TIMEOUT` | LLM API 调用超时时间（秒）（默认：`1800`） |
| `HERMES_API_CALL_STALE_TIMEOUT` | 非流式陈旧调用超时时间（秒）（默认：`300`）。对于本地提供商，当未设置时自动禁用。也可通过 `config.yaml` 中的 `providers.&lt;id&gt;.stale_timeout_seconds` 或 `providers.&lt;id&gt;.models.&lt;model&gt;.stale_timeout_seconds` 配置。 |
| `HERMES_STREAM_READ_TIMEOUT` | 流式套接字读取超时时间（秒）（默认：`120`）。对于本地提供商，自动增加到 `HERMES_API_TIMEOUT`。如果本地 LLM 在长时间代码生成期间超时，请增加此值。 |
| `HERMES_STREAM_STALE_TIMEOUT` | 陈旧流检测超时时间（秒）（默认：`180`）。对于本地提供商自动禁用。如果在此窗口内没有数据块到达，将触发连接终止。 |
| `HERMES_STREAM_RETRIES` | 在临时网络错误时，流中重连尝试次数（默认：`3`）。 |
| `HERMES_AGENT_TIMEOUT` | 运行中 Agent 的网关不活动超时时间（秒）（默认：`900`）。每次工具调用和流式令牌都会重置此计时器。设置为 `0` 可禁用。 |
| `HERMES_AGENT_TIMEOUT_WARNING` | 网关：在不活动达到此秒数后发送警告消息（默认：`HERMES_AGENT_TIMEOUT` 的 75%）。 |
| `HERMES_AGENT_NOTIFY_INTERVAL` | 网关：长时间运行的 Agent 轮次中，进度通知之间的间隔秒数。 |
| `HERMES_CHECKPOINT_TIMEOUT` | 文件系统检查点创建超时时间（秒）（默认：`30`）。 |
| `HERMES_EXEC_ASK` | 在网关模式下启用执行批准提示（`true`/`false`） |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 启用从 `./.hermes/plugins/` 自动发现仓库本地插件（`true`/`false`，默认：`false`） |
| `HERMES_PLUGINS_DEBUG` | 设置为 `1`/`true` 可在 stderr 上输出详细的插件发现日志——包括扫描的目录、解析的清单、跳过原因，以及解析或 `register()` 失败时的完整回溯。面向插件开发者。 |
| `HERMES_BACKGROUND_NOTIFICATIONS` | 网关中的后台进程通知模式：`all`（默认）、`result`、`error`、`off` |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 在 API 调用时注入的临时系统提示（不会持久化到会话中） |
| `HERMES_PREFILL_MESSAGES_FILE` | 包含在 API 调用时注入的临时预填充消息的 JSON 文件路径。 |
| `HERMES_ALLOW_PRIVATE_URLS` | `true`/`false`——允许工具获取 localhost/私有网络 URL。在网关模式下默认关闭。 |
| `HERMES_REDACT_SECRETS` | `true`/`false`——控制工具输出、日志和聊天响应中的秘密信息编辑（默认：`true`）。 |
| `HERMES_WRITE_SAFE_ROOT` | 可选目录前缀，限制 `write_file`/`patch` 的写入范围；路径超出此范围需要批准。 |
| `HERMES_DISABLE_FILE_STATE_GUARD` | 设置为 `1` 可关闭 `patch`/`write_file` 上的“自读取后文件已更改”保护。 |
| `HERMES_CORE_TOOLS` | 用于规范核心工具列表的逗号分隔覆盖（高级功能，很少需要）。 |
| `HERMES_BUNDLED_SKILLS` | 用于启动时加载的捆绑技能列表的逗号分隔覆盖。 |
| `HERMES_OPTIONAL_SKILLS` | 首次运行时自动安装的可选技能名称列表，以逗号分隔。 |
| `HERMES_DEBUG_INTERRUPT` | 设置为 `1` 可将详细的中断/取消跟踪记录到 `agent.log`。 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_DUMP_REQUEST_STDOUT` | 将 API 请求负载转储到 stdout 而不是日志文件。 |
| `HERMES_OAUTH_TRACE` | 设置为 `1` 可记录 OAuth 令牌交换和刷新尝试。包含经过编辑的时间信息。 |
| `HERMES_OAUTH_FILE` | 覆盖 OAuth 凭据存储的路径（默认：`~/.hermes/auth.json`）。 |
| `HERMES_AGENT_HELP_GUIDANCE` | 为自定义部署向系统提示追加额外的指导文本。 |
| `HERMES_AGENT_LOGO` | 覆盖 CLI 启动时的 ASCII 横幅标志。 |
| `DELEGATION_MAX_CONCURRENT_CHILDREN` | 每个 `delegate_task` 批次的最大并行子 Agent 数量（默认：`3`，下限为 1，无上限）。也可通过 `config.yaml` 中的 `delegation.max_concurrent_children` 配置——配置值优先级更高。 |
<a id="interface"></a>
## 接口

| 变量 | 描述 |
|----------|-------------|
| `HERMES_TUI` | 当设置为 `1` 时，启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等价于传入 `--tui`。 |
| `HERMES_TUI_DIR` | 预构建的 `ui-tui/` 目录路径（必须包含 `dist/entry.js` 以及填充好的 `node_modules`）。用于发行版和 Nix，跳过首次启动时的 `npm install`。 |
| `HERMES_TUI_RESUME` | 启动时通过 ID 恢复指定的 TUI 会话。设置后，`hermes --tui` 会跳过创建新会话，而是加载对应的命名会话——在断开连接或终端崩溃后重新挂接时很有用。 |
| `HERMES_TUI_THEME` | 强制 TUI 颜色主题：`light`、`dark`，或一个原始的 6 字符背景十六进制值（例如 `ffffff` 或 `1a1a2e`）。未设置时，Hermes 自动通过 `COLORFGBG` 和终端背景查询检测；此变量会覆盖那些没有设置 `COLORFGBG` 的终端（Ghostty、Warp、iTerm2 等）上的检测。 |
| `HERMES_INFERENCE_MODEL` | 在不修改 `config.yaml` 的情况下，强制 `hermes -z` / `hermes chat` 使用的模型。与 `HERMES_INFERENCE_PROVIDER` 配合使用。适用于需要在每次运行中覆盖默认模型的脚本调用方（扫描器、CI、批量执行器）。 |

<a id="session-settings"></a>
## 会话设置

| 变量 | 描述 |
|----------|-------------|
| `SESSION_IDLE_MINUTES` | 在 N 分钟无活动后重置会话（默认：1440） |
| `SESSION_RESET_HOUR` | 每天重置的小时（24 小时制，默认：4 = 凌晨 4 点） |
| `HERMES_SESSION_ID` | **自动导出到 Hermes 启动的每个工具子进程**（`terminal`、`execute_code`、持久 shell、Docker/Singularity 后端、委托的 subagent 运行）。由 Agent 设置为当前会话 ID；从工具调用的用户脚本可以读取它，以便将其输出、遥测或副作用与发起该操作的 Hermes 会话关联起来。**你不应该手动设置它**——从父 shell 覆盖它只在 Agent 运行之外生效，一旦 Agent 启动一个会话，它就会被覆盖。 |

<a id="context-compression-config-yaml-only"></a>
## 上下文压缩（仅限 config.yaml）

上下文压缩完全通过 `config.yaml` 配置——没有对应的环境变量。阈值设置在 `compression:` 块中，摘要模型/提供者在 `auxiliary.compression:` 下。

```yaml
compression:
  enabled: true
  threshold: 0.50
  target_ratio: 0.20         # 要保留为最近尾部的阈值比例
  protect_last_n: 20         # 保持未压缩的最小最近消息数
```

:::info 旧版迁移
<a id="legacy-migration"></a>
包含 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 的旧配置会在首次加载时自动迁移到 `auxiliary.compression.*`。
:::

<a id="auxiliary-task-overrides"></a>
## 辅助任务覆盖

| 变量 | 描述 |
|----------|-------------|
| `AUXILIARY_VISION_PROVIDER` | 覆盖视觉任务的提供者 |
| `AUXILIARY_VISION_MODEL` | 覆盖视觉任务的模型 |
| `AUXILIARY_VISION_BASE_URL` | 视觉任务的自定义 OpenAI 兼容端点 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配对的 API 密钥 |
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | 覆盖网页提取/摘要的提供者 |
| `AUXILIARY_WEB_EXTRACT_MODEL` | 覆盖网页提取/摘要的模型 |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | 网页提取/摘要的自定义 OpenAI 兼容端点 |
| `AUXILIARY_WEB_EXTRACT_API_KEY` | 与 `AUXILIARY_WEB_EXTRACT_BASE_URL` 配对的 API 密钥 |
对于任务特定的直接端点，Hermes 使用该任务配置的 API 密钥或 `OPENAI_API_KEY`。它不会为这些自定义端点复用 `OPENROUTER_API_KEY`。

<a id="fallback-providers-config-yaml-only"></a>
## 回退提供商（仅限 config.yaml）

主模型的回退链仅通过 `config.yaml` 配置——没有对应的环境变量。添加一个顶级 `fallback_providers` 列表，包含 `provider` 和 `model` 键，以便在主模型遇到错误时自动启用故障转移。

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

为了向后兼容，仍然支持旧的顶级 `fallback_model` 单一提供商格式，但新配置应使用 `fallback_providers`。

完整详情请参阅[回退提供商](/user-guide/features/fallback-providers)。

<a id="provider-routing-config-yaml-only"></a>
## 提供商路由（仅限 config.yaml）

以下内容放在 `~/.hermes/config.yaml` 的 `provider_routing` 部分：

| 键 | 描述 |
|-----|-------------|
| `sort` | 对提供商进行排序：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许的提供商标识列表（例如 `["anthropic", "google"]`） |
| `ignore` | 要跳过的提供商标识列表 |
| `order` | 按顺序尝试的提供商标识列表 |
| `require_parameters` | 仅使用支持所有请求参数的提供商（`true`/`false`） |
| `data_collection` | `"allow"`（默认）或 `"deny"` 以排除存储数据的提供商 |

:::tip
使用 `hermes config set` 设置环境变量——它会自动保存到正确的文件中（密钥保存到 `.env`，其他所有内容保存到 `config.yaml`）。
:::
