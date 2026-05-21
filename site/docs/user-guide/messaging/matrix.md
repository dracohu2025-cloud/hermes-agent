---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

<a id="matrix-setup"></a>
# Matrix 设置

Hermes Agent 集成了 Matrix，这是开放的、联合联邦的消息协议。Matrix 允许你运行自己的家庭服务器（homeserver），或者使用 matrix.org 这样的公共服务器——无论哪种方式，你都能掌控自己的通讯。该机器人通过 `mautrix` Python SDK 连接，经过 Hermes Agent 管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片、音频、视频，以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix 家庭服务器配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在开始设置之前，先介绍大多数人最关心的部分：Hermes 连接后的行为表现。

<a id="how-hermes-behaves"></a>
## Hermes 的行为表现

| 场景 | 行为 |
|---------|----------|
| **私聊（DM）** | Hermes 会响应每一条消息，无需 `@提及`。每个私聊拥有独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可以在私聊中通过 `@提及` 机器人来开启一个线程。 |
| **房间** | 默认情况下，Hermes 需要 `@提及` 才会响应。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 可开启自由响应房间。房间邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果你在线程中回复，Hermes 会将线程上下文与主房间时间线隔离。机器人已经参与的线程不需要提及。 |
| **自动线程** | 默认情况下，Hermes 会在房间内为其响应的每条消息自动创建一个线程，从而使对话保持隔离。设置 `MATRIX_AUTO_THREAD=false` 可禁用。 |
| **多人共享房间** | 默认情况下，Hermes 在房间内按用户隔离会话历史。同一房间中的两个人不会共享同一份对话记录，除非你明确禁用了该功能。 |

:::tip
机器人会在被邀请时自动加入房间。只需邀请机器人的 Matrix 用户到任意房间，它就会加入并开始响应。
:::

<a id="session-model-in-matrix"></a>
### Matrix 中的会话模型

默认情况下：

- 每个私聊都有独立的会话
- 每个线程都有独立的会话命名空间
- 共享房间中的每个用户在房间内拥有独立的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享同一份对话记录时，才将其设为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

- 用户之间共享上下文增长和 token 成本
- 某人的长时间、大量工具任务可能会膨胀所有人的上下文
- 某人的进行中运行可能会打断同一房间内其他人的后续操作

<a id="mention-and-threading-configuration"></a>
### 提及和线程配置

你可以通过环境变量或 `config.yaml` 配置提及和自动线程行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @提及（默认：true）
  free_response_rooms:            # 免除提及要求的房间
    - "!abc123:matrix.org"
  auto_thread: true               # 自动为响应创建线程（默认：true）
  dm_mention_threads: false       # 在私聊中被 @提及时创建线程（默认：false）
```
或者通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
MATRIX_REACTIONS=true          # 默认值：true —— 处理过程中会发 emoji 反应
```

:::tip 禁用反应
将 `MATRIX_REACTIONS=false` 可以关闭机器人在入站消息上发出的处理生命周期 emoji 反应（👀/✅/❌）。在反应事件过于频繁或并非所有参与客户端都支持反应的房间中，这个选项很有用。
:::

:::note
如果你是从一个没有 `MATRIX_REQUIRE_MENTION` 的版本升级上来的，之前机器人会回复房间中的所有消息。要保留这一行为，请设置 `MATRIX_REQUIRE_MENTION=false`。
:::

<a id="disabling-reactions"></a>
本指南将带你完成完整的设置流程——从创建机器人账号到发送第一条消息。

<a id="step-1-create-a-bot-account"></a>
## 第一步：创建机器人账号

你需要为机器人准备一个 Matrix 用户账号。有以下几种方式：

<a id="option-a-register-on-your-homeserver-recommended"></a>
### 方式 A：在你的家服务器上注册（推荐）

如果你运行自己的家服务器（Synapse、Conduit、Dendrite）：

1. 使用管理员 API 或注册工具创建一个新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，比如 `hermes` —— 完整的用户 ID 将是 `@hermes:your-server.org`。

<a id="option-b-use-matrix-org-or-another-public-homeserver"></a>
### 方式 B：使用 matrix.org 或其他公共家服务器

1. 前往 [Element Web](https://app.element.io) 并创建一个新账号。
2. 为你的机器人选一个用户名（例如 `hermes-bot`）。

<a id="option-c-use-your-own-account"></a>
### 方式 C：使用你自己的账号

你也可以以你自己的用户身份运行 Hermes。这意味着机器人会以你的名义发消息——对个人助手来说很有用。

<a id="step-2-get-an-access-token"></a>
## 第二步：获取访问令牌

Hermes 需要一个访问令牌来与家服务器进行身份验证。你有两个选项：

<a id="option-a-access-token-recommended"></a>
### 方式 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账号登录 [Element](https://app.element.io)。
2. 前往 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级** —— 访问令牌会显示在那里。
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

响应中会包含一个 `access_token` 字段 —— 复制它。

:::warning[请确保你的访问令牌安全]
访问令牌拥有对机器人 Matrix 账号的完全访问权限。切勿公开分享或将其提交到 Git。如果令牌泄露，请通过注销该用户的所有会话来撤销它。
:::

<a id="option-b-password-login"></a>
### 方式 B：密码登录

除了提供访问令牌，你也可以直接给 Hermes 提供机器人的用户 ID 和密码。Hermes 会在启动时自动登录。这种方式更简单，但密码会存储在你的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

<a id="step-3-find-your-matrix-user-id"></a>
## 第三步：找到你的 Matrix 用户 ID
Hermes Agent 使用您的 Matrix 用户 ID 来控制哪些人可以与机器人交互。Matrix 用户 ID 的格式为 `@username:server`。

要找到您的 ID：

1. 打开 [Element](https://app.element.io)（或您喜欢的 Matrix 客户端）。
2. 点击头像 → **设置**。
3. 您的用户 ID 会显示在个人资料的顶部（例如 `@alice:matrix.org`）。

:::tip
Matrix 用户 ID 始终以 `@` 开头，并包含一个 `:` 后跟服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

<a id="step-4-configure-hermes-agent"></a>
## 第 4 步：配置 Hermes Agent

<a id="option-a-interactive-setup-recommended"></a>
### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Matrix**，然后按要求提供您的 homeserver URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到您的 `~/.hermes/.env` 文件中：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略则从令牌自动检测）
# MATRIX_USER_ID=@hermes:matrix.example.org

# 安全：限制哪些人可以与机器人交互
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

# 安全
MATRIX_ALLOWED_USERS=@alice:matrix.example.org
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 保持共享房间中每位参与者的上下文隔离。

<a id="start-the-gateway"></a>
### 启动网关

配置完成后，启动 Matrix 网关：

```bash
hermes gateway
```

机器人应连接到您的 homeserver，并在几秒内开始同步。向它发送一条消息 – 可以是私聊，也可以是它已加入的房间 – 以进行测试。

:::tip
您可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

<a id="end-to-end-encryption-e2ee"></a>
## 端到端加密（E2EE）

Hermes 支持 Matrix 端到端加密，因此您可以在加密房间中与机器人聊天。

<a id="requirements"></a>
### 要求

E2EE 需要 `mautrix` 库（含加密扩展）和 `libolm` C 库：

```bash
# 安装带 E2EE 支持的 mautrix
pip install 'mautrix[encryption]'

# 或者使用 hermes 扩展安装
pip install 'hermes-agent[matrix]'
```

您还需要在系统上安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

<a id="enable-e2ee"></a>
### 启用 E2EE

添加到您的 `~/.hermes/.env`：

```bash
MATRIX_ENCRYPTION=true
```

启用 E2EE 后，Hermes：

- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/`（旧版本安装：`~/.hermes/matrix/store/`）
- 在首次连接时上传设备密钥
- 自动解密传入消息并加密传出消息
- 被邀请时自动加入加密房间
<a id="cross-signing-verification-recommended"></a>
### 交叉签名验证（推荐）

如果你的 Matrix 账号启用了交叉签名（Element 默认开启），请设置恢复密钥，以便机器人在启动时能自行签名其设备。若不设置，其他 Matrix 客户端可能在设备密钥轮换后拒绝与该机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... your recovery key here
```

**在哪里找到：** 在 Element 中，进入 **设置** → **安全与隐私** → **加密** → 你的恢复密钥（也称为“安全密钥”）。这是你在首次设置交叉签名时被要求保存的密钥。

每次启动时，如果设置了 `MATRIX_RECOVERY_KEY`，Hermes 会从家服务器的安全秘密存储中导入交叉签名密钥，并对当前设备进行签名。此操作是幂等的，可以安全地永久启用。

:::warning[删除加密存储]
如果你删除 `~/.hermes/platforms/matrix/store/crypto.db`，机器人将丢失其加密身份。仅用相同的设备 ID 重启 **无法** 完全恢复——家服务器上仍保留了用旧身份密钥签名的一次性密钥，对端无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况，并拒绝启用端到端加密（E2EE），日志会记录：`device XXXX has stale one-time keys on the server signed with a previous identity key`。

**最简单的恢复方法：生成一个新的访问令牌**（这会获得一个没有过期密钥历史记录的新设备 ID）。请参见下方“从启用了 E2EE 的旧版本升级”部分。这是最可靠的途径，无需触碰家服务器数据库。

**手动恢复**（高级——保留相同的设备 ID）：

1. 停止 Synapse，并从其数据库中删除旧设备：
   ```bash
   sudo systemctl stop matrix-synapse
   sudo sqlite3 /var/lib/matrix-synapse/homeserver.db "
     DELETE FROM e2e_device_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_one_time_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_fallback_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM devices WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
   "
   sudo systemctl start matrix-synapse
   ```
   或者通过 Synapse 管理 API（注意用户 ID 需要 URL 编码）：
   ```bash
   curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
     'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
   ```
   注意：通过管理 API 删除设备可能会同时使关联的访问令牌失效。之后你可能需要生成一个新令牌。

2. 删除本地加密存储并重启 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # 重启 hermes
   ```

其他 Matrix 客户端（Element、matrix-commander）可能会缓存旧设备密钥。恢复后，在 Element 中输入 `/discardsession` 以强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人会自动回退到纯文本（未加密）客户端。你会在日志中看到一条警告。
:::
<a id="home-room"></a>
## 主房间（Home Room）

你可以指定一个“主房间”，机器人会向该房间发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方式：

<a id="using-the-slash-command"></a>
### 使用斜杠命令

在任意一个机器人所在 Matrix 房间内输入 `/sethome`。该房间即成为主房间。

<a id="manual-configuration"></a>
### 手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

<a id="room-allowlist-allowedrooms"></a>
## 房间许可名单（`allowed_rooms`）

将机器人限制在一组固定的 Matrix 房间内。设置后，机器人**仅**在列表中的房间 ID 对应的房间内响应——来自其他任何房间的消息都会被静默忽略，即使提到了机器人。

**私聊（直接聊天房间）不受此过滤限制**，因此授权用户始终可以一对一联系机器人。

```yaml
matrix:
  allowed_rooms:
    - "!abc123def456:matrix.example.org"
    - "!opsroom789:matrix.example.org"
```

或者通过环境变量（逗号分隔）：

```bash
MATRIX_ALLOWED_ROOMS="!abc123def456:matrix.example.org,!opsroom789:matrix.example.org"
```

行为说明：

- 空 / 未设置 → 无限制（默认）。
- 非空 → 房间 ID 必须在列表中。该检查**优先于**其他任何拦截条件（提及要求、发送者许可名单等）。
- 使用房间的**内部 ID**（`!abc...:server`），而不是它的别名（`#room:server`）。你可以在 Element 中通过房间 → 设置 → 高级找到房间的内部 ID。

另请参阅：[管理员/用户斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。


:::tip
如何查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → 此处会显示**内部房间 ID**（以 `!` 开头）。
:::

<a id="troubleshooting"></a>
## 故障排除

<a id="bot-is-not-responding-to-messages"></a>
### 机器人不回复消息

**原因**：机器人未加入该房间，或者 `MATRIX_ALLOWED_USERS` 中没有包含你的用户 ID。

**解决办法**：邀请机器人加入房间——收到邀请后它会自动加入。确认你的用户 ID 在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重新启动网关。

<a id="bot-joins-rooms-but-silently-drops-every-message-clock-skew"></a>
### 机器人加入房间但静默丢弃每条消息（时钟偏差）

**原因**：主机的系统时钟比实际时间快。Matrix 适配器会应用一个 5 秒的启动缓冲过滤器（`event_ts < startup_ts - 5`），以忽略从初始同步中重放的事件。当系统时钟偏快时，每个传入的事件看起来都“比启动时间更早”，因此在到达消息处理器之前就被丢弃——机器人显示已连接但从不回复。参见 [#12614](https://github.com/NousResearch/hermes-agent/issues/12614)。

**症状**：网关日志显示 `Matrix: dropped N live events as 'too old' more than 30s after startup`。

**解决办法**：使用 NTP 同步主机时钟并重启机器人：

```bash
# Debian/Ubuntu
sudo timedatectl set-ntp true
timedatectl status   # 确认 "System clock synchronized: yes"

# macOS
sudo sntp -sS time.apple.com
```

<a id="failed-to-authenticate-whoami-failed-on-startup"></a>
### 启动时显示“Failed to authenticate”/“whoami failed”

**原因**：访问令牌或 homeserver URL 不正确。

**解决办法**：确认 `MATRIX_HOMESERVER` 指向你的 homeserver（包含 `https://`，末尾无斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效——可以用 curl 测试：
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回了你的用户信息，则令牌有效。如果返回错误，请生成一个新令牌。

<a id="mautrix-not-installed-error"></a>
### "mautrix not installed" 错误

**原因**：未安装 `mautrix` Python 包。

**修复**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或者使用 Hermes extras：

```bash
pip install 'hermes-agent[matrix]'
```

<a id="encryption-errors-could-not-decrypt-event"></a>
### 加密错误 / "could not decrypt event"

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备不受信任。

**修复**：
1. 确认系统已安装 `libolm`（参见上面的 E2EE 部分）。
2. 确保 `.env` 中设置了 `MATRIX_ENCRYPTION=true`。
3. 在 Matrix 客户端（如 Element）中，进入机器人的个人资料 → 会话 → 验证/信任机器人的设备。
4. 如果机器人刚加入加密房间，它只能解密*加入后*发送的消息。旧消息无法访问。

<a id="upgrading-from-a-previous-version-with-e2ee"></a>
### 从带 E2EE 的旧版本升级

:::tip
如果你还手动删除了 `crypto.db`，请参见上面 E2EE 部分的“删除加密存储”警告——需要额外步骤从 homeserver 清除过期的一次性密钥。
:::

如果你之前使用 Hermes 时开启了 `MATRIX_ENCRYPTION=true`，并且正在升级到使用新的基于 SQLite 的加密存储的版本，机器人的加密身份已更改。你的 Matrix 客户端（Element）可能缓存了旧设备密钥，并拒绝与机器人共享加密会话。

**症状**：机器人连接正常，日志显示“E2EE enabled”，但所有消息都显示“could not decrypt event”，且机器人始终不回复。

**原因**：旧的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。机器人创建了全新的加密身份，但你的 Matrix 客户端仍然缓存了旧密钥，因此不会与密钥发生更改的设备共享房间的加密会话。这是 Matrix 的安全特性——客户端会将同一设备更改的身份密钥视为可疑。

**修复**（一次性迁移）：

1. **生成新的访问令牌**以获得新的设备 ID。最简单的方式：

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

2. **删除旧的加密状态**：

   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db
   rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
   ```

3. **设置你的恢复密钥**（如果你使用跨签名——大多数 Element 用户都使用）。添加到 `~/.hermes/.env`：

   ```bash
   MATRIX_RECOVERY_KEY=EsT... your recovery key here
   ```
这让机器人能在启动时使用交叉签名密钥进行自签名，因此 Element 会立即信任新设备。如果不这样做，Element 可能会认为新设备未经验证，并拒绝分享加密会话。在 Element 中，前往 **设置** → **安全与隐私** → **加密** 找到你的恢复密钥。

4. **强制你的 Matrix 客户端轮换加密会话**。在 Element 中，打开与机器人的私信房间并输入 `/discardsession`。这会强制 Element 创建一个新的加密会话并将其共享给机器人的新设备。

5. **重启网关**：

   ```bash
   hermes gateway run
   ```

   如果已设置 `MATRIX_RECOVERY_KEY`，你将在日志中看到 `Matrix: cross-signing verified via recovery key`。

6. **发送一条新消息**。机器人应能正常解密并回复。

:::note
迁移完成后，*升级之前*发送的消息无法被解密——旧的加密密钥已丢失。这仅影响过渡期；新消息正常工作。
:::

:::tip
**全新的安装不受影响。** 仅当你在旧版 Hermes 上已有可用的 E2EE 设置并正在升级时，才需要此迁移。

**为什么需要新的访问令牌？** 每个 Matrix 访问令牌绑定到特定的设备 ID。使用新的加密密钥重复使用相同的设备 ID 会导致其他 Matrix 客户端不信任该设备（它们将更改的身份密钥视为潜在的安全问题）。新访问令牌带有新的设备 ID，没有过期的密钥历史，因此其他客户端会立即信任它。
:::

<a id="proxy-mode-e2ee-on-macos"></a>
## 代理模式（macOS 上的 E2EE）

Matrix E2EE 需要 `libolm`，而该库在 macOS ARM64（Apple Silicon）上无法编译。`hermes-agent[matrix]` 附加组件仅限 Linux 使用。如果你使用 macOS，代理模式让你可以在 Linux 虚拟机上的 Docker 容器中运行 E2EE，而实际 Agent 则原生运行在 macOS 上，可完全访问本地文件、内存和技能。

<a id="how-it-works"></a>
### 工作原理

```
macOS（宿主机）：
  └─ hermes gateway
       ├─ api_server 适配器 ← 监听 0.0.0.0:8642
       ├─ AIAgent ← 唯一真相来源
       ├─ 会话、内存、技能
       └─ 本地文件访问（Obsidian、项目等）

Linux 虚拟机（Docker）：
  └─ hermes gateway（代理模式）
       ├─ Matrix 适配器 ← E2EE 解密/加密
       └─ HTTP 转发 → macOS:8642/v1/chat/completions
           （无 LLM API 密钥、无 Agent、无推理）
```

Docker 容器仅处理 Matrix 协议 + E2EE。当消息到达时，它解密并将文本通过标准 HTTP 请求转发给宿主机。宿主机运行 Agent、调用工具、生成响应并流式返回。容器加密响应并发送到 Matrix。所有会话统一——CLI、Matrix、Telegram 以及其他任何平台共享相同的内存和对话历史。

<a id="step-1-configure-the-host-macos"></a>
### 第一步：配置宿主机（macOS）

启用 API 服务器，使宿主机接受来自 Docker 容器的传入请求。

在 `~/.hermes/.env` 中添加：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```
- `API_SERVER_HOST=0.0.0.0` 绑定所有接口，以便 Docker 容器能够访问。
- 非环回绑定时需要 `API_SERVER_KEY`。选择强随机字符串。
- API 服务器默认运行在 8642 端口（如需更改，使用 `API_SERVER_PORT`）。

启动网关：

```bash
hermes gateway
```

你会看到 API 服务器与你配置的其他平台一起启动。验证它可以从虚拟机访问：

```bash
# 从 Linux 虚拟机
curl http://<mac-ip>:8642/health
```

<a id="step-2-configure-the-docker-container-linux-vm"></a>
### 第 2 步：配置 Docker 容器（Linux 虚拟机）

容器需要 Matrix 凭据和代理 URL。它不需要 LLM API 密钥。

**`docker-compose.yml`:**

```yaml
services:
  hermes-matrix:
    build: .
    environment:
      # Matrix 凭据
      MATRIX_HOMESERVER: "https://matrix.example.org"
      MATRIX_ACCESS_TOKEN: "syt_..."
      MATRIX_ALLOWED_USERS: "@you:matrix.example.org"
      MATRIX_ENCRYPTION: "true"
      MATRIX_DEVICE_ID: "HERMES_BOT"

      # 代理模式——转发到主机 Agent
      GATEWAY_PROXY_URL: "http://192.168.1.100:8642"
      GATEWAY_PROXY_KEY: "your-secret-key-here"
    volumes:
      - ./matrix-store:/root/.hermes/platforms/matrix/store
```

**`Dockerfile`:**

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libolm-dev && rm -rf /var/lib/apt/lists/*
RUN pip install 'hermes-agent[matrix]'

CMD ["hermes", "gateway"]
```

这就是完整的容器。不需要 OpenRouter、Anthropic 或任何推理提供商的 API 密钥。

<a id="step-3-start-both"></a>
### 第 3 步：启动两者

1. 先启动主机网关：
   ```bash
   hermes gateway
   ```

2. 启动 Docker 容器：
   ```bash
   docker compose up -d
   ```

3. 在加密的 Matrix 房间中发送一条消息。容器解密消息，转发给主机，并将响应流式传回。

<a id="configuration-reference"></a>
### 配置参考

代理模式在**容器端**（瘦网关）配置：

| 设置 | 描述 |
|---------|-------------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如 `http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于认证的 Bearer 令牌（必须与主机上的 `API_SERVER_KEY` 匹配） |
| `gateway.proxy_url` | 与 `GATEWAY_PROXY_URL` 相同，但写在 `config.yaml` 中 |

主机端需要：

| 设置 | 描述 |
|---------|-------------|
| `API_SERVER_ENABLED` | 设置为 `true` |
| `API_SERVER_KEY` | Bearer 令牌（与容器共享） |
| `API_SERVER_HOST` | 设置为 `0.0.0.0` 以允许网络访问 |
| `API_SERVER_PORT` | 端口号（默认：`8642`） |

<a id="works-for-any-platform"></a>
### 适用于任何平台

代理模式不仅限于 Matrix。任何平台适配器都可以使用——在任何网关实例上设置 `GATEWAY_PROXY_URL`，它将转发到远程 Agent，而不是本地运行一个 Agent。这对于任何需要平台适配器在与 Agent 不同的环境中运行的部署（网络隔离、端到端加密要求、资源限制）都很有用。

:::tip
会话连续性通过 `X-Hermes-Session-Id` 头部维护。主机的 API 服务器通过此 ID 跟踪会话，因此对话可以在消息之间持续存在，就像使用本地 Agent 一样。
:::
:::note
**限制（v1）：** 远程 Agent 的工具进度消息不会回传——用户只能看到流式输出的最终响应，而看不到单个工具调用。危险命令的审批提示在主机端处理，不会转发给 Matrix 用户。这些问题可以在未来更新中解决。
:::

<a id="sync-issues-bot-falls-behind"></a>
### 同步问题 / 机器人响应滞后

**原因**：长时间运行的工具执行会延迟同步循环，或者家庭服务器响应缓慢。

**修复**：同步循环在出错时会自动每 5 秒重试一次。请检查 Hermes 日志中与同步相关的警告。如果机器人持续滞后，请确保你的家庭服务器有足够的资源。

<a id="bot-is-offline"></a>
### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：家庭服务器 URL 错误、访问令牌过期、家庭服务器无法访问。

<a id="user-not-allowed-bot-ignores-you"></a>
### "用户不被允许" / 机器人忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATRIX_ALLOWED_USERS` 里，然后重启网关。请使用完整的 `@user:server` 格式。

<a id="security"></a>
## 安全性

:::warning
务必设置 `MATRIX_ALLOWED_USERS` 来限制可以与机器人交互的用户。作为安全措施，如果没有设置，网关默认会拒绝所有用户。只添加你信任的用户 ID——授权用户拥有 Agent 的全部能力，包括工具使用和系统访问权限。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

<a id="notes"></a>
## 备注

- **任意家庭服务器**：适用于 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 家庭服务器。无需特定的家庭服务器软件。
- **联邦**：如果你在联邦家庭服务器上，机器人可以与其他服务器的用户通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 中。
- **自动加入**：机器人会自动接受房间邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图片、音频、视频和文件附件。媒体通过 Matrix 内容仓库 API 上传到你的家庭服务器。
- **原生语音消息（MSC3245）**：Matrix 适配器会自动为发出的语音消息添加 `org.matrix.msc3245.voice` 标记。这意味着 TTS 响应和语音音频在 Element 及其他支持 MSC3245 的客户端中会渲染为**原生语音气泡**，而不是作为普通的音频文件附件。带有 MSC3245 标记的传入语音消息也会被正确识别并路由到语音转文字转录。无需任何配置——这一切都是自动完成的。
