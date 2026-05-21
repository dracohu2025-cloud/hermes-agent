---
title: "注册 Microsoft Graph 应用程序"
description: "Azure 门户操作指南：创建为 Teams 会议管道提供支持的应用注册"
---

<a id="register-a-microsoft-graph-application"></a>
# 注册 Microsoft Graph 应用程序

Teams 会议管道使用**仅应用**（守护程序）身份验证从 Microsoft Graph 读取会议转录、录制及相关工件——无需用户登录，也无需每次会议进行交互式同意。这需要一个具有管理员同意的应用程序权限的 Azure AD 应用程序注册。

本指南将引导您完成：

1. 创建应用注册
2. 创建客户端密钥
3. 授予管道所需的 Graph API 权限
4. 管理员同意这些权限
5. （可选）使用应用程序访问策略将应用范围限定到特定用户

您需要**租户管理员权限**（或由管理员代表您授予同意）才能完成此操作。请记下您收集的值——它们最终会放入 `~/.hermes/.env` 文件中。

<a id="prerequisites"></a>
## 前提条件

- 一个 Microsoft 365 租户，拥有 Teams Premium 或 Teams 许可证，能够生成会议转录和录制
- 对 [entra.microsoft.com](https://entra.microsoft.com) 上 Azure 门户的管理员访问权限
- 一个可公开访问的 HTTPS 端点，用于接收 Graph 变更通知（稍后在 webhook 监听器步骤中设置）

<a id="step-1-create-the-app-registration"></a>
## 步骤 1：创建应用注册

1. 以租户管理员身份登录 [entra.microsoft.com](https://entra.microsoft.com)。
2. 导航到 **标识 → 应用程序 → 应用注册**。
3. 点击 **新注册**。
4. 填写：
   - **名称：** `Hermes Teams Meeting Pipeline`（或任何您能识别的名称）。
   - **受支持的帐户类型：** *仅此组织目录中的帐户（单租户）*。
   - **重定向 URI：** 留空——仅应用身份验证不需要此设置。
5. 点击 **注册**。

您将进入应用的概览页面。复制两个值：

- **应用程序（客户端）ID** → `MSGRAPH_CLIENT_ID`
- **目录（租户）ID** → `MSGRAPH_TENANT_ID`

<a id="step-2-create-a-client-secret"></a>
## 步骤 2：创建客户端密钥

1. 在左侧导航中，打开 **证书和机密**。
2. 点击 **新客户端机密**。
3. **说明：** `hermes-graph-secret`。**过期时间：** 选择一个符合您轮换策略的值（通常为 6-24 个月）。
4. 点击 **添加**。
5. 立即复制 **值** 列——它只显示一次。该值即为 `MSGRAPH_CLIENT_SECRET`。

> **机密 ID** 列不是密钥。您需要的是 **值** 列。

<a id="step-3-grant-graph-api-permissions"></a>
## 步骤 3：授予 Graph API 权限

该管道使用最小可行的一组应用程序权限。只添加您需要的权限；每个权限都会扩大应用在租户范围内的读取能力。

1. 在左侧导航中，打开 **API 权限**。
2. 点击 **添加权限** → **Microsoft Graph** → **应用程序权限**。
3. 从下表中添加与您希望管道执行的操作相匹配的权限。
4. 添加后，点击 **为 `&lt;your tenant&gt;` 授予管理员同意**。每个权限的“状态”列应变为绿色对勾。

<a id="required-for-transcript-first-summaries"></a>
### 转录优先摘要所需的权限

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `OnlineMeetings.Read.All` | 读取 Teams 在线会议元数据（主题、参与者、加入 URL）。 |
| `OnlineMeetingTranscript.Read.All` | 读取 Teams 生成的会议转录。 |
<a id="required-for-recording-fallback-when-a-transcript-is-unavailable"></a>
### 录制的回退所需（当无法获取转录内容时）

| 权限 | 作用 |
|------------|--------------------------|
| `OnlineMeetingRecording.Read.All` | 下载 Teams 会议录制文件，用于离线 STT 处理。 |
| `CallRecords.Read.All` | 当仅知道加入 URL 时，通过通话记录解析会议。 |

<a id="required-for-outbound-summary-delivery-graph-mode-only"></a>
### 对外发送摘要所需（仅 Graph 模式）

如果 `platforms.teams.extra.delivery_mode` 设置为 `graph`，则管道会通过 Graph API 将摘要发布到 Teams 频道或聊天中。如果你改用 `incoming_webhook` 投递模式，则可以跳过这些。

| 权限 | 作用 |
|------------|--------------------------|
| `ChannelMessage.Send` | 以应用身份向 Teams 频道发布消息。 |
| `Chat.ReadWrite.All` | 向 1:1 聊天和群组聊天发布消息（仅当你将 `chat_id` 设为投递目标时）。 |

<a id="not-recommended"></a>
### 不推荐

- `OnlineMeetings.ReadWrite.All` / `Chat.ReadWrite`（不带 `.All`）—— 权限范围超出管道所需。
- 委托权限 —— 管道使用仅应用（客户端凭据）流；没有用户登录时，委托权限无法生效。

<a id="step-4-recommended-scope-the-app-with-an-application-access-policy"></a>
## 第 4 步：（推荐）使用应用程序访问策略限定应用范围

默认情况下，像 `OnlineMeetings.Read.All` 这样的应用程序权限会让应用能够访问租户中的**每个**会议。对于合作伙伴演示和开发租户来说，这没问题；但在生产环境中，你几乎肯定需要限制哪些用户的会议可以被应用读取。

Microsoft 提供 **应用程序访问策略** 正是为了这个目的。该策略仅通过 PowerShell 管理，没有门户 UI。

在安装了 MicrosoftTeams 模块并已连接（`Connect-MicrosoftTeams`）的管理员 PowerShell 中执行：

```powershell
# 创建限定 Hermes 应用范围的策略
New-CsApplicationAccessPolicy `
  -Identity "Hermes-Meeting-Pipeline-Policy" `
  -AppIds "<MSGRAPH_CLIENT_ID>" `
  -Description "将 Hermes 会议管道限制为仅允许列表中的用户"

# 将策略授予特定用户，管道可以读取这些用户的会议
Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "alice@example.com"

Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "bob@example.com"
```

授予后，策略传播可能需要最多 30 分钟。用以下命令验证：

```powershell
Test-CsApplicationAccessPolicy -Identity "alice@example.com" -AppId "<MSGRAPH_CLIENT_ID>"
```

如果没有该策略，**任何**用户的会议都是可读的——这正是权限本身所允许的。在生产租户上不要跳过这一步。

<a id="step-5-write-the-credentials-to-your-env-file"></a>
## 第 5 步：将凭据写入环境变量文件

将你收集到的三个值放入 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<directory-tenant-id>
MSGRAPH_CLIENT_ID=<application-client-id>
MSGRAPH_CLIENT_SECRET=<client-secret-value>
```

设置文件权限，确保只有你能读取机密信息：

```bash
chmod 600 ~/.hermes/.env
```

<a id="step-6-verify-the-token-flow"></a>
## 第 6 步：验证令牌流程
Hermes 附带了一个 Graph 认证冒烟测试。在您的 Hermes 安装目录下运行：

```python
python -c "
import asyncio
from tools.microsoft_graph_auth import MicrosoftGraphTokenProvider
provider = MicrosoftGraphTokenProvider.from_env()
token = asyncio.run(provider.get_access_token())
print('Token acquired, length:', len(token))
print(provider.inspect_token_health())
"
```

成功运行会打印一个长 token 字符串和一个健康状态字典，其中显示 `cached: True` 以及一个接近 3600 的 `expires_in_seconds` 值。失败则会抛出 `MicrosoftGraphTokenError` 并附带 Azure 错误码——最常见的有：

| Azure 错误 | 含义 | 修复方法 |
|-------------|------|----------|
| `AADSTS7000215: Invalid client secret` | 机密值不匹配或已过期。 | 在步骤 2 中生成一个新机密；更新 `.env` 文件。 |
| `AADSTS700016: Application not found` | `MSGRAPH_CLIENT_ID` 错误或租户错误。 | 再次确认步骤 1 中的值是否来自同一个应用。 |
| `AADSTS90002: Tenant not found` | `MSGRAPH_TENANT_ID` 中有拼写错误。 | 从应用概览页面重新复制目录（租户）ID。 |
| 调用时（非 token 获取时）出现 `insufficient_claims` | Token 已获取，但 Graph 返回 401/403。 | 您跳过了步骤 3 的管理员同意，或者添加了权限但未重新同意。请重新访问 API 权限并再次点击 **授予管理员同意**。 |

<a id="rotating-the-client-secret"></a>
## 轮换客户端机密

Azure 客户端机密有硬性过期时间。在您的机密过期之前：

1. 在步骤 2 中创建第二个客户端机密，但不要删除第一个。
2. 将 `~/.hermes/.env` 中的 `MSGRAPH_CLIENT_SECRET` 更新为新值。
3. 重启网关以使新机密生效：`hermes gateway restart`。
4. 使用上面的冒烟测试进行验证。
5. 从 Azure 门户中删除旧机密。

<a id="next-steps"></a>
## 下一步

凭证验证通过后，请继续：

- **Webhook 监听器设置** — 启动 `msgraph_webhook` 网关平台，用于接收 Graph 变更通知。
- **流水线配置** — 配置 Teams 会议流水线运行时和操作员 CLI。
- **出站投递** — 将摘要内容写回 Teams 频道或聊天。

这些页面会与添加相应运行时的 PR 一同发布。本凭证设置是一个独立的先决条件，可以提前安全完成。
