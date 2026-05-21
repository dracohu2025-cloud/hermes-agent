---
sidebar_position: 16
title: "xAI Grok OAuth（SuperGrok / X Premium+）"
description: "使用你的 SuperGrok 或 X Premium+ 订阅登录，即可在 Hermes Agent 中使用 Grok 模型 — 无需 API 密钥"
---

<a id="xai-grok-oauth-supergrok-x-premium"></a>
# xAI Grok OAuth（SuperGrok / X Premium+）

Hermes Agent 通过基于浏览器的 OAuth 登录流程支持 xAI Grok，与 [accounts.x.ai](https://accounts.x.ai) 对接，使用 **SuperGrok 订阅**（[grok.com](https://x.ai/grok)）或 **X Premium+ 订阅**（关联的 X 账号）均可。无需 `XAI_API_KEY`——只需一次性登录，Hermes 会在后台自动刷新你的会话。

当你使用已开通 Premium+ 的 X 账号登录时，xAI 会自动将订阅状态关联到你的 xAI 会话，因此 OAuth 流程与直接为 SuperGrok 订阅者提供的流程完全一致。

传输层复用 `codex_responses` 适配器（xAI 暴露了一个类 Responses 的端点），因此推理、工具调用、流式传输和提示缓存无需任何适配器改动即可正常工作。

Hermes 中所有直连 xAI 的功能面——TTS、图像生成、视频生成和语音转文字——都共享同一个 OAuth Bearer 令牌，所以一次登录即可覆盖全部四个功能。

<a id="overview"></a>
## 概览

| 项目 | 值 |
|------|-------|
| Provider ID | `xai-oauth` |
| 显示名称 | xAI Grok OAuth（SuperGrok / X Premium+） |
| 认证类型 | 浏览器 OAuth 2.0 PKCE（回环回调） |
| 传输层 | xAI Responses API（`codex_responses`） |
| 默认模型 | `grok-4.3` |
| 端点 | `https://api.x.ai/v1` |
| 认证服务器 | `https://accounts.x.ai` |
| 需要环境变量 | 否（此提供者**不**使用 `XAI_API_KEY`） |
| 订阅 | [SuperGrok](https://x.ai/grok) 或 [X Premium+](https://x.com/i/premium_sign_up)——参见下方说明 |

<a id="prerequisites"></a>
## 前置条件

- Python 3.9+
- 已安装 Hermes Agent
- 你的 xAI 账号拥有有效的 **SuperGrok** 订阅，**或者**你登录所用的 X 账号拥有 **X Premium+** 订阅（xAI 会自动关联订阅信息）
- 本地机器上可用的浏览器（远程会话可使用 `--no-browser`）

:::warning xAI 可能根据层级限制 OAuth API 访问权限
xAI 后端会对 OAuth API 表面执行自己的允许列表，已有案例显示即使应用内订阅处于活跃状态，标准 SuperGrok 订阅者仍会被拒绝（返回 `HTTP 403`，参见问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。如果 OAuth 登录在浏览器中成功，但推理返回 403，请设置 `XAI_API_KEY` 并切换到 API 密钥路径（`provider: xai`）——目前该路径不受相同的限制。
:::
<a id="xai-may-restrict-oauth-api-access-by-tier"></a>

<a id="quick-start"></a>
## 快速开始

```bash
# 启动提供者和模型选择器
hermes model
# → 从提供者列表中选择 "xAI Grok OAuth（SuperGrok / X Premium+）"
# → Hermes 会在你的浏览器中打开 accounts.x.ai
# → 在浏览器中批准访问权限
# → 选择一个模型（grok-4.3 在顶部）
# → 开始聊天

hermes
```

首次登录后，凭据会保存在 `~/.hermes/auth.json` 中，并在过期前自动刷新。

<a id="logging-in-manually"></a>
## 手动登录

你可以不经过模型选择器直接触发登录：

```bash
hermes auth add xai-oauth
```

<a id="remote-headless-sessions"></a>
### 远程 / 无头会话

在服务器、容器或没有浏览器可用的 SSH 会话中，Hermes 会检测到远程环境，并打印授权 URL 而非打开浏览器。
**重要提示：** 环回监听器仍然运行在远程机器上的 `127.0.0.1:56121`。xAI 的重定向需要到达*该*监听器，因此除非你转发端口，否则在你的笔记本电脑上打开该 URL 会失败（`无法建立连接。我们无法访问你的应用。`）：

```bash
# In a separate terminal on your local machine:
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# Then in your SSH session on the remote machine:
hermes auth add xai-oauth --no-browser
# Open the printed authorize URL in your local browser.
```

通过跳板机/堡垒机：添加 `-J jump-user@jump-host`。

查看 [通过 SSH / 远程主机进行 OAuth](./oauth-over-ssh.md) 获取完整的逐步指导，包括 ProxyJump 链、mosh/tmux 和 ControlMaster 的陷阱。

<a id="browser-only-remotes-cloud-shell-codespaces-ec2-instance-connect"></a>
### 仅浏览器的远程环境（Cloud Shell、Codespaces、EC2 Instance Connect）

如果你没有常规的 SSH 客户端（例如，你在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台内运行 Hermes），那么上述 `ssh -L` 方法不可用。请改用 `--manual-paste`——Hermes 会跳过环回监听器，并允许你直接从浏览器粘贴失败的回调 URL：

```bash
hermes auth add xai-oauth --manual-paste
# Or via the model picker:
hermes model --manual-paste
```

查看 [通过 SSH / 远程主机进行 OAuth](./oauth-over-ssh.md#browser-only-remote-cloud-shell--codespaces--ec2-instance-connect) 获取完整指南。回归修复 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923)。

<a id="how-the-login-works"></a>
## 登录工作原理

1. Hermes 打开你的浏览器并跳转到 `accounts.x.ai`。
2. 你登录（或确认现有会话）并批准访问。
3. xAI 重定向回 Hermes，令牌保存到 `~/.hermes/auth.json`。
4. 此后，Hermes 会在后台刷新访问令牌——你将保持登录状态，直到你执行 `hermes auth remove xai-oauth` 或在你的 xAI 账户设置中撤销访问权限。

<a id="checking-login-status"></a>
## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分将显示每个提供者的当前状态，包括 `xai-oauth`。

<a id="switching-models"></a>
## 切换模型

```bash
hermes model
# → Select "xAI Grok OAuth (SuperGrok / X Premium+)"
# → Pick from the model list (grok-4.3 is pinned to the top)
```

或直接设置模型：

```bash
hermes config set model.default grok-4.3
hermes config set model.provider xai-oauth
```

<a id="configuration-reference"></a>
## 配置参考

登录后，`~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: grok-4.3
  provider: xai-oauth
  base_url: https://api.x.ai/v1
```

<a id="provider-aliases"></a>
### 提供者别名

以下所有别名都解析为 `xai-oauth`：

```bash
hermes --provider xai-oauth        # canonical
hermes --provider grok-oauth       # alias
hermes --provider x-ai-oauth       # alias
hermes --provider xai-grok-oauth   # alias
```

<a id="direct-to-xai-tools-tts-image-video-transcription-x-search"></a>
## 直接调用 xAI 工具（TTS / 图像 / 视频 / 转录 / X 搜索）

一旦你通过 OAuth 登录，每个直接调用 xAI 的工具都会自动重用相同的 bearer 令牌——**无需单独设置**，除非你更想使用 API 密钥。
为每个工具选择后端：

```bash
hermes tools
# → 文本转语音         → "xAI TTS"
# → 图像生成           → "xAI Grok Imagine (image)"
# → 视频生成           → "xAI Grok Imagine"
# → X (Twitter) 搜索    → "xAI Grok OAuth (SuperGrok / X Premium+)"
```

如果 OAuth 令牌已存储，选择器会确认并跳过凭据提示。如果既没有 OAuth 也没有设置 `XAI_API_KEY`，选择器会提供一个三项菜单：OAuth 登录、粘贴 API 密钥或跳过。

:::note 视频生成默认关闭
`video_gen` 工具集默认禁用。在 `hermes tools` → `🎬 Video Generation`（按空格键）中启用后，Agent 才能调用 `video_generate`。否则 Agent 可能会回退到内置的 ComfyUI skill，该 skill 也被标记为视频生成。
:::

<a id="video-generation-is-off-by-default"></a>
:::note X 搜索在配置了 xAI 凭据时自动启用
当配置了 xAI 凭据（SuperGrok / X Premium+ OAuth 令牌或 `XAI_API_KEY`）时，`x_search` 工具集会自​动启用。如果不希望这样，可以通过 `hermes tools` → `🐦 X (Twitter) Search`（按空格键）显式禁用。该工具通过 xAI 内置的 `x_search` Responses API 路由——它可以与你的 SuperGrok / X Premium+ OAuth 登录或付费的 `XAI_API_KEY` 配合使用，并且在两者都配置时优先使用 OAuth（使用你的订阅配额而非 API 消耗）。当未配置任何 xAI 凭据时，即使工具集已启用，其工具模式也会对模型隐藏。
:::

<a id="x-search-auto-enables-when-xai-credentials-are-present"></a>
<a id="models"></a>
### 模型

| 工具 | 模型 | 说明 |
|------|-------|------|
| 聊天 | `grok-4.3` | 默认；通过 OAuth 登录时自动选择 |
| 聊天 | `grok-4.20-0309-reasoning` | 推理变体 |
| 聊天 | `grok-4.20-0309-non-reasoning` | 非推理变体 |
| 聊天 | `grok-4.20-multi-agent-0309` | 多 Agent 变体 |
| 图像 | `grok-imagine-image` | 默认；约 5–10 秒 |
| 图像 | `grok-imagine-image-quality` | 更高保真度；约 10–20 秒 |
| 视频 | `grok-imagine-video` | 文本转视频和图像转视频；最多 7 张参考图像 |
| TTS | (默认语音) | xAI `/v1/tts` 端点 |

聊天目录实时衍生自磁盘上的 `models.dev` 缓存；该缓存刷新后，新的 xAI 版本会自动出现。`grok-4.3` 始终固定在列表顶部。

<a id="environment-variables"></a>
## 环境变量

| 变量 | 效果 |
|--------|-------|
| `XAI_BASE_URL` | 覆盖默认的 `https://api.x.ai/v1` 端点（很少需要）。 |
| `HERMES_INFERENCE_PROVIDER` | 在运行时强制指定活动提供者，例如 `HERMES_INFERENCE_PROVIDER=xai-oauth hermes`。 |

<a id="troubleshooting"></a>
## 问题排除

<a id="token-expired-not-re-logging-in-automatically"></a>
### 令牌已过期——未自动重新登录

Hermes 在每次会话前刷新令牌，并在收到 401 时再次反应式刷新。如果刷新因 `invalid_grant`（刷新令牌被撤销或账户已轮换）而失败，Hermes 会显示一条类型化的重新认证消息，而不是崩溃。

当刷新失败是致命的（HTTP 4xx、`invalid_grant`、已撤销授权等）时，Hermes 会将刷新令牌标记为无效并在本地隔离——后续调用将跳过注定失败的刷新尝试，而不是反复重放同一个 401。Agent 会显示一条“需要重新认证”的消息，并在你再次登录之前保持静默。
**修复：** 再次运行 `hermes auth add xai-oauth` 以重新开始登录。隔离状态会在下一次成功交换后清除。

<a id="authorization-timed-out"></a>
### 授权超时

环回监听器有一个有限的过期窗口（默认 180 秒）。如果你没有及时批准登录，Hermes 会引发超时错误。

**修复：** 重新运行 `hermes auth add xai-oauth`（或 `hermes model`）。流程会重新开始。

<a id="state-mismatch-possible-csrf"></a>
### 状态不匹配（可能为 CSRF）

Hermes 检测到授权服务器返回的 `state` 值与其发送的不匹配。

**修复：** 重新运行登录。如果问题持续存在，请检查是否有代理或重定向修改了 OAuth 响应。

<a id="logging-in-from-a-remote-server"></a>
### 从远程服务器登录

在 SSH 或容器会话中，Hermes 会打印授权 URL 而不是打开浏览器。环回回调监听器仍然绑定在远程主机的 `127.0.0.1:56121` 上——如果没有 SSH 本地转发，你的笔记本电脑浏览器无法访问它：

```bash
# Local machine, separate terminal:
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# Remote machine:
hermes auth add xai-oauth --no-browser
```

完整指南（跳板机、mosh/tmux、端口冲突）：[通过 SSH 进行 OAuth / 远程主机](./oauth-over-ssh.md)。

<a id="http-403-after-a-successful-login-tier-entitlement"></a>
### 登录成功后出现 HTTP 403（层级/权限）

在浏览器中完成了 OAuth，令牌已保存，但推理或令牌刷新返回了 `HTTP 403`，并带有类似于 *"The caller does not have permission to execute the specified operation"* 的消息。

这**不是**令牌过期的问题——重新运行 `hermes model` 不会改变它。xAI 后端被发现会限制 OAuth API 访问仅限于特定的 SuperGrok 层级，即使应用内订阅处于活动状态（问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。

**修复：** 设置 `XAI_API_KEY` 并切换到 API 密钥路径：

```bash
export XAI_API_KEY=xai-...
hermes config set model.provider xai
```

或者，如果需要使用 OAuth 路线，请前往 [x.ai/grok](https://x.ai/grok) 升级你的订阅。

<a id="no-xai-credentials-found-error-at-runtime"></a>
### 运行时出现“未找到 xAI 凭据”错误

认证存储中没有 `xai-oauth` 条目，也没有设置 `XAI_API_KEY`。你可能尚未登录，或者凭据文件已被删除。

**修复：** 运行 `hermes model` 并选择 xAI Grok OAuth 提供者，或运行 `hermes auth add xai-oauth`。

<a id="logging-out"></a>
## 登出

要删除所有已存储的 xAI Grok OAuth 凭据：

```bash
hermes auth logout xai-oauth
```

这会清除 `auth.json` 中的单例 OAuth 条目以及 `xai-oauth` 的任何凭据池行。如果你只想删除单个池条目，请使用 `hermes auth remove xai-oauth &lt;index|id|label&gt;`（运行 `hermes auth list xai-oauth` 查看它们）。

<a id="see-also"></a>
## 参见

- [通过 SSH 进行 OAuth / 远程主机](./oauth-over-ssh.md) — 如果 Hermes 与你的浏览器不在同一台机器上，必读
- [AI Providers 参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置](../user-guide/configuration.md)
- [语音与 TTS](../user-guide/features/tts.md)
