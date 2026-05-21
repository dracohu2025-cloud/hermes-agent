---
sidebar_position: 15
title: "MiniMax OAuth"
description: "通过浏览器 OAuth 登录 MiniMax，在 Hermes Agent 中使用 MiniMax-M2.7 系列模型——无需 API 密钥"
---

<a id="minimax-oauth"></a>
# MiniMax OAuth

Hermes Agent 通过基于浏览器的 OAuth 登录流程支持 **MiniMax**，使用与 [MiniMax 门户](https://www.minimax.io) 相同的凭据。无需 API 密钥或信用卡——只需登录一次，Hermes 会自动刷新你的会话。

传输层复用了 `anthropic_messages` 适配器（MiniMax 在 `/anthropic` 路径下暴露了一个兼容 Anthropic Messages 的端点），因此所有现有的工具调用、流式传输和上下文功能无需修改适配器即可正常工作。

<a id="overview"></a>
## 概览

| 项目 | 值 |
|------|-------|
| 提供商 ID | `minimax-oauth` |
| 显示名称 | MiniMax (OAuth) |
| 认证类型 | 浏览器 OAuth (PKCE 设备码流程) |
| 传输层 | Anthropic Messages 兼容 (`anthropic_messages`) |
| 模型 | `MiniMax-M2.7`, `MiniMax-M2.7-highspeed` |
| 全局端点 | `https://api.minimax.io/anthropic` |
| 中国端点 | `https://api.minimaxi.com/anthropic` |
| 需要环境变量 | 否（此提供商**不**使用 `MINIMAX_API_KEY`） |

<a id="prerequisites"></a>
## 前提条件

- Python 3.9+
- 已安装 Hermes Agent
- 在 [minimax.io](https://www.minimax.io)（全球）或 [minimaxi.com](https://www.minimaxi.com)（中国）拥有 MiniMax 账户
- 本地机器上有可用的浏览器（远程会话可使用 `--no-browser`）

<a id="quick-start"></a>
## 快速开始

```bash
# 启动提供商和模型选择器
hermes model
# → 从提供商列表中选择 "MiniMax (OAuth)"
# → Hermes 会在浏览器中打开 MiniMax 授权页面
# → 在浏览器中批准访问
# → 选择一个模型（MiniMax-M2.7 或 MiniMax-M2.7-highspeed）
# → 开始对话

hermes
```

首次登录后，凭据会存储在 `~/.hermes/auth.json` 中，并在每次会话前自动刷新。

<a id="logging-in-manually"></a>
## 手动登录

你可以不通过模型选择器直接触发登录：

```bash
hermes auth add minimax-oauth
```

<a id="china-region"></a>
### 中国区域

如果你的账户位于中国平台（`minimaxi.com`），请改用中国区域的 OAuth 提供商 ID `minimax-cn`，或者跳过 OAuth 直接配置 `MINIMAX_CN_API_KEY` / `MINIMAX_CN_BASE_URL`。旧文档中提到的 `--region cn` 标志**未**通过 CLI 的参数解析器连接；请改用 `minimax-cn` 提供商：

```bash
hermes auth add minimax-cn --type oauth   # 如果你的 CN 账户支持 OAuth
# 或者更简单：
echo 'MINIMAX_CN_API_KEY=your-key' >> ~/.hermes/.env
```

<a id="remote-headless-sessions"></a>
### 远程 / 无头会话

在服务器或容器中，如果没有可用的浏览器：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 会打印验证 URL 和用户代码——在任何设备上打开该 URL，并在提示时输入代码。

<a id="the-oauth-flow"></a>
## OAuth 流程

Hermes 针对 MiniMax OAuth 端点实现了 PKCE 设备码流程：

1. Hermes 生成一对 PKCE 验证器 / 挑战值以及一个随机状态值。
2. 它向 `{base_url}/oauth/code` 发送 POST 请求（包含挑战值），并收到一个 `user_code` 和 `verification_uri`。
3. 你的浏览器打开 `verification_uri`。如果提示，请输入 `user_code`。
4. Hermes 轮询 `{base_url}/oauth/token`，直到收到令牌（或超时）。
5. 令牌（`access_token`、`refresh_token`、过期时间）会保存到 `~/.hermes/auth.json` 中的 `minimax-oauth` 键下。
令牌刷新（标准 OAuth `refresh_token` 授权）在每个会话启动时自动运行，前提是访问令牌距离过期不到 60 秒。

<a id="checking-login-status"></a>
## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分会显示：

```
✓ MiniMax OAuth  (logged in, region=global)
```

如果未登录，则显示：

```
⚠ MiniMax OAuth  (not logged in)
```

<a id="switching-models"></a>
## 切换模型

```bash
hermes model
# → Select "MiniMax (OAuth)"
# → Pick from the model list
```

或者直接设置模型：

```bash
hermes config set model MiniMax-M2.7
hermes config set provider minimax-oauth
```

<a id="configuration-reference"></a>
## 配置参考

登录后，`~/.hermes/config.yaml` 会包含类似以下内容：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```

<a id="region-endpoints"></a>
### 区域端点

| 提供者标识 | 门户 | 推理端点 |
|-------------|--------|-------------------|
| `minimax-oauth`（全球） | `https://api.minimax.io` | `https://api.minimax.io/anthropic` |
| `minimax-cn`（中国） | `https://api.minimaxi.com` | `https://api.minimaxi.com/anthropic` |

<a id="provider-aliases"></a>
### 提供者别名

以下所有名称都会解析为 `minimax-oauth`：

```bash
hermes --provider minimax-oauth    # canonical
hermes --provider minimax-portal   # alias
hermes --provider minimax-global   # alias
hermes --provider minimax_oauth    # alias (underscore form)
```

<a id="environment-variables"></a>
## 环境变量

`minimax-oauth` 提供者**不**使用 `MINIMAX_API_KEY` 或 `MINIMAX_BASE_URL`。这些变量仅用于基于 API 密钥的 `minimax` 和 `minimax-cn` 提供者。

| 变量 | 作用 |
|----------|--------|
| `MINIMAX_API_KEY` | 仅由 `minimax` 提供者使用——`minimax-oauth` 会忽略 |
| `MINIMAX_CN_API_KEY` | 仅由 `minimax-cn` 提供者使用——`minimax-oauth` 会忽略 |

要在运行时强制使用 `minimax-oauth` 提供者：

```bash
HERMES_INFERENCE_PROVIDER=minimax-oauth hermes
```

<a id="models"></a>
## 模型

| 模型 | 最佳用途 |
|-------|----------|
| `MiniMax-M2.7` | 长上下文推理、复杂工具调用 |
| `MiniMax-M2.7-highspeed` | 更低延迟、较轻任务、辅助调用 |

两个模型都支持高达 200,000 令牌的上下文。

当 `minimax-oauth` 作为主提供者时，`MiniMax-M2.7-highspeed` 也会自动用作视觉和委派任务的辅助模型。

<a id="troubleshooting"></a>
## 故障排除

<a id="token-expired-not-re-logging-in-automatically"></a>
### 令牌过期——未自动重新登录

如果访问令牌在过期 60 秒之内，Hermes 会在每个会话启动时刷新令牌。如果访问令牌已经过期（例如长时间离线后），刷新会在下一个请求时自动进行。如果刷新失败并返回 `refresh_token_reused` 或 `invalid_grant`，Hermes 会将会话标记为需要重新登录。

当刷新失败是终局性的（HTTP 4xx、`invalid_grant`、已撤销的授权等），Hermes 会将刷新令牌标记为失效并在本地隔离，以免不断重试已无望的交换。Agent 会显示一条“re-authentication required”消息，并保持不干扰，直到你重新登录。
**修复：** 重新运行 `hermes auth add minimax-oauth` 以重新登录。下一次成功交换后，隔离会自动清除。

<a id="authorization-timed-out"></a>
### 授权超时

设备码流程有有限的到期时间窗口。如果你没有及时批准登录，Hermes 会抛出一个超时错误。

**修复：** 重新运行 `hermes auth add minimax-oauth`（或 `hermes model`）。流程会重新开始。

<a id="state-mismatch-possible-csrf"></a>
### 状态不匹配（可能为 CSRF）

Hermes 检测到授权服务器返回的 `state` 值与它发送的不一致。

**修复：** 重新运行登录。如果问题持续，检查是否有代理或重定向修改了 OAuth 响应。

<a id="logging-in-from-a-remote-server"></a>
### 从远程服务器登录

如果 `hermes` 无法打开浏览器窗口，请使用 `--no-browser`：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 会打印出 URL 和验证码。你可以在任意设备上打开该 URL 并完成登录流程。

<a id="not-logged-into-minimax-oauth-error-at-runtime"></a>
### 运行时出现“未登录 MiniMax OAuth”错误

认证存储中没有 `minimax-oauth` 的凭据。你尚未登录，或者凭据文件已被删除。

**修复：** 运行 `hermes model` 并选择 MiniMax（OAuth），或者运行 `hermes auth add minimax-oauth`。

<a id="logging-out"></a>
## 登出

要删除已存储的 MiniMax OAuth 凭据：

```bash
hermes auth remove minimax-oauth
```

<a id="see-also"></a>
## 另请参阅

- [AI 提供商参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置](../user-guide/configuration.md)
- [hermes doctor](../reference/cli-commands.md)
