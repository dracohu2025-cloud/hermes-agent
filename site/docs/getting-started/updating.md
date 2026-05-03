---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或卸载它"
---

# 更新与卸载 {#updating-uninstalling}

## 更新 {#updating}

使用一条命令更新到最新版本：

```bash
hermes update
```

该命令会拉取最新代码、更新依赖，并提示你配置自上次更新以来新增的任何选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加它们。如果你跳过了那个提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新过程中发生了什么 {#what-happens-during-an-update}

当你运行 `hermes update` 时，会执行以下步骤：

1. **配对数据快照** — 保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则以及其他在运行时会被修改的状态文件）。可通过 `hermes backup restore --state pre-update` 回滚。
2. **Git 拉取** — 从 `main` 分支拉取最新代码并更新子模块
3. **依赖安装** — 运行 `uv pip install -e ".[all]"` 以获取新增或变更的依赖
4. **配置迁移** — 检测自你的版本以来新增的配置选项，并提示你进行设置
5. **网关自动重启** — 更新完成后，正在运行的网关会被刷新，以便新代码立即生效。由服务管理的网关（Linux 上的 systemd，macOS 上的 launchd）会通过服务管理器重启。当 Hermes 能够将运行中的 PID 映射回某个配置文件时，手动启动的网关会自动重新启动。

### 仅预览：`hermes update --check` {#preview-only-hermes-update-check}

想知道在实际拉取之前你是否落后于 `origin/main`？运行 `hermes update --check` — 它会获取远程信息，并排显示你的本地提交和最新的远程提交，如果同步则退出码为 `0`，如果落后则退出码为 `1`。不会修改任何文件，也不会重启网关。适用于那些以“是否有更新”为条件的脚本和 cron 任务。

### 完整的更新前备份：`--backup` {#full-pre-update-backup-backup}

对于高价值配置文件（生产网关、共享团队安装），你可以选择在拉取前对 `HERMES_HOME`（配置、认证、会话、技能、配对）进行完整备份：

```bash
hermes update --backup
```

或者将其设为每次运行的默认行为：

```yaml
# ~/.hermes/config.yaml
update:
  backup: true
```

`--backup` 在早期版本中是始终开启的行为，但在大型 home 目录上每次更新都会增加几分钟时间，因此现在改为可选。上面的轻量级配对数据快照仍然无条件运行。

预期输出如下：

```
$ hermes update
Updating Hermes Agent...
📥 正在拉取最新代码...
Already up to date.  (或: Updating abc1234..def5678)
📦 正在更新依赖...
✅ 依赖已更新
🔍 正在检查新的配置选项...
✅ 配置已是最新  (或: Found 2 new options — running migration...)
🔄 正在重启网关...
✅ 网关已重启
✅ Hermes Agent 更新成功！
```

### 推荐的更新后验证 {#recommended-post-update-validation}

`hermes update` 处理了主要的更新流程，但快速验证可以确认一切顺利落地：

1. `git status --short` — 如果工作树意外变脏，请在继续之前检查
2. `hermes doctor` — 检查配置、依赖和服务健康状态
3. `hermes --version` — 确认版本号按预期更新
4. 如果你使用网关：`hermes gateway status`
5. 如果 `doctor` 报告 npm 审计问题：在标记的目录中运行 `npm audit fix`
:::warning 更新后工作目录不干净
如果 `hermes update` 之后 `git status --short` 显示了意外的更改，请先停下来检查这些更改，然后再继续。这通常意味着本地修改被重新应用到了更新后的代码上，或者某个依赖步骤刷新了锁文件。
:::

### 如果终端在更新过程中断开连接 {#if-your-terminal-disconnects-mid-update}
<a id="dirty-working-tree-after-update"></a>

`hermes update` 自身具备防止意外终端丢失的保护：

- 更新过程会忽略 `SIGHUP` 信号，因此关闭 SSH 会话或终端窗口不会再中断安装过程。`pip` 和 `git` 子进程会继承这一保护，所以 Python 环境不会因为连接断开而只安装了一半。
- 更新运行期间，所有输出都会镜像到 `~/.hermes/logs/update.log`。如果终端消失了，重新连接后检查该日志，看看更新是否完成以及网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT）和系统关机（SIGTERM）仍然会被处理——这些是故意的取消操作，而非意外。

你不再需要将 `hermes update` 包裹在 `screen` 或 `tmux` 中来应对终端断开。

### 检查当前版本 {#checking-your-current-version}

```bash
hermes version
```

与 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行对比。

### 从消息平台更新 {#updating-from-messaging-platforms}

你也可以直接从 Telegram、Discord、Slack 或 WhatsApp 发送以下命令进行更新：

```
/update
```

这会拉取最新代码、更新依赖并重启正在运行的网关。机器人在重启期间会短暂离线（通常 5–15 秒），然后恢复运行。

### 手动更新 {#manual-update}

如果你是通过手动方式安装的（而非快速安装器）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（获取新的依赖）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查是否有新的配置选项
hermes config check
hermes config migrate   # 交互式地添加任何缺失的选项
```

### 回滚说明 {#rollback-instructions}

如果更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到特定提交
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果网关正在运行，重启它
hermes gateway restart
```

要回滚到特定的发布标签：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
如果新增了配置选项，回滚可能会导致配置不兼容。回滚后运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中移除任何无法识别的选项。
:::

### Nix 用户注意事项 {#note-for-nix-users}

如果你是通过 Nix flake 安装的，更新由 Nix 包管理器管理：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者使用最新版本重建
nix profile upgrade hermes-agent
```
Nix 安装是不可变的——回滚由 Nix 的生成系统处理：

```bash
nix profile rollback
```

更多详情请参见 [Nix 安装](./nix-setup.md)。

---

## 卸载 {#uninstalling}

```bash
hermes uninstall
```

卸载程序会提供选项，让你保留配置文件（`~/.hermes/`），以便将来重新安装。

### 手动卸载 {#manual-uninstall}

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选——如果计划重新安装，请保留
```

:::info
如果你已将网关安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
