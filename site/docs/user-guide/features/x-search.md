---
title: X (Twitter) 搜索
description: 使用 xAI 内置的 x_search Responses 工具，让 Agent 可以直接搜索 X（Twitter）上的帖子和讨论串——支持 SuperGrok OAuth 登录或 XAI_API_KEY 两种方式。
sidebar_label: X (Twitter) 搜索
sidebar_position: 7
---

<a id="x-twitter-search"></a>
# X (Twitter) 搜索

`x_search` 工具让 Agent 可以直接搜索 X（Twitter）上的帖子、个人资料和讨论串。它由 xAI 在 Responses API（`https://api.x.ai/v1/responses`）中内置的 `x_search` 工具提供支持——Grok 在服务端完成搜索，并返回带有原始帖子引用链接的综合结果。

**当你特别想要获取 X 上当前的讨论、反应或说法时，请使用此工具代替 `web_search`**。对于常规网页，继续使用 `web_search` / `web_extract`。

<a id="authentication"></a>
## 身份验证

当 **任一** xAI 凭证路径可用时，`x_search` 工具即会注册：

| 凭证 | 来源 | 配置方式 |
|------------|--------|-------|
| **SuperGrok / X Premium+ OAuth**（推荐） | 通过浏览器在 `accounts.x.ai` 登录，自动刷新 | `hermes auth add xai-oauth` — 参见 [xAI Grok OAuth（SuperGrok / X Premium+）](../../guides/xai-grok-oauth.md) |
| **`XAI_API_KEY`** | 付费 xAI API 密钥 | 在 `~/.hermes/.env` 中设置 |

两者都使用相同的端点、相同的载荷——唯一的区别是 bearer token。**当两者都配置时，SuperGrok OAuth 优先**，因此 x_search 会使用你的订阅配额，而不是消耗付费 API 额度。

该工具的 `check_fn` 会在每次重建模型的工具列表时运行 xAI 凭证解析器。若返回 `True`，表示 bearer 可获取且非空，并且（如果已过期）已成功刷新。如果令牌被吊销且刷新失败，该工具会从架构中隐藏；模型根本看不到它。

<a id="enabling-the-tool"></a>
## 启用工具

当存在 xAI 凭证（OAuth token 或 `XAI_API_KEY`）时自动启用。如果你不希望启用，可以通过 `hermes tools` → Search → x_search 显式禁用。

```bash
hermes tools
# → 🐦 X (Twitter) 搜索   (按空格键切换开启)
```

选择器提供两种凭证选择：

1. **xAI Grok OAuth（SuperGrok 订阅）** — 如果你尚未登录，会打开浏览器跳转到 `accounts.x.ai`
2. **xAI API 密钥** — 提示输入 `XAI_API_KEY`

两种选择都能满足门控要求。你可以选择你已有的任何一种凭证；使用任何一种凭证，工具的行为完全相同。如果两者都配置了，调用时 OAuth 将优先。

<a id="configuration"></a>
## 配置

```yaml
# ~/.hermes/config.yaml
x_search:
  # 调用 Responses 时使用的 xAI 模型。
  # 推荐默认使用 grok-4.20-reasoning；任何支持 x_search 工具的 Grok 模型都可用。
  model: grok-4.20-reasoning

  # 请求超时时间（秒）。x_search 在复杂查询时可能需要 60–120 秒——默认值已留足余量。最低：30。
  timeout_seconds: 180

  # 遇到 5xx / ReadTimeout / ConnectionError 时的自动重试次数。
  # 每次重试会进行退避（1.5 倍尝试秒数，上限 5 秒）。
  retries: 2
```

<a id="tool-parameters"></a>
## 工具参数

Agent 调用 `x_search` 时使用以下参数：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `query` | 字符串（必填） | 在 X 上搜索的内容。 |
| `allowed_x_handles` | 字符串数组 | 可选，限定仅搜索这些用户（最多 10 个）。开头的 `@` 会被自动去除。 |
| `excluded_x_handles` | 字符串数组 | 可选，排除这些用户（最多 10 个）。与 `allowed_x_handles` 互斥。 |
| `from_date` | 字符串 | 可选，开始日期，格式 `YYYY-MM-DD`。 |
| `to_date` | 字符串 | 可选，结束日期，格式 `YYYY-MM-DD`。 |
| `enable_image_understanding` | 布尔值 | 要求 xAI 分析匹配帖子中的图片。 |
| `enable_video_understanding` | 布尔值 | 要求 xAI 分析匹配帖子中的视频。 |
该工具返回 JSON，包含以下字段：

- `answer` — Grok 合成的文本回复
- `citations` — Responses API 顶层字段返回的引用
- `inline_citations` — 从消息体中提取的 `url_citation` 注释（每个包含 `url`、`title`、`start_index`、`end_index`）
- `degraded` — 当设置了任何筛选条件（`allowed_x_handles`、`excluded_x_handles`、`from_date`、`to_date`）且两个引用通道都返回空时，值为 `true`。此时 `answer` 是根据模型自身知识合成的，而非来自 X 索引，因此应视为无来源。其他情况（包括“未设置筛选条件”的情况——一个宽泛的无来源回答只是回答，而非筛选失败）值为 `false`
- `degraded_reason` — 简短字符串，说明哪些筛选条件处于激活状态；当 `degraded` 为 `false` 时，值为 `null`
- `credential_source` — 如果 OAuth 解析成功，值为 `"xai-oauth"`；如果 API 密钥解析成功，值为 `"xai"`
- `model`、`query`、`provider`、`tool`、`success`

<a id="date-validation"></a>
### 日期验证

`from_date` / `to_date` 在 HTTP 调用前会在客户端进行验证：

- 如果提供了这两个参数，它们必须能解析为 `YYYY-MM-DD` 格式。
- 当两者都设置时，`from_date` 必须早于或等于 `to_date`。
- `from_date` 不能晚于 UTC 当前日期——因为尚未开始的时间窗口内不可能存在帖子，所以该调用必然返回零条引用。
- 允许 `to_date` 为未来日期（调用者可以合法地请求“从昨天到明天”来捕获即将发布的帖子）。

验证失败会以结构化的 `{"error": "..."}` 工具结果形式呈现，而不会向 xAI 发起 HTTP 调用。

<a id="example"></a>
## 示例

与 Agent 对话：

> 人们在 X 上对新的 Grok 图像功能有什么看法？请重点关注来自 @xai 的回复。

Agent 将：

1. 调用 `x_search`，参数为 `query="reactions to new Grok image features"`、`allowed_x_handles=["xai"]`
2. 获取合成的回答以及指向具体帖子的引用列表
3. 回复答案和引用

<a id="troubleshooting"></a>
## 故障排除

<a id="no-xai-credentials-available"></a>
### "No xAI credentials available"

当两种认证路径都失败时，工具会显示此信息。请在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，或运行 `hermes auth add xai-oauth` 并完成浏览器登录。然后重启会话，以便 Agent 重新读取工具注册表。

<a id="xsearch-is-not-enabled-for-this-model"></a>
### "`x_search` is not enabled for this model"

配置的 `x_search.model` 没有访问服务端 `x_search` 工具的权限。请切换到 `grok-4.20-reasoning`（默认值）或其他支持该工具的 Grok 模型。查看 [xAI 文档](https://docs.x.ai/) 获取当前支持的模型列表。

<a id="tool-doesn-t-appear-in-the-schema"></a>
### 工具未出现在 schema 中

可能有两个原因：

1. **未启用工具集。** 运行 `hermes tools` 并确认 `🐦 X (Twitter) Search` 已勾选。
2. **没有 xAI 凭据。** check_fn 返回 False，因此 schema 保持隐藏。运行 `hermes auth status` 确认 xai-oauth 登录状态，并检查是否设置了 `XAI_API_KEY`（如果你使用的是 API 密钥路径）。

<a id="degraded-true-answer-with-no-citations"></a>
### `degraded: true` — 无引用的回答

当你使用了 `allowed_x_handles`、`excluded_x_handles` 或日期范围，且返回的响应中 `degraded` 为 `true` 时，说明 xAI 的 X 索引没有找到匹配的帖子，但 Grok 仍然根据自身训练数据生成了合成回答。该回答没有来源——请勿将其视为真实的 X 结果。
值得检查的原因：

- **用户名拼写错误。** 去掉 `@`，仔细检查拼写，并确认该账号存在。
- **日期范围过窄** 或滑动到了今天之前的帖子；扩大范围重试。
- **xAI 索引缺口。** 某些活跃账号即使定期发帖，也可能偶发地在 `x_search` 中无法显示。等待几分钟后重试，或当你需要确切某个账号的时间线时，使用 `xurl` 技能直接读取 X API。

<a id="see-also"></a>
## 另请参阅

- [xAI Grok OAuth（SuperGrok 订阅）](../../guides/xai-grok-oauth.md) — OAuth 设置指南
- [网页搜索与提取](web-search.md) — 用于通用（非 X）网页搜索
- [工具参考](../../reference/tools-reference.md) — 完整工具目录
