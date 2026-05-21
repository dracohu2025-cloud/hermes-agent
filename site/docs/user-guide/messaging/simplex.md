<a id="simplex-chat"></a>
# SimpleX Chat

[SimpleX Chat](https://simplex.chat/) 是一个私密、去中心化的消息平台，用户自己掌控联系人和群组。与其他平台不同，SimpleX 不分配持久的用户 ID——每个联系人在连接时由一个不透明的内部 ID 标识，这使其成为最私密的即时通讯工具之一。

<a id="prerequisites"></a>
## 前提条件

- **simplex-chat** CLI 已安装并以守护进程方式运行
- Python 包 **websockets**（`pip install websockets`）

<a id="install-simplex-chat"></a>
## 安装 simplex-chat

从 [simplex-chat GitHub releases](https://github.com/simplex-chat/simplex-chat/releases) 页面下载最新版本，或通过 Docker 安装：

```bash
# Linux / macOS 二进制文件
curl -L https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-22_04-x86-64 -o simplex-chat
chmod +x simplex-chat

# 或使用 Docker
docker run -p 5225:5225 simplexchat/simplex-chat -p 5225
```

<a id="start-the-daemon"></a>
## 启动守护进程

```bash
simplex-chat -p 5225
```

守护进程默认在 `ws://127.0.0.1:5225` 上监听 WebSocket。

<a id="configure-hermes"></a>
## 配置 Hermes

<a id="via-setup-wizard"></a>
### 通过设置向导

```bash
hermes setup gateway
```

选择 **SimpleX Chat** 并按提示操作。

<a id="via-environment-variables"></a>
### 通过环境变量

将这些内容添加到 `~/.hermes/.env`：

```
SIMPLEX_WS_URL=ws://127.0.0.1:5225
SIMPLEX_ALLOWED_USERS=<contact-id-1>,<contact-id-2>
SIMPLEX_HOME_CHANNEL=<contact-id>
```

| 变量 | 是否必需 | 描述 |
|---|---|---|
| `SIMPLEX_WS_URL` | 是 | simplex-chat 守护进程的 WebSocket URL |
| `SIMPLEX_ALLOWED_USERS` | 推荐 | 允许使用该 agent 的联系人 ID，以逗号分隔 |
| `SIMPLEX_ALLOW_ALL_USERS` | 可选 | 设为 `true` 以允许所有联系人（请谨慎使用） |
| `SIMPLEX_HOME_CHANNEL` | 可选 | 用于 cron 任务投递的默认联系人 ID |
| `SIMPLEX_HOME_CHANNEL_NAME` | 可选 | 主频道的人类可读标签 |

<a id="find-your-contact-id"></a>
## 查找你的联系人 ID

启动守护进程后，与你的 agent 联系人打开一个对话。联系人 ID 会出现在会话日志中，或通过 `hermes send_message action=list` 查看。

<a id="authorization"></a>
## 授权

默认情况下 **所有联系人被拒绝**。你必须执行以下操作之一：

1. 将 `SIMPLEX_ALLOWED_USERS` 设置为以逗号分隔的联系人 ID 列表，或
2. 使用 **DM 配对**——向机器人发送任意消息，它会回复一个配对码。通过 `hermes gateway pair` 输入该码。

<a id="using-simplex-with-cron-jobs"></a>
## 在 cron 任务中使用 SimpleX

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="simplex",          # 使用 SIMPLEX_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或指定特定联系人：

```python
send_message(target="simplex:<contact-id>", message="Done!")
```

<a id="privacy-notes"></a>
## 隐私说明

- SimpleX 从不透露电话号码或电子邮件地址——联系人使用不透明 ID
- Hermes 与守护进程之间的连接是本地 WebSocket（`ws://127.0.0.1:5225`）——数据不会离开你的机器
- 消息在到达守护进程之前已由 SimpleX 协议进行端到端加密

<a id="troubleshooting"></a>
## 故障排除

**"无法连接到守护进程"**——确保 `simplex-chat -p 5225` 正在运行，并且端口与 `SIMPLEX_WS_URL` 匹配。
**"websockets not installed"** — 运行 `pip install websockets`。

**收不到消息** — 检查联系人的 ID 是否在 `SIMPLEX_ALLOWED_USERS` 中，或者通过 DM 配对进行批准。
