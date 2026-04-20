---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本，或将其卸载"
---

# 更新与卸载 {#updating-uninstalling}

## 更新 {#updating}

一条命令即可更新到最新版本：

```bash
hermes update
```

这条命令会拉取最新代码、更新依赖，并提示你配置自上次更新以来新增的所有选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新期间会发生什么 {#what-happens-during-an-update}

运行 `hermes update` 时，会依次执行以下步骤：

1. **Git pull** — 从 `main` 分支拉取最新代码并更新子模块
2. **依赖安装** — 运行 `uv pip install -e ".[all]"` 以获取新增或变更的依赖
3. **配置迁移** — 检测自你的版本以来新增的配置选项，并提示你进行设置
4. **Gateway 自动重启** — 如果 gateway 服务正在运行（Linux 上为 systemd，macOS 上为 launchd），更新完成后会**自动重启**，以便新代码立即生效

预期输出如下：

```
$ hermes update
Updating Hermes Agent...
📥 Pulling latest code...
Already up to date.  (or: Updating abc1234..def5678)
📦 Updating dependencies...
✅ Dependencies updated
🔍 Checking for new config options...
✅ Config is up to date  (or: Found 2 new options — running migration...)
🔄 Restarting gateway service...
✅ Gateway restarted
✅ Hermes Agent updated successfully!
```

### 建议的更新后验证 {#recommended-post-update-validation}

`hermes update` 已经处理了主要的更新流程，但快速验证一下可以确认一切干净利落：

1. `git status --short` — 如果工作树意外变脏，先检查再继续
2. `hermes doctor` — 检查配置、依赖和服务健康状态
3. `hermes --version` — 确认版本号如预期般提升
4. 如果你使用 gateway：`hermes gateway status`
5. 如果 `doctor` 报告 npm audit 问题：在标记的目录中运行 `npm audit fix`

:::warning 更新后工作树变脏
如果 `hermes update` 之后 `git status --short` 显示了意外的变更，先停下来检查再继续。这通常意味着本地修改被重新应用到了更新后的代码之上，或者某个依赖步骤刷新了 lockfile。
:::

<a id="dirty-working-tree-after-update"></a>
### 如果终端在更新中途断开 {#if-your-terminal-disconnects-mid-update}

`hermes update` 会保护自己免受意外终端丢失的影响：

- 更新会忽略 `SIGHUP`，所以关闭 SSH 会话或终端窗口不会再导致安装中途被杀。`pip` 和 `git` 子进程会继承这一保护，因此 Python 环境不会因为连接断开而装到一半。
- 所有输出都会在更新运行时同步镜像到 `~/.hermes/logs/update.log`。如果你的终端消失了，重新连接后查看日志即可了解更新是否完成、gateway 重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT）和系统关机（SIGTERM）仍然会被响应——那些是主动取消，不是意外。

你不再需要把 `hermes update` 包在 `screen` 或 `tmux` 里来防止终端掉线。

### 查看当前版本 {#checking-your-current-version}

```bash
hermes version
```

与 [GitHub releases 页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行对比。

### 从消息平台更新 {#updating-from-messaging-platforms}

你也可以直接从 Telegram、Discord、Slack 或 WhatsApp 发送以下指令来更新：

```
/update
```

这会拉取最新代码、更新依赖并重启 gateway。Bot 在重启期间会短暂离线（通常 5–15 秒），然后恢复运行。

### 手动更新 {#manual-update}

如果你是手动安装的（没有通过快速安装器）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（获取新依赖）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查新增配置选项
hermes config check
hermes config migrate   # 以交互方式添加任何缺失的选项
```
### 回退说明 {#rollback-instructions}

如果更新引入了问题，你可以回退到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回退到指定的 commit
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果 gateway 正在运行，重启它
hermes gateway restart
```

回退到指定的 release tag：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
如果新版本添加了配置项，回退可能会导致配置不兼容。回退后运行 `hermes config check`，如果遇到错误，从 `config.yaml` 中删除所有无法识别的选项。
:::

### Nix 用户须知 {#note-for-nix-users}

如果你通过 Nix flake 安装，更新由 Nix 包管理器管理：

```bash
# 更新 flake input
nix flake update hermes-agent

# 或者升级到最新版本
nix profile upgrade hermes-agent
```

Nix 安装是不可变的——回退由 Nix 的 generation 系统处理：

```bash
nix profile rollback
```

更多细节请参见 [Nix 安装](./nix-setup.md)。

---

## 卸载 {#uninstalling}

```bash
hermes uninstall
```

卸载程序会让你选择是否保留配置文件（`~/.hermes/`），以便将来重新安装。

### 手动卸载 {#manual-uninstall}

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选——如果计划重新安装，可以保留
```

:::info
如果你将 gateway 安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
