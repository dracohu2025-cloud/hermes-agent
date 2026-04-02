---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 配置

Hermes Agent 集成了 Matrix，一个开放、联邦化的消息协议。Matrix 允许你运行自己的 homeserver 或使用公共服务器（如 matrix.org）——无论哪种方式，你都能控制自己的通信。机器人通过 `matrix-nio` Python SDK 连接，通过 Hermes Agent 管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图像、音频、视频以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix homeserver 配合工作——Synapse、Conduit、Dendrite 或 matrix.org。

在配置之前，以下是大多数人想知道的部分：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 上下文 | 行为 |
|---------|----------|
| **私聊（DM）** | Hermes 响应每条消息。无需 `@提及`。每个私聊都有自己的会话。 |
| **房间** | Hermes 响应其加入的房间中的所有消息。房间邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果你在线程中回复，Hermes 会将线程上下文与主房间的时间线隔离。 |
| **多用户共享的房间** | 默认情况下，Hermes 在房间内为每个用户隔离会话历史。同一房间中的两个人不会共享一个对话记录，除非你明确禁用该功能。 |

:::tip
机器人被邀请时会自动加入房间。只需将机器人的 Matrix 用户邀请到任意房间，它就会加入并开始响应。
:::

### Matrix 中的会话模型

默认情况下：

- 每个私聊都有自己的会话
- 每个线程都有自己的会话命名空间
- 共享房间中的每个用户在该房间内都有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅在明确希望整个房间共享一个对话时将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

- 用户共享上下文增长和令牌成本
- 一个人的长时间、工具繁多的任务可能膨胀所有人的上下文
- 一个人的正在进行的运行可能中断同一房间中其他人的后续对话

本指南将带你完成完整的配置过程——从创建机器人账户到发送第一条消息。

## 步骤 1：创建机器人账户

你需要为机器人创建一个 Matrix 用户账户。有几种方法可以做到这一点：

### 选项 A：在你的 Homeserver 上注册（推荐）

如果你运行自己的 homeserver（Synapse、Conduit、Dendrite）：

1. 使用管理 API 或注册工具创建新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，如 `hermes`——完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共 Homeserver

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为你的机器人选择一个用户名（例如，`hermes-bot`）。

### 选项 C：使用你自己的账户

你也可以将 Hermes 作为你自己的用户运行。这意味着机器人会以你的名义发布消息——适合用作个人助手。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来与 homeserver 进行身份验证。你有两个选项：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方式：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 进入 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级**——访问令牌在那里显示。
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

响应包含一个 `access_token` 字段——复制它。

:::warning[保护好你的访问令牌]
访问令牌赋予对机器人 Matrix 账户的完全访问权限。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的全部会话来撤销它。
:::

### 选项 B：密码登录

不提供访问令牌，你可以向 Hermes 提供机器人的用户 ID 和密码。Hermes 将在启动时自动登录。这更简单，但意味着密码存储在你的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 步骤 3：找到你的 Matrix 用户 ID

Hermes Agent 使用你的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 遵循格式 `@username:server`。

要找到你的用户 ID：

1. 打开 [Element](https://app.element.io)（或你喜欢的 Matrix 客户端）。
2. 点击你的头像 → **设置**。
3. 你的用户 ID 显示在配置文件顶部（例如，`@alice:matrix.org`）。

:::tip
Matrix 用户 ID 始终以 `@` 开头，并包含一个 `:` 后面跟着服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式配置（推荐）

运行引导式配置命令：

```bash
hermes gateway setup
```

提示时选择 **Matrix**，然后按要求提供你的 homeserver URL、访问令牌（或用户 ID + 密码）和允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略，将从令牌自动检测）
# MATRIX_USER_ID=@hermes:matrix.example.org

# 安全：限制谁可以与机器人交互
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

可选行为设置在 `~/.hermes/config.yaml`：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享房间中保持每个参与者的上下文隔离

### 启动网关

配置完成后，启动 Matrix 网关：

```bash
hermes gateway
```

机器人应该连接到你的 homeserver 并在几秒钟内开始同步。给它发送一条消息——无论是私聊还是在它已加入的房间中——来进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或作为 systemd 服务运行以实现持久操作。详情请参阅部署文档。
:::

## 端到端加密（E2EE）

Hermes 支持 Matrix 端到端加密，因此你可以在加密房间中与你的机器人聊天。

### 要求

E2EE 需要带有加密额外功能的 `matrix-nio` 库和 `libolm` C 库：

```bash
# 安装支持 E2EE 的 matrix-nio
pip install 'matrix-nio[e2e]'

# 或者通过 hermes extras 安装
pip install 'hermes-agent[matrix]'
```

你的系统上还需要安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用 E2EE

添加到你的 `~/.hermes/.env`：

```bash
MATRIX_ENCRYPTION=true
```

当 E2EE 启用时，Hermes：

- 将加密密钥存储在 `~/.hermes/matrix/store/`
- 在首次连接时上传设备密钥
- 自动解密传入消息并加密传出消息
- 被邀请时自动加入加密房间

:::warning
如果你删除 `~/.hermes/matrix/store/` 目录，机器人将丢失其加密密钥。你需要在 Matrix 客户端中再次验证设备。如果你想保留加密会话，请备份此目录。
:::

:::info
如果 `matrix-nio[e2e]` 未安装或 `libolm` 缺失，机器人会自动回退到普通（非加密）客户端。你会在日志中看到警告。
:::

## 主场房间

你可以指定一个“主场房间”，机器人向该房间发送主动消息（例如 cron 作业输出、提醒和通知）。有两种设置方式：
### 使用斜杠命令

在机器人所在的任何 Matrix 房间中，输入 `/sethome`。该房间将成为主房间。

### 手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

:::tip
要查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → **内部房间 ID** 显示在那里（以 `!` 开头）。
:::

## 故障排除

### 机器人不响应消息

**原因**：机器人尚未加入房间，或者 `MATRIX_ALLOWED_USERS` 未包含你的用户 ID。

**解决方法**：邀请机器人加入房间 — 收到邀请后它会自动加入。确认你的用户 ID 在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重启网关。

### 启动时出现“身份验证失败”/“whoami 失败”

**原因**：访问令牌或家庭服务器 URL 不正确。

**解决方法**：确认 `MATRIX_HOMESERVER` 指向你的家庭服务器（包含 `https://`，末尾没有斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效 — 尝试用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回你的用户信息，则令牌有效。如果返回错误，请生成新令牌。

### “matrix-nio 未安装”错误

**原因**：未安装 `matrix-nio` Python 包。

**解决方法**：安装它：

```bash
pip install 'matrix-nio[e2e]'
```

或者使用 Hermes 扩展包：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误 / “无法解密事件”

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备未被信任。

**解决方法**：
1.  确认你的系统上安装了 `libolm`（参见上面的 E2EE 部分）。
2.  确保在你的 `.env` 文件中设置了 `MATRIX_ENCRYPTION=true`。
3.  在你的 Matrix 客户端（Element）中，进入机器人的个人资料 → **会话** → 验证/信任机器人的设备。
4.  如果机器人刚加入一个加密房间，它只能解密在它加入*之后*发送的消息。旧消息无法访问。

### 同步问题 / 机器人落后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者家庭服务器速度慢。

**解决方法**：同步循环在出错时会自动每 5 秒重试一次。检查 Hermes 日志中与同步相关的警告。如果机器人持续落后，请确保你的家庭服务器有足够的资源。

### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：家庭服务器 URL 错误、访问令牌过期、家庭服务器无法访问。

### “用户未授权” / 机器人忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATRIX_ALLOWED_USERS`，然后重启网关。使用完整的 `@user:server` 格式。

## 安全

:::warning
务必设置 `MATRIX_ALLOWED_USERS` 以限制可以与机器人交互的用户。如果不设置，作为安全措施，网关默认会拒绝所有用户。只添加你信任的用户 ID — 授权用户可以完全访问 Agent 的功能，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

-   **任何家庭服务器**：适用于 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 家庭服务器。不需要特定的家庭服务器软件。
-   **联邦**：如果你在联邦家庭服务器上，机器人可以与来自其他服务器的用户通信 — 只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 中。
-   **自动加入**：机器人会自动接受房间邀请并加入。加入后立即开始响应。
-   **媒体支持**：Hermes 可以发送和接收图像、音频、视频和文件附件。媒体使用 Matrix 内容存储库 API 上传到你的家庭服务器。
-   **原生语音消息 (MSC3245)**：Matrix 适配器会自动为发出的语音消息打上 `org.matrix.msc3245.voice` 标签。这意味着 TTS 响应和语音音频在 Element 和其他支持 MSC3245 的客户端中会呈现为**原生语音气泡**，而不是通用的音频文件附件。带有 MSC3245 标签的传入语音消息也能被正确识别并路由到语音转文字转录。无需配置 — 自动生效。
