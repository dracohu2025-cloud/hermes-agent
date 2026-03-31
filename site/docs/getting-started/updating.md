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

此命令会拉取最新代码、更新依赖项，并提示你配置自上次更新以来新增的任何选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 来查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 通过消息平台更新

你也可以直接从 Telegram、Discord、Slack 或 WhatsApp 发送以下命令来更新：

```
/update
```

此命令会拉取最新代码、更新依赖项，并重启网关。

### 手动更新

如果你是手动安装的（而非通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码和子模块
git pull origin main
git submodule update --init --recursive

# 重新安装（会获取新的依赖项）
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"

# 检查新的配置选项
hermes config check
hermes config migrate   # 交互式添加任何缺失的选项
```

---

## 卸载

```bash
hermes uninstall
```

卸载程序会询问你是否保留配置文件（`~/.hermes/`）以便将来重新安装。

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
