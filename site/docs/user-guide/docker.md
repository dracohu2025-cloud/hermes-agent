# Hermes Agent 与 Docker

想在宿主机上不安装任何包就能运行 Hermes Agent 吗？这个方案能帮你搞定。

这让你可以在容器中运行智能体，下面列出了最相关的几种运行模式。

容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在从宿主机挂载到 `/opt/data` 的单一目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

这会让你进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。这个操作只需要做一次。强烈建议在此阶段为网关设置一个聊天系统以便工作。

## 以网关模式运行

配置完成后，以后台方式运行容器作为持久化网关（Telegram、Discord、Slack、WhatsApp 等）：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## 交互式运行（CLI 聊天）

要针对一个正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

## 升级

拉取最新的镜像并重新创建容器。你的数据目录保持不变。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```
