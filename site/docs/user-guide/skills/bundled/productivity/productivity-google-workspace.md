---
title: "Google Workspace — 通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格"
sidebar_label: "Google Workspace"
description: "通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="google-workspace"></a>
# Google Workspace

通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格。

<a id="skill-metadata"></a>
## 技能元信息

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/google-workspace` |
| 版本 | `1.1.0` |
| 作者 | Nous Research |
| 许可协议 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Google`, `Gmail`, `Calendar`, `Drive`, `Sheets`, `Docs`, `Contacts`, `Email`, `OAuth` |
| 相关技能 | [`himalaya`](/user-guide/skills/bundled/email/email-himalaya) |

<a id="reference-full-skill-md"></a>
## 参考：完整版 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。当技能处于活动状态时，Agent 会将其视为指令。
:::

# Google Workspace

通过 Hermes 托管的 OAuth 和一个轻量 CLI 封装，操作 Gmail、日历、云端硬盘、联系人、表格和文档。当 `gws` 已安装时，该技能会将其作为执行后端，以获得更广泛的 Google Workspace 覆盖能力；否则会回退到内置的 Python 客户端实现。

<a id="references"></a>
## 参考资料

- `references/gmail-search-syntax.md` — Gmail 搜索运算符（is:unread, from:, newer_than: 等）

<a id="scripts"></a>
## 脚本

- `scripts/setup.py` — OAuth2 设置（运行一次以完成授权）
- `scripts/google_api.py` — 兼容包装 CLI。当可用时，它优先使用 `gws` 进行操作，同时保留 Hermes 原有的 JSON 输出契约。

<a id="first-time-setup"></a>
## 首次设置

设置过程完全非交互式——你一步步驱动它，以便在 CLI、Telegram、Discord 或任何平台上都能工作。

首先定义一个缩写：

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
```

<a id="step-0-check-if-already-set-up"></a>
### 第 0 步：检查是否已经设置

```bash
$GSETUP --check
```

如果输出 `AUTHENTICATED`，请跳到“使用”部分——设置已经完成。

<a id="step-1-triage-ask-the-user-what-they-need"></a>
### 第 1 步：分类——询问用户需要什么

在启动 OAuth 设置之前，向用户询问**两个问题**：

**问题 1：“你需要哪些 Google 服务？只需要邮件，还是也需要日历/云端硬盘/表格/文档？”**

- **仅邮件** → 他们根本不需要这个技能。请改用 `himalaya` 技能——它通过 Gmail 应用密码（设置 → 安全 → 应用密码）工作，只需 2 分钟即可设置，无需 Google Cloud 项目。加载 himalaya 技能并按照其设置说明操作。

- **邮件 + 日历** → 继续使用此技能，但在认证时使用 `--services email,calendar`，这样同意屏幕只询问他们实际需要的作用域。

- **仅日历/云端硬盘/表格/文档** → 继续使用此技能，并使用较窄的 `--services` 集合，如 `calendar,drive,sheets,docs`。

- **完整的 Workspace 访问** → 继续使用此技能，并使用默认的 `all` 服务集合。

**问题 2：“你的 Google 账户是否使用了高级保护（需要硬件安全密钥才能登录）？如果不确定，很可能没有——这是一项你需要明确注册的功能。”**
- **否 / 不确定** → 标准设置。继续往下看。
- **是** → 他们的 Workspace 管理员必须先将 OAuth 客户端 ID 添加到组织的允许应用列表中，否则第 4 步将无法生效。请提前告知他们。

<a id="step-2-create-oauth-credentials-one-time-5-minutes"></a>
### 第 2 步：创建 OAuth 凭据（一次性操作，约 5 分钟）

告知用户：

> 你需要一个 Google Cloud OAuth 客户端。这是一次性设置：
>
> 1. 创建或选择一个项目：
>    https://console.cloud.google.com/projectselector2/home/dashboard
> 2. 从 API 库启用所需 API：
>    https://console.cloud.google.com/apis/library
>    启用：Gmail API、Google Calendar API、Google Drive API、
>    Google Sheets API、Google Docs API、People API
> 3. 在此处创建 OAuth 客户端：
>    https://console.cloud.google.com/apis/credentials
>    凭据 → 创建凭据 → OAuth 2.0 客户端 ID
> 4. 应用类型："桌面应用" → 创建
> 5. 如果应用仍处于测试状态，请在此处将用户的 Google 账号添加为测试用户：
>    https://console.cloud.google.com/auth/audience
>    受众 → 测试用户 → 添加用户
> 6. 下载 JSON 文件并告诉我文件路径
>
> 重要 Hermes CLI 提示：如果文件路径以 `/` 开头，请不要在 CLI 中仅发送裸路径作为单独消息，因为它可能被误认为是斜杠命令。请将其放在句子中发送，例如：
> `JSON 文件路径是：/home/user/Downloads/client_secret_....json`

一旦他们提供了路径：

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

如果他们粘贴的是原始的客户端 ID / 客户端密钥值而不是文件路径，请自行为他们编写一个有效的桌面 OAuth JSON 文件，将其保存在显式位置（例如 `~/Downloads/hermes-google-client-secret.json`），然后对该文件运行 `--client-secret`。

<a id="step-3-get-authorization-url"></a>
### 第 3 步：获取授权 URL

使用第 1 步中选择的服务集。示例：

```bash
$GSETUP --auth-url --services email,calendar --format json
$GSETUP --auth-url --services calendar,drive,sheets,docs --format json
$GSETUP --auth-url --services all --format json
```

这将返回一个包含 `auth_url` 字段的 JSON，同时将确切的 URL 保存到 `~/.hermes/google_oauth_last_url.txt`。

此步骤的 Agent 规则：
- 提取 `auth_url` 字段，并将该确切 URL 作为单行发送给用户。
- 告知用户，浏览器在批准后很可能会在 `http://localhost:1` 上失败，这是预期行为。
- 告诉他们从浏览器地址栏复制完整的重定向 URL。
- 如果用户遇到 `Error 403: access_denied`，请直接将其引导至 `https://console.cloud.google.com/auth/audience`，让他们将自己添加为测试用户。

<a id="step-4-exchange-the-code"></a>
### 第 4 步：交换代码

用户将粘贴回类似 `http://localhost:1/?code=4/0A...&scope=...` 的 URL 或仅粘贴代码字符串。两者均可。`--auth-url` 步骤会在本地存储一个临时的待处理 OAuth 会话，以便 `--auth-code` 稍后可以完成 PKCE 交换，即使在无头系统上也是如此：

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED" --format json
```

如果 `--auth-code` 因代码过期、已被使用或来自较旧的浏览器标签页而失败，现在会返回一个新的 `fresh_auth_url`。在这种情况下，请立即将新 URL 发送给用户，并让他们仅使用最新的浏览器重定向重试。
<a id="step-5-verify"></a>
### 步骤 5：验证

```bash
$GSETUP --check
```

应输出 `AUTHENTICATED`。设置完成——此后 token 会自动刷新。

<a id="notes"></a>
### 注意事项

- Token 存储在 `~/.hermes/google_token.json`，并会自动刷新。
- 临时的 OAuth 会话状态/验证器会存储在 `~/.hermes/google_oauth_pending.json`，直到授权交换完成。
- 如果安装了 `gws`，`google_api.py` 会指向同一个 `~/.hermes/google_token.json` 凭据文件。用户无需再单独运行 `gws auth login` 流程。
- 撤销授权：`$GSETUP --revoke`

<a id="usage"></a>
## 使用

所有命令都通过 API 脚本执行。将 `GAPI` 设为快捷方式：

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

<a id="gmail"></a>
### Gmail

```bash
# 搜索（返回 JSON 数组，包含 id、from、subject、date、snippet）
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# 阅读完整邮件（返回 JSON，包含正文文本）
$GAPI gmail get MESSAGE_ID

# 发送
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "Message text"

# 回复（自动关联线程并设置 In-Reply-To 头）
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail reply MESSAGE_ID --from '"Support Bot" <user@example.com>' --body "Thanks"

# 标签
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

<a id="calendar"></a>
### 日历

```bash
# 列出事件（默认接下来 7 天）
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# 创建事件（ISO 8601 格式，需要时区）
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# 删除事件
$GAPI calendar delete EVENT_ID
```

<a id="drive"></a>
### Drive

```bash
# 搜索已有文件
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# 获取单个文件的元数据
$GAPI drive get FILE_ID

# 上传本地文件（自动检测 MIME 类型）
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# 下载（二进制文件直接下载；Google 原生文件会导出为合理的默认格式——文档→pdf、表格→csv、演示文稿→pdf、绘图→png）
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# 创建文件夹
$GAPI drive create-folder "Reports"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# 分享
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # 任何拥有链接的人
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# 删除——默认放入回收站（可恢复）。使用 --permanent 可跳过回收站。
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent
```
<a id="contacts"></a>
### 联系人

```bash
$GAPI contacts list --max 20
```

<a id="sheets"></a>
### 电子表格

```bash
# 创建一个新电子表格
$GAPI sheets create --title "Q4 Budget"
$GAPI sheets create --title "Inventory" --sheet-name "Stock"

# 读取
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# 写入
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# 追加行
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

<a id="docs"></a>
### 文档

```bash
# 读取
$GAPI docs get DOC_ID

# 创建新文档（可选择是否附带正文）
$GAPI docs create --title "Meeting Notes"
$GAPI docs create --title "Draft" --body "First paragraph..."

# 向现有文档末尾追加文本
$GAPI docs append DOC_ID --text "Additional content to append"
```

<a id="output-format"></a>
## 输出格式

所有命令均返回 JSON。可使用 `jq` 解析或直接读取。关键字段：

- **Gmail 搜索**：`[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail 获取**：`{id, threadId, from, to, subject, date, labels, body}`
- **Gmail 发送/回复**：`{status: "sent", id, threadId}`
- **日历列表**：`[{id, summary, start, end, location, description, htmlLink}]`
- **日历创建**：`{status: "created", id, summary, htmlLink}`
- **Drive 搜索**：`[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive 获取**：`{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive 上传**：`{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive 下载**：`{status: "downloaded", id, name, path, mimeType}`
- **Drive 创建文件夹**：`{status: "created", id, name, webViewLink}`
- **Drive 分享**：`{status: "shared", permissionId, fileId, role, type}`
- **Drive 删除**：`{status: "trashed" | "deleted", fileId, permanent}`
- **联系人列表**：`[{name, emails: [...], phones: [...]}]`
- **Sheets 获取**：`[[cell, cell, ...], ...]`
- **Sheets 创建**：`{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs 创建**：`{status: "created", documentId, title, url}`
- **Docs 追加**：`{status: "appended", documentId, inserted_at, characters}`

<a id="rules"></a>
## 规则

1. **除非先与用户确认，否则绝不能发送邮件、创建/删除日历事件、删除 Drive 文件、分享文件或修改文档/电子表格。** 展示将要执行的操作（收件人、文件 ID、内容、分享角色）并请求批准。对于 `drive delete`，优先使用默认的回收站（可撤销），而非 `--permanent`。
2. **首次使用前检查身份验证**——运行 `setup.py --check`。如果失败，引导用户完成设置。
3. **复杂查询请参考 Gmail 搜索语法说明**——使用 `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")` 加载。
4. **日历时间必须包含时区**——始终使用带偏移量的 ISO 8601（例如 `2026-03-01T10:00:00-06:00`）或 UTC（`Z`）。
5. **遵守速率限制**——避免连续快速调用 API。尽可能批量读取。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方法 |
|------|----------|
| `NOT_AUTHENTICATED` | 执行上述设置步骤 2-5 |
| `REFRESH_FAILED` | 令牌已撤销或过期——重新执行步骤 3-5 |
| `HttpError 403: Insufficient Permission` | 缺少 API 作用域——运行 `$GSETUP --revoke`，然后重新执行步骤 3-5 |
| `AUTHENTICATED (partial)` 或“Token missing scopes” | 新的写入能力（Drive 写入/删除、Docs 创建/编辑）需要重新授权。运行 `$GSETUP --revoke`，然后重新执行步骤 3-5 以授予升级后的作用域 |
| `HttpError 403: Access Not Configured` | API 未启用——用户需要在 Google Cloud Console 中启用它 |
| `ModuleNotFoundError` | 运行 `$GSETUP --install-deps` |
| 高级保护阻止身份验证 | 工作区管理员必须将 OAuth 客户端 ID 加入白名单 |
<a id="revoking-access"></a>
## 撤销访问权限

```bash
$GSETUP --revoke
```
