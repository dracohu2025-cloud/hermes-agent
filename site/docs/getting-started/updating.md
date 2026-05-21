---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或卸载它"
---

<a id="updating-uninstalling"></a>
# 更新与卸载

<a id="updating"></a>
## 更新

<a id="git-installs"></a>
### Git 安装

使用一条命令更新到最新版本：

```bash
hermes update
```

这会从 `main` 分支拉取最新代码、更新依赖，并提示你配置上次更新后新增的任何选项。

<a id="pip-installs"></a>
### pip 安装

PyPI 发布版跟踪的是**标签版本**（主版本和次版本），而不是 `main` 上的每次提交。检查更新并升级的方法：

```bash
hermes update --check    # 查看 PyPI 上是否有更新的版本
hermes update            # 运行 pip install --upgrade hermes-agent
```

或者手动执行：

```bash
pip install --upgrade hermes-agent    # 或: uv pip install --upgrade hermes-agent
```

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了那个提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 交互式地添加它们。
:::

<a id="what-happens-during-an-update-git-installs"></a>
### 更新过程中发生了什么（Git 安装）

当你运行 `hermes update` 时，会执行以下步骤：

1. **配对数据快照** — 保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则以及其它在运行时会被修改的状态文件）。可通过[快照与回滚](../user-guide/checkpoints-and-rollback.md)中描述的快照恢复流程来恢复，或解压 Hermes 在 `~/.hermes/` 目录旁写入的最新快速快照压缩包来手动恢复。
2. **Git 拉取** — 从 `main` 分支拉取最新代码并更新子模块
3. **依赖安装** — 运行 `uv pip install -e ".[all]"` 以获取新增或变更的依赖
4. **配置迁移** — 检测自你上次版本后新增的配置选项，并提示你设置它们
5. **网关自动重启** — 更新完成后运行的网关会被刷新，使新代码立即生效。由服务管理的网关（Linux 上的 systemd、macOS 上的 launchd）会通过服务管理器重启。手动启动的网关，在 Hermes 能够将运行中的 PID 映射回对应配置文件时，会自动重新启动。

<a id="preview-only-hermes-update-check"></a>
### 仅预览：`hermes update --check`

想在拉取之前知道是否有可用更新？运行 `hermes update --check`——对于 Git 安装，它会拉取并与 `origin/main` 比较提交记录；对于 pip 安装，它会向 PyPI 查询最新发布版本。不会修改任何文件，也不会重启网关。适用于脚本和定时任务中需要“是否有更新”作为判断条件的场景。

<a id="full-pre-update-backup-backup"></a>
### 完整的更新前备份：`--backup`

对于高价值的配置文件（生产环境网关、共享团队安装），你可以选择在拉取前对 `HERMES_HOME` 进行完整备份（配置、认证、会话、技能、配对）：

```bash
hermes update --backup
```

或者将其设为每次运行的默认行为：

```yaml
# ~/.hermes/config.yaml
updates:
  pre_update_backup: true
```

`--backup` 在早期版本中是始终开启的行为，但在大型配置目录上每次更新都会增加数分钟的时间，因此现在变成了可选功能。上面提到的轻量级配对数据快照仍然无条件运行。
<a id="windows-another-hermes-exe-is-running"></a>
### Windows：另一个 `hermes.exe` 正在运行

在 Windows 上，如果检测到另一个 `hermes.exe` 进程正在占用 venv 入口可执行文件（最常见的是 Hermes Desktop 应用生成的的后台进程、另一个终端中打开的 `hermes` REPL，或正在运行的网关），`hermes update` 将拒绝执行：

```
$ hermes update
✗ 另一个 hermes.exe 正在运行：
    PID 12345  hermes.exe

  现在更新将无法覆盖 ...\venv\Scripts\hermes.exe，因为
  Windows 阻止对正在运行的可执行文件进行 REPLACE。

  请关闭 Hermes Desktop，退出所有打开的 `hermes` REPL，并
  停止网关（`hermes gateway stop`）后重试。
  如果您已经确认这些进程不会写入 venv，可以使用 `hermes update --force` 覆盖。
```

关闭列出的进程后重新运行。如果您确定并发进程不会造成干扰（这种情况很少见——通常仅在防病毒软件垫片被错误归因时有用），请传递 `--force` 跳过检查。在这种情况下，更新程序仍会以指数退避重试 `.exe` 重命名，并在锁顽固时，通过 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 将替换计划安排到下一次重启，从而完成更新。

预期输出如下：

```
$ hermes update
更新 Hermes Agent...
📥 拉取最新代码...
Already up to date.  （或：Updating abc1234..def5678）
📦 更新依赖...
✅ 依赖已更新
🔍 检查新配置选项...
✅ 配置已是最新  （或：Found 2 new options — running migration...）
🔄 重启网关...
✅ 网关已重启
✅ Hermes Agent 更新成功！
```

<a id="recommended-post-update-validation"></a>
### 推荐的更新后验证

`hermes update` 处理了主更新流程，但快速验证可确认一切顺利落地：

1. `git status --short` — 如果工作树意外变脏，请先检查再继续
2. `hermes doctor` — 检查配置、依赖和服务健康状态
3. `hermes --version` — 确认版本已如期更新
4. 如果您使用网关：`hermes gateway status`
5. 如果 `doctor` 报告 npm 审计问题：在标记的目录中运行 `npm audit fix`

:::warning 更新后工作树脏乱
<a id="dirty-working-tree-after-update"></a>
如果 `hermes update` 后 `git status --short` 显示意外更改，请先停止并检查它们再继续。这通常意味着本地修改被重新应用到更新后的代码之上，或者某个依赖步骤刷新了锁文件。
:::

<a id="if-your-terminal-disconnects-mid-update"></a>
### 如果终端在更新中断开连接

`hermes update` 对意外的终端丢失做了保护：

- 更新忽略 `SIGHUP`，因此关闭 SSH 会话或终端窗口不再会中途杀死更新。`pip` 和 `git` 子进程继承此保护，因此 Python 环境不会因连接断开而处于半安装状态。
- 更新期间所有输出都会镜像到 `~/.hermes/logs/update.log`。如果您的终端消失，请重新连接并检查日志，以查看更新是否完成以及网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT）和系统关机（SIGTERM）仍然受支持——这些是有意取消，而非意外。
你不再需要把 `hermes update` 包裹在 `screen` 或 `tmux` 里来防止终端断连。

<a id="checking-your-current-version"></a>
### 检查当前版本

```bash
hermes version
```

与 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行比对。

<a id="updating-from-messaging-platforms"></a>
### 通过消息平台更新

你也可以直接在 Telegram、Discord、Slack、WhatsApp 或 Teams 中通过发送以下命令来更新：

```
/update
```

这会拉取最新代码、更新依赖项，并重新启动正在运行的 gateway。重启期间 bot 会短暂离线（通常 5–15 秒），然后恢复运行。

<a id="manual-update"></a>
### 手动更新

如果你是通过手动方式安装的（不是使用快速安装器）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码
git pull origin main

# 重新安装（会拉取新的依赖）
uv pip install -e ".[all]"

# 检查是否有新的配置选项
hermes config check
hermes config migrate   # 交互式添加缺失的选项
```

<a id="rollback-instructions"></a>
### 回滚指南

如果某个更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到指定的 commit
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果 gateway 正在运行，则重启
hermes gateway restart
```

回滚到指定的发布标签：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
如果新增了配置选项，回滚可能导致配置不兼容。回滚后请运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中删除未被识别的选项。
:::

<a id="note-for-nix-users"></a>
### 对 Nix 用户的说明

如果你是通过 Nix flake 安装的，更新由 Nix 包管理器管理：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者使用最新版本重建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的——回滚由 Nix 的 generation 系统处理：

```bash
nix profile rollback
```

详情请参见 [Nix 安装指南](./nix-setup.md)。

---

<a id="uninstalling"></a>
## 卸载

<a id="git-installs"></a>
### Git 安装

```bash
hermes uninstall
```

卸载程序会提供选项，让你保留配置文件（`~/.hermes/`），以便将来重新安装。

<a id="pip-installs"></a>
### pip 安装

```bash
pip uninstall hermes-agent
rm -rf ~/.hermes            # 可选——如果你打算重新安装，可以保留
```

<a id="manual-uninstall"></a>
### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选——如果你打算重新安装，可以保留
```

:::info
如果你将 gateway 安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
