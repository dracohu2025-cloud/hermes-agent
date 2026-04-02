---
sidebar_position: 7
---

# Profile 命令参考

本页涵盖所有与 [Hermes profiles](../user-guide/profiles.md) 相关的命令。有关通用 CLI 命令，请参见 [CLI Commands Reference](./cli-commands.md)。

## `hermes profile`

```bash
hermes profile <subcommand>
```

管理 profiles 的顶层命令。运行 `hermes profile` 不带子命令时会显示帮助。

| 子命令 | 说明 |
|------------|-------------|
| `list` | 列出所有 profiles。 |
| `use` | 设置当前激活（默认）的 profile。 |
| `create` | 创建一个新的 profile。 |
| `delete` | 删除一个 profile。 |
| `show` | 显示 profile 的详细信息。 |
| `alias` | 重新生成 profile 的 shell 别名。 |
| `rename` | 重命名一个 profile。 |
| `export` | 导出 profile 为 tar.gz 归档文件。 |
| `import` | 从 tar.gz 归档导入 profile。 |

## `hermes profile list`

```bash
hermes profile list
```

列出所有 profiles。当前激活的 profile 会用 `*` 标记。

**示例：**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

无选项。

## `hermes profile use`

```bash
hermes profile use <name>
```

将 `<name>` 设置为当前激活的 profile。之后所有不带 `-p` 参数的 `hermes` 命令都会使用该 profile。

| 参数 | 说明 |
|----------|-------------|
| `<name>` | 要激活的 profile 名称。使用 `default` 可切换回基础 profile。 |

**示例：**

```bash
hermes profile use work
hermes profile use default
```

## `hermes profile create`

```bash
hermes profile create <name> [options]
```

创建一个新的 profile。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `<name>` | 新 profile 的名称。必须是有效的目录名（字母数字、连字符、下划线）。 |
| `--clone` | 从当前 profile 复制 `config.yaml`、`.env` 和 `SOUL.md`。 |
| `--clone-all` | 从当前 profile 复制所有内容（配置、记忆、技能、会话、状态）。 |
| `--clone-from <profile>` | 从指定的 profile 克隆，而非当前 profile。需与 `--clone` 或 `--clone-all` 一起使用。 |

**示例：**

```bash
# 空白 profile — 需要完整配置
hermes profile create mybot

# 仅克隆当前 profile 的配置
hermes profile create work --clone

# 克隆当前 profile 的所有内容
hermes profile create backup --clone-all

# 从指定 profile 克隆配置
hermes profile create work2 --clone --clone-from work
```

## `hermes profile delete`

```bash
hermes profile delete <name> [options]
```

删除一个 profile 并移除其 shell 别名。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `<name>` | 要删除的 profile。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例：**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
这会永久删除该 profile 的整个目录，包括所有配置、记忆、会话和技能。无法删除当前激活的 profile。
:::

## `hermes profile show`

```bash
hermes profile show <name>
```

显示 profile 的详细信息，包括其主目录、配置的模型、激活的平台和磁盘使用情况。

| 参数 | 说明 |
|----------|-------------|
| `<name>` | 要查看的 profile。 |

**示例：**

```bash
$ hermes profile show work
Profile:    work
Home:       ~/.hermes/profiles/work
Model:      anthropic/claude-sonnet-4
Platforms:  telegram, discord
Skills:     12 installed
Disk:       48 MB
```

## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

重新生成位于 `~/.local/bin/<name>` 的 shell 别名脚本。如果别名被误删或在移动 Hermes 安装后需要更新别名时很有用。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `<name>` | 要创建或更新别名的 profile。 |
| `--remove` | 移除该包装脚本，而非创建。 |
| `--name <alias>` | 自定义别名名称（默认是 profile 名称）。 |

**示例：**

```bash
hermes profile alias work
# 创建/更新 ~/.local/bin/work

hermes profile alias work --name mywork
# 创建 ~/.local/bin/mywork

hermes profile alias work --remove
# 移除包装脚本
```

## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

重命名一个 profile。会更新目录和 shell 别名。

| 参数 | 说明 |
|----------|-------------|
| `<old-name>` | 当前 profile 名称。 |
| `<new-name>` | 新的 profile 名称。 |

**示例：**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export`

```bash
hermes profile export <name> [options]
```

将 profile 导出为压缩的 tar.gz 归档文件。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `<name>` | 要导出的 profile。 |
| `-o`, `--output <path>` | 输出文件路径（默认是 `<name>.tar.gz`）。 |

**示例：**

```bash
hermes profile export work
# 在当前目录创建 work.tar.gz

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import`

```bash
hermes profile import <archive> [options]
```

从 tar.gz 归档导入 profile。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `<archive>` | 要导入的 tar.gz 归档路径。 |
| `--name <name>` | 导入后 profile 的名称（默认从归档推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从归档推断 profile 名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

全局参数，用于在不改变默认激活 profile 的情况下，针对某个命令临时指定使用的 profile。该参数会覆盖当前激活的 profile，直到命令执行完毕。

| 选项 | 说明 |
|--------|-------------|
| `-p <name>`, `--profile <name>` | 本次命令使用的 profile。 |

**示例：**

```bash
hermes -p work chat -q "Check the server status"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

## `hermes completion`

```bash
hermes completion <shell>
```

生成 shell 补全脚本。包括 profile 名称和 profile 子命令的补全。

| 参数 | 说明 |
|----------|-------------|
| `<shell>` | 要生成补全的 shell 类型：`bash` 或 `zsh`。 |

**示例：**

```bash
# 安装补全
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc

# 重新加载 shell
source ~/.bashrc
```

安装后，Tab 补全支持：
- `hermes profile <TAB>` — 子命令（list、use、create 等）
- `hermes profile use <TAB>` — profile 名称
- `hermes -p <TAB>` — profile 名称

## 参见

- [Profiles 用户指南](../user-guide/profiles.md)
- [CLI 命令参考](./cli-commands.md)
- [FAQ — Profiles 部分](./faq.md#profiles)
