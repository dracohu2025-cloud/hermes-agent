---
sidebar_position: 3
title: "更新与卸载"
description: "如何将 Hermes Agent 更新到最新版本或卸载它"
---

# 更新与卸载

## 更新

使用一条命令即可更新到最新版本：

```bash
hermes update
```

此命令会拉取最新代码，更新依赖项，并提示你配置自上次更新以来新增的任何选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新期间会发生什么

当你运行 `hermes update` 时，会发生以下步骤：

1. **Git pull** — 从 `main` 分支拉取最新代码并更新子模块
2. **依赖项安装** — 运行 `uv pip install -e ".[all]"` 以获取新的或更改的依赖项
3. **配置迁移** — 检测自你当前版本以来新增的配置选项，并提示你设置它们
4. **网关自动重启** — 如果网关服务正在运行（Linux 上为 systemd，macOS 上为 launchd），更新完成后会**自动重启**，以便新代码立即生效

预期的输出如下所示：

```
$ hermes update
正在更新 Hermes Agent...
📥 正在拉取最新代码...
Already up to date.  (或: Updating abc1234..def5678)
📦 正在更新依赖项...
✅ 依赖项已更新
🔍 正在检查新的配置选项...
✅ 配置是最新的  (或: 发现 2 个新选项 — 正在运行迁移...)
🔄 正在重启网关服务...
✅ 网关已重启
✅ Hermes Agent 更新成功！
```

### 检查当前版本

```bash
hermes version
```

与 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases) 上的最新版本进行比较，或检查可用更新：

```bash
hermes update --check
```

### 通过消息平台更新

你也可以直接从 Telegram、Discord、Slack 或 WhatsApp 发送以下命令来更新：

```
/update
```

这会拉取最新代码，更新依赖项，并重启网关。机器人将在重启期间短暂离线（通常为 5-15 秒），然后恢复。

### 手动更新

如果你是手动安装的（不是通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（获取新的依赖项）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查新的配置选项
hermes config check
hermes config migrate   # 以交互方式添加任何缺失的选项
```

### 回滚说明

如果更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到特定的提交
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# 如果网关正在运行，则重启它
hermes gateway restart
```

要回滚到特定的发布标签：

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
如果添加了新选项，回滚可能会导致配置不兼容。回滚后运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中删除任何无法识别的选项。
:::

### 给 Nix 用户的说明

如果你是通过 Nix flake 安装的，更新通过 Nix 包管理器管理：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者用最新版本重新构建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的 — 回滚由 Nix 的生成系统处理：

```bash
nix profile rollback
```

更多详情请参阅 [Nix 设置](./nix-setup.md)。

---

## 卸载

```bash
hermes uninstall
```

卸载程序会给你选择是否保留配置文件（`~/.hermes/`）以便将来重新安装。

### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选 — 如果你计划重新安装，请保留
```

:::info
如果你将网关安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
