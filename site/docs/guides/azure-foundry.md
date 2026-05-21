---
sidebar_position: 15
title: "Microsoft Foundry"
description: "使用 Hermes Agent 与 Microsoft Foundry——OpenAI 风格和 Anthropic 风格的端点，自动检测传输协议和已部署的模型"
---

<a id="microsoft-foundry"></a>
# Microsoft Foundry

Hermes Agent 的 `azure-foundry` 提供程序支持 Microsoft Foundry（原 Azure AI Foundry）和 Azure OpenAI。单个 Foundry 资源可以托管两种不同传输格式的模型：

- **OpenAI 风格** — 在类似 `https://&lt;resource&gt;.openai.azure.com/openai/v1` 的端点上进行 `POST /v1/chat/completions`。用于 GPT-4.x、GPT-5.x、Llama、Mistral 以及大多数开放权重模型。
- **Anthropic 风格** — 在类似 `https://&lt;resource&gt;.services.ai.azure.com/anthropic` 的端点上进行 `POST /v1/messages`。当 Microsoft Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时使用。

设置向导会探测你的端点，自动检测其使用的传输协议、可用的部署以及每个模型的上下文长度。

<a id="prerequisites"></a>
## 先决条件

- 一个至少有一个部署的 Microsoft Foundry 或 Azure OpenAI 资源
- 该部署的端点 URL
- **要么** 一个 API 密钥（来自 Azure Portal 的 "Keys and Endpoint" 下）**要么** 在 Foundry 资源上拥有 **Azure AI User** RBAC 角色（如果你计划使用 Microsoft Entra ID，即 Microsoft 推荐的无密钥路径）。在 Microsoft 重命名推广期间，某些租户可能将该角色显示为 **Foundry User**。

<a id="quick-start"></a>
## 快速开始

```bash
hermes model
# → Select "Azure Foundry"
# → Enter your endpoint URL
# → Choose Authentication:
#     1. API key
#     2. Microsoft Entra ID  (managed identity / workload identity / az login)
# → (Entra) Hermes probes DefaultAzureCredential; on success it never asks for a key
# → (API key) Enter your API key
# Hermes probes the endpoint and auto-detects transport + models
# → Pick a model from the list (or type a deployment name manually)
```

该向导将：

1. **嗅探 URL 路径** — 以 `/anthropic` 结尾的 URL 会被识别为 Microsoft Foundry Claude 路由。
2. **探测 `GET &lt;base&gt;/models`** — 如果端点返回一个 OpenAI 形状的模型列表，Hermes 会切换到 `chat_completions` 并用返回的部署 ID 预填充选择器。
3. **探测 Anthropic Messages 形状** — 对于不暴露 `/models` 但接受 Anthropic Messages 格式的端点的回退。
4. **回退到手动输入** — 拒绝所有探测的私有/受限端点仍然有效；你可以手动选择 API 模式并输入部署名称。

所选模型的上下文长度通过 Hermes 的标准元数据链（`models.dev`、提供程序元数据和硬编码的族回退）解析，并存储在 `config.yaml` 中，以便模型能够正确调整其上下文窗口大小。

<a id="microsoft-entra-id-keyless-rbac-recommended"></a>
## Microsoft Entra ID（无密钥，RBAC）— 推荐

Microsoft 推荐将[使用 Microsoft Entra ID 的无密钥身份验证](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id)用于生产环境中的 Foundry 工作负载。Hermes 支持对**两种** API 面的 Entra ID：

- **OpenAI 风格**（`api_mode: chat_completions` / `codex_responses`）— GPT-4/5、Llama、Mistral、DeepSeek 等。
- **Anthropic 风格**（`api_mode: anthropic_messages`）— Microsoft Foundry 上的 Claude 模型。

Foundry 的 RBAC 是每个资源级别的（`Azure AI User` 角色授予两个 API 面的权限；某些租户可能显示为 `Foundry User`），并且 Microsoft 为两者记录了相同的推理范围（`https://ai.azure.com/.default`）。底层机制：
- **OpenAI 风格**：使用 OpenAI Python SDK 原生的可调用 `api_key=` 参数——SDK 会为每个请求自动生成一个全新的 JWT。
- **Anthropic 风格**：使用安装了请求事件钩子的 `httpx.Client`，该钩子由 `agent.azure_identity_adapter.build_bearer_http_client` 安装，因为 Anthropic SDK 本身不支持可调用的 `auth_token`。钩子会在每次出站请求时重写 `Authorization: Bearer &lt;fresh-jwt&gt;`。相同的 Microsoft RBAC、相同的 Foundry 作用域——唯一的区别在于 SDK 协议。

<a id="why-use-entra-id"></a>
### 为什么要使用 Entra ID？

- 无需轮换或吊销长生命周期的 API 密钥。
- 基于 RBAC 的访问控制——在 Foundry 资源上授予或移除 `Azure AI User` 角色，无需重写配置。
- 访问和审计日志按分配对象进行分割，而不是所有调用者共享一个静态密钥。
- 通过托管标识为 Azure VM、AKS Pod、App Service、Functions、Container Apps 和 Foundry Agent Service 提供单一认证入口。
- 为 CI/CD 流水线提供工作负载标识和服务主体流程。

<a id="one-time-setup-azure-side"></a>
### 一次性设置（Azure 侧）

1. 在 Azure 门户中，打开你的 Foundry 资源 → **访问控制 (IAM)** → **添加 → 添加角色分配**。
2. 选择 **Azure AI User** 角色（如果租户中有重命名的角色，则选 **Foundry User**）。
3. 将其分配给：
   - **你的用户账户**——用于通过 `az login` 进行本地开发。
   - **托管标识或工作负载标识**——用于 Azure 托管的计算环境（推荐用于生产环境）。
   - **Foundry Agent Service 代管的 agent 的 agent 标识**——当 Hermes 在代管 agent 内部运行时。
   - **服务主体**——当工作负载标识不可用时，用于 CI/CD 流水线。
4. 等待约 5 分钟，让角色生效。

等价的 Azure CLI 命令：

```bash
az role assignment create \
  --assignee <principal-or-agent-identity-client-id> \
  --role "Azure AI User" \
  --scope <foundry-resource-id>
```

<a id="one-time-setup-hermes-side"></a>
### 一次性设置（Hermes 侧）

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入你的终端 URL
# → 认证方式：2 (Microsoft Entra ID)
# → （可选）用户分配的托管标识客户端 ID
# → （可选）Azure 租户 ID
# → Hermes 探测 DefaultAzureCredential() 并报告哪个内部凭证成功了
#    （例如 AzureCliCredential、ManagedIdentityCredential）
```

向导会运行一个带时间限制的预检探测（10 秒超时）。如果失败，它提供“先保存，稍后再验证”的选项——当你在尚没有凭证但运行时会有凭证的机器上配置时非常有用（例如为托管标识部署准备配置）。

`azure-identity` 会在首次使用时通过 Hermes 的惰性安装路径自动安装。要提前安装：

```bash
pip install azure-identity
```

<a id="configuration-written-to-config-yaml"></a>
### 写入 `config.yaml` 的配置

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  auth_mode: entra_id
  default: gpt-4o
  context_length: 128000
  entra:
    scope: https://ai.azure.com/.default        # 仅在覆盖默认值时使用
```

Hermes 仅在 `config.yaml` 中管理一个 Entra 特定的旋钮：
- **`scope`** — OAuth 资源作用域。默认为微软记录的推理作用域（`https://ai.azure.com/.default`）。仅当你的资源是针对非标准受众预配时才需覆盖此值。

其他所有内容（租户、服务主体密钥、联合令牌文件、主权云认证机构、代理偏好）均由 `azure-identity` 直接从标准 `AZURE_*` 环境变量中读取——请参阅下面的[凭据解析顺序](#credential-resolution-order)。将这些变量设置在 `~/.hermes/.env` 或你的部署环境中，完全按照微软 SDK 参考文档的描述进行。

在 Entra 模式下，`~/.hermes/.env` 中不会存储任何机密信息——`azure-identity` 会在进程内缓存令牌（如果可用，还会缓存在你的操作系统钥匙串 / `~/.IdentityService` 中）。

<a id="credential-resolution-order"></a>
### 凭据解析顺序

`azure-identity` 的 `DefaultAzureCredential` 在每次令牌请求时会按以下链式顺序尝试，并在第一个成功返回令牌的凭据处停止：

1. **环境凭据** — `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET`（或 `AZURE_CLIENT_CERTIFICATE_PATH` / `AZURE_FEDERATED_TOKEN_FILE`）。
2. **工作负载标识** — `AZURE_FEDERATED_TOKEN_FILE`（AKS 联合令牌 / OIDC）。
3. **托管标识** — 虚拟机的 IMDS 端点（`169.254.169.254`）；应用服务 / 函数 / 容器应用的 `IDENTITY_ENDPOINT`。Foundry Agent Service 托管的 Agent 使用托管 Agent 的 Agent 标识。
4. **Visual Studio Code** — Azure 帐户扩展。
5. **Azure CLI** — `az login` 会话。
6. **Azure Developer CLI** — `azd auth login`。
7. **Azure PowerShell** — `Connect-AzAccount`。
8. **代理**（仅限 Windows / WSL）— Web 帐户管理器。

交互式浏览器凭据在无人值守的 Hermes 运行中默认被排除；请改用 Azure CLI、Azure Developer CLI、托管标识、工作负载标识或服务主体凭据。

<a id="deployment-patterns"></a>
### 部署模式

**本地开发：**
```bash
az login
hermes model   # 选择 Azure Foundry → Entra ID
hermes         # 使用你的 az login 令牌
```

**Azure VM / 函数 / 应用服务 / 容器应用（系统分配托管标识）：**
1. 在计算资源上启用系统分配标识。
2. 在 Foundry 资源上为该标识授予 `Azure AI User`（或 `Foundry User`）角色。
3. 在 config.yaml 中设置 `model.auth_mode: entra_id`——无需环境变量。

**Azure VM / 函数 / 应用服务 / 容器应用（用户分配托管标识）：**
- 将 `AZURE_CLIENT_ID` 设置为用户分配标识的客户端 ID，以便 `DefaultAzureCredential` 选择正确的标识。

**Foundry Agent Service 托管 Agent：**
- 创建托管 Agent，并在 Foundry 资源上为该 Agent 的标识授予 `Azure AI User`（或 `Foundry User`）角色。Hermes 从托管 Agent 内部使用 `ManagedIdentityCredential`；角色分配应属于 Agent 标识，而不仅仅是父项目或你的用户。

**AKS 工作负载标识（替代 AAD Pod 标识）：**
- 使用工作负载标识的客户端 ID 注释 Pod 的服务帐户。
- Pod 的联合令牌文件通过 `AZURE_FEDERATED_TOKEN_FILE` 自动检测。
- `model.auth_mode: entra_id` 无需进一步配置更改即可工作。
**服务主体（Service principal）在 CI 中：**
- 在运行器环境中设置 `AZURE_TENANT_ID`、`AZURE_CLIENT_ID`、`AZURE_CLIENT_SECRET`。

<a id="sovereign-clouds-government-china"></a>
#### 主权云（政府云、中国云）

导出 `AZURE_AUTHORITY_HOST`（例如，Azure Government 使用 `https://login.microsoftonline.us`，Azure 中国区使用 `https://login.partner.microsoftonline.cn`）。`azure-identity` 会直接读取该变量。

<a id="health-checks"></a>
### 健康检查

当 `model.auth_mode: entra_id` 时，`hermes doctor` 会针对 `DefaultAzureCredential` 运行一个 10 秒的探测，并报告哪个内部凭据获胜（环境变量存在、托管标识端点可达等）。

`hermes auth` 显示一个结构化的状态块：

```
azure-foundry (Microsoft Entra ID):
  Endpoint: https://my-resource.openai.azure.com/openai/v1
  Scope: https://ai.azure.com/.default
  Status: configured; live token probe is skipped here
```

<a id="limitations"></a>
### 限制

- **Anthropic 风格的端点使用 httpx 事件钩子。** Anthropic Python SDK 原生不支持可调用的 `auth_token`（≤ 0.86.0）。Hermes 在自定义的 `httpx.Client` 上安装了一个请求事件钩子，该钩子为每个出站请求生成一个新的 JWT，并重写 `Authorization: Bearer &lt;jwt&gt;`。这在功能上等同于 OpenAI SDK 原生的 `Callable[[], str]` 契约，但增加了一层间接层。如果未来版本的 Anthropic SDK 添加了一流的可调用认证支持，Hermes 将透明地切换到该方式。
- **批处理作业和 `multiprocessing.Pool`。** Entra 令牌提供程序是一个闭包，无法跨进程边界进行 pickle 序列化。`batch_runner.py` 会自动从工作进程配置中移除该可调用对象，并让每个工作进程从 `config.yaml` 重建自己的提供程序——无需用户操作，但每个工作进程在启动时都会进行一次凭证链遍历。
- **`auth.json` 中不持久化 bearer JWT。** Hermes 不会复制 `azure-identity` 的内部令牌缓存；冷启动时会在首次推理时走一遍凭证链。

<a id="configuration-written-to-config-yaml"></a>
## 配置（写入 `config.yaml`）

运行向导后，你会看到类似这样的内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # 或 "anthropic_messages"
  default: gpt-5.4-mini              # 你的部署/模型名称
  context_length: 400000             # 自动检测
```

而在 `~/.hermes/.env` 中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

<a id="openai-style-endpoints-gpt-llama-etc"></a>
## OpenAI 风格端点（GPT、Llama 等）

Azure OpenAI 的 v1 GA 端点接受标准的 `openai` Python 客户端，只需极少的更改：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为：

- **GPT-5.x、codex 和 o 系列自动路由到 Responses API。** Microsoft Foundry 将 GPT-5 / codex / o1 / o3 / o4 模型部署为仅支持 Responses API——对这些模型调用 `/chat/completions` 会返回 `400 "The requested operation is unsupported."`。Hermes 通过名称检测这些模型系列，并透明地将 `api_mode` 升级为 `codex_responses`，即使 `config.yaml` 中仍然写着 `api_mode: chat_completions`。GPT-4、GPT-4o、Llama、Mistral 等其他部署仍使用 `/chat/completions`。
- **自动使用 `max_completion_tokens`。** Azure OpenAI（与直接使用 OpenAI 类似）要求对 gpt-4o、o 系列和 gpt-5.x 模型使用 `max_completion_tokens`。Hermes 会根据端点发送正确的参数。
- **需要 `api-version` 的 v1 之前端点。** 如果你有一个遗留的 base URL，例如 `https://&lt;resource&gt;.openai.azure.com/openai?api-version=2025-04-01-preview`，Hermes 会提取查询字符串并通过 `default_query` 在每次请求中转发（OpenAI SDK 在拼接路径时通常会丢弃该查询字符串）。
<a id="anthropic-style-endpoints-claude-via-microsoft-foundry"></a>
## Anthropic 风格端点（通过 Microsoft Foundry 使用 Claude）

针对 Claude 部署，请使用 Anthropic 风格的路由：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

关键行为：

- **`/v1` 会从 base URL 中移除。** Anthropic SDK 会为每个请求 URL 追加 `/v1/messages` —— Hermes 会在将 URL 交给 SDK 之前移除尾部 `/v1`，以避免出现双 `//v1` 路径的问题。
- **`api-version` 通过 `default_query` 传递，而非追加到 URL 上。** Azure Anthropic 要求一个 `api-version` 查询字符串。如果将其硬编码到 base URL 中，会产生类似 `/anthropic?api-version=.../v1/messages` 的畸形路径，导致 404 错误。Hermes 改为通过 Anthropic SDK 的 `default_query` 传递 `api-version=2025-04-15`。
- **使用 Bearer 认证而非 `x-api-key`。** Azure 的 Anthropic 兼容路由要求使用 `Authorization: Bearer &lt;key&gt;`，而不是 Anthropic 原生的 `x-api-key` 头。Hermes 检测 base URL 中是否包含 `azure.com`，并将 API 密钥通过 SDK 的 `auth_token` 字段传递给上层，从而确保正确的头部信息送达上游。
- **保留 1M 上下文窗口的 beta 头。** Azure 仍然通过 `anthropic-beta: context-1m-2025-08-07` 头来控制 Claude 的百万 Token 上下文（Opus 4.6/4.7、Sonnet 4.6）。Hermes 在 Azure 路径上保留该 beta 头（该头信息在原生 Anthropic OAuth 请求中会被移除，因为部分订阅拒绝该头，但 Azure 要求保留）。
- **禁用 OAuth Token 刷新。** Azure 部署使用静态 API 密钥。适用于 Anthropic Console 的 `~/.claude/.credentials.json` OAuth Token 刷新循环会针对 Azure 端点明确跳过，以防止 Claude Code 的 OAuth Token 在会话中途覆盖掉你的 Azure 密钥。

<a id="alternative-provider-anthropic-azure-base-url"></a>
## 替代方案：`provider: anthropic` + Azure base URL

如果你已经配置了 `provider: anthropic`，只想让它指向 Microsoft Foundry 上的 Claude，你可以完全跳过 `azure-foundry` provider：

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

同时在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY`。Hermes 会检测 base URL 中是否包含 `azure.com`，并绕过 Claude Code 的 OAuth Token 链，直接使用 Azure 密钥进行 `x-api-key` 认证。

`key_env` 是规范的 snake_case 字段名；`api_key_env`（以及驼峰形式的 `keyEnv` / `apiKeyEnv`）可以作为别名使用。如果同时设置了 `key_env` 和 `AZURE_ANTHROPIC_KEY` / `ANTHROPIC_API_KEY`，则 `key_env` 指定的环境变量优先。

<a id="model-discovery"></a>
## 模型发现

Azure **不**暴露一个纯 API 密钥的端点来列出你*已部署*的模型部署。列举部署需要 Azure 资源管理器认证（`az cognitiveservices account deployment list`），并需要 Azure AD 主体，而不是推理 API 密钥。

Hermes 能做到的是：

- Azure OpenAI v1 端点（`&lt;resource&gt;.openai.azure.com/openai/v1`）会暴露 `GET /models`，返回该资源的**可用**模型目录。Hermes 利用这个列表来预填充模型选择器。
- Microsoft Foundry `/anthropic` 路由：通过 URL 路径检测，模型名称手动输入。
- 私有/防火墙后的端点：手动输入，并显示一条友好的“无法探测”提示。
您始终可以直接输入部署名称——Hermes 不会对返回列表进行校验。

<a id="environment-variables"></a>
## 环境变量

| 变量 | 用途 |
|----------|---------|
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI 的主 API 密钥（api_key 模式） |
| `AZURE_FOUNDRY_BASE_URL` | 端点 URL（通过 `hermes model` 设置；环境变量作为备用） |
| `AZURE_ANTHROPIC_KEY` | 用于 `provider: anthropic` + Azure 基础 URL（`ANTHROPIC_API_KEY` 的替代方案） |
| `AZURE_TENANT_ID` | 服务主体流程的 Entra ID 租户 |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载标识或用户分配的托管标识） |
| `AZURE_CLIENT_SECRET` | 服务主体机密 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（机密的替代方案） |
| `AZURE_FEDERATED_TOKEN_FILE` | 工作负载标识联合令牌路径（AKS） |
| `AZURE_AUTHORITY_HOST` | 主权云权威主机覆盖 |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | 适用于应用服务、Functions 和容器应用的托管标识端点；虚拟机通常改用 IMDS |

Azure SDK 直接读取 `AZURE_*` 环境变量。Hermes 从不检查这些变量，仅在 `hermes doctor` 输出中报告哪些来源存在。

<a id="troubleshooting"></a>
## 故障排查

**gpt-5.x 部署出现 401 Unauthorized。**
Azure 在 `/chat/completions` 上提供 gpt-5.x，而不是 `/responses`。当 URL 包含 `openai.azure.com` 时，Hermes 会自动处理，但如果您看到 401 且正文为 `Invalid API key`，请检查 `config.yaml` 中的 `api_mode` 是否为 `chat_completions`。

**在 `/v1/messages?api-version=.../v1/messages` 上出现 404。**
这是修复前 Azure Anthropic 设置中的 URL 格式错误问题。升级 Hermes——`api-version` 参数现在通过 `default_query` 传递，而不是嵌入到基础 URL 中，因此 SDK 在 URL 拼接时不会破坏它。

**向导提示“自动检测未完成”。**
端点拒绝了 `/models` 探测和 Anthropic Messages 探测。对于防火墙后面或具有 IP 白名单的私有端点，这是正常现象。回退到手动 API 模式选择并输入部署名称——一切仍可正常工作，Hermes 只是无法预填选择器。

**选择了错误的传输方式。**
再次运行 `hermes model`，向导将重新探测。如果探测仍然选择错误模式，可以直接编辑 `config.yaml`：

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # 或 chat_completions
```

**Entra ID：切换到 `auth_mode: entra_id` 后出现“凭据链耗尽”或 401 Unauthorized。**
- 运行 `az login` 刷新开发会话（缓存的令牌可能已过期）。
- 验证 `Azure AI User`（或 `Foundry User`）角色分配是否生效：`az role assignment list --assignee &lt;user-or-identity-id&gt;` 应该会列出该角色在 Foundry 资源上的分配。角色传播可能需要最多 5 分钟。
- 对于用户分配的托管标识，请仔细检查 `AZURE_CLIENT_ID` 是否与附加到计算资源的标识匹配。
- 运行 `hermes doctor`——Azure Entra 探测会报告令牌获取是否成功，并包含修复提示。
**Entra ID：向导预检卡住或超时。**
10 秒的预检是一种软检查。请选择“仍然保存并稍后验证”，在部署到目标环境后运行 `hermes doctor`。常见原因包括令牌服务不可访问或本地登录状态过期——在 CI 中建议使用工作负载标识，使用服务主体时设置 `AZURE_TENANT_ID`+`AZURE_CLIENT_ID`+`AZURE_CLIENT_SECRET`，或在本地开发时运行 `az login`。

**使用 Entra ID 的 Anthropic 风格端点返回 401。**
验证在 Foundry 资源上分配了相同的 `Azure AI User`（或 `Foundry User`）角色（它同时覆盖 `/openai/v1` 和 `/anthropic` 路径）。如果向导期间 OpenAI 风格的探测可以正常工作，但运行时 `claude-*` 请求失败，最常见的原因是前一次向导运行遗留的过时 `model.entra.scope`——从 `config.yaml` 中删除 `entra.scope` 这一行，以便运行时回退到默认的 `https://ai.azure.com/.default` 范围。

<a id="related"></a>
## 相关

- [环境变量](/reference/environment-variables)
- [配置](/user-guide/configuration)
- [AWS Bedrock](/guides/aws-bedrock) — 另一个主流云提供商集成
- [Microsoft：为 Foundry 配置 Entra ID](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id) — 免密钥路径的官方文档
