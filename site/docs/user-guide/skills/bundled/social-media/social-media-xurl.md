---
title: "Xurl — 通过 xurl CLI 使用 X/Twitter：发帖、搜索、私信、媒体、v2 API"
sidebar_label: "Xurl"
description: "通过 xurl CLI 使用 X/Twitter：发帖、搜索、私信、媒体、v2 API"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Xurl {#xurl}

通过 xurl CLI 使用 X/Twitter：发帖、搜索、私信、媒体、v2 API。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/social-media/xurl` |
| 版本 | `1.1.1` |
| 作者 | xdevplatform + openclaw + Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `twitter`, `x`, `social-media`, `xurl`, `official-api` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# xurl — 通过官方 CLI 使用 X (Twitter) API {#xurl-x-twitter-api-via-the-official-cli}

`xurl` 是 X 开发者平台的官方 CLI，用于调用 X API。它支持常用操作的快捷命令，以及针对任意 v2 端点的原始 curl 风格访问。所有命令均以 JSON 格式输出到标准输出。

使用此技能可以：
- 发帖、回复、引用、删除帖子
- 搜索帖子、读取时间线/提及
- 点赞、转推、收藏
- 关注、取消关注、屏蔽、静音
- 私信
- 媒体上传（图片和视频）
- 原始访问任意 X API v2 端点
- 多应用/多账户工作流

此技能取代了旧的 `xitter` 技能（该技能封装了一个第三方 Python CLI）。`xurl` 由 X 开发者平台团队维护，支持 OAuth 2.0 PKCE 自动刷新，覆盖了更广泛的 API 范围。

---

## 密钥安全（必须遵守） {#secret-safety-mandatory}

在 Agent/LLM 会话中操作时的关键规则：

- **切勿**读取、打印、解析、总结、上传或发送 `~/.xurl` 到 LLM 上下文。
- **切勿**要求用户将凭据/令牌粘贴到聊天中。
- 用户必须在其自己的机器上手动填写 `~/.xurl` 中的密钥。
- **切勿**在 Agent 会话中推荐或执行带有内联密钥的认证命令。
- **切勿**在 Agent 会话中使用 `--verbose` / `-v` —— 这可能会暴露认证头/令牌。
- 要验证凭据是否存在，仅可使用：`xurl auth status`。

Agent 命令中禁止使用的标志（它们接受内联密钥）：
`--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`

应用凭据注册和凭据轮换必须由用户在 Agent 会话之外手动完成。注册凭据后，用户使用 `xurl auth oauth2` 进行认证——同样在 Agent 会话之外进行。令牌以 YAML 格式持久化到 `~/.xurl`。每个应用都有独立的令牌。OAuth 2.0 令牌会自动刷新。

---

## 安装 {#installation}

选择其中一种方法。在 Linux 上，shell 脚本或 `go install` 是最简单的。

```bash
# Shell 脚本（安装到 ~/.local/bin，无需 sudo，适用于 Linux 和 macOS）
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash

# Homebrew（macOS）
brew install --cask xdevplatform/tap/xurl

# npm
npm install -g @xdevplatform/xurl

# Go
go install github.com/xdevplatform/xurl@latest
```
验证：

```bash
xurl --help
xurl auth status
```

如果 `xurl` 已安装，但 `auth status` 显示没有应用或令牌，用户需要手动完成身份验证——请参见下一节。

---

## 一次性用户设置（用户在 Agent 外部运行这些步骤） {#one-time-user-setup-user-runs-these-outside-the-agent}

这些步骤必须由用户直接执行，**而不是**由 Agent 执行，因为它们涉及粘贴密钥。请将用户引导至本区块，不要替他们执行。

1. 在 https://developer.x.com/en/portal/dashboard 创建或打开一个应用
2. 将重定向 URI 设置为 `http://localhost:8080/callback`
3. 复制应用的客户端 ID 和客户端密钥
4. 在本地注册应用（用户运行此命令）：
   ```bash
   xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
   ```
5. 进行身份验证（指定 `--app` 将令牌绑定到你的应用）：
   ```bash
   xurl auth oauth2 --app my-app
   ```
   （这会打开浏览器进行 OAuth 2.0 PKCE 流程。）

   如果 X 在 OAuth 后的 `/2/users/me` 查询中返回 `UsernameNotFound` 错误或 403，请显式传递你的用户名（xurl v1.1.0+）：
   ```bash
   xurl auth oauth2 --app my-app YOUR_USERNAME
   ```
   这会将令牌绑定到你的用户名，并跳过有问题的 `/2/users/me` 调用。
6. 将该应用设为默认，以便所有命令都使用它：
   ```bash
   xurl auth default my-app
   ```
7. 验证：
   ```bash
   xurl auth status
   xurl whoami
   ```

完成这些后，Agent 就可以使用下面的任何命令，无需进一步设置。OAuth 2.0 令牌会自动刷新。

> **常见陷阱：** 如果在 `xurl auth oauth2` 中省略了 `--app my-app`，OAuth 令牌会保存到内置的 `default` 应用配置文件中——该配置文件没有客户端 ID 或客户端密钥。即使 OAuth 流程看似成功，命令也会因身份验证错误而失败。如果遇到这种情况，请重新运行 `xurl auth oauth2 --app my-app` 和 `xurl auth default my-app`。

---

## 快速参考 {#quick-reference}

| 操作 | 命令 |
| --- | --- |
| 发布 | `xurl post "Hello world!"` |
| 回复 | `xurl reply POST_ID "Nice post!"` |
| 引用 | `xurl quote POST_ID "My take"` |
| 删除帖子 | `xurl delete POST_ID` |
| 阅读帖子 | `xurl read POST_ID` |
| 搜索帖子 | `xurl search "QUERY" -n 10` |
| 我是谁 | `xurl whoami` |
| 查找用户 | `xurl user @handle` |
| 首页时间线 | `xurl timeline -n 20` |
| 提及 | `xurl mentions -n 10` |
| 点赞 / 取消点赞 | `xurl like POST_ID` / `xurl unlike POST_ID` |
| 转发 / 取消转发 | `xurl repost POST_ID` / `xurl unrepost POST_ID` |
| 收藏 / 取消收藏 | `xurl bookmark POST_ID` / `xurl unbookmark POST_ID` |
| 列出收藏 / 点赞 | `xurl bookmarks -n 10` / `xurl likes -n 10` |
| 关注 / 取消关注 | `xurl follow @handle` / `xurl unfollow @handle` |
| 正在关注 / 粉丝 | `xurl following -n 20` / `xurl followers -n 20` |
| 屏蔽 / 取消屏蔽 | `xurl block @handle` / `xurl unblock @handle` |
| 静音 / 取消静音 | `xurl mute @handle` / `xurl unmute @handle` |
| 发送私信 | `xurl dm @handle "message"` |
| 列出私信 | `xurl dms -n 10` |
| 上传媒体 | `xurl media upload path/to/file.mp4` |
| 媒体状态 | `xurl media status MEDIA_ID` |
| 列出应用 | `xurl auth apps list` |
| 移除应用 | `xurl auth apps remove NAME` |
| 设置默认应用 | `xurl auth default APP_NAME [USERNAME]` |
| 按请求指定应用 | `xurl --app NAME /2/users/me` |
| 身份验证状态 | `xurl auth status` |
注意：
- `POST_ID` 也接受完整 URL（例如 `https://x.com/user/status/1234567890`）—— xurl 会自动提取 ID。
- 用户名可以带或不带开头的 `@`。

---

## 命令详情 {#command-details}

### 发帖 {#posting}

```bash
xurl post "Hello world!"
xurl post "Check this out" --media-id MEDIA_ID
xurl post "Thread pics" --media-id 111 --media-id 222

xurl reply 1234567890 "Great point!"
xurl reply https://x.com/user/status/1234567890 "Agreed!"
xurl reply 1234567890 "Look at this" --media-id MEDIA_ID

xurl quote 1234567890 "Adding my thoughts"
xurl delete 1234567890
```

### 阅读与搜索 {#reading-search}

```bash
xurl read 1234567890
xurl read https://x.com/user/status/1234567890

xurl search "golang"
xurl search "from:elonmusk" -n 20
xurl search "#buildinpublic lang:en" -n 15
```

### 用户、时间线、提及 {#users-timeline-mentions}

```bash
xurl whoami
xurl user elonmusk
xurl user @XDevelopers

xurl timeline -n 25
xurl mentions -n 20
```

### 互动 {#engagement}

```bash
xurl like 1234567890
xurl unlike 1234567890

xurl repost 1234567890
xurl unrepost 1234567890

xurl bookmark 1234567890
xurl unbookmark 1234567890

xurl bookmarks -n 20
xurl likes -n 20
```

### 社交关系图 {#social-graph}

```bash
xurl follow @XDevelopers
xurl unfollow @XDevelopers

xurl following -n 50
xurl followers -n 50

# 查看其他用户的社交关系图
xurl following --of elonmusk -n 20
xurl followers --of elonmusk -n 20

xurl block @spammer
xurl unblock @spammer
xurl mute @annoying
xurl unmute @annoying
```

### 私信 {#direct-messages}

```bash
xurl dm @someuser "Hey, saw your post!"
xurl dms -n 25
```

### 媒体上传 {#media-upload}

```bash
# 自动检测类型
xurl media upload photo.jpg
xurl media upload video.mp4

# 显式指定类型/分类
xurl media upload --media-type image/jpeg --category tweet_image photo.jpg

# 视频需要服务端处理——检查状态（或轮询）
xurl media status MEDIA_ID
xurl media status --wait MEDIA_ID

# 完整工作流
xurl media upload meme.png                  # 返回媒体 ID
xurl post "lol" --media-id MEDIA_ID
```

---

## 原始 API 访问 {#raw-api-access}

以上快捷方式覆盖了常见操作。对于其他需求，可以使用原始 curl 风格模式直接调用任意 X API v2 端点：

```bash
# GET
xurl /2/users/me

# POST 带 JSON 请求体
xurl -X POST /2/tweets -d '{"text":"Hello world!"}'

# DELETE / PUT / PATCH
xurl -X DELETE /2/tweets/1234567890

# 自定义请求头
xurl -H "Content-Type: application/json" /2/some/endpoint

# 强制流式响应
xurl -s /2/tweets/search/stream

# 完整 URL 同样支持
xurl https://api.x.com/2/users/me
```

---

## 全局标志 {#global-flags}

| 标志 | 简写 | 说明 |
| --- | --- | --- |
| `--app` | | 使用指定的已注册应用（覆盖默认值） |
| `--auth` | | 强制指定认证类型：`oauth1`、`oauth2` 或 `app` |
| `--username` | `-u` | 使用哪个 OAuth2 账户（如果存在多个） |
| `--verbose` | `-v` | **Agent 会话中禁止使用**——会泄露认证头信息 |
| `--trace` | `-t` | 添加 `X-B3-Flags: 1` 追踪头 |

---

## 流式处理 {#streaming}

流式端点会自动检测。已知的包括：

- `/2/tweets/search/stream`
- `/2/tweets/sample/stream`
- `/2/tweets/sample10/stream`
使用 `-s` 强制在任何端点上启用流式输出。

---

## 输出格式

所有命令均以 JSON 格式输出到标准输出。结构遵循 X API v2：

```json
{ "data": { "id": "1234567890", "text": "Hello world!" } }
```

错误也是 JSON 格式：

```json
{ "errors": [ { "message": "Not authorized", "code": 403 } ] }
```

---

## 常见工作流

### 发布带图片的帖子
```bash
xurl media upload photo.jpg
xurl post "看看这张照片！" --media-id MEDIA_ID
```

### 回复一条对话
```bash
xurl read https://x.com/user/status/1234567890
xurl reply 123

## 归属说明

- 上游 CLI：https://github.com/xdevplatform/xurl（X 开发者平台团队，Chris Park 等人）
- 上游 Agent 技能：https://github.com/openclaw/openclaw/blob/main/skills/xurl/SKILL.md
- Hermes 适配：按照 Hermes 技能规范重新格式化；安全防护措施逐字保留。
