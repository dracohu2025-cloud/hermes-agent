---
sidebar_position: 9
title: "Matrix 设置"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 集成了 Matrix，这是一个开放、联邦式的消息协议。Matrix 允许你运行自己的家庭服务器，或使用像 matrix.org 这样的公共服务器——无论哪种方式，你都能控制自己的通信。该机器人通过 `matrix-nio` Python SDK 连接，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片、音频、视频以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix 家庭服务器配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在开始设置之前，以下是大多数人最想了解的部分：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **私信** | Hermes 会响应每一条消息。不需要 `@提及`。每个私信都有其独立的会话。 |
| **群组** | Hermes 会响应它已加入的群组中的所有消息。群组邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果你在某个线程中回复，Hermes 会将该线程的上下文与主群组时间线隔离开。 |
| **多用户共享的群组** | 默认情况下，Hermes 在群组内为每个用户隔离会话历史。两个人在同一个群组中交谈不会共享一个对话记录，除非你明确禁用此功能。 |

:::tip
机器人被邀请时会自动加入群组。只需将机器人的 Matrix 用户邀请到任何群组，它就会加入并开始响应。
:::

### Matrix 中的会话模型

默认情况下：

- 每个私信获得独立的会话
- 每个线程获得独立的会话命名空间
- 共享群组中的每个用户在该群组内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个群组共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作群组可能有用，但也意味着：

- 用户共享上下文增长和令牌成本
- 一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
- 一个人正在运行的任务可能会中断同群组中另一个人的后续操作

本指南将引导你完成完整的设置过程——从创建机器人账户到发送第一条消息。

## 步骤 1：创建机器人账户

你需要一个 Matrix 用户账户作为机器人。有几种方法可以实现：

### 选项 A：在你的家庭服务器上注册（推荐）

如果你运行自己的家庭服务器（Synapse、Conduit、Dendrite）：

1. 使用管理员 API 或注册工具创建新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，例如 `hermes`——完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共家庭服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为你的机器人选择一个用户名（例如，`hermes-bot`）。

### 选项 C：使用你自己的账户

你也可以将 Hermes 作为你自己的用户运行。这意味着机器人将以你的身份发布消息——适用于个人助理。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来向家庭服务器进行身份验证。你有两个选择：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 转到 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级**——访问令牌显示在那里。
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
访问令牌授予对机器人 Matrix 账户的完全访问权限。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

除了提供访问令牌，你还可以给 Hermes 机器人的用户 ID 和密码。Hermes 将在启动时自动登录。这更简单，但意味着密码会存储在你的 `.env` 文件中。

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

# 可选：用户 ID（如果省略，则从令牌自动检测）
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

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享群组内保持每个参与者的上下文隔离

### 启动网关

配置完成后，启动 Matrix 网关：

```bash
hermes gateway
```

机器人应该连接到你的家庭服务器并在几秒钟内开始同步。发送一条消息给它——无论是私信还是它已加入的群组——进行测试。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 端到端加密（E2EE）

Hermes 支持 Matrix 端到端加密，因此你可以在加密的群组中与你的机器人聊天。

### 要求

E2EE 需要带有加密额外功能的 `matrix-nio` 库和 `libolm` C 库：

```bash
# 安装支持 E2EE 的 matrix-nio
pip install 'matrix-nio[e2e]'

# 或使用 hermes 额外功能安装
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

添加到你的 `~/.hermes/.env`：

```bash
MATRIX_ENCRYPTION=true
```

启用 E2EE 后，Hermes：

- 将加密密钥存储在 `~/.hermes/matrix/store/`
- 在首次连接时上传设备密钥
- 自动解密传入消息并加密传出消息
- 被邀请时自动加入加密群组

:::warning
如果你删除 `~/.hermes/matrix/store/` 目录，机器人将丢失其加密密钥。你将需要在 Matrix 客户端中重新验证设备。如果你想保留加密会话，请备份此目录。
:::

:::info
如果 `matrix-nio[e2e]` 未安装或 `libolm` 缺失，机器人会自动回退到普通（未加密）客户端。你会在日志中看到警告。
:::

## 主群组

你可以指定一个“主群组”，机器人可以在其中发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在任何机器人所在的 Matrix 群组中键入 `/sethome`。该群组将成为主群组。

### 手动配置

将此添加到你的 `~/.hermes/.env`：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

:::tip
要查找群组 ID：在 Element 中，进入群组 → **设置** → **高级** → **内部群组 ID** 显示在那里（以 `!` 开头）。
:::

## 故障排除

### 机器人不响应消息

**原因**：机器人尚未加入群组，或者 `MATRIX_ALLOWED_USERS` 不包含你的用户 ID。

**修复**：邀请机器人加入群组——它会在被邀请时自动加入。验证你的用户 ID 是否在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@用户:服务器` 格式）。重启网关。

### 启动时出现“身份验证失败”/“whoami 失败”

**原因**：访问令牌或家庭服务器 URL 不正确。

**修复**：验证 `MATRIX_HOMESERVER` 指向你的家庭服务器（包含 `https://`，无尾部斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效——用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回你的用户信息，则令牌有效。如果返回错误，请生成新令牌。

### “matrix-nio 未安装”错误

**原因**：未安装 `matrix-nio` Python 包。

**修复**：安装它：

```bash
pip install 'matrix-nio[e2e]'
```

或使用 Hermes 额外功能：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误/“无法解密事件”

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备不受信任。

**修复**：
1. 验证 `libolm` 是否已安装在你的系统上（参见上面的 E2EE 部分）。
2. 确保在你的 `.env` 中设置了 `MATRIX_ENCRYPTION=true`。
3. 在你的 Matrix 客户端（Element）中，转到机器人的个人资料 → **会话** → 验证/信任机器人的设备。
4. 如果机器人刚刚加入加密群组，它只能解密在它加入*之后*发送的消息。较早的消息无法访问。

### 同步问题/机器人落后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者家庭服务器速度慢。

**修复**：同步循环在出错时每 5 秒自动重试。检查 Hermes 日志中与同步相关的警告。如果机器人持续落后，请确保你的家庭服务器有足够的资源。

### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：错误的家庭服务器 URL、过期的访问令牌、家庭服务器无法访问。

### “用户不允许”/机器人忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `MATRIX_ALLOWED_USERS` 并重启网关。使用完整的 `@用户:服务器` 格式。

## 安全

:::warning
始终设置 `MATRIX_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，网关默认会拒绝所有用户作为安全措施。只添加你信任的用户 ID——授权用户可以完全访问代理的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

- **任何家庭服务器**：可与 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 家庭服务器配合使用。不需要特定的家庭服务器软件。
- **联邦**：如果你在联邦家庭服务器上，机器人可以与来自其他服务器的用户通信——只需将他们的完整 `@用户:服务器` ID 添加到 `MATRIX_ALLOWED_USERS`。
- **自动加入**：机器人自动接受群组邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图片、音频、视频和文件附件。媒体使用 Matrix 内容存储库 API 上传到你的家庭服务器。
