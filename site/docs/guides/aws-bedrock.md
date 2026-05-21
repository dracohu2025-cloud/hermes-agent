---
sidebar_position: 14
title: "AWS Bedrock"
description: "使用 Hermes Agent 与 Amazon Bedrock — 原生 Converse API、IAM 认证、Guardrails、跨区域推理"
---

<a id="aws-bedrock"></a>
# AWS Bedrock

Hermes Agent 支持将 Amazon Bedrock 作为原生提供商，使用 **Converse API**（而非兼容 OpenAI 的端点）。这使您可以完全访问 Bedrock 生态系统：IAM 认证、Guardrails、跨区域推理配置文件以及所有基础模型。

<a id="prerequisites"></a>
## 前提条件

- **AWS 凭证** — [boto3 凭证链](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)支持的任意来源：
  - IAM 实例角色（EC2、ECS、Lambda — 零配置）
  - `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` 环境变量
  - 用于 SSO 或命名配置文件的 `AWS_PROFILE`
  - 用于本地开发的 `aws configure`
- **boto3** — 使用 `pip install hermes-agent[bedrock]` 安装
- **IAM 权限** — 至少需要：
  - `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream`（用于推理）
  - `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`（用于模型发现）

:::tip EC2 / ECS / Lambda
在 AWS 计算服务中，附加一个包含 `AmazonBedrockFullAccess` 的 IAM 角色即可，无需 API 密钥，无需 `.env` 配置 — Hermes 会自动检测实例角色。
:::

<a id="quick-start"></a>
## 快速开始

```bash
# 安装 Bedrock 支持
pip install hermes-agent[bedrock]

# 选择 Bedrock 作为提供商
hermes model
# → 选择 "更多提供商..." → "AWS Bedrock"
# → 选择您的区域和模型

# 开始对话
hermes chat
```

<a id="configuration"></a>
## 配置

运行 `hermes model` 后，您的 `~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: us.anthropic.claude-sonnet-4-6
  provider: bedrock
  base_url: https://bedrock-runtime.us-east-2.amazonaws.com

bedrock:
  region: us-east-2
```

<a id="region"></a>
### 区域

通过以下任意方式设置 AWS 区域（优先级从高到低）：

1. `config.yaml` 中的 `bedrock.region`
2. `AWS_REGION` 环境变量
3. `AWS_DEFAULT_REGION` 环境变量
4. 默认：`us-east-1`

<a id="guardrails"></a>
### Guardrails

要将 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 应用于所有模型调用：

```yaml
bedrock:
  region: us-east-2
  guardrail:
    guardrail_identifier: "abc123def456"  # 来自 Bedrock 控制台
    guardrail_version: "1"                # 版本号或 "DRAFT"
    stream_processing_mode: "async"       # "sync" 或 "async"
    trace: "disabled"                     # "enabled"、"disabled" 或 "enabled_full"
```

<a id="model-discovery"></a>
### 模型发现

Hermes 通过 Bedrock 控制平面自动发现可用模型。您可以自定义发现行为：

```yaml
bedrock:
  discovery:
    enabled: true
    provider_filter: ["anthropic", "amazon"]  # 仅显示这些提供商
    refresh_interval: 3600                     # 缓存 1 小时
```

<a id="available-models"></a>
## 可用模型

Bedrock 模型使用 **推理配置文件 ID** 进行按需调用。`hermes model` 选择器会自动显示这些模型，推荐模型排在顶部：

| 模型 | ID | 说明 |
|-------|-----|-------|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | 推荐 — 速度与能力的最佳平衡 |
| Claude Opus 4.6 | `us.anthropic.claude-opus-4-6-v1` | 能力最强 |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 最快的 Claude |
| Amazon Nova Pro | `us.amazon.nova-pro-v1:0` | Amazon 旗舰型号 |
| Amazon Nova Micro | `us.amazon.nova-micro-v1:0` | 最快、最便宜 |
| DeepSeek V3.2 | `deepseek.v3.2` | 强大的开源模型 |
| Llama 4 Scout 17B | `us.meta.llama4-scout-17b-instruct-v1:0` | Meta 最新型号 |
:::info 跨区域推理
以 `us.` 前缀开头的模型使用跨区域推理配置文件，可提供更好的容量并在 AWS 区域间自动故障转移。以 `global.` 前缀开头的模型则路由到全球所有可用区域。
:::

<a id="switching-models-mid-session"></a>
## 在会话中切换模型

对话期间使用 `/model` 命令：
<a id="cross-region-inference"></a>

```
/model us.amazon.nova-pro-v1:0
/model deepseek.v3.2
/model us.anthropic.claude-opus-4-6-v1
```

<a id="diagnostics"></a>
## 诊断

```bash
hermes doctor
```

诊断程序会检查：
- AWS 凭证是否可用（环境变量、IAM 角色、SSO）
- `boto3` 是否已安装
- Bedrock API 是否可达（ListFoundationModels）
- 当前区域可用模型数量

<a id="gateway-messaging-platforms"></a>
## 网关（消息平台）

Bedrock 可与所有 Hermes 网关平台（Telegram、Discord、Slack、飞书等）配合使用。将 Bedrock 配置为你的提供商，然后正常启动网关：

```bash
hermes gateway setup
hermes gateway start
```

网关读取 `config.yaml` 并使用相同的 Bedrock 提供商配置。

<a id="troubleshooting"></a>
## 故障排除

<a id="no-api-key-found-no-aws-credentials"></a>
### “未找到 API 密钥” / “无 AWS 凭证”

Hermes 按以下顺序检查凭证：
1. `AWS_BEARER_TOKEN_BEDROCK`
2. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
3. `AWS_PROFILE`
4. EC2 instance metadata (IMDS)
5. ECS container credentials
6. Lambda execution role

如果都未找到，请运行 `aws configure` 或为你的计算实例附加一个 IAM 角色。

<a id="invocation-of-model-id-with-on-demand-throughput-isn-t-supported"></a>
### “不支持使用按需吞吐量调用模型 ID ...”

请使用**推理配置文件 ID**（以 `us.` 或 `global.` 为前缀）而不是纯粹的基础模型 ID。例如：
- ❌ `anthropic.claude-sonnet-4-6`
- ✅ `us.anthropic.claude-sonnet-4-6`

<a id="throttlingexception"></a>
### “ThrottlingException”

你已达到 Bedrock 的每个模型速率限制。Hermes 会自动退避重试。要提高限制，请在 [AWS Service Quotas 控制台](https://console.aws.amazon.com/servicequotas/) 请求增加配额。

<a id="one-click-aws-deployment"></a>
## 一键 AWS 部署

使用 CloudFormation 在 EC2 上实现完全自动化部署：

**[sample-hermes-agent-on-aws-with-bedrock](https://github.com/JiaDe-Wu/sample-hermes-agent-on-aws-with-bedrock)** — 创建 VPC、IAM 角色、EC2 实例，并自动配置 Bedrock。可一键部署到任何区域。
