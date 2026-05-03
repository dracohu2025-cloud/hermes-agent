---
sidebar_position: 15
title: "MiniMax OAuth"
description: "通过浏览器 OAuth 登录 MiniMax，在 Hermes Agent 中使用 MiniMax-M2.7 模型——无需 API 密钥"
---

# MiniMax OAuth {#minimax-oauth}

Hermes Agent 通过基于浏览器的 OAuth 登录流程支持 **MiniMax**，使用与 [MiniMax 门户](https://www.minimax.io) 相同的凭据。无需 API 密钥或信用卡——只需登录一次，Hermes 会自动刷新你的会话。

传输层复用了 `anthropic_messages` 适配器（MiniMax 在 `/anthropic` 路径下暴露了一个兼容 Anthropic Messages 的端点），因此所有现有的工具调用、流式传输和上下文功能无需任何适配器更改即可正常工作。

## 概览 {#overview}

| 项目 | 值 |
|------|-------|
| 提供商 ID | `minimax-oauth` |
| 显示名称 | MiniMax (OAuth) |
| 认证类型 | 浏览器 OAuth (PKCE 设备码流程) |
| 传输层 | 兼容 Anthropic Messages (`anthropic_messages`) |
| 模型 | `MiniMax-M2.7`、`MiniMax-M2.7-highspeed` |
| 全球端点 | `https://api.minimax.io/anthropic` |
| 中国端点 | `https://api.minimaxi.com/anthropic` |
| 需要环境变量 | 否（此提供商**不**使用 `MINIMAX_API_KEY`） |

## 前提条件 {#prerequisites}

- Python 3.9+
- 已安装 Hermes Agent
- 在 [minimax.io](https://www.minimax.io)（全球）或 [minimaxi.com](https://www.minimaxi.com)（中国）拥有 MiniMax 账户
- 本地机器上有可用的浏览器（或对远程会话使用 `--no-browser`）

## 快速开始 {#quick-start}

```bash
# 启动提供商和模型选择器
hermes model
# → 从提供商列表中选择 "MiniMax (OAuth)"
# → Hermes 会在浏览器中打开 MiniMax 授权页面
# → 在浏览器中批准访问
# → 选择一个模型（MiniMax-M2.7 或 MiniMax-M2.7-highspeed）
# → 开始聊天

hermes
```

首次登录后，凭据会存储在 `~/.hermes/auth.json` 中，并在每次会话前自动刷新。

## 手动登录 {#logging-in-manually}

你可以不通过模型选择器直接触发登录：

```bash
hermes auth add minimax-oauth
```

### 中国区域 {#china-region}

如果你的账户在中国平台（`minimaxi.com`）上，请传递 `--region cn` 参数：

```bash
hermes auth add minimax-oauth --region cn
```

### 远程 / 无头会话 {#remote-headless-sessions}

在服务器或容器上，如果没有可用的浏览器：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 会打印验证 URL 和用户代码——在任何设备上打开该 URL，并在提示时输入代码。

## OAuth 流程 {#the-oauth-flow}

Hermes 针对 MiniMax OAuth 端点实现了 PKCE 设备码流程：

1. Hermes 生成一对 PKCE 验证器/挑战值和一个随机状态值。
2. 它向 `{base_url}/oauth/code` 发送 POST 请求（包含挑战值），并收到一个 `user_code` 和 `verification_uri`。
3. 你的浏览器打开 `verification_uri`。如果提示，请输入 `user_code`。
4. Hermes 轮询 `{base_url}/oauth/token`，直到收到令牌（或超时）。
5. 令牌（`access_token`、`refresh_token`、过期时间）保存到 `~/.hermes/auth.json` 中的 `minimax-oauth` 键下。

令牌刷新（标准 OAuth `refresh_token` 授权）会在每次会话启动时自动进行，当访问令牌距离过期时间不足 60 秒时触发。

## 检查登录状态 {#checking-login-status}

```bash
hermes doctor
```
`◆ Auth Providers` 部分将显示：

```
✓ MiniMax OAuth  (已登录，区域=global)
```

或者，如果未登录：

```
⚠ MiniMax OAuth  (未登录)
```

## 切换模型 {#switching-models}

```bash
hermes model
# → 选择 "MiniMax (OAuth)"
# → 从模型列表中选取
```

或者直接设置模型：

```bash
hermes config set model MiniMax-M2.7
hermes config set provider minimax-oauth
```

## 配置参考 {#configuration-reference}

登录后，`~/.hermes/config.yaml` 将包含类似以下内容：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```

### `--region` 标志 {#region-flag}

| 值 | 门户 | 推理端点 |
|-------|--------|-------------------|
| `global`（默认） | `https://api.minimax.io` | `https://api.minimax.io/anthropic` |
| `cn` | `https://api.minimaxi.com` | `https://api.minimaxi.com/anthropic` |

### 提供者别名 {#provider-aliases}

以下所有别名都解析为 `minimax-oauth`：

```bash
hermes --provider minimax-oauth    # 规范名称
hermes --provider minimax-portal   # 别名
hermes --provider minimax-global   # 别名
hermes --provider minimax_oauth    # 别名（下划线形式）
```

## 环境变量 {#environment-variables}

`minimax-oauth` 提供者**不**使用 `MINIMAX_API_KEY` 或 `MINIMAX_BASE_URL`。这些变量仅用于基于 API 密钥的 `minimax` 和 `minimax-cn` 提供者。

| 变量 | 作用 |
|----------|--------|
| `MINIMAX_API_KEY` | 仅由 `minimax` 提供者使用 — `minimax-oauth` 忽略 |
| `MINIMAX_CN_API_KEY` | 仅由 `minimax-cn` 提供者使用 — `minimax-oauth` 忽略 |

要在运行时强制使用 `minimax-oauth` 提供者：

```bash
HERMES_INFERENCE_PROVIDER=minimax-oauth hermes
```

## 模型 {#models}

| 模型 | 最佳用途 |
|-------|----------|
| `MiniMax-M2.7` | 长上下文推理、复杂工具调用 |
| `MiniMax-M2.7-highspeed` | 低延迟、轻量任务、辅助调用 |

两个模型均支持最多 200,000 个 token 的上下文。

当 `minimax-oauth` 是主要提供者时，`MiniMax-M2.7-highspeed` 也会自动用作视觉和委派任务的辅助模型。

## 故障排除 {#troubleshooting}

### Token 已过期 — 未自动重新登录 {#token-expired-not-re-logging-in-automatically}

Hermes 会在每次会话启动时刷新 token（如果距离过期时间在 60 秒内）。如果访问 token 已经过期（例如长时间离线后），刷新会在下一次请求时自动进行。如果刷新失败并返回 `refresh_token_reused` 或 `invalid_grant`，Hermes 会将会话标记为需要重新登录。

**解决方法：** 再次运行 `hermes auth add minimax-oauth` 以启动全新登录。

### 授权超时 {#authorization-timed-out}

设备码流程有固定的过期窗口。如果你未及时批准登录，Hermes 会引发超时错误。

**解决方法：** 重新运行 `hermes auth add minimax-oauth`（或 `hermes model`）。流程会重新开始。

### 状态不匹配（可能的 CSRF） {#state-mismatch-possible-csrf}

Hermes 检测到授权服务器返回的 `state` 值与它发送的不匹配。

**解决方法：** 重新运行登录。如果问题持续存在，请检查是否有代理或重定向修改了 OAuth 响应。
### 从远程服务器登录 {#logging-in-from-a-remote-server}

如果 `hermes` 无法打开浏览器窗口，请使用 `--no-browser`：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 会输出 URL 和验证码。在任何设备上打开该 URL 并完成登录流程。

### 运行时出现 "Not logged into MiniMax OAuth" 错误 {#not-logged-into-minimax-oauth-error-at-runtime}

认证存储中没有 `minimax-oauth` 的凭据。您尚未登录，或者凭据文件已被删除。

**解决方法：** 运行 `hermes model` 并选择 MiniMax (OAuth)，或运行 `hermes auth add minimax-oauth`。

## 退出登录 {#logging-out}

要删除已存储的 MiniMax OAuth 凭据：

```bash
hermes auth remove minimax-oauth
```

## 参见 {#see-also}

- [AI Providers 参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置](../user-guide/configuration.md)
- [hermes doctor](../reference/cli-commands.md)
