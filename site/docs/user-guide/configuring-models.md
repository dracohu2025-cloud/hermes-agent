---
sidebar_position: 3
---

<a id="configuring-models"></a>
# 配置模型

Hermes 使用两种模型槽位：

- **主模型** — Agent 用来思考的模型。每条用户消息、每次工具调用循环、每次流式响应都经过这个模型。
- **辅助模型** — Agent 外包给较小副任务的模型。包括上下文压缩、视觉（图像分析）、网页摘要生成、审批评分、MCP 工具路由、会话标题生成以及技能搜索。每个任务都有自己的槽位，并且可以独立覆盖。

本页介绍如何从仪表盘配置这两类模型。如果你更喜欢配置文件或 CLI，请直接跳到底部的[替代方法](#alternative-methods)。

<a id="the-models-page"></a>
## 模型页面

打开仪表盘，点击侧边栏中的 **模型**。你会看到两个区域：

1. **模型设置** — 顶部面板，在这里为各槽位分配模型。
2. **使用分析** — 按排名展示的卡片，显示所选时间段内运行过会话的每个模型，包含 Token 数量、成本及能力徽章。

![模型页面概览](/img/docs/dashboard-models/overview.png)

顶部卡片是 **模型设置** 面板。主行始终显示 Agent 将为新会话启动的模型。点击 **更改** 打开选择器。

<a id="setting-the-main-model"></a>
## 设置主模型

点击主模型行上的 **更改**：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器包含两列：

- **左侧** — 已认证的提供商。只有你已经设置好（已配置 API 密钥、已 OAuth 授权或定义为自定义端点）的提供商才会显示在这里。如果某个提供商缺失，请前往 **密钥** 页面添加其凭证。
- **右侧** — 针对所选提供商的精选模型列表。这些是 Hermes 为该提供商推荐的 Agent 模型，而非原始的 `/models` 导出的所有模型（在 OpenRouter 上，该导出包含 400 多个模型，包括 TTS、图像生成器、重排序器等）。

在过滤框中输入内容，可按提供商名称、别名或模型 ID 进行筛选。

选择一个模型，点击 **切换**，Hermes 会将其写入 `~/.hermes/config.yaml` 的 `model` 部分。**此操作仅适用于新会话**——任何已经打开的聊天标签页将继续使用其启动时的模型。若要在当前聊天中热切换，请在该聊天内使用 `/model` 斜杠命令。

<a id="setting-auxiliary-models"></a>
## 设置辅助模型

点击 **显示辅助模型** 展开八个任务槽位：

![展开的辅助面板](/img/docs/dashboard-models/auxiliary-expanded.png)

每个辅助任务默认都为 `auto`——这意味着 Hermes 也会为该任务使用你的主模型。当你希望某个副任务使用更便宜或更快的模型时，可以覆盖特定任务。

<a id="common-override-patterns"></a>
### 常见覆盖模式

| 任务 | 何时覆盖 |
|---|---|
| **标题生成** | 几乎总是。一个 $0.10/M 的 flash 模型在生成会话标题方面和 Opus 一样好。默认配置在 OpenRouter 上将其设置为 `google/gemini-3-flash-preview`。 |
| **视觉** | 当你的主模型是不带视觉功能的编码模型（例如 Kimi、DeepSeek）时。将其指向 `google/gemini-2.5-flash` 或 `gpt-4o-mini`。 |
| **压缩** | 当你为了总结上下文而在 Opus/M2.7 上浪费推理 Token 时。一个快速聊天模型以 1/50 的成本完成相同工作。 |
| **审批** | 用于 `approval_mode: smart` 时——一个快速/便宜的模型（haiku、flash、gpt-5-mini）决定是否自动批准低风险命令。在这里使用昂贵的模型是浪费。 |
| **网页提取** | 当你大量使用 `web_extract` 时。逻辑与压缩相同——摘要不需要推理。 |
| **技能中心** | `hermes skills search` 会用到这个。通常设为 `auto` 即可。 |
| **MCP** | MCP 工具路由。通常设为 `auto` 即可。 |
<a id="per-task-override"></a>
### 按任务单独覆盖

点击任意辅助行的 **Change** 按钮。会弹出同样的选择器，操作方式也一样——选择提供商 + 模型，然后点击 Switch。该行会更新显示为 `provider · model`，而不是 `auto (use main model)`。

<a id="reset-all-to-auto"></a>
### 全部重置为自动

如果你调整过度想重新开始，点击辅助区域顶部的 **Reset all to auto**。每个槽位都会恢复使用主模型。

<a id="the-use-as-shortcut"></a>
## "Use as" 快捷方式

页面上的每个模型卡片都有一个 **Use as** 下拉菜单。这是快速路径——在分析数据中选一个模型，点击 **Use as**，一键将其分配给主槽位或任意特定辅助任务：

![Use as 下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

下拉菜单包含：

- **Main model** —— 等同于点击主行的 Change。
- **All auxiliary tasks** —— 将此模型一次性分配给全部 8 个辅助槽位。当你只想让所有次要任务都跑在一个便宜的 flash 模型上时很实用。
- **Individual task options** —— Vision、Web Extract、Compression 等。每个任务当前已分配的模型会标记为 `current`。

当卡片当前被分配了某个任务时，会带有 `main` 或 `aux · &lt;task&gt;` 徽章——这样你一眼就能看出哪些历史模型被用在了哪里。

<a id="what-gets-written-to-config-yaml"></a>
## 写入 `config.yaml` 的内容

通过仪表盘保存时，Hermes 会写入 `~/.hermes/config.yaml`：

**主模型：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4.7
  base_url: ''        # 切换提供商时清空
  api_mode: chat_completions
```

**辅助覆盖（示例——vision 使用 gemini-flash）：**
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash
    base_url: ''
    api_key: ''
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

**辅助任务设为自动（默认）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... 其他字段不变
```

`provider: auto` 配合 `model: ''` 告诉 Hermes 对该任务使用主模型。

<a id="when-does-it-take-effect"></a>
## 何时生效？

- **CLI**（`hermes chat`）：下次调用 `hermes chat` 时生效。
- **Gateway**（Telegram、Discord、Slack 等）：下一个*新*会话生效。已有会话保持原有模型。如果你想强制所有会话都应用变更，请重启 gateway（`hermes gateway restart`）。
- **仪表盘聊天标签页**（`/chat`）：下一个新 PTY 生效。当前打开的聊天保持原有模型——在聊天内使用 `/model` 可热切换。

变更不会使正在运行的会话的提示缓存失效。这是有意为之：在会话内切换主模型需要重置缓存（系统提示包含模型特定的内容），我们把这个操作保留给聊天内的显式 `/model` 斜杠命令。

<a id="troubleshooting"></a>
## 故障排除

<a id="no-authenticated-providers-in-the-picker"></a>
### 选择器中显示"No authenticated providers"

Hermes 只列出有有效凭据的提供商。检查侧边栏中的 **Keys**——你应该能看到以下之一：API 密钥、成功的 OAuth、或自定义端点 URL。如果你想要的提供商不在那里，运行 `hermes setup` 来配置它，或者前往 **Keys** 添加环境变量。
<a id="main-model-didn-t-change-in-my-running-chat"></a>
### 当前聊天中的主模型没有变化

这是正常行为。仪表盘写入 `config.yaml`，新会话读取该文件。当前打开的聊天是正在运行的 Agent 进程——它会保留启动时使用的模型。在聊天中使用 `/model <名称>` 可以热切换该特定会话的模型。

<a id="auxiliary-override-didn-t-take-effect"></a>
### 辅助覆写“未生效”

请检查以下三点：

1. **你是否启动了新会话？** 现有聊天不会重新读取配置。
2. **`provider` 是否设置为 `auto` 之外的值？** 如果该字段显示为 `auto`，则该任务仍在使用你的主模型。点击 **Change（更改）** 并选择一个真实的提供商。
3. **提供商是否已认证？** 如果你将 `minimax` 分配给某个任务，但没有 MiniMax API 密钥，该任务会回退到 openrouter 默认设置，并在 `agent.log` 中记录警告。

<a id="i-picked-a-model-but-hermes-switched-providers-on-me"></a>
### 我选了一个模型，但 Hermes 给我切换了提供商

在 OpenRouter（或任何聚合器）上，裸模型名称会首先在聚合器内解析。因此 OpenRouter 上的 `claude-sonnet-4` 会变成 `anthropic/claude-sonnet-4.6`，并保留在你的 OpenRouter 认证中。但如果你在原生 Anthropic 认证下输入了 `claude-sonnet-4`，它则会保持为 `claude-sonnet-4-6`。如果你看到意外的提供商切换，请检查你当前的提供商是否符合预期——选择器始终在对话框顶部显示当前的提供商。

<a id="alternative-methods"></a>
## 其他方法

<a id="cli-slash-command"></a>
### CLI 斜杠命令

在任何 `hermes chat` 会话内部：

```
/model gpt-5.4 --provider openrouter             # 仅当前会话
/model gpt-5.4 --provider openrouter --global    # 同时持久化到 config.yaml
```

`--global` 的作用与仪表盘的 **Change（更改）** 按钮相同，并且会就地切换正在运行的会话。

<a id="custom-aliases"></a>
### 自定义别名

为你经常使用的模型定义简短的名称，然后在 CLI 或任何消息平台上使用 `/model <别名>`：

```yaml
# ~/.hermes/config.yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
```

或者从 shell 中使用（短格式 `provider/model`）：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

然后在聊天中使用 `/model fav` 或 `/model grok`。用户别名会覆盖内置短名称（如 `sonnet`、`kimi`、`opus` 等）。完整参考请参见 [自定义模型别名](/reference/slash-commands#custom-model-aliases)。

<a id="hermes-model-subcommand"></a>
### `hermes model` 子命令

```bash
hermes model            # 交互式提供商 + 模型选择器（切换默认值的规范方式）
```

`hermes model` 会引导你依次选择提供商、进行认证（OAuth 流程会打开浏览器；API 密钥提供商会提示输入密钥），然后从该提供商的精选目录中选择具体模型。选择结果会被写入 `~/.hermes/config.yaml` 中的 `model.provider` 和 `model.model`。

若要列出提供商/模型而不启动选择器，请使用仪表盘或下面的 REST 端点。若要查看 CLI 当前实际将使用什么：`hermes config get model` 和 `hermes status`。
<a id="direct-config-edit"></a>
### 直接配置编辑

编辑 `~/.hermes/config.yaml` 并重启所有读取该文件的进程。完整模式参见[配置参考](./configuration.md)。

<a id="rest-api"></a>
### REST API

仪表盘使用三个端点。适用于编写脚本：

```bash
# 列出已认证的 provider 和精选模型列表
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/options

# 读取当前主模型 + 辅助任务分配
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/auxiliary

# 设置主模型
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"main","provider":"openrouter","model":"anthropic/claude-opus-4.7"}' \
  http://localhost:PORT/api/model/set

# 覆盖单个辅助任务
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"vision","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 为所有辅助任务分配同一个模型
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# 将所有辅助任务重置为自动
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"__reset__","provider":"","model":""}' \
  http://localhost:PORT/api/model/set
```

会话令牌在启动时注入仪表盘的 HTML 中，并在每次服务器重启时轮换。如果你要针对正在运行的仪表盘编写脚本，可以从浏览器开发者工具中获取它（`window.__HERMES_SESSION_TOKEN__`）。
