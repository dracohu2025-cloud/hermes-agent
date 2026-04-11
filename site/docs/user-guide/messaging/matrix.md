---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 集成了 Matrix，这是一种开放的联邦式消息协议。Matrix 允许你运行自己的家庭服务器（homeserver）或使用像 matrix.org 这样的公共服务器——无论哪种方式，你都能掌控自己的通信。该机器人通过 `mautrix` Python SDK 进行连接，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图像、音频、视频以及可选的端到端加密（E2EE）。

Hermes 适用于任何 Matrix 家庭服务器——Synapse、Conduit、Dendrite 或 matrix.org。

在设置之前，这里是大多数人最关心的问题：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 上下文 | 行为 |
|---------|----------|
| **私聊 (DMs)** | Hermes 会回复每一条消息。无需 `@mention`。每个私聊都有其独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可在私聊中被 `@mention` 时开启一个线程。 |
| **群聊 (Rooms)** | 默认情况下，Hermes 需要 `@mention` 才会回复。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 以开启自由回复模式。房间邀请会自动接受。 |
| **线程 (Threads)** | Hermes 支持 Matrix 线程 (MSC3440)。如果你在线程中回复，Hermes 会将线程上下文与主房间时间线隔离开来。机器人已经参与的线程不需要提及（mention）。 |
| **自动线程 (Auto-threading)** | 默认情况下，Hermes 会为它在房间中回复的每条消息自动创建一个线程。这可以保持对话的独立性。设置 `MATRIX_AUTO_THREAD=false` 可禁用此功能。 |
| **多用户共享房间** | 默认情况下，Hermes 会在房间内为每个用户隔离会话历史。除非你明确禁用，否则在同一个房间里交谈的两个人不会共享同一个对话记录。 |

:::tip
机器人被邀请时会自动加入房间。只需将机器人的 Matrix 用户邀请到任何房间，它就会加入并开始响应。
:::

### Matrix 中的会话模型

默认情况下：

- 每个私聊都有自己的会话
- 每个线程都有自己的会话命名空间
- 共享房间中的每个用户在房间内都有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间很有用，但也意味着：

- 用户共享上下文增长和 Token 成本
- 某个人长时间使用工具的任务可能会占用其他所有人的上下文
- 某个人正在进行的任务可能会中断同一房间内另一个人的后续操作

### 提及（Mention）与线程配置

你可以通过环境变量或 `config.yaml` 配置提及和自动线程行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @mention（默认：true）
  free_response_rooms:            # 免除提及要求的房间
    - "!abc123:matrix.org"
  auto_thread: true               # 自动为回复创建线程（默认：true）
  dm_mention_threads: false       # 在私聊中被 @mentioned 时创建线程（默认：false）
```

或者通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
```

:::note
如果你是从没有 `MATRIX_REQUIRE_MENTION` 的版本升级而来，机器人之前会回复房间内的所有消息。要保持该行为，请设置 `MATRIX_REQUIRE_MENTION=false`。
:::

本指南将引导你完成整个设置过程——从创建机器人账号到发送第一条消息。

## 第 1 步：创建机器人账号

你需要一个 Matrix 用户账号供机器人使用。有几种方法可以做到这一点：

### 选项 A：在你的家庭服务器上注册（推荐）

如果你运行自己的家庭服务器（Synapse、Conduit、Dendrite）：

1. 使用管理 API 或注册工具创建一个新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，如 `hermes` ——完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共家庭服务器

1. 前往 [Element Web](https://app.element.io) 并创建一个新账号。
2. 为你的机器人选择一个用户名（例如 `hermes-bot`）。

### 选项 C：使用你自己的账号

你也可以将 Hermes 作为你自己的用户运行。这意味着机器人会以你的身份发布消息——这对个人助理很有用。

## 第 2 步：获取访问令牌（Access Token）

Hermes 需要一个访问令牌来向家庭服务器进行身份验证。你有两个选择：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账号登录 [Element](https://app.element.io)。
2. 前往 **设置 (Settings)** → **帮助与关于 (Help & About)**。
3. 向下滚动并展开 **高级 (Advanced)** ——访问令牌会显示在那里。
4. **立即复制它。**

**通过 API：**

```bash
curl -X POST https://your-server/_matrix/client/v3/login \
  -H "Content-Type: application/json" \
  -d '{
    "type": "m.login.password",
    "user": "@hermes:your-server.org",
    "password": "your-password"
  }'
```

响应中包含一个 `access_token` 字段——复制它。

:::warning[妥善保管你的访问令牌]
访问令牌拥有对机器人 Matrix 账号的完全访问权限。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

你可以直接提供机器人的用户 ID 和密码，而不是提供访问令牌。Hermes 会在启动时自动登录。这种方法更简单，但意味着密码会存储在你的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 第 3 步：查找你的 Matrix 用户 ID

Hermes Agent 使用你的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 遵循 `@username:server` 的格式。

查找你的 ID：

1. 打开 [Element](https://app.element.io)（或你首选的 Matrix 客户端）。
2. 点击你的头像 → **设置 (Settings)**。
3. 你的用户 ID 显示在个人资料顶部（例如 `@alice:matrix.org`）。

:::tip
Matrix 用户 ID 总是以 `@` 开头，并包含一个 `:`，后面跟着服务器名称。例如：`@alice:matrix.org`，`@bob:your-server.com`。
:::

## 第 4 步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Matrix**，然后根据要求提供你的家庭服务器 URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略，将从令牌中自动检测）
# MATRIX_USER_ID=@hermes:matrix.example.org

# 安全性：限制谁可以与机器人交互
MATRIX_ALLOWED_USERS=@alice:matrix.example.org

# 多个允许的用户（逗号分隔）
# MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
```

**使用密码登录：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_USER_ID=@hermes:matrix.example.org
MATRIX_PASSWORD=***

# 安全性
MATRIX_ALLOWED_USERS=@alice:matrix.example.org
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 会在共享房间内保持每个参与者的上下文独立。

### 启动网关

配置完成后，启动 Matrix 网关：

```bash
hermes gateway
```

机器人应该会在几秒钟内连接到你的家庭服务器并开始同步。发送一条消息——无论是私聊还是在它已加入的房间中——进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行，或作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 端到端加密 (E2EE)

Hermes 支持 Matrix 端到端加密，因此你可以在加密房间中与你的机器人聊天。
### 要求

E2EE 需要带有加密扩展的 `mautrix` 库以及 `libolm` C 库：

```bash
# 安装支持 E2EE 的 mautrix
pip install 'mautrix[encryption]'

# 或者安装 hermes 扩展
pip install 'hermes-agent[matrix]'
```

你还需要在系统中安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用 E2EE

在你的 `~/.hermes/.env` 中添加：

```bash
MATRIX_ENCRYPTION=true
```

启用 E2EE 后，Hermes 会：

- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/` 中（旧版本安装路径为：`~/.hermes/matrix/store/`）
- 在首次连接时上传设备密钥
- 自动解密收到的消息并加密发出的消息
- 在受邀时自动加入加密房间

:::warning
如果你删除了 `~/.hermes/platforms/matrix/store/` 目录，机器人将丢失其加密密钥。你需要再次在 Matrix 客户端中验证该设备。如果你想保留加密会话，请备份此目录。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人会自动回退到普通（未加密）客户端模式。你会在日志中看到警告。
:::

## 主房间 (Home Room)

你可以指定一个“主房间”，让机器人在此发送主动消息（例如 cron 任务输出、提醒和通知）。有两种设置方式：

### 使用斜杠命令

在机器人所在的任何 Matrix 房间中输入 `/sethome`。该房间即成为主房间。

### 手动配置

在你的 `~/.hermes/.env` 中添加：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

:::tip
查找房间 ID 的方法：在 Element 中，进入房间 → **设置 (Settings)** → **高级 (Advanced)** → 即可看到 **内部房间 ID (Internal room ID)**（以 `!` 开头）。
:::

## 故障排除

### 机器人对消息没有响应

**原因**：机器人未加入房间，或者 `MATRIX_ALLOWED_USERS` 中未包含你的用户 ID。

**解决方法**：邀请机器人进入房间——它会自动加入。确认你的用户 ID 已包含在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重启网关。

### 启动时出现 "Failed to authenticate" / "whoami failed"

**原因**：访问令牌或家庭服务器 (homeserver) URL 不正确。

**解决方法**：确认 `MATRIX_HOMESERVER` 指向你的家庭服务器（包含 `https://`，末尾不要加斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效——尝试使用 curl 进行测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回了你的用户信息，则令牌有效。如果返回错误，请生成一个新的令牌。

### 出现 "mautrix not installed" 错误

**原因**：未安装 `mautrix` Python 包。

**解决方法**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或者使用 Hermes 扩展安装：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误 / "could not decrypt event"

**原因**：缺少加密密钥、未安装 `libolm` 或机器人的设备未被信任。

**解决方法**：
1. 确认系统中已安装 `libolm`（参见上文的 E2EE 部分）。
2. 确保 `.env` 中已设置 `MATRIX_ENCRYPTION=true`。
3. 在你的 Matrix 客户端 (Element) 中，进入机器人的个人资料 → **会话 (Sessions)** → 验证/信任机器人的设备。
4. 如果机器人刚加入加密房间，它只能解密加入*之后*发送的消息。旧消息无法访问。

### 同步问题 / 机器人滞后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者家庭服务器响应缓慢。

**解决方法**：同步循环在出错时会自动每 5 秒重试一次。检查 Hermes 日志中是否有与同步相关的警告。如果机器人持续滞后，请确保你的家庭服务器资源充足。

### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出的错误消息。常见问题：家庭服务器 URL 错误、访问令牌过期、家庭服务器无法访问。

### "User not allowed" / 机器人忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `MATRIX_ALLOWED_USERS`，然后重启网关。请使用完整的 `@user:server` 格式。

## 安全性

:::warning
务必设置 `MATRIX_ALLOWED_USERS` 以限制谁可以与机器人交互。如果不设置，作为安全措施，网关默认会拒绝所有用户。仅添加你信任的人的用户 ID——授权用户拥有 Agent 功能的完全访问权限，包括工具使用和系统访问权限。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。

## 注意事项

- **任意家庭服务器**：适用于 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 家庭服务器。不需要特定的家庭服务器软件。
- **联邦 (Federation)**：如果你在联邦家庭服务器上，机器人可以与来自其他服务器的用户通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 即可。
- **自动加入**：机器人会自动接受房间邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图像、音频、视频和文件附件。媒体通过 Matrix 内容存储库 API 上传到你的家庭服务器。
- **原生语音消息 (MSC3245)**：Matrix 适配器会自动为发出的语音消息添加 `org.matrix.msc3245.voice` 标记。这意味着 TTS 响应和语音音频在 Element 及其他支持 MSC3245 的客户端中会渲染为**原生语音气泡**，而不是通用的音频文件附件。带有 MSC3245 标记的传入语音消息也会被正确识别并路由到语音转文字转录。无需任何配置，此功能自动生效。
