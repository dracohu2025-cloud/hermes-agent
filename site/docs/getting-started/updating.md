---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或将其卸载"
---

# 更新与卸载

## 更新

只需一条命令即可更新到最新版本：

```bash
hermes update
```

该命令会拉取最新代码、更新依赖项，并提示你配置自上次更新以来新增的任何选项。

:::tip 提示
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 进行交互式添加。
:::

### 更新过程中会发生什么

当你运行 `hermes update` 时，会执行以下步骤：

1. **Git pull** — 从 `main` 分支拉取最新代码并更新子模块。
2. **依赖安装** — 运行 `uv pip install -e ".[all]"` 以获取新增或变更的依赖。
3. **配置迁移** — 检测自当前版本以来新增的配置选项，并提示你进行设置。
4. **Gateway 自动重启** — 如果 Gateway 服务正在运行（Linux 上的 systemd 或 macOS 上的 launchd），它会在更新完成后**自动重启**，以便新代码立即生效。

预期的输出如下所示：

```
$ hermes update
Updating Hermes Agent...
📥 Pulling latest code...
Already up to date.  (或: Updating abc1234..def5678)
📦 Updating dependencies...
✅ Dependencies updated
🔍 Checking for new config options...
✅ Config is up to date  (或: Found 2 new options — running migration...)
🔄 Restarting gateway service...
✅ Gateway restarted
✅ Hermes Agent updated successfully!
```

### 推荐的更新后验证

虽然 `hermes update` 处理了主要的更新流程，但进行快速验证可以确保一切正常：

1. `git status --short` — 如果工作树出现意外的改动，请在继续前进行检查。
2. `hermes doctor` — 检查配置、依赖项和服务健康状况。
3. `hermes --version` — 确认版本号已按预期升级。
4. 如果你使用了 Gateway：执行 `hermes gateway status`。
5. 如果 `doctor` 报告了 npm 审计问题：在标记的目录中运行 `npm audit fix`。

:::warning 更新后工作树不干净
如果运行 `hermes update` 后 `git status --short` 显示了意外的更改，请停止操作并在继续前检查这些更改。这通常意味着本地修改被重新应用到了更新后的代码之上，或者某个依赖步骤刷新了 lockfile。
:::

### 查看当前版本

```bash
hermes version
```

你可以将其与 [GitHub releases 页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行对比，或检查可用更新：

```bash
hermes update --check
```

### 通过消息平台更新

你也可以直接通过 Telegram、Discord、Slack 或 WhatsApp 发送以下指令进行更新：

```
/update
```

这将拉取最新代码、更新依赖并重启 Gateway。Bot 在重启期间会短暂离线（通常为 5-15 秒），然后恢复运行。

### 手动更新

如果你是手动安装的（不是通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（获取新依赖）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查新配置选项
hermes config check
hermes config migrate   # 交互式添加任何缺失的选项
```

### 回滚说明

如果更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到特定的 commit
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果 Gateway 正在运行，请重启它
hermes gateway restart
```

要回滚到特定的发布标签（Release Tag）：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning 警告
如果添加了新选项，回滚可能会导致配置不兼容。回滚后请运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中删除任何无法识别的选项。
:::

### Nix 用户注意事项

如果你是通过 Nix flake 安装的，更新由 Nix 包管理器管理：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者使用最新版本重新构建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的 —— 回滚由 Nix 的 generation 系统处理：

```bash
nix profile rollback
```

详见 [Nix 安装指南](./nix-setup.md)。

---

## 卸载

```bash
hermes uninstall
```

卸载程序会询问你是否保留配置文件（`~/.hermes/`），以便将来重新安装。

### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选 — 如果计划重新安装则保留
```

:::info 信息
如果你将 Gateway 安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
