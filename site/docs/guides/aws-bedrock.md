---
sidebar_position: 14
title: "AWS Bedrock"
description: "将 Hermes Agent 与 Amazon Bedrock 配合使用 — 原生 Converse API、IAM 认证、Guardrails 以及跨区域推理"
---

# AWS Bedrock {#aws-bedrock}

Hermes Agent 原生支持 Amazon Bedrock，使用的是 **Converse API**，而非 OpenAI 兼容端点。这让你可以完整使用 Bedrock 生态：IAM 认证、Guardrails、跨区域推理配置，以及所有基础模型。

## 前置条件 {#prerequisites}

- **AWS 凭证** — 支持 [boto3 凭证链](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) 能识别的任何来源：
  - IAM 实例角色（EC2、ECS、Lambda — 零配置）
  - `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` 环境变量
  - `AWS_PROFILE` 用于 SSO 或命名配置
  - `aws configure` 用于本地开发
- **boto3** — 通过 `pip install hermes-agent[bedrock]` 安装
- **IAM 权限** — 至少需要：
  - `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream`（推理）
  - `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`（模型发现）

:::tip EC2 / ECS / Lambda
在 AWS 计算服务上，附加一个带有 `AmazonBedrockFullAccess` 的 IAM 角色即可。不需要 API 密钥，不需要 `.env` 配置 — Hermes 会自动检测实例角色。
:::

## 快速开始 {#quick-start}

```bash
# 安装 Bedrock 支持
pip install hermes-agent[bedrock]

# 选择 Bedrock 作为你的 provider
hermes model
# → 选择 "More providers..." → "AWS Bedrock"
# → 选择你的区域和模型

# 开始对话
hermes chat
```

## 配置 {#configuration}

运行 `hermes model` 后，你的 `~/.hermes/config.yaml` 会包含：

```yaml
model:
  default: us.anthropic.claude-sonnet-4-6
  provider: bedrock
  base_url: https://bedrock-runtime.us-east-2.amazonaws.com

bedrock:
  region: us-east-2
```

### 区域 {#region}

可以通过以下任一方式设置 AWS 区域（优先级从高到低）：

1. `config.yaml` 中的 `bedrock.region`
2. `AWS_REGION` 环境变量
3. `AWS_DEFAULT_REGION` 环境变量
4. 默认值：`us-east-1`

### Guardrails {#guardrails}

要为所有模型调用应用 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)：

```yaml
bedrock:
  region: us-east-2
  guardrail:
    guardrail_identifier: "abc123def456"  # 从 Bedrock 控制台获取
    guardrail_version: "1"                # 版本号或 "DRAFT"
    stream_processing_mode: "async"       # "sync" 或 "async"
    trace: "disabled"                     # "enabled"、"disabled" 或 "enabled_full"
```

### 模型发现 {#model-discovery}

Hermes 会通过 Bedrock 控制平面自动发现可用模型。你可以自定义发现行为：

```yaml
bedrock:
  discovery:
    enabled: true
    provider_filter: ["anthropic", "amazon"]  # 只显示这些提供商的模型
    refresh_interval: 3600                     # 缓存 1 小时
```

## 可用模型 {#available-models}

Bedrock 模型使用**推理配置 ID** 进行按需调用。`hermes model` 选择器会自动显示这些 ID，推荐模型排在前面：

| 模型 | ID | 说明 |
|-------|-----|-------|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | 推荐 — 速度与能力的最佳平衡 |
| Claude Opus 4.6 | `us.anthropic.claude-opus-4-6-v1` | 能力最强 |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 最快的 Claude |
| Amazon Nova Pro | `us.amazon.nova-pro-v1:0` | Amazon 的旗舰模型 |
| Amazon Nova Micro | `us.amazon.nova-micro-v1:0` | 最快、最便宜 |
| DeepSeek V3.2 | `deepseek.v3.2` | 强劲的开源模型 |
| Llama 4 Scout 17B | `us.meta.llama4-scout-17b-instruct-v1:0` | Meta 最新模型 |

:::info 跨区域推理
以 `us.` 为前缀的模型使用跨区域推理配置，能提供更好的容量和跨 AWS 区域的自动故障转移。以 `global.` 为前缀的模型会在全球所有可用区域间路由。
<a id="cross-region-inference"></a>
:::

## 会话中切换模型 {#switching-models-mid-session}

在对话过程中使用 `/model` 命令：

```
/model us.amazon.nova-pro-v1:0
/model deepseek.v3.2
/model us.anthropic.claude-opus-4-6-v1
```

## 诊断 {#diagnostics}

```bash
hermes doctor
```

doctor 会检查：
- AWS 凭证是否可用（环境变量、IAM 角色、SSO）
- `boto3` 是否已安装
- Bedrock API 是否可访问（ListFoundationModels）
- 你所在区域可用的模型数量
## Gateway（消息平台） {#gateway-messaging-platforms}

Bedrock 支持所有 Hermes gateway 平台（Telegram、Discord、Slack、飞书等）。将 Bedrock 配置为您的 provider，然后正常启动 gateway：

```bash
hermes gateway setup
hermes gateway start
```

gateway 会读取 `config.yaml`，并使用相同的 Bedrock provider 配置。

## 故障排查 {#troubleshooting}

### "No API key found" / "No AWS credentials" {#no-api-key-found-no-aws-credentials}

Hermes 按以下顺序检查凭证：
1. `AWS_BEARER_TOKEN_BEDROCK`
2. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
3. `AWS_PROFILE`
4. EC2 实例元数据（IMDS）
5. ECS 容器凭证
6. Lambda 执行角色

如果都没找到，请运行 `aws configure`，或者为您的计算实例附加一个 IAM 角色。

### "Invocation of model ID ... with on-demand throughput isn't supported" {#invocation-of-model-id-with-on-demand-throughput-isn-t-supported}

请使用**推理配置文件 ID**（前缀为 `us.` 或 `global.`），而不是裸的基础模型 ID。例如：
- ❌ `anthropic.claude-sonnet-4-6`
- ✅ `us.anthropic.claude-sonnet-4-6`

### "ThrottlingException" {#throttlingexception}

您已触碰到 Bedrock 的每模型速率限制。Hermes 会自动退避重试。如需提高限制，请在 [AWS Service Quotas 控制台](https://console.aws.amazon.com/servicequotas/) 申请配额提升。
