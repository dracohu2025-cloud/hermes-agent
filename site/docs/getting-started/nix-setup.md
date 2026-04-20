---
sidebar_position: 3
title: "Nix & NixOS 安装配置"
description: "使用 Nix 安装和部署 Hermes Agent — 从快速 `nix run` 到完全声明式的 NixOS 模块（含容器模式）"
---

# Nix & NixOS 安装配置 {#nix-nixos-setup}

Hermes Agent 提供了一个 Nix flake，包含三层集成方式：

| 层级 | 适用人群 | 获得内容 |
|------|---------|---------|
| **`nix run` / `nix profile install`** | 任何 Nix 用户（macOS、Linux） | 预构建二进制文件，包含所有依赖 — 之后使用标准 CLI 工作流 |
| **NixOS 模块（原生）** | NixOS 服务器部署 | 声明式配置、加固的 systemd 服务、托管密钥 |
| **NixOS 模块（容器）** | 需要自我修改的 Agent | 以上全部，外加一个持久化的 Ubuntu 容器，Agent 可以在其中执行 `apt`/`pip`/`npm install` |

:::info 与标准安装的区别
`curl | bash` 安装器自行管理 Python、Node 和依赖。Nix flake 替代了这一切 — 每个 Python 依赖都是由 [uv2nix](https://github.com/pyproject-nix/uv2nix) 构建的 Nix derivation，运行时工具（Node.js、git、ripgrep、ffmpeg）被包装到二进制文件的 PATH 中。没有运行时的 pip，没有 venv 激活，没有 `npm install`。

**对于非 NixOS 用户**，这只改变了安装步骤。之后的所有操作（`hermes setup`、`hermes gateway install`、编辑配置）与标准安装完全一致。

<a id="what-s-different-from-the-standard-install"></a>
**对于 NixOS 模块用户**，整个生命周期都不同：配置放在 `configuration.nix` 中，密钥通过 sops-nix/agenix 管理，服务是一个 systemd 单元，CLI 配置命令被禁用。你管理 hermes 的方式与管理任何其他 NixOS 服务相同。
:::

## 前置要求 {#prerequisites}

- **已启用 flakes 的 Nix** — 推荐 [Determinate Nix](https://install.determinate.systems)（默认启用 flakes）
- 所用服务的 **API 密钥**（至少需要一个 OpenRouter 或 Anthropic 的密钥）

---

## 快速开始（任何 Nix 用户） {#quick-start-any-nix-user}

无需克隆仓库。Nix 会自动获取、构建并运行所有内容：

```bash
# 直接运行（首次使用时会构建，之后使用缓存）
nix run github:NousResearch/hermes-agent -- setup
nix run github:NousResearch/hermes-agent -- chat

# 或持久化安装
nix profile install github:NousResearch/hermes-agent
hermes setup
hermes chat
```

执行 `nix profile install` 后，`hermes`、`hermes-agent` 和 `hermes-acp` 就会加入你的 PATH。从此之后的工作流与[标准安装](./installation.md)完全一致 — `hermes setup` 会引导你选择提供商，`hermes gateway install` 会设置 launchd（macOS）或 systemd 用户服务，配置文件存放在 `~/.hermes/`。

<details>
<summary><strong>从本地克隆构建</strong></summary>

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
nix build
./result/bin/hermes setup
```

</details>

---

## NixOS 模块 {#nixos-module}

该 flake 导出了 `nixosModules.default` — 一个完整的 NixOS 服务模块，以声明式方式管理用户创建、目录、配置生成、密钥、文档和服务生命周期。

:::note
此模块需要 NixOS。对于非 NixOS 系统（macOS、其他 Linux 发行版），请使用上述的 `nix profile install` 和标准 CLI 工作流。
:::

### 添加 Flake 输入 {#add-the-flake-input}

```nix
# /etc/nixos/flake.nix（或你的系统 flake）
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    hermes-agent.url = "github:NousResearch/hermes-agent";
  };

  outputs = { nixpkgs, hermes-agent, ... }: {
    nixosConfigurations.your-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        hermes-agent.nixosModules.default
        ./configuration.nix
      ];
    };
  };
}
```

### 最小配置 {#minimal-configuration}

```nix
# configuration.nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
    addToSystemPackages = true;
  };
}
```

就这些。`nixos-rebuild switch` 会创建 `hermes` 用户、生成 `config.yaml`、接入密钥并启动 gateway — 这是一个长期运行的服务，负责将 Agent 连接到消息平台（Telegram、Discord 等）并监听传入消息。
:::warning 需要密钥
上面的 `environmentFiles` 行假设你已经配置了 [sops-nix](https://github.com/Mic92/sops-nix) 或 [agenix](https://github.com/ryantm/agenix)。文件中至少应包含一个 LLM 提供商的密钥（例如 `OPENROUTER_API_KEY=sk-or-...`）。完整配置请参阅 [密钥管理](#secrets-management)。如果你还没有密钥管理工具，可以先用一个普通文件作为起点——但要确保它不是全局可读的：
<a id="secrets-are-required"></a>

```bash
echo "OPENROUTER_API_KEY=sk-or-your-key" | sudo install -m 0600 -o hermes /dev/stdin /var/lib/hermes/env
```

```nix
services.hermes-agent.environmentFiles = [ "/var/lib/hermes/env" ];
```
:::

:::tip addToSystemPackages
设置 `addToSystemPackages = true` 会做两件事：把 `hermes` CLI 放到系统 PATH 上，**并且**全局设置 `HERMES_HOME`，这样交互式 CLI 就能和 gateway 服务共享状态（会话、技能、cron）。如果不设置，在 shell 里运行 `hermes` 会创建一个独立的 `~/.hermes/` 目录。
:::

### 感知容器的 CLI {#container-aware-cli}

:::info
当 `container.enable = true` 且 `addToSystemPackages = true` 时，主机上的**每一个** `hermes` 命令都会自动路由到受管理的容器中。这意味着你的交互式 CLI 会话和 gateway 服务运行在同一个环境里——可以使用容器中安装的所有包和工具。

- 路由是透明的：`hermes chat`、`hermes sessions list`、`hermes version` 等命令在底层都会 exec 进容器
- 所有 CLI 标志都会原样转发
- 如果容器没有运行，CLI 会短暂重试（交互式使用会显示 5 秒的 spinner，脚本则静默等待 10 秒），然后给出明确的错误——不会静默回退
- 如果你在开发 hermes 代码库，可以设置 `HERMES_DEV=1` 来绕过容器路由，直接运行本地 checkout

设置 `container.hostUsers` 可以创建 `~/.hermes` 到服务状态目录的符号链接，这样主机 CLI 和容器就能共享会话、配置和记忆：

```nix
services.hermes-agent = {
  container.enable = true;
  container.hostUsers = [ "your-username" ];
  addToSystemPackages = true;
};
```

`hostUsers` 中列出的用户会自动加入 `hermes` 组，以获得文件权限。

**Podman 用户：** NixOS 服务以 root 身份运行容器。Docker 用户通过 `docker` 组 socket 获得访问权限，但 Podman 的 rootful 容器需要 sudo。为你的容器运行时配置免密 sudo：

```nix
security.sudo.extraRules = [{
  users = [ "your-username" ];
  commands = [{
    command = "/run/current-system/sw/bin/podman";
    options = [ "NOPASSWD" ];
  }];
}];
```

CLI 会自动检测何时需要 sudo 并透明地使用它。如果没有这个配置，你就需要手动运行 `sudo hermes chat`。
:::

### 验证是否正常工作 {#verify-it-works}

执行 `nixos-rebuild switch` 后，检查服务是否正在运行：

```bash
# 检查服务状态
systemctl status hermes-agent

# 查看日志（按 Ctrl+C 停止）
journalctl -u hermes-agent -f

# 如果 addToSystemPackages 为 true，测试 CLI
hermes version
hermes config       # 显示生成的配置
```

### 选择部署模式 {#choosing-a-deployment-mode}

该模块支持两种模式，由 `container.enable` 控制：

| | **Native**（默认） | **Container** |
|---|---|---|
| 运行方式 | 主机上的加固 systemd 服务 | 持久化的 Ubuntu 容器，`/nix/store` 绑定挂载 |
| 安全性 | `NoNewPrivileges`、`ProtectSystem=strict`、`PrivateTmp` | 容器隔离，内部以非特权用户运行 |
| Agent 能否自行安装包 | 不能——只能使用 Nix 提供的 PATH 上的工具 | 可以——`apt`、`pip`、`npm` 安装的包在重启后仍然保留 |
| 配置界面 | 相同 | 相同 |
| 适用场景 | 标准部署、最高安全性、可复现性 | Agent 需要运行时安装包、可变环境、实验性工具 |

启用容器模式只需加一行：

```nix
{
  services.hermes-agent = {
    enable = true;
    container.enable = true;
    # ... 其余配置完全相同
  };
}
```
:::info
容器模式会通过 `mkDefault` 自动启用 `virtualisation.docker.enable`。如果你用 Podman，把 `container.backend` 设为 `"podman"`，并把 `virtualisation.docker.enable` 设为 `false`。
:::

---

## 配置 {#configuration}

### 声明式设置 {#declarative-settings}

`settings` 选项接受任意 attrset，会被渲染成 `config.yaml`。它支持在多个模块定义之间做深度合并（通过 `lib.recursiveUpdate`），所以你可以把配置拆到多个文件里：

```nix
# base.nix
services.hermes-agent.settings = {
  model.default = "anthropic/claude-sonnet-4";
  toolsets = [ "all" ];
  terminal = { backend = "local"; timeout = 180; };
};

# personality.nix
services.hermes-agent.settings = {
  display = { compact = false; personality = "kawaii"; };
  memory = { memory_enabled = true; user_profile_enabled = true; };
};
```

两者在求值时会被深度合并。Nix 声明的键总是优先于磁盘上已有 `config.yaml` 里的同名键，但 **Nix 没碰过的用户添加的键会被保留**。也就是说，如果 Agent 或手动编辑添加了 `skills.disabled`、`streaming.enabled` 这类键，执行 `nixos-rebuild switch` 后它们依然存在。

:::note 模型名称
<a id="model-naming"></a>
`settings.model.default` 要用你的提供商所要求的模型标识符。用 [OpenRouter](https://openrouter.ai)（默认）时，格式类似 `"anthropic/claude-sonnet-4"` 或 `"google/gemini-3-flash"`。如果你直连某个提供商（Anthropic、OpenAI），把 `settings.model.base_url` 指向他们的 API，并使用他们的原生模型 ID（例如 `"claude-sonnet-4-20250514"`）。不设置 `base_url` 时，Hermes 默认走 OpenRouter。
:::

:::tip 发现可用的配置键
<a id="discovering-available-config-keys"></a>
运行 `nix build .#configKeys && cat result`，可以看到从 Python 的 `DEFAULT_CONFIG` 中提取出的所有叶子配置键。你可以把现有的 `config.yaml` 直接贴进 `settings` attrset —— 结构是一一对应的。
:::

<details>
<summary><strong>完整示例：所有常用自定义设置</strong></summary>

```nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    container.enable = true;

    # ── 模型 ──────────────────────────────────────────────────────────
    settings = {
      model = {
        base_url = "https://openrouter.ai/api/v1";
        default = "anthropic/claude-opus-4.6";
      };
      toolsets = [ "all" ];
      max_turns = 100;
      terminal = { backend = "local"; cwd = "."; timeout = 180; };
      compression = {
        enabled = true;
        threshold = 0.85;
        summary_model = "google/gemini-3-flash-preview";
      };
      memory = { memory_enabled = true; user_profile_enabled = true; };
      display = { compact = false; personality = "kawaii"; };
      agent = { max_turns = 60; verbose = false; };
    };

    # ── 密钥 ────────────────────────────────────────────────────────
    environmentFiles = [ config.sops.secrets."hermes-env".path ];

    # ── 文档 ──────────────────────────────────────────────────────
    documents = {
      "USER.md" = ./documents/USER.md;
    };

    # ── MCP 服务器 ────────────────────────────────────────────────────
    mcpServers.filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };

    # ── 容器选项 ──────────────────────────────────────────────
    container = {
      image = "ubuntu:24.04";
      backend = "docker";
      hostUsers = [ "your-username" ];
      extraVolumes = [ "/home/user/projects:/projects:rw" ];
      extraOptions = [ "--gpus" "all" ];
    };

    # ── 服务调优 ─────────────────────────────────────────────────
    addToSystemPackages = true;
    extraArgs = [ "--verbose" ];
    restart = "always";
    restartSec = 5;
  };
}
```

</details>

### 逃生通道：自带配置 {#escape-hatch-bring-your-own-config}

如果你想完全在 Nix 之外管理 `config.yaml`，可以用 `configFile`：

```nix
services.hermes-agent.configFile = /etc/hermes/config.yaml;
```

这会彻底绕过 `settings` —— 不做合并，也不生成文件。每次激活时，该文件会被原样复制到 `$HERMES_HOME/config.yaml`。
### 自定义速查表 {#customization-cheatsheet}

Nix 用户最常想改的东西，快速参考：

| 我想…… | 选项 | 示例 |
|---|---|---|
| 更换 LLM 模型 | `settings.model.default` | `"anthropic/claude-sonnet-4"` |
| 使用不同的提供商接口 | `settings.model.base_url` | `"https://openrouter.ai/api/v1"` |
| 添加 API 密钥 | `environmentFiles` | `[ config.sops.secrets."hermes-env".path ]` |
| 给 Agent 设定个性 | `${services.hermes-agent.stateDir}/.hermes/SOUL.md` | 直接管理该文件 |
| 添加 MCP 工具服务器 | `mcpServers.&lt;name&gt;` | 参见 [MCP 服务器](#mcp-servers) |
| 将主机目录挂载到容器 | `container.extraVolumes` | `[ "/data:/data:rw" ]` |
| 向容器传递 GPU 访问权限 | `container.extraOptions` | `[ "--gpus" "all" ]` |
| 使用 Podman 替代 Docker | `container.backend` | `"podman"` |
| 在主机 CLI 和容器之间共享状态 | `container.hostUsers` | `[ "sidbin" ]` |
| 向服务 PATH 添加工具（仅原生模式） | `extraPackages` | `[ pkgs.pandoc pkgs.imagemagick ]` |
| 使用自定义基础镜像 | `container.image` | `"ubuntu:24.04"` |
| 覆盖 hermes 软件包 | `package` | `inputs.hermes-agent.packages.${system}.default.override { ... }` |
| 更改状态目录 | `stateDir` | `"/opt/hermes"` |
| 设置 Agent 的工作目录 | `workingDirectory` | `"/home/user/projects"` |

---

## 密钥管理 {#secrets-management}

:::danger 永远不要把 API 密钥放在 `settings` 或 `environment` 里
Nix 表达式中的值最终会进入 `/nix/store`，而这是全局可读的。请始终使用 `environmentFiles` 配合密钥管理工具。
:::

`environment`（非敏感变量）和 `environmentFiles`（密钥文件）都会在激活时（`nixos-rebuild switch`）合并到 `$HERMES_HOME/.env` 中。Hermes 每次启动都会读取这个文件，所以修改后只需执行 `systemctl restart hermes-agent` 即可生效——不需要重建容器。
<a id="never-put-api-keys-in-settings-or-environment"></a>

### sops-nix {#sops-nix}

```nix
{
  sops = {
    defaultSopsFile = ./secrets/hermes.yaml;
    age.keyFile = "/home/user/.config/sops/age/keys.txt";
    secrets."hermes-env" = { format = "yaml"; };
  };

  services.hermes-agent.environmentFiles = [
    config.sops.secrets."hermes-env".path
  ];
}
```

密钥文件包含键值对：

```yaml
# secrets/hermes.yaml (用 sops 加密)
hermes-env: |
    OPENROUTER_API_KEY=sk-or-...
    TELEGRAM_BOT_TOKEN=123456:ABC...
    ANTHROPIC_API_KEY=sk-ant-...
```

### agenix {#agenix}

```nix
{
  age.secrets.hermes-env.file = ./secrets/hermes-env.age;

  services.hermes-agent.environmentFiles = [
    config.age.secrets.hermes-env.path
  ];
}
```

### OAuth / 认证预置 {#oauth-auth-seeding}

对于需要 OAuth 的平台（例如 Discord），首次部署时可以用 `authFile` 预置凭证：

```nix
{
  services.hermes-agent = {
    authFile = config.sops.secrets."hermes/auth.json".path;
    # authFileForceOverwrite = true;  # 每次激活都覆盖
  };
}
```

只有当 `auth.json` 不存在时才会复制该文件（除非 `authFileForceOverwrite = true`）。运行时的 OAuth token 刷新会写入状态目录，并在重建后保留。

---

## 文档 {#documents}

`documents` 选项会把文件安装到 Agent 的工作目录（即 `workingDirectory`，Agent 将其作为工作空间读取）。Hermes 按约定查找特定文件名：

- **`USER.md`** —— 关于 Agent 正在交互的用户的信息。
- 你放在这里的任何其他文件，Agent 都能看到，作为工作空间文件。

Agent 的身份文件是独立的：Hermes 从 `$HERMES_HOME/SOUL.md` 加载主 `SOUL.md`，在 NixOS 模块中对应 `${services.hermes-agent.stateDir}/.hermes/SOUL.md`。把 `SOUL.md` 放在 `documents` 里只会创建一个工作空间文件，不会替换主角色文件。

```nix
{
  services.hermes-agent.documents = {
    "USER.md" = ./documents/USER.md;  # 路径引用，从 Nix store 复制
  };
}
```

值可以是内联字符串或路径引用。每次执行 `nixos-rebuild switch` 时都会安装这些文件。

---

## MCP 服务器 {#mcp-servers}

`mcpServers` 选项以声明方式配置 [MCP（Model Context Protocol）](https://modelcontextprotocol.io) 服务器。每个服务器使用 **stdio**（本地命令）或 **HTTP**（远程 URL）传输方式。
### Stdio Transport（本地服务器） {#stdio-transport-local-servers}

```nix
{
  services.hermes-agent.mcpServers = {
    filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };
    github = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-github" ];
      env.GITHUB_PERSONAL_ACCESS_TOKEN = "\${GITHUB_TOKEN}"; # 从 .env 解析
    };
  };
}
```

:::tip
`env` 中的环境变量值会在运行时从 `$HERMES_HOME/.env` 解析。请使用 `environmentFiles` 注入密钥——切勿将 token 直接写入 Nix 配置。
:::

### HTTP Transport（远程服务器） {#http-transport-remote-servers}

```nix
{
  services.hermes-agent.mcpServers.remote-api = {
    url = "https://mcp.example.com/v1/mcp";
    headers.Authorization = "Bearer \${MCP_REMOTE_API_KEY}";
    timeout = 180;
  };
}
```

### 带 OAuth 的 HTTP Transport {#http-transport-with-oauth}

对于使用 OAuth 2.1 的服务器，设置 `auth = "oauth"`。Hermes 实现了完整的 PKCE 流程——包括元数据发现、动态客户端注册、token 交换和自动刷新。

```nix
{
  services.hermes-agent.mcpServers.my-oauth-server = {
    url = "https://mcp.example.com/mcp";
    auth = "oauth";
  };
}
```

Token 存储在 `$HERMES_HOME/mcp-tokens/&lt;server-name&gt;.json`，重启和重建后仍然保留。

<details>
<summary><strong>无头服务器的首次 OAuth 授权</strong></summary>

首次 OAuth 授权需要基于浏览器的同意流程。在无头部署中，Hermes 会将授权 URL 打印到 stdout/日志，而不是直接打开浏览器。

**选项 A：交互式引导** —— 通过 `docker exec`（容器模式）或 `sudo -u hermes`（原生模式）运行一次流程：

```bash
# 容器模式
docker exec -it hermes-agent \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth

# 原生模式
sudo -u hermes HERMES_HOME=/var/lib/hermes/.hermes \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
```

容器使用 `--network=host`，因此主机浏览器可以访问 `127.0.0.1` 上的 OAuth 回调监听器。

**选项 B：预置 token** —— 在工作站上完成流程，然后复制 token：

```bash
hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
scp ~/.hermes/mcp-tokens/my-oauth-server{,.client}.json \
    server:/var/lib/hermes/.hermes/mcp-tokens/
# 注意：chown hermes:hermes, chmod 0600
```

</details>

### Sampling（服务器发起的 LLM 请求） {#sampling-server-initiated-llm-requests}

部分 MCP 服务器可以向 Agent 请求 LLM 补全：

```nix
{
  services.hermes-agent.mcpServers.analysis = {
    command = "npx";
    args = [ "-y" "analysis-server" ];
    sampling = {
      enabled = true;
      model = "google/gemini-3-flash";
      max_tokens_cap = 4096;
      timeout = 30;
      max_rpm = 10;
    };
  };
}
```

---

## 托管模式 {#managed-mode}

当 hermes 通过 NixOS 模块运行时，以下 CLI 命令会被**拦截**，并给出指向 `configuration.nix` 的明确错误：

| 被拦截的命令 | 原因 |
|---|---|
| `hermes setup` | 配置是声明式的——请在 Nix 配置中编辑 `settings` |
| `hermes config edit` | 配置由 `settings` 生成 |
| `hermes config set &lt;key&gt; &lt;value&gt;` | 配置由 `settings` 生成 |
| `hermes gateway install` | systemd 服务由 NixOS 管理 |
| `hermes gateway uninstall` | systemd 服务由 NixOS 管理 |

这样可以防止 Nix 声明的配置与磁盘实际状态出现偏差。检测依赖两个信号：

1. **`HERMES_MANAGED=true`** 环境变量 —— 由 systemd 服务设置，gateway 进程可见
2. **`HERMES_HOME` 中的 `.managed` 标记文件** —— 由激活脚本设置，交互式 shell 可见（例如 `docker exec -it hermes-agent hermes config set ...` 也会被拦截）

如需修改配置，请编辑 Nix 配置并运行 `sudo nixos-rebuild switch`。

---

## 容器架构 {#container-architecture}

:::info
本节仅在 `container.enable = true` 时 relevant。原生模式部署可跳过。
:::
当容器模式启用时，hermes 在一个持久化的 Ubuntu 容器内运行，Nix 构建的二进制文件以只读方式从宿主机 bind mount 进去：

```
Host                                    Container
────                                    ─────────
/nix/store/...-hermes-agent-0.1.0  ──►  /nix/store/... (ro)
~/.hermes -> /var/lib/hermes/.hermes       (symlink bridge, per hostUsers)
/var/lib/hermes/                    ──►  /data/          (rw)
  ├── current-package -> /nix/store/...    (symlink, updated each rebuild)
  ├── .gc-root -> /nix/store/...           (prevents nix-collect-garbage)
  ├── .container-identity                  (sha256 hash, triggers recreation)
  ├── .hermes/                             (HERMES_HOME)
  │   ├── .env                             (merged from environment + environmentFiles)
  │   ├── config.yaml                      (Nix-generated, deep-merged by activation)
  │   ├── .managed                         (marker file)
  │   ├── .container-mode                  (routing metadata: backend, exec_user, etc.)
  │   ├── state.db, sessions/, memories/   (runtime state)
  │   └── mcp-tokens/                      (OAuth tokens for MCP servers)
  ├── home/                                ──►  /home/hermes    (rw)
  └── workspace/                           (MESSAGING_CWD)
      ├── SOUL.md                          (from documents option)
      └── (agent-created files)

Container writable layer (apt/pip/npm):   /usr, /usr/local, /tmp
```

Nix 构建的二进制文件能在 Ubuntu 容器里工作，是因为 `/nix/store` 被 bind mount 进去了——它自带自己的解释器和所有依赖，所以不依赖容器的系统库。容器入口点通过一个 `current-package` 软链接来解析：`/data/current-package/bin/hermes gateway run --replace`。执行 `nixos-rebuild switch` 时，只有软链接会被更新——容器保持运行。

### 什么情况下什么会保留 {#what-persists-across-what}

| 事件 | 容器是否重建？ | `/data`（状态） | `/home/hermes` | 可写层（`apt`/`pip`/`npm`） |
|---|---|---|---|---|
| `systemctl restart hermes-agent` | 否 | 保留 | 保留 | 保留 |
| `nixos-rebuild switch`（代码变更） | 否（软链接更新） | 保留 | 保留 | 保留 |
| 宿主机重启 | 否 | 保留 | 保留 | 保留 |
| `nix-collect-garbage` | 否（GC root） | 保留 | 保留 | 保留 |
| 镜像变更（`container.image`） | **是** | 保留 | 保留 | **丢失** |
| 卷/选项变更 | **是** | 保留 | 保留 | **丢失** |
| `environment`/`environmentFiles` 变更 | 否 | 保留 | 保留 | 保留 |

容器只在 **identity hash** 变更时才会重建。该哈希涵盖：schema 版本、镜像、`extraVolumes`、`extraOptions` 以及入口点脚本。环境变量、设置、文档或 hermes 包本身的变更都**不会**触发重建。

:::warning 可写层丢失
当 identity hash 变更时（镜像升级、新增卷、新增容器选项），容器会被销毁并从 `container.image` 的新拉取中重建。可写层里通过 `apt install`、`pip install` 或 `npm install` 安装的包都会丢失。`/data` 和 `/home/hermes` 中的状态会被保留（这些是 bind mount）。

<a id="writable-layer-loss"></a>
如果 Agent 依赖特定包，可以考虑把它们预装进自定义镜像（`container.image = "my-registry/hermes-base:latest"`），或者在 Agent 的 SOUL.md 里写脚本安装它们。
:::

### GC Root 保护 {#gc-root-protection}

`preStart` 脚本会在 `${stateDir}/.gc-root` 创建一个指向当前 hermes 包的 GC root。这能防止 `nix-collect-garbage` 删除正在运行的二进制文件。如果 GC root 意外损坏，重启服务会重新创建它。

---

## 开发 {#development}

### 开发 Shell {#dev-shell}

flake 提供了一个开发 shell，包含 Python 3.11、uv、Node.js 和所有运行时工具：

```bash
cd hermes-agent
nix develop

# Shell 提供：
#   - Python 3.11 + uv（首次进入时把依赖装到 .venv）
#   - Node.js 20、ripgrep、git、openssh、ffmpeg 在 PATH 上
#   - Stamp-file 优化：如果依赖没变，重新进入几乎是瞬时的

hermes setup
hermes chat
```
### direnv（推荐） {#direnv-recommended}

项目自带的 `.envrc` 会自动激活开发环境：

```bash
cd hermes-agent
direnv allow    # 只需执行一次
# 之后进入目录几乎是瞬时的（通过 stamp 文件跳过依赖安装）
```

### Flake 检查 {#flake-checks}

该 flake 包含了构建时验证，可在 CI 和本地运行：

```bash
# 运行所有检查
nix flake check

# 单独检查
nix build .#checks.x86_64-linux.package-contents   # 二进制文件存在 + 版本号
nix build .#checks.x86_64-linux.entry-points-sync  # pyproject.toml ↔ Nix 包同步
nix build .#checks.x86_64-linux.cli-commands        # gateway/config 子命令
nix build .#checks.x86_64-linux.managed-guard       # HERMES_MANAGED 阻止修改
nix build .#checks.x86_64-linux.bundled-skills      # 包内包含 skills
nix build .#checks.x86_64-linux.config-roundtrip    # 合并脚本保留用户配置项
```

<details>
<summary><strong>每项检查的具体内容</strong></summary>

| 检查项 | 验证内容 |
|---|---|
| `package-contents` | `hermes` 和 `hermes-agent` 二进制文件存在，且 `hermes version` 可运行 |
| `entry-points-sync` | `pyproject.toml` 中每个 `[project.scripts]` 入口都在 Nix 包中有对应的 wrapped binary |
| `cli-commands` | `hermes --help` 显示 `gateway` 和 `config` 子命令 |
| `managed-guard` | `HERMES_MANAGED=true hermes config set ...` 输出 NixOS 错误提示 |
| `bundled-skills` | Skills 目录存在，包含 SKILL.md 文件，wrapper 中设置了 `HERMES_BUNDLED_SKILLS` |
| `config-roundtrip` | 7 种合并场景：全新安装、Nix 覆盖、用户配置项保留、混合合并、MCP 增量合并、嵌套深度合并、幂等性 |

</details>

---

## 选项参考 {#options-reference}

### 核心 {#core}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enable` | `bool` | `false` | 启用 hermes-agent 服务 |
| `package` | `package` | `hermes-agent` | 使用的 hermes-agent 包 |
| `user` | `str` | `"hermes"` | 系统用户 |
| `group` | `str` | `"hermes"` | 系统用户组 |
| `createUser` | `bool` | `true` | 自动创建用户/用户组 |
| `stateDir` | `str` | `"/var/lib/hermes"` | 状态目录（`HERMES_HOME` 的父目录） |
| `workingDirectory` | `str` | `"${stateDir}/workspace"` | Agent 工作目录（`MESSAGING_CWD`） |
| `addToSystemPackages` | `bool` | `false` | 将 `hermes` CLI 加入系统 PATH，并全局设置 `HERMES_HOME` |

### 配置 {#configuration}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `settings` | `attrs`（深度合并） | `{}` | 声明式配置，渲染为 `config.yaml`。支持任意嵌套；多个定义通过 `lib.recursiveUpdate` 合并 |
| `configFile` | `null` 或 `path` | `null` | 现有 `config.yaml` 的路径。设置后将完全覆盖 `settings` |

### 密钥与环境 {#secrets-environment}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `environmentFiles` | `listOf str` | `[]` | 包含密钥的环境文件路径。激活时合并到 `$HERMES_HOME/.env` |
| `environment` | `attrsOf str` | `{}` | 非密钥环境变量。**在 Nix store 中可见** —— 不要在这里放密钥 |
| `authFile` | `null` 或 `path` | `null` | OAuth 凭据种子文件。仅在首次部署时复制 |
| `authFileForceOverwrite` | `bool` | `false` | 每次激活时都从 `authFile` 覆盖 `auth.json` |

### 文档 {#documents}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `documents` | `attrsOf (either str path)` | `{}` | 工作区文件。键为文件名，值为内联字符串或路径。激活时安装到 `workingDirectory` |

### MCP 服务器 {#mcp-servers}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `mcpServers` | `attrsOf submodule` | `{}` | MCP 服务器定义，合并到 `settings.mcp_servers` |
| `mcpServers.&lt;name&gt;.command` | `null` 或 `str` | `null` | 服务器命令（stdio 传输） |
| `mcpServers.&lt;name&gt;.args` | `listOf str` | `[]` | 命令参数 |
| `mcpServers.&lt;name&gt;.env` | `attrsOf str` | `{}` | 服务器进程的环境变量 |
| `mcpServers.&lt;name&gt;.url` | `null` 或 `str` | `null` | 服务器端点 URL（HTTP/StreamableHTTP 传输） |
| `mcpServers.&lt;name&gt;.headers` | `attrsOf str` | `{}` | HTTP 请求头，例如 `Authorization` |
| `mcpServers.&lt;name&gt;.auth` | `null` 或 `"oauth"` | `null` | 认证方式。`"oauth"` 启用 OAuth 2.1 PKCE |
| `mcpServers.&lt;name&gt;.enabled` | `bool` | `true` | 启用或禁用该服务器 |
| `mcpServers.&lt;name&gt;.timeout` | `null` 或 `int` | `null` | 工具调用超时（秒，默认 120） |
| `mcpServers.&lt;name&gt;.connect_timeout` | `null` 或 `int` | `null` | 连接超时（秒，默认 60） |
| `mcpServers.&lt;name&gt;.tools` | `null` 或 `submodule` | `null` | 工具过滤（`include`/`exclude` 列表） |
| `mcpServers.&lt;name&gt;.sampling` | `null` 或 `submodule` | `null` | 服务器发起的 LLM 请求的采样配置 |
### Service Behavior {#service-behavior}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `extraArgs` | `listOf str` | `[]` | `hermes gateway` 的额外参数 |
| `extraPackages` | `listOf package` | `[]` | 添加到服务 PATH 的额外包（仅原生模式） |
| `restart` | `str` | `"always"` | systemd `Restart=` 策略 |
| `restartSec` | `int` | `5` | systemd `RestartSec=` 值 |

### Container {#container}

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `container.enable` | `bool` | `false` | 启用 OCI 容器模式 |
| `container.backend` | `enum ["docker" "podman"]` | `"docker"` | 容器运行时 |
| `container.image` | `str` | `"ubuntu:24.04"` | 基础镜像（运行时拉取） |
| `container.extraVolumes` | `listOf str` | `[]` | 额外卷挂载（格式 `host:container:mode`） |
| `container.extraOptions` | `listOf str` | `[]` | 传给 `docker create` 的额外参数 |
| `container.hostUsers` | `listOf str` | `[]` | 交互式用户，会获得指向服务 stateDir 的 `~/.hermes` 符号链接，并自动加入 `hermes` 组 |

---

## 目录结构 {#directory-layout}

### 原生模式 {#native-mode}

```
/var/lib/hermes/                     # stateDir（属主 hermes:hermes，权限 0750）
├── .hermes/                         # HERMES_HOME
│   ├── config.yaml                  # Nix 生成（每次重建时深度合并）
│   ├── .managed                     # 标记：禁止 CLI 修改配置
│   ├── .env                         # 由 environment + environmentFiles 合并而来
│   ├── auth.json                    # OAuth 凭据（初始化后自行管理）
│   ├── gateway.pid
│   ├── state.db
│   ├── mcp-tokens/                  # MCP 服务器的 OAuth token
│   ├── sessions/
│   ├── memories/
│   ├── skills/
│   ├── cron/
│   └── logs/
├── home/                            # Agent 的 HOME
└── workspace/                       # MESSAGING_CWD
    ├── SOUL.md                      # 来自 documents 选项
    └── (agent 创建的文件)
```

### 容器模式 {#container-mode}

目录结构相同，挂载到容器内：

| 容器路径 | 主机路径 | 模式 | 说明 |
|---|---|---|---|
| `/nix/store` | `/nix/store` | `ro` | Hermes 二进制及所有 Nix 依赖 |
| `/data` | `/var/lib/hermes` | `rw` | 所有状态、配置、工作区 |
| `/home/hermes` | `${stateDir}/home` | `rw` | 持久化的 Agent home —— 用于 `pip install --user`、工具缓存等 |
| `/usr`、`/usr/local`、`/tmp` | （可写层） | `rw` | `apt`/`pip`/`npm` 安装 —— 重启后保留，重建容器时丢失 |

---

## 更新 {#updating}

```bash
# 更新 flake input
nix flake update hermes-agent --flake /etc/nixos

# 重建
sudo nixos-rebuild switch
```

容器模式下，`current-package` 符号链接会被更新，Agent 重启后会使用新二进制。无需重建容器，也不会丢失已安装的包。

---

## 故障排查 {#troubleshooting}

<a id="podman-users"></a>
:::tip Podman 用户
下面所有 `docker` 命令在 `podman` 中同样适用。如果你设置了 `container.backend = "podman"`，按需替换即可。
:::

<a id="service-logs"></a>
### 服务日志 {#podman-users}

```bash
# 两种模式使用同一个 systemd 单元
journalctl -u hermes-agent -f

# 容器模式：也可以直接查看
docker logs -f hermes-agent
```

### 容器检查 {#container-inspection}

```bash
systemctl status hermes-agent
docker ps -a --filter name=hermes-agent
docker inspect hermes-agent --format='{{.State.Status}}'
docker exec -it hermes-agent bash
docker exec hermes-agent readlink /data/current-package
docker exec hermes-agent cat /data/.container-identity
```

### 强制重建容器 {#force-container-recreation}

如果需要重置可写层（全新的 Ubuntu）：

```bash
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

### 验证密钥是否已加载 {#verify-secrets-are-loaded}

如果 Agent 启动了但无法向 LLM 提供商认证，检查 `.env` 文件是否正确合并：

```bash
# 原生模式
sudo -u hermes cat /var/lib/hermes/.hermes/.env

# 容器模式
docker exec hermes-agent cat /data/.hermes/.env
```

### GC Root 验证 {#gc-root-verification}

```bash
nix-store --query --roots $(docker exec hermes-agent readlink /data/current-package)
```
### 常见问题 {#common-issues}

| 现象 | 原因 | 解决方法 |
|---|---|---|
| `Cannot save configuration: managed by NixOS` | CLI 保护机制生效 | 编辑 `configuration.nix` 并执行 `nixos-rebuild switch` |
| 容器意外重建 | `extraVolumes`、`extraOptions` 或 `image` 发生变更 | 正常现象——可写层会重置。重新安装软件包或使用自定义镜像 |
| `hermes version` 显示旧版本 | 容器未重启 | `systemctl restart hermes-agent` |
| `/var/lib/hermes` 权限被拒绝 | 状态目录权限为 `0750 hermes:hermes` | 使用 `docker exec` 或 `sudo -u hermes` |
| `nix-collect-garbage` 删除了 hermes | GC root 缺失 | 重启服务（preStart 会重新创建 GC root） |
| `no container with name or ID "hermes-agent"`（Podman） | Podman rootful 容器对普通用户不可见 | 为 podman 配置免密 sudo（参见 [容器感知 CLI](#container-aware-cli) 章节） |
| `unable to find user hermes` | 容器仍在启动中（entrypoint 尚未创建用户） | 稍等几秒重试——CLI 会自动重试 |
