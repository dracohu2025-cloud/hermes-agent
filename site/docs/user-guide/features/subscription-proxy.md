---
sidebar_position: 15
title: "订阅代理"
description: "将你的 Nous Portal 订阅（或其他 OAuth 提供方）用作外部应用的 OpenAI 兼容端点"
---

<a id="subscription-proxy"></a>
# 订阅代理

订阅代理是一个本地 HTTP 服务器，允许外部应用——OpenViking、Karakeep、Open WebUI，以及任何支持 OpenAI 兼容聊天补全的应用——把你由 Hermes 管理的提供方订阅用作它们的 LLM 端点。代理会自动附上正确的凭据（自动刷新），因此应用永远不需要一个静态的 API 密钥。

这与 [API 服务器](./api-server.md) 不同：

| | API 服务器 | 订阅代理 |
|---|---|---|
| 提供的内容 | 你的 Agent（完整的工具集、记忆、技能） | 原始模型推理 |
| 使用场景 | “把 Hermes 当作聊天后端” | “在另一个应用中使用我的 Portal 订阅” |
| 认证 | 你的 `API_SERVER_KEY` | 任意 bearer 令牌（代理会附上真实的令牌） |
| 工具调用 | 是 —— Agent 运行工具 | 否 —— 仅透传 |

当你希望将 **Agent** 作为后端时，使用 API 服务器。当你只想通过订阅使用 **模型** 时，使用代理。

<a id="quick-start"></a>
## 快速开始

<a id="1-log-into-your-provider-one-time"></a>
### 1. 登录你的提供方（一次性操作）

```bash
hermes login nous
```

这会打开你的浏览器进行 Nous Portal OAuth 流程。Hermes 将刷新令牌保存在 `~/.hermes/auth.json` —— 所有 Hermes 提供方登录信息都保存在同一个地方。

<a id="2-start-the-proxy"></a>
### 2. 启动代理

```bash
hermes proxy start
```

```
为 Nous Portal 启动 Hermes 代理
  监听地址：  http://127.0.0.1:8645/v1
  转发到：    （根据你的订阅按请求解析）
  客户端可使用任意 bearer 令牌 —— 代理会附上你的真实凭据。
```

让它在前台保持运行。如果你希望在登出后仍然运行，可以使用 `tmux`、`nohup` 或 systemd 单元。

<a id="3-point-your-app-at-it"></a>
### 3. 将你的应用指向它

任何兼容 OpenAI 的应用配置都需要以下三个参数：

```
Base URL:   http://127.0.0.1:8645/v1
API key:    任意内容（例如 "sk-unused"）
Model:      Hermes-4-70B    # 或 Hermes-4.3-36B、Hermes-4-405B
```

代理会忽略来自你应用的 `Authorization` 请求头，并将你真实的 Portal 凭据附加到上游请求中。当 bearer 令牌接近过期时会自动刷新。

<a id="available-providers"></a>
## 可用的提供方

```bash
hermes proxy providers
```

当前提供的：`nous`（Nous Portal）。通过实现 `hermes_cli/proxy/adapters/` 中的 `UpstreamAdapter` 接口，可以添加更多 OAuth 提供方。

<a id="check-status"></a>
## 检查状态

```bash
hermes proxy status
```

```
Hermes 代理上游适配器

  [nous    ] Nous Portal — 就绪（bearer 令牌过期时间：2026-05-15T06:43:21Z）
```

如果你看到 `not logged in`，请运行 `hermes login nous`。如果你看到 `credentials need attention`，说明你的刷新令牌已被吊销（很少发生——如果你从 Portal 网页界面退出登录就会触发）——只需重新运行 `hermes login nous`。

<a id="allowed-paths"></a>
## 允许的路径

代理只转发上游实际提供服务的路径。对于 Nous Portal：

| 路径 | 用途 |
|------|------|
| `/v1/chat/completions` | 聊天补全（流式 + 非流式） |
| `/v1/completions` | 旧版文本补全 |
| `/v1/embeddings` | 嵌入向量 |
| `/v1/models` | 模型列表 |

其他路径（`/v1/images/generations`、`/v1/audio/speech` 等）会返回 404，并附带清晰的错误信息，指出允许的路径。这可以防止无关的客户端向上游泄漏奇怪的请求。
<a id="configuring-openviking-to-use-portal"></a>
## 配置 OpenViking 使用 Portal

[OpenViking](https://github.com/volcengine/OpenViking) 是一个上下文数据库，需要 LLM 提供商来支持其 VLM（用于提取记忆的视觉/语言模型）和嵌入模型。通过代理，你可以将其 `vlm.api_base` 指向本地代理：

编辑 `~/.openviking/ov.conf`：

```json
{
  "vlm": {
    "provider": "openai",
    "model": "Hermes-4-70B",
    "api_base": "http://127.0.0.1:8645/v1",
    "api_key": "unused-proxy-attaches-real-creds"
  }
}
```

然后在终端中与 `openviking-server` 一起启动代理：

```bash
# 终端 1
hermes proxy start

# 终端 2
openviking-server
```

现在，OpenViking 的 VLM 调用将通过你的 Portal 订阅进行。嵌入模型方面仍然需要自己的提供商——Portal 确实提供 `/v1/embeddings` 端点，但模型选择取决于你的套餐支持情况；请查看 `portal.nousresearch.com/models`。

<a id="configuring-karakeep-or-any-bookmark-summarizer-app"></a>
## 配置 Karakeep（或任何书签/摘要应用）

[Karakeep](https://karakeep.app/) 使用兼容 OpenAI 的 API 进行书签摘要。在其配置中：

```bash
# Karakeep .env
OPENAI_API_BASE_URL=http://127.0.0.1:8645/v1
OPENAI_API_KEY=any-non-empty-string
INFERENCE_TEXT_MODEL=Hermes-4-70B
```

同样的模式也适用于 Open WebUI、LobeChat、NextChat 或任何其他兼容 OpenAI 的客户端。

<a id="exposing-on-lan"></a>
## 在局域网中暴露

默认情况下，代理绑定 `127.0.0.1`（仅限本地主机）。要让网络中的其他机器使用它：

```bash
hermes proxy start --host 0.0.0.0 --port 8645
```

⚠ **请注意：** 你网络中的任何人都可以使用你的 Portal 订阅。代理本身没有身份验证——它接受任何 bearer 令牌。如果你在受信任网络之外暴露此代理，请使用防火墙、VPN 或带有适当身份验证的反向代理。

<a id="rate-limits"></a>
## 速率限制

你的 Portal 套餐的 RPM/TPM 限制适用于整个代理。代理不会进行扇出或池化——它是一个带有你完整订阅配额的单一 bearer。在 [portal.nousresearch.com](https://portal.nousresearch.com) 监控使用情况。

<a id="architecture"></a>
## 架构

代理设计得尽可能精简。每个请求的处理流程：

1. 从你的应用接收 `POST /v1/chat/completions`
2. 查找适配器的当前凭证（如果即将过期则刷新）
3. 逐字转发请求体，并附带 `Authorization: Bearer &lt;minted-key&gt;`
4. 原样流式返回响应（保留 SSE）

无转换。不记录请求体。无 Agent 循环。代理只是一个附加凭证的透传层。

<a id="future-more-oauth-providers"></a>
## 未来：更多 OAuth 提供商

适配器系统是可插拔的。添加新的提供商（例如 HuggingFace、GitHub Copilot 的聊天端点、通过 OAuth 的 Anthropic）需要在 `hermes_cli/proxy/adapters/&lt;provider&gt;.py` 中实现 `UpstreamAdapter`，并在 `adapters/__init__.py` 中注册。在协议层面不兼容 OpenAI 的提供商（例如 Anthropic Messages API）需要转换层，这超出了当前范围。
