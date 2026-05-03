---
title: "Here.Now — 将静态站点发布到 {slug}"
sidebar_label: "Here.Now"
description: "将静态站点发布到 {slug}"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Here.Now {#here-now}

将静态站点发布到 &#123;slug&#125;.here.now，并将私有文件存储在云端 Drive 中，用于 Agent 之间的交接。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/here-now` 安装 |
| 路径 | `optional-skills/productivity/here-now` |
| 版本 | `1.15.3` |
| 作者 | here.now |
| 许可证 | MIT |
| 平台 | macos, linux |
| 标签 | `here.now`, `herenow`, `publish`, `deploy`, `hosting`, `static-site`, `web`, `share`, `URL`, `drive`, `storage` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="here-now"></a>
# here.now

here.now 让 Agent 能够发布网站并将私有文件存储在云端 Drive 中。

使用 here.now 完成两项工作：

- **站点**：在 `{slug}.here.now` 发布网站和文件。
- **Drive**：将私有 Agent 文件存储在云端文件夹中。

## 当前文档 {#current-docs}

**在回答关于 here.now 功能、特性或工作流程的问题之前，请先阅读当前文档：**

→ **https://here.now/docs**

请阅读文档：

- 在对话中首次涉及 here.now 相关交互时
- 当用户询问如何执行某项操作时
- 当用户询问哪些功能可用、受支持或被推荐时
- 在告知用户某项功能不受支持之前

需要参考当前文档的主题（不要仅依赖本地技能文本）：

- Drive 和 Drive 共享
- 自定义域名
- 支付和支付门控
- 分叉
- 代理路由和服务变量
- 句柄和链接
- 限制和配额
- SPA 路由
- 错误处理和修复
- 功能可用性

**如果文档和实时 API 行为不一致，请以实时 API 行为为准。**

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于正在进行的操作，优先使用实时 API 行为。

## 要求 {#requirements}

- 必需二进制文件：`curl`、`file`、`jq`
- 可选环境变量：`$HERENOW_API_KEY`
- 可选 Drive 令牌变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭据文件：`~/.herenow/credentials`
- 技能辅助脚本路径：
  - `${HERMES_SKILL_DIR}/scripts/publish.sh` 用于发布站点
  - `${HERMES_SKILL_DIR}/scripts/drive.sh` 用于私有 Drive 存储

## 创建站点 {#create-a-site}

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {文件或目录} --client hermes
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

底层是一个三步流程：创建/更新 -> 上传文件 -> 完成。站点在完成步骤成功之前不会上线。

如果没有 API 密钥，这将创建一个 **匿名站点**，24 小时后过期。
如果保存了 API 密钥，站点将是永久的。

**文件结构：** 对于 HTML 站点，请将 `index.html` 放在要发布的目录的根目录下，而不是子目录中。该目录的内容将成为站点的根目录。例如，发布 `my-site/` 目录，其中包含 `my-site/index.html` —— 不要发布包含 `my-site/` 的父文件夹。
你也可以发布不带任何 HTML 的原始文件。单个文件会获得一个丰富的自动查看器（图片、PDF、视频、音频）。多个文件则会生成一个自动目录列表，包含文件夹导航和图片画廊。

## 更新已有站点 {#update-an-existing-site}

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --slug {slug} --client hermes
```

更新匿名站点时，脚本会自动从 `.herenow/state.json` 加载 `claimToken`。传入 `--claim-token {token}` 可覆盖。

已认证的更新需要保存的 API 密钥。

## 使用 Drive {#use-a-drive}

当用户需要为 Agent 文件提供私有云存储时，使用 Drive：文档、上下文、记忆、计划、资产、媒体、研究、代码，以及任何其他需要持久保存但无需发布为网站的内容。

每个已登录账户都有一个名为 `My Drive` 的默认 Drive。

```bash
DRIVE="${HERMES_SKILL_DIR}/scripts/drive.sh"
bash "$DRIVE" default
bash "$DRIVE" ls "My Drive"
bash "$DRIVE" put "My Drive" notes/today.md --from ./notes/today.md
bash "$DRIVE" cat "My Drive" notes/today.md
bash "$DRIVE" share "My Drive" --perms write --prefix notes/ --ttl 7d
```

使用作用域 Drive 令牌进行 Agent 之间的交接。如果你收到一个 `herenow_drive` 分享块，请使用其 `token` 作为 `Authorization: Bearer &lt;token&gt;` 发送到 `api_base`，当存在 `pathPrefix` 时遵守它，并在写入时保留 ETag。`pathPrefix` 为 `null` 表示完全 Drive 访问权限。如果该技能可用，优先使用 `drive.sh`；否则直接调用列出的 API 操作。

## API 密钥存储 {#api-key-storage}

发布脚本从以下来源读取 API 密钥（第一个匹配项优先）：

1. `--api-key {key}` 标志（仅限 CI/脚本使用——交互式使用中避免）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐用于 Agent）

要存储密钥，请将其写入凭据文件：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要**：收到 API 密钥后，请立即保存——自己运行上面的命令。不要要求用户手动运行。在交互式会话中避免通过 CLI 标志（例如 `--api-key`）传递密钥；凭据文件是首选的存储方式。

切勿将凭据或本地状态文件（`~/.herenow/credentials`、`.herenow/state.json`）提交到版本控制。

## 获取 API 密钥 {#getting-an-api-key}

要从匿名（24 小时）站点升级为永久站点：

1. 询问用户的电子邮件地址。
2. 请求一次性登录码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“请检查收件箱，找到来自 here.now 的登录码，然后粘贴到这里。”
4. 验证代码并获取 API 密钥：

```bash
curl -sS https://here.now/api/auth/agent/verify-code \
  -H "content-type: application/json" \
  -d '{"email":"user@example.com","code":"ABCD-2345"}'
```

5. 自己保存返回的 `apiKey`（不要要求用户执行此操作）：
```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

## 状态文件 {#state-file}

每次创建/更新站点后，脚本会在工作目录中写入 `.herenow/state.json`：

```json
{
  "publishes": {
    "bright-canvas-a7k2": {
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "claimToken": "abc123",
      "claimUrl": "https://here.now/claim?slug=bright-canvas-a7k2&token=abc123",
      "expiresAt": "2026-02-18T01:00:00.000Z"
    }
  }
}
```

在创建或更新站点之前，你可以检查此文件以查找之前的 slug。请将 `.herenow/state.json` 仅视为内部缓存。切勿将此本地文件路径作为 URL 展示，也切勿将其作为认证模式、过期时间或 claim URL 的权威来源。

## 告知用户的内容 {#what-to-tell-the-user}

对于已发布的站点：

- 始终分享当前脚本运行输出的 `siteUrl`。
- 读取并遵循脚本 stderr 中的 `publish_result.*` 行以确定认证模式。
- 当 `publish_result.auth_mode=authenticated` 时：告知用户该站点是**永久**的，并已保存到其账户。无需 claim URL。
- 当 `publish_result.auth_mode=anonymous` 时：告知用户该站点**在 24 小时后过期**。分享 claim URL（如果 `publish_result.claim_url` 非空且以 `https://` 开头），以便他们可以永久保留。警告 claim token 仅返回一次，无法恢复。
- 切勿让用户检查 `.herenow/state.json` 来获取 claim URL 或认证状态。

对于 Drives：

- 不要将 Drive 文件描述为公共 URL。
- 告知用户 Drive 内容是私有的，除非使用作用域 token 共享。
- 当与其他 Agent 共享访问权限时，优先使用具有窄 `pathPrefix` 和短 TTL 的作用域 token。

## publish.sh 选项 {#publish-sh-options}

| 标志                        | 描述                                      |
| --------------------------- | ----------------------------------------- |
| `--slug {slug}`             | 更新现有站点而非创建新站点                |
| `--claim-token {token}`     | 覆盖匿名更新的 claim token                |
| `--title {text}`            | 查看器标题（非 HTML 站点）                |
| `--description {text}`      | 查看器描述                                |
| `--ttl {seconds}`           | 设置过期时间（仅限认证模式）              |
| `--client {name}`           | 用于归属的 Agent 名称（例如 `hermes`）    |
| `--base-url {url}`          | API 基础 URL（默认：`https://here.now`）  |
| `--allow-nonherenow-base-url` | 允许向非默认 `--base-url` 发送认证信息    |
| `--api-key {key}`           | API 密钥覆盖（优先使用凭据文件）          |
| `--spa`                     | 启用 SPA 路由（为未知路径提供 index.html）|
| `--forkable`                | 允许他人 fork 此站点                      |

## 超越 publish.sh {#beyond-publish-sh}

对于 Drive 操作，请使用 `drive.sh` 或 Drive API。对于更广泛的账户和站点管理（删除、元数据、密码、支付、域名、句柄、链接、变量、代理路由、fork、复制等），请参阅当前文档：
→ **https://here.now/docs**

完整文档：https://here.now/docs
