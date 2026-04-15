---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent 以及将 Docker 用作终端后端"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 的结合主要有两种不同的方式：

1. **在 Docker 中运行 Hermes** —— Agent 本身在容器内运行（本页面的主要内容）。
2. **将 Docker 作为终端后端** —— Agent 运行在你的宿主机上，但在 Docker 沙箱内执行命令（参见 [配置 → terminal.backend](./configuration.md)）。

本页面涵盖选项 1。容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在从宿主机挂载到 `/opt/data` 的单个目录中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

## 快速开始

如果你是第一次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器以运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需要执行一次此操作。强烈建议此时设置好一个聊天系统，以便网关（gateway）能够正常工作。

## 以网关模式运行

配置完成后，将容器作为持久网关（Telegram、Discord、Slack、WhatsApp 等）在后台运行：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## 以交互模式运行 (CLI 聊天)

要针对现有的数据目录开启交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

## 持久化卷

`/opt/data` 卷是所有 Hermes 状态的唯一事实来源。它映射到你宿主机的 `~/.hermes/` 目录，包含以下内容：

| 路径 | 内容 |
|------|----------|
| `.env` | API 密钥和机密信息 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 的性格/身份设定 |
| `sessions/` | 对话历史 |
| `memories/` | 持久化记忆库 |
| `skills/` | 已安装的技能 |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

:::warning 警告
切勿同时针对同一个数据目录运行两个 Hermes 容器 —— 会话文件和记忆库并非为并发访问而设计。
:::

## 环境变量转发

API 密钥是从容器内的 `/opt/data/.env` 读取的。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接使用 `-e` 标志会覆盖 `.env` 中的值。这对于 CI/CD 或不希望将密钥存储在磁盘上的机密管理器集成非常有用。

## Docker Compose 示例 {#docker-compose-example}

对于持久化的网关部署，使用 `docker-compose.yaml` 会很方便：

```yaml
version: "3.8"
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes:/opt/data
    # 如果不想使用 .env 文件，取消注释以转发特定的环境变量：
    # environment:
    #   - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    #   - OPENAI_API_KEY=${OPENAI_API_KEY}
    #   - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

使用 `docker compose up -d` 启动，并使用 `docker compose logs -f hermes` 查看日志。

## 资源限制

Hermes 容器需要适度的资源。建议的最低配置：

| 资源 | 最低要求 | 推荐配置 |
|----------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核 | 2 核 |
| 磁盘 (数据卷) | 500 MB | 2+ GB (随会话/技能增长) |

浏览器自动化（Playwright/Chromium）是最耗内存的功能。如果你不需要浏览器工具，1 GB 就足够了。如果启用浏览器工具，请至少分配 2 GB。

在 Docker 中设置限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## Dockerfile 的作用

官方镜像基于 `debian:13.4`，包含以下内容：

- 带有所有 Hermes 依赖项的 Python 3 (`pip install -e ".[all]"`)
- Node.js + npm（用于浏览器自动化和 WhatsApp 桥接）
- 带有 Chromium 的 Playwright (`npx playwright install --with-deps chromium`)
- 作为系统工具的 ripgrep 和 ffmpeg
- WhatsApp 桥接程序 (`scripts/whatsapp-bridge/`)

入口脚本 (`docker/entrypoint.sh`) 在首次运行时会引导数据卷：
- 创建目录结构（`sessions/`、`memories/`、`skills/` 等）
- 如果不存在 `.env`，则复制 `.env.example` → `.env`
- 如果缺失，则复制默认的 `config.yaml`
- 如果缺失，则复制默认的 `SOUL.md`
- 使用基于清单（manifest）的方法同步捆绑的技能（保留用户编辑）
- 然后使用你传递的任何参数运行 `hermes`

## 升级

拉取最新镜像并重新创建容器。你的数据目录不会被触动。

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

## 技能和凭据文件

当使用 Docker 作为执行环境时（不是上述方法，而是 Agent 在 Docker 沙箱内运行命令时），Hermes 会自动将技能目录（`~/.hermes/skills/`）和技能声明的任何凭据文件作为只读卷挂载到容器中。这意味着技能脚本、模板和引用在沙箱内均可用，无需手动配置。

SSH 和 Modal 后端也会进行同样的同步 —— 在执行每个命令之前，技能和凭据文件会通过 rsync 或 Modal 挂载 API 上传。

## 故障排除

### 容器立即退出

检查日志：`docker logs hermes`。常见原因：
- 缺失或无效的 `.env` 文件 —— 请先以交互方式运行以完成设置
- 如果运行并暴露了端口，可能存在端口冲突

### "Permission denied" 错误

容器默认以 root 身份运行。如果你宿主机的 `~/.hermes/` 是由非 root 用户创建的，权限通常可以正常工作。如果遇到错误，请确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

### 浏览器工具无法工作

Playwright 需要共享内存。在你的 Docker 运行命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络问题后网关未重新连接

`--restart unless-stopped` 标志可以处理大多数瞬时故障。如果网关卡住，请重启容器：

```sh
docker restart hermes
```

### 检查容器健康状况

```sh
docker logs --tail 50 hermes          # 查看最近日志
docker exec hermes hermes version     # 验证版本
docker stats hermes                    # 查看资源占用
```
