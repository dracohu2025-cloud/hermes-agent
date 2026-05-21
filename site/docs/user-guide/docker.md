---
sidebar_position: 7
title: "Docker"
description: "在 Docker 中运行 Hermes Agent，并将 Docker 作为终端后端"
---

<a id="hermes-agent-docker"></a>
# Hermes Agent — Docker

Hermes Agent 与 Docker 的交集有两种不同的方式：

1. **在 Docker 中运行 Hermes**——Agent 本身在容器内运行（本页主要关注点）
2. **Docker 作为终端后端**——Agent 在宿主机上运行，但每条命令都在一个单独的、持久的 Docker 沙箱容器中执行，该容器在 Hermes 进程生命周期内跨越工具调用、`/new` 和子 Agents 持续存在（参见[配置 → Docker 后端](./configuration.md#docker-backend)）

本页介绍的是第一种方式。容器将所有用户数据（配置、API 密钥、会话、技能、记忆）存储在宿主机的挂载目录 `/opt/data` 中。镜像本身是无状态的，可以通过拉取新版本进行升级，而不会丢失任何配置。

<a id="quick-start"></a>
## 快速开始

如果你是首次运行 Hermes Agent，请在宿主机上创建一个数据目录，并以交互方式启动容器来运行设置向导：

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将进入设置向导，它会提示你输入 API 密钥并将其写入 `~/.hermes/.env`。你只需执行一次。强烈建议此时为网关配置一个聊天系统以便其工作。

<a id="running-in-gateway-mode"></a>
## 以网关模式运行

配置完成后，以后台持久网关（Telegram、Discord、Slack、WhatsApp 等）的方式运行容器：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 暴露了网关的 [OpenAI 兼容 API 服务器](./features/api-server.md)和健康检查端点。如果你只使用聊天平台（Telegram、Discord 等），此端口是可选的；但如果你希望仪表盘或外部工具访问网关，则必须暴露。

注意：API 服务器由 `API_SERVER_ENABLED=true` 控制开关。如果要将其暴露到容器内部 `127.0.0.1` 之外，还需设置 `API_SERVER_HOST=0.0.0.0` 和 `API_SERVER_KEY`（至少 8 个字符——可使用 `openssl rand -hex 32` 生成）。示例：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -e API_SERVER_ENABLED=true \
  -e API_SERVER_HOST=0.0.0.0 \
  -e API_SERVER_KEY=your_api_key_here \
  -e API_SERVER_CORS_ORIGINS='*' \
  nousresearch/hermes-agent gateway run
```

在面向互联网的机器上开放任何端口都存在安全风险。除非你了解风险，否则不应这样做。

<a id="running-the-dashboard"></a>
## 运行仪表盘

内置的 Web 仪表盘作为可选副进程，在与网关相同的容器中运行。设置 `HERMES_DASHBOARD=1` 并暴露端口 `9119`，同时保留网关的 `8642` 端口：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

入口点会在后台启动 `hermes dashboard`（以非 root 用户 `hermes` 身份运行），然后通过 `exec` 执行主命令。仪表盘的输出在 `docker logs` 中以 `[dashboard]` 为前缀，便于与网关日志区分。
| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设为 `1`（或 `true` / `yes`）以在启动主命令时一并启动仪表板 | *(未设置 — 仪表板不启动)* |
| `HERMES_DASHBOARD_HOST` | 仪表板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 仪表板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_TUI` | 设为 `1` 以暴露浏览器内的聊天标签页（通过 PTY/WebSocket 嵌入 `hermes --tui`） | *(未设置)* |

默认的 `HERMES_DASHBOARD_HOST=0.0.0.0` 是必须的，这样宿主机才能通过发布的端口访问仪表板；在此情况下入口点会自动向 `hermes dashboard` 传递 `--insecure` 参数。如果你希望将仪表板限制为仅容器内访问（例如在 sidecar 中通过反向代理访问），可以覆盖为 `127.0.0.1`。

:::note
仪表板的侧进程**不受监护**——如果它崩溃了，将保持关闭状态直到容器重启。不支持将其作为独立容器运行：仪表板的网关存活检测需要与网关进程共享 PID 命名空间。
:::

<a id="running-interactively-cli-chat"></a>
## 交互式运行（CLI 聊天）

针对正在运行的数据目录打开交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者如果你已经在运行的容器中打开了终端（例如通过 Docker Desktop），直接运行：

```sh
/opt/hermes/.venv/bin/hermes
```

<a id="persistent-volumes"></a>
## 持久卷

`/opt/data` 卷是所有 Hermes 状态数据的单一真相来源。它映射到宿主机的 `~/.hermes/` 目录，包含以下内容：

| 路径 | 内容 |
|------|----------|
| `.env` | API 密钥和机密 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 人格/身份 |
| `sessions/` | 对话历史 |
| `memories/` | 持久记忆存储 |
| `skills/` | 已安装的技能 |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 皮肤 |

:::warning
切勿同时针对同一数据目录运行两个 Hermes **网关**容器——会话文件和记忆存储不支持并发写入访问。
:::

<a id="multi-profile-support"></a>
## 多配置文件支持

Hermes 支持[多个配置文件](../reference/profile-commands.md)——即独立的 `~/.hermes/` 目录，让你可以在单个安装中运行独立的 Agent（不同的 SOUL、技能、记忆、会话、凭据）。**在 Docker 下运行时，不建议使用 Hermes 内置的多配置文件功能。**

相反，推荐的模式是**每个配置文件对应一个容器**，每个容器将宿主机的独立目录绑定挂载为 `/opt/data`：

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
与在 Docker 中使用多个配置文件相比，采用独立容器的好处在于：

- **隔离性** — 每个容器拥有独立的文件系统、进程表和资源限制。一个配置中的崩溃、依赖变更或异常会话不会影响其他配置。
- **独立生命周期** — 可以分别升级、重启、暂停或回滚每个 Agent（执行 `docker restart hermes-work` 不会影响 `hermes-personal`）。
- **清晰的端口和网络隔离** — 每个网关绑定各自的主机端口；聊天平台或 API 服务器之间不存在串扰风险。
- **更简单的认知模型** — 容器即配置。备份、迁移和权限都跟随绑定挂载的目录，无需额外记忆 `--profile` 参数。
- **避免并发写风险** — 上述关于不要针对同一数据目录运行两个网关的警告，同样适用于单个容器内的多个配置。

在 Docker Compose 中，这意味着为每个配置声明一个服务，使用不同的 `container_name`、`volumes` 和 `ports`：

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

<a id="environment-variable-forwarding"></a>
## 环境变量传递

API 密钥从容器内的 `/opt/data/.env` 读取。你也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接使用 `-e` 标志会覆盖 `.env` 中的值。这对于不想将密钥写入磁盘的 CI/CD 或秘密管理器集成非常有用。

:::note 寻找将 Docker 作为**终端后端**的用法？
<a id="looking-for-docker-as-the-terminal-backend"></a>
本页面介绍如何在 Docker 内部运行 Hermes 本身。如果你希望 Hermes 在 Docker 沙箱容器内（每个 Hermes 进程对应一个持久容器）执行 Agent 的 `terminal`/`execute_code` 调用，那是另一个独立的配置块 —— `terminal.backend: docker` 加上 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_run_as_host_user` 和 `terminal.docker_extra_args`。完整设置参见[配置 → Docker 后端](configuration.md#docker-backend)。
:::

<a id="docker-compose-example"></a>
## Docker Compose 示例 {#docker-compose-example}

对于需要同时运行网关和仪表板的持久化部署，使用 `docker-compose.yaml` 会很方便：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"   # 网关 API
      - "9119:9119"   # 仪表板（仅在 HERMES_DASHBOARD=1 时可达）
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD=1
      # 取消注释以传递特定环境变量（代替使用 .env 文件）：
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```
从 `docker compose up -d` 启动，用 `docker compose logs -f` 查看日志。仪表盘输出会带有 `[dashboard]` 前缀，方便从网关日志中过滤。

<a id="resource-limits"></a>
## 资源限制

Hermes 容器需要中等资源。建议的最低配置如下：

| 资源 | 最低 | 推荐 |
|--------|---------|-------------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核 | 2 核 |
| 磁盘（数据卷） | 500 MB | 2+ GB（随会话/技能增长） |

浏览器自动化（Playwright/Chromium）是最消耗内存的功能。如果不需要浏览器工具，1 GB 就够用。如果启用了浏览器工具，至少分配 2 GB。

在 Docker 中设置限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

<a id="what-the-dockerfile-does"></a>
## Dockerfile 做了什么

官方镜像基于 `debian:13.4`，包含：

- Python 3 及所有 Hermes 依赖（`uv pip install -e ".[all]"`）
- Node.js + npm（用于浏览器自动化和 WhatsApp 桥接）
- Playwright 和 Chromium（`npx playwright install --with-deps chromium --only-shell`）
- ripgrep、ffmpeg、git 和 tini 作为系统工具
- **`docker-cli`** —— 使得容器内运行的 Agent 可以驱动宿主机的 Docker 守护进程（通过绑定挂载 `/var/run/docker.sock` 可选择启用），用于执行 `docker build`、`docker run`、容器检查等操作。
- **`openssh-client`** —— 启用容器内的 [SSH 终端后端](/user-guide/configuration#ssh-backend)。SSH 后端会调用系统 `ssh` 二进制程序；如果没有这个组件，在容器化安装中它会静默失败。
- WhatsApp 桥接（`scripts/whatsapp-bridge/`）

入口点脚本（`docker/entrypoint.sh`）会在首次运行时初始化数据卷：
- 创建目录结构（`sessions/`、`memories/`、`skills/` 等）
- 如果不存在 `.env` 文件，则将 `.env.example` 复制为 `.env`
- 如果缺少默认 `config.yaml`，则复制一份
- 如果缺少默认 `SOUL.md`，则复制一份
- 使用基于清单的方式同步内置技能（保留用户编辑内容）
- 当 `HERMES_DASHBOARD=1` 时，可选地启动 `hermes dashboard` 作为后台子进程（参见 [运行仪表盘](#running-the-dashboard)）
- 然后使用你传入的任何参数运行 `hermes`

:::warning
除非你让 `/opt/hermes/docker/entrypoint.sh` 留在命令链中，否则不要覆盖镜像的入口点。入口点会在网关状态文件创建之前将 root 权限降级为 `hermes` 用户。默认情况下，在官方镜像中以 root 身份启动 `hermes gateway run` 会被拒绝，因为这可能会在 `/opt/data` 中留下 root 所属的文件，并导致后续仪表盘或网关启动失败。只有在你主动接受这一风险时，才设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

<a id="upgrading"></a>
## 升级

拉取最新镜像并重新创建容器。你的数据目录不受影响。

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

<a id="skills-and-credential-files"></a>
## 技能与凭证文件

当使用 Docker 作为执行环境（不是上述方法，而是 Agent 在 Docker 沙箱内部运行命令——参见 [配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用复用同一个长期运行的容器，并自动将技能目录（`~/.hermes/skills/`）以及技能声明的任何凭证文件以只读卷的形式绑定挂载到该容器中。技能脚本、模板和引用无需手动配置即可在沙箱内使用；由于容器在 Hermes 进程的生命周期内一直存在，你安装的任何依赖项或写入的文件都会保留到下一次工具调用。

同样的同步机制也适用于 SSH 和 Modal 后端——在执行每条命令之前，技能和凭证文件会通过 rsync 或 Modal mount API 上传。

<a id="connecting-to-local-inference-servers-vllm-ollama-etc"></a>
## 连接本地推理服务器（vLLM、Ollama 等）

当 Hermes 运行在 Docker 中，而你的推理服务器（vLLM、Ollama、text-generation-inference 等）也运行在宿主机上或另一个容器中时，网络方面需要额外注意。

<a id="docker-compose-recommended"></a>
### Docker Compose（推荐）

将两个服务放在同一个 Docker 网络上。这是最可靠的方式：

```yaml
services:
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --served-model-name my-model
      --host 0.0.0.0
      --port 8000
    ports:
      - "8000:8000"
    networks:
      - hermes-net
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

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

networks:
  hermes-net:
    driver: bridge
```

然后在你的 `~/.hermes/config.yaml` 中使用 **容器名称** 作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::tip 要点
<a id="key-points"></a>
- 使用**容器名称**（`vllm`）作为主机名——不要用 `localhost` 或 `127.0.0.1`，因为它们指向的是 Hermes 容器本身。
- `model` 的值必须与你传递给 vLLM 的 `--served-model-name` 一致。
- 将 `api_key` 设置为任意非空字符串（vLLM 需要该头部但默认不校验）。
- `base_url` **不要**包含末尾斜杠。
:::

<a id="standalone-docker-run-no-compose"></a>
### 独立 Docker 运行（无 Compose）

如果你的推理服务器直接在宿主机上运行（不在 Docker 内），macOS/Windows 上使用 `host.docker.internal`，Linux 上使用 `--network host`：

**macOS / Windows：**

```sh
docker run -d \
  --name hermes \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://host.docker.internal:8000/v1
  api_key: "none"
```
**Linux（主机网络）：**

```sh
docker run -d \
  --name hermes \
  --network host \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://127.0.0.1:8000/v1
  api_key: "none"
```

:::warning 使用 `--network host` 时，`-p` 标志会被忽略——所有容器端口将直接暴露在主机上。
:::

<a id="verifying-connectivity"></a>
### 验证连通性

在 Hermes 容器内部，确认推理服务器可达：

<a id="with-network-host-the-p-flag-is-ignored-all-container-ports-are-directly-exposed-on-the-host"></a>
```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

你应该会看到一个列出已提供模型的 JSON 响应。如果失败，请检查：

1. 两个容器位于同一 Docker 网络（`docker network inspect hermes-net`）
2. 推理服务器监听在 `0.0.0.0` 而不是 `127.0.0.1`
3. 端口号匹配

<a id="ollama"></a>
### Ollama

Ollama 的工作方式相同。如果 Ollama 运行在主机上，请使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（Linux 使用 `--network host`）。如果 Ollama 在自己的容器中且位于同一 Docker 网络上：

```yaml
model:
  provider: custom
  model: llama3
  base_url: http://ollama:11434/v1
  api_key: "none"
```

<a id="troubleshooting"></a>
## 故障排除

<a id="container-exits-immediately"></a>
### 容器立即退出

检查日志：`docker logs hermes`。常见原因：
- 缺少或无效的 `.env` 文件——先以交互方式运行以完成设置
- 如果使用暴露端口运行，则可能存在端口冲突

<a id="permission-denied-errors"></a>
### “权限被拒绝”错误

容器的入口点通过 `gosu` 将权限降级为非 root 的 `hermes` 用户（UID 10000）。如果你主机的 `~/.hermes/` 目录由不同的 UID 所有，请设置 `HERMES_UID`/`HERMES_GID` 以匹配你的主机用户，或确保数据目录可写：

```sh
chmod -R 755 ~/.hermes
```

<a id="browser-tools-not-working"></a>
### 浏览器工具无法工作

Playwright 需要共享内存。在 Docker run 命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

<a id="gateway-not-reconnecting-after-network-issues"></a>
### 网关在网络问题后无法重新连接

`--restart unless-stopped` 标志可处理大多数临时故障。如果网关卡住，请重启容器：

```sh
docker restart hermes
```

<a id="checking-container-health"></a>
### 检查容器健康状况

```sh
docker logs --tail 50 hermes          # Recent logs
docker run -it --rm nousresearch/hermes-agent:latest version     # Verify version
docker stats hermes                    # Resource usage
```
