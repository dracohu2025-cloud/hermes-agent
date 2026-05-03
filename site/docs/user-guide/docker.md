---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent，并将 Docker 用作终端后端"
---

# Hermes Agent — Docker {#hermes-agent-docker}

Docker 与 Hermes Agent 有两种不同的结合方式：

1. **在 Docker 中运行 Hermes** — Agent 本身在容器内运行（本页主要关注）
2. **Docker 作为终端后端** — Agent 在宿主机上运行，但在 Docker 沙箱中执行命令（参见 [配置 → terminal.backend](./configuration.md)）

本页介绍第一种方式。容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在宿主机挂载到 `/opt/data` 的单个目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始 {#quick-start}

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这会进入设置向导，提示你输入 API 密钥，并将其写入 `~/.hermes/.env`。你只需执行一次。强烈建议此时为网关设置一个聊天系统。

## 以网关模式运行 {#running-in-gateway-mode}

配置完成后，以后台持久化网关（Telegram、Discord、Slack、WhatsApp 等）的方式运行容器：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 暴露了网关的 [OpenAI 兼容 API 服务器](./features/api-server.md) 和健康检查端点。如果你只使用聊天平台（Telegram、Discord 等），此端口是可选的；但如果需要仪表盘或外部工具访问网关，则必须暴露。

在面向互联网的机器上开放任何端口都存在安全风险。除非你了解相关风险，否则不应这样做。

## 运行仪表盘 {#running-the-dashboard}

内置的 Web 仪表盘可以作为独立容器与网关一起运行。

要将仪表盘作为独立容器运行，请将其指向网关的健康检查端点，以便跨容器检测网关状态：

```sh
docker run -d \
  --name hermes-dashboard \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 9119:9119 \
  -e GATEWAY_HEALTH_URL=http://$HOST_IP:8642 \
  nousresearch/hermes-agent dashboard
```

将 `$HOST_IP` 替换为运行网关容器的机器的 IP 地址（例如 `192.168.1.100`），或者如果两个容器共享同一个网络，则使用 Docker 网络主机名（参见下面的 [Compose 示例](#docker-compose-example)）。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `GATEWAY_HEALTH_URL` | 网关 API 服务器的基础 URL，例如 `http://gateway:8642` | *（未设置 — 仅本地 PID 检查）* |
| `GATEWAY_HEALTH_TIMEOUT` | 健康检查超时时间（秒） | `3` |

如果没有设置 `GATEWAY_HEALTH_URL`，仪表盘会回退到本地进程检测——这仅在网关运行在同一容器或同一宿主机上时才有效。
## 交互式运行（CLI 聊天） {#running-interactively-cli-chat}

要针对正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果你已经在运行的容器中打开了终端（例如通过 Docker Desktop），只需运行：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久化卷 {#persistent-volumes}

`/opt/data` 卷是所有 Hermes 状态的唯一真实来源。它映射到主机的 `~/.hermes/` 目录，包含以下内容：

| 路径 | 内容 |
|------|------|
| `.env` | API 密钥和机密信息 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 个性/身份 |
| `sessions/` | 对话历史 |
| `memories/` | 持久化记忆存储 |
| `skills/` | 已安装的技能 |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

:::warning
切勿同时运行两个 Hermes **gateway** 容器指向同一个数据目录——会话文件和记忆存储不支持并发写入。在 gateway 旁边运行 dashboard 容器是安全的，因为 dashboard 只读取数据。
:::

## 多配置文件支持 {#multi-profile-support}

Hermes 支持[多个配置文件](../reference/profile-commands.md)——独立的 `~/.hermes/` 目录，让你从单个安装中运行独立的 Agent（不同的 SOUL、技能、记忆、会话、凭据）。**在 Docker 下运行时，不建议使用 Hermes 内置的多配置文件功能。**

相反，推荐的模式是**每个配置文件一个容器**，每个容器将其自己的主机目录绑定挂载为 `/opt/data`：

```sh
# 工作配置文件
docker run -d \
  --name hermes-work \
  --restart unless-stopped \
  -v ~/.hermes-work:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run

# 个人配置文件
docker run -d \
  --name hermes-personal \
  --restart unless-stopped \
  -v ~/.hermes-personal:/opt/data \
  -p 8643:8642 \
  nousresearch/hermes-agent gateway run
```

为什么在 Docker 中使用独立容器而不是配置文件：

- **隔离性**——每个容器拥有自己的文件系统、进程表和资源限制。一个配置文件中的崩溃、依赖变更或失控会话不会影响另一个。
- **独立生命周期**——分别升级、重启、暂停或回滚每个 Agent（`docker restart hermes-work` 不会影响 `hermes-personal`）。
- **清晰的端口和网络分离**——每个 gateway 绑定自己的主机端口；聊天平台或 API 服务器之间没有串扰风险。
- **更简单的思维模型**——容器就是配置文件。备份、迁移和权限都遵循绑定挂载的目录，无需记住额外的 `--profile` 标志。
- **避免并发写入风险**——上面关于切勿同时运行两个 gateway 指向同一数据目录的警告同样适用于单个容器内的配置文件。

在 Docker Compose 中，这只需为每个配置文件声明一个服务，并设置不同的 `container_name`、`volumes` 和 `ports`：
```yaml
services:
  hermes-work:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-work
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes-work:/opt/data

  hermes-personal:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-personal
    restart: unless-stopped
    command: gateway run
    ports:
      - "8643:8642"
    volumes:
      - ~/.hermes-personal:/opt/data
```

## 环境变量转发 {#environment-variable-forwarding}

API 密钥从容器内的 `/opt/data/.env` 文件中读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接使用 `-e` 标志会覆盖 `.env` 中的值。这在 CI/CD 或密钥管理器集成中非常有用，因为你不想把密钥留在磁盘上。

## Docker Compose 示例 {#docker-compose-example}

对于需要同时运行网关和仪表盘的持久化部署，使用 `docker-compose.yaml` 会更方便：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net
    # 取消注释以转发特定环境变量（代替使用 .env 文件）：
    # environment:
    #   - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    #   - OPENAI_API_KEY=${OPENAI_API_KEY}
    #   - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"

  dashboard:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-dashboard
    restart: unless-stopped
    command: dashboard --host 0.0.0.0 --insecure
    ports:
      - "9119:9119"
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - GATEWAY_HEALTH_URL=http://hermes:8642
    networks:
      - hermes-net
    depends_on:
      - hermes
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"

networks:
  hermes-net:
    driver: bridge
```

使用 `docker compose up -d` 启动，用 `docker compose logs -f` 查看日志。

## 资源限制 {#resource-limits}

Hermes 容器需要适中的资源。推荐的最低配置如下：

| 资源 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核 | 2 核 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随会话/技能增长） |

浏览器自动化（Playwright/Chromium）是最消耗内存的功能。如果你不需要浏览器工具，1 GB 就足够了。如果启用了浏览器工具，请至少分配 2 GB。

在 Docker 中设置限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## Dockerfile 做了什么 {#what-the-dockerfile-does}

官方镜像基于 `debian:13.4`，并包含以下内容：

- Python 3 及所有 Hermes 依赖（`uv pip install -e ".[all]"`）
- Node.js + npm（用于浏览器自动化和 WhatsApp 桥接）
- 带 Chromium 的 Playwright（`npx playwright install --with-deps chromium --only-shell`）
- ripgrep、ffmpeg、git 和 tini 作为系统工具
- **`docker-cli`** —— 这样容器内运行的 Agent 可以驱动宿主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 来启用），用于 `docker build`、`docker run`、容器检查等操作。
- **`openssh-client`** —— 支持从容器内部使用 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统的 `ssh` 二进制文件；如果没有这个包，在容器化安装中会静默失败。
- WhatsApp 桥接（`scripts/whatsapp-bridge/`）
入口脚本（`docker/entrypoint.sh`）会在首次运行时初始化数据卷：
- 创建目录结构（`sessions/`、`memories/`、`skills/` 等）
- 如果不存在 `.env` 文件，则将 `.env.example` 复制为 `.env`
- 如果缺少默认的 `config.yaml`，则复制一份
- 如果缺少默认的 `SOUL.md`，则复制一份
- 使用基于清单的方式同步内置技能（保留用户编辑的内容）
- 然后根据你传入的参数运行 `hermes`

## 升级 {#upgrading}

拉取最新镜像并重新创建容器。你的数据目录不会受影响。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

或者使用 Docker Compose：

```sh
docker compose pull
docker compose up -d
```

## 技能与凭证文件 {#skills-and-credential-files}

当使用 Docker 作为执行环境时（不是上述方法，而是 Agent 在 Docker 沙箱内运行命令），Hermes 会自动将技能目录（`~/.hermes/skills/`）以及技能声明的任何凭证文件以只读卷的形式绑定挂载到容器中。这意味着技能脚本、模板和引用在沙箱内可直接使用，无需手动配置。

SSH 和 Modal 后端也会执行相同的同步操作——在执行每条命令之前，技能和凭证文件会通过 rsync 或 Modal 挂载 API 上传。

## 故障排除 {#troubleshooting}

### 容器立即退出 {#container-exits-immediately}

检查日志：`docker logs hermes`。常见原因：
- `.env` 文件缺失或无效——先以交互模式运行以完成设置
- 如果使用暴露端口，可能存在端口冲突

### "Permission denied" 错误 {#permission-denied-errors}

容器的入口脚本会通过 `gosu` 将权限降级为非 root 的 `hermes` 用户（UID 10000）。如果你的宿主机 `~/.hermes/` 由不同的 UID 拥有，请设置 `HERMES_UID`/`HERMES_GID` 以匹配你的宿主机用户，或者确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

### 浏览器工具无法工作 {#browser-tools-not-working}

Playwright 需要共享内存。在 Docker run 命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络问题后网关无法重新连接 {#gateway-not-reconnecting-after-network-issues}

`--restart unless-stopped` 标志可以处理大多数临时故障。如果网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状态 {#checking-container-health}

```sh
docker logs --tail 50 hermes          # 最近的日志
docker run -it --rm nousresearch/hermes-agent:latest version     # 验证版本
docker stats hermes                    # 资源使用情况
```
