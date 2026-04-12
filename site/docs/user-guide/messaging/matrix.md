---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 集成了 Matrix，这是一个开放、联邦式的消息协议。Matrix 允许你运行自己的家庭服务器，或使用像 matrix.org 这样的公共服务器——无论哪种方式，你都能控制自己的通信。机器人通过 `mautrix` Python SDK 连接，通过 Hermes Agent 的处理管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片、音频、视频以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix 家庭服务器配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在开始设置之前，这里是你可能最想知道的部分：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **私聊** | Hermes 会响应每条消息。不需要 `@提及`。每个私聊都有其独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可在私聊中 `@提及` 机器人时创建一个线程。 |
| **群聊** | 默认情况下，Hermes 需要 `@提及` 才会响应。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 以创建自由响应房间。房间邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果你在某个线程中回复，Hermes 会将该线程的上下文与主房间时间线隔离开。机器人已参与过的线程不需要提及。 |
| **自动创建线程** | 默认情况下，Hermes 会为它在房间中响应的每条消息自动创建一个线程。这可以保持对话的隔离性。设置 `MATRIX_AUTO_THREAD=false` 来禁用此功能。 |
| **多用户共享房间** | 默认情况下，Hermes 会在房间内为每个用户隔离会话历史。两个人在同一个房间内交谈不会共享一个对话记录，除非你明确禁用此功能。 |

:::tip
机器人被邀请时会自动加入房间。只需将机器人的 Matrix 用户邀请到任何房间，它就会加入并开始响应。
:::

### Matrix 中的会话模型

默认情况下：
- 每个私聊都有其独立的会话
- 每个线程都有其独立的会话命名空间
- 共享房间中的每个用户在该房间内都有其独立的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：
- 用户共享上下文增长和令牌成本
- 一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
- 一个人正在运行的任务可能会中断另一个人在同一房间内的后续操作

### 提及和线程配置

你可以通过环境变量或 `config.yaml` 配置提及和自动创建线程的行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @提及（默认：true）
  free_response_rooms:            # 免除提及要求的房间
    - "!abc123:matrix.org"
  auto_thread: true               # 为响应自动创建线程（默认：true）
  dm_mention_threads: false       # 在私聊中被 @提及 时创建线程（默认：false）
```

或通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
```

:::note
如果你是从没有 `MATRIX_REQUIRE_MENTION` 的版本升级而来，机器人之前会响应房间中的所有消息。要保留该行为，请设置 `MATRIX_REQUIRE_MENTION=false`。
:::

本指南将引导你完成完整的设置过程——从创建机器人账户到发送第一条消息。

## 步骤 1：创建机器人账户

你需要为机器人创建一个 Matrix 用户账户。有几种方法可以实现：

### 选项 A：在你的家庭服务器上注册（推荐）

如果你运行自己的家庭服务器（Synapse、Conduit、Dendrite）：

1. 使用管理员 API 或注册工具创建新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，例如 `hermes` —— 完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共家庭服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为你的机器人选择一个用户名（例如，`hermes-bot`）。

### 选项 C：使用你自己的账户

你也可以将 Hermes 作为你自己的用户运行。这意味着机器人将以你的身份发布消息——对于个人助手很有用。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来向家庭服务器进行身份验证。你有两个选择：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方式：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 转到 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级** —— 访问令牌显示在那里。
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

响应中包含一个 `access_token` 字段 —— 复制它。

:::warning[妥善保管你的访问令牌]
访问令牌授予对机器人 Matrix 账户的完全访问权限。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

你可以不提供访问令牌，而是给 Hermes 机器人的用户 ID 和密码。Hermes 将在启动时自动登录。这更简单，但意味着密码会存储在你的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 步骤 3：找到你的 Matrix 用户 ID

Hermes Agent 使用你的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 遵循格式 `@用户名:服务器`。

要找到你的用户 ID：

1. 打开 [Element](https://app.element.io)（或你首选的 Matrix 客户端）。
2. 点击你的头像 → **设置**。
3. 你的用户 ID 显示在个人资料顶部（例如，`@alice:matrix.org`）。

:::tip
Matrix 用户 ID 总是以 `@` 开头，并包含一个 `:` 后跟服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

当提示时选择 **Matrix**，然后按要求提供你的家庭服务器 URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略，将从令牌自动检测）
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

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享房间内保持每个参与者的上下文隔离

### 启动网关

配置完成后，启动 Matrix 网关：

```bash
hermes gateway
```

机器人应该连接到你的家庭服务器并在几秒钟内开始同步。发送一条消息给它——无论是私聊还是它已加入的房间——进行测试。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 端到端加密（E2EE）

Hermes 支持 Matrix 端到端加密，因此你可以在加密房间中与你的机器人聊天。
### 要求

端到端加密需要带有加密额外功能的 `mautrix` 库以及 `libolm` C 库：

```bash
# 安装支持 E2EE 的 mautrix
pip install 'mautrix[encryption]'

# 或者通过 hermes extras 安装
pip install 'hermes-agent[matrix]'
```

你还需要在系统上安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用 E2EE

添加到你的 `~/.hermes/.env` 文件中：

```bash
MATRIX_ENCRYPTION=true
```

启用 E2EE 后，Hermes：

- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/`（旧版本安装：`~/.hermes/matrix/store/`）
- 在首次连接时上传设备密钥
- 自动解密接收到的消息并加密发送的消息
- 在被邀请时自动加入加密房间

### 交叉签名验证（推荐）

如果你的 Matrix 账户启用了交叉签名（Element 中的默认设置），请设置恢复密钥，以便 bot 在启动时能自行签署其设备。如果没有这个，其他 Matrix 客户端在设备密钥轮换后可能会拒绝与 bot 共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥放在这里
```

**在哪里找到它**：在 Element 中，转到 **设置** → **安全与隐私** → **加密** → 你的恢复密钥（也称为“安全密钥”）。这是你首次设置交叉签名时被要求保存的密钥。

每次启动时，如果设置了 `MATRIX_RECOVERY_KEY`，Hermes 会从家庭服务器的安全秘密存储中导入交叉签名密钥，并签署当前设备。这是幂等的，可以永久安全地启用。

:::warning
如果你删除了 `~/.hermes/platforms/matrix/store/` 目录，bot 将丢失其加密密钥。你将需要在你的 Matrix 客户端中重新验证该设备。如果你想保留加密会话，请备份此目录。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，bot 会自动回退到普通（未加密）客户端。你会在日志中看到警告。
:::

## 主房间

你可以指定一个“主房间”，bot 会向该房间发送主动消息（例如 cron 作业输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在 bot 所在的任何 Matrix 房间中键入 `/sethome`。该房间将成为主房间。

### 手动配置

将此添加到你的 `~/.hermes/.env` 文件中：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

:::tip
要查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → **内部房间 ID** 显示在那里（以 `!` 开头）。
:::

## 故障排除

### Bot 不响应消息

**原因**：Bot 尚未加入房间，或者 `MATRIX_ALLOWED_USERS` 未包含你的用户 ID。

**解决方法**：邀请 bot 加入房间 — 它会在被邀请时自动加入。确认你的用户 ID 在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重启网关。

### 启动时出现“身份验证失败” / “whoami 失败”

**原因**：访问令牌或家庭服务器 URL 不正确。

**解决方法**：验证 `MATRIX_HOMESERVER` 指向你的家庭服务器（包含 `https://`，末尾没有斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效 — 使用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回你的用户信息，则令牌有效。如果返回错误，请生成一个新令牌。

### “mautrix 未安装”错误

**原因**：未安装 `mautrix` Python 包。

**解决方法**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或者通过 Hermes extras 安装：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误 / “无法解密事件”

**原因**：缺少加密密钥、未安装 `libolm`，或者 bot 的设备不受信任。

**解决方法**：
1. 验证系统上已安装 `libolm`（参见上面的 E2EE 部分）。
2. 确保在你的 `.env` 文件中设置了 `MATRIX_ENCRYPTION=true`。
3. 在你的 Matrix 客户端（Element）中，转到 bot 的个人资料 -> 会话 -> 验证/信任 bot 的设备。
4. 如果 bot 刚加入一个加密房间，它只能解密在它加入*之后*发送的消息。旧消息无法访问。

### 从先前使用 E2EE 的版本升级

如果你之前使用 Hermes 时设置了 `MATRIX_ENCRYPTION=true`，并且正在升级到使用新的基于 SQLite 的加密存储的版本，那么 bot 的加密身份已更改。你的 Matrix 客户端（Element）可能会缓存旧的设备密钥，并拒绝与 bot 共享加密会话。

**症状**：Bot 连接并在日志中显示“E2EE enabled”，但所有消息都显示“could not decrypt event”，并且 bot 从不响应。

**发生了什么**：旧的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。Bot 创建了一个新的加密身份，但你的 Matrix 客户端仍然缓存着旧密钥，并且不会与密钥已更改的设备共享房间的加密会话。这是 Matrix 的一项安全功能 — 客户端将同一设备更改的身份密钥视为可疑。

**解决方法**（一次性迁移）：

1.  **生成一个新的访问令牌**以获取新的设备 ID。最简单的方法：

    ```bash
    curl -X POST https://your-server/_matrix/client/v3/login \
      -H "Content-Type: application/json" \
      -d '{
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": "@hermes:your-server.org"},
        "password": "***",
        "initial_device_display_name": "Hermes Agent"
      }'
    ```

    复制新的 `access_token` 并更新 `~/.hermes/.env` 中的 `MATRIX_ACCESS_TOKEN`。

2.  **删除旧的加密状态**：

    ```bash
    rm -f ~/.hermes/platforms/matrix/store/crypto.db
    rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
    ```

3.  **设置你的恢复密钥**（如果你使用交叉签名 — 大多数 Element 用户都使用）。添加到 `~/.hermes/.env`：

    ```bash
    MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥放在这里
    ```

    这允许 bot 在启动时使用交叉签名密钥自行签署，因此 Element 会立即信任新设备。如果没有这个，Element 可能会将新设备视为未验证，并拒绝共享加密会话。在 Element 的 **设置** → **安全与隐私** → **加密** 下找到你的恢复密钥。

4.  **强制你的 Matrix 客户端轮换加密会话**。在 Element 中，打开与 bot 的私聊房间并键入 `/discardsession`。这会强制 Element 创建一个新的加密会话并与 bot 的新设备共享。

5.  **重启网关**：

    ```bash
    hermes gateway run
    ```

    如果设置了 `MATRIX_RECOVERY_KEY`，你应该在日志中看到 `Matrix: cross-signing verified via recovery key`。

6.  **发送一条新消息**。Bot 应该能正常解密并响应。

:::note
迁移后，*升级前*发送的消息无法解密 — 旧的加密密钥已丢失。这只影响过渡期；新消息正常工作。
:::

:::tip
**新安装不受影响。** 此迁移仅在你之前使用旧版 Hermes 设置了有效的 E2EE 并正在升级时才需要。

**为什么需要新的访问令牌？** 每个 Matrix 访问令牌都绑定到特定的设备 ID。使用新的加密密钥重用相同的设备 ID 会导致其他 Matrix 客户端不信任该设备（它们将更改的身份密钥视为潜在的安全漏洞）。新的访问令牌会获得一个没有陈旧密钥历史的新设备 ID，因此其他客户端会立即信任它。
:::

### 同步问题 / bot 落后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者家庭服务器速度慢。

**解决方法**：同步循环在出错时会自动每 5 秒重试一次。检查 Hermes 日志中与同步相关的警告。如果 bot 持续落后，请确保你的家庭服务器有足够的资源。

### Bot 离线

**原因**：Hermes 网关未运行，或者连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：错误的家庭服务器 URL、过期的访问令牌、家庭服务器无法访问。
### “用户无权限” / Bot 忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 列表中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATRIX_ALLOWED_USERS` 环境变量，然后重启网关。请使用完整的 `@user:server` 格式。

## 安全

:::warning
务必设置 `MATRIX_ALLOWED_USERS` 来限制可以与 bot 交互的人员。如果不设置，出于安全考虑，网关默认会拒绝所有用户。只添加你信任的用户 ID —— 授权用户拥有对 Agent 功能的完全访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

-   **支持任何家庭服务器**：可与 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 家庭服务器配合使用。无需特定的家庭服务器软件。
-   **联邦**：如果你在联邦家庭服务器上，bot 可以与其他服务器的用户通信 —— 只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 中。
-   **自动加入**：bot 会自动接受房间邀请并加入。加入后立即开始响应。
-   **媒体支持**：Hermes 可以发送和接收图片、音频、视频和文件附件。媒体通过 Matrix 内容存储库 API 上传到你的家庭服务器。
-   **原生语音消息 (MSC3245)**：Matrix 适配器会自动为发出的语音消息打上 `org.matrix.msc3245.voice` 标签。这意味着 TTS 响应和语音音频在 Element 及其他支持 MSC3245 的客户端中会呈现为**原生语音气泡**，而不是普通的音频文件附件。带有 MSC3245 标签的传入语音消息也能被正确识别并路由到语音转文字转录。无需配置 —— 此功能自动生效。
