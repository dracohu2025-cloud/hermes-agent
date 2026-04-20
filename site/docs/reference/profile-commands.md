---
sidebar_position: 7
---

<a id="profile-commands-reference"></a>
# 配置文件命令参考

本页涵盖了所有与 [Hermes 配置文件](../user-guide/profiles.md) 相关的命令。关于通用 CLI 命令，请参阅 [CLI 命令参考](./cli-commands.md)。

<a id="hermes-profile"></a>
## `hermes profile`

```bash
hermes profile <子命令>
```

管理配置文件的总命令。不带子命令运行 `hermes profile` 会显示帮助信息。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use` | 设置活动（默认）配置文件。 |
| `create` | 创建新的配置文件。 |
| `delete` | 删除配置文件。 |
| `show` | 显示配置文件的详细信息。 |
| `alias` | 为配置文件重新生成 shell 别名。 |
| `rename` | 重命名配置文件。 |
| `export` | 将配置文件导出为 tar.gz 归档文件。 |
| `import` | 从 tar.gz 归档文件导入配置文件。 |

<a id="hermes-profile-list"></a>
## `hermes profile list`

```bash
hermes profile list
```

列出所有配置文件。当前活动的配置文件会用 `*` 标记。

**示例：**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

无选项。

<a id="hermes-profile-use"></a>
## `hermes profile use`

```bash
hermes profile use <名称>
```

将 `<名称>` 设置为活动配置文件。所有后续的 `hermes` 命令（不带 `-p` 参数）都将使用此配置文件。

| 参数 | 描述 |
|----------|-------------|
| `<名称>` | 要激活的配置文件名称。使用 `default` 可返回基础配置文件。 |

**示例：**

```bash
hermes profile use work
hermes profile use default
```

<a id="hermes-profile-create"></a>
## `hermes profile create`

```bash
hermes profile create <名称> [选项]
```

创建一个新的配置文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<名称>` | 新配置文件的名称。必须是有效的目录名（字母数字、连字符、下划线）。 |
| `--clone` | 从当前配置文件复制 `config.yaml`、`.env` 和 `SOUL.md`。 |
| `--clone-all` | 从当前配置文件复制所有内容（配置、记忆、技能、会话、状态）。 |
| `--clone-from <配置文件>` | 从指定的配置文件克隆，而不是当前配置文件。与 `--clone` 或 `--clone-all` 一起使用。 |
| `--no-alias` | 跳过包装脚本的创建。 |

创建配置文件**不会**使该配置文件的目录成为终端命令的默认项目/工作空间目录。如果你希望某个配置文件在特定项目中启动，请在该配置文件的 `config.yaml` 中设置 `terminal.cwd`。

**示例：**

```bash
# 空白配置文件 — 需要完整设置
hermes profile create mybot

# 仅从当前配置文件克隆配置
hermes profile create work --clone

# 从当前配置文件克隆所有内容
hermes profile create backup --clone-all

# 从指定配置文件克隆配置
hermes profile create work2 --clone --clone-from work
```
<a id="hermes-profile-delete"></a>
## `hermes profile delete`

```bash
hermes profile delete <name> [options]
```

删除一个配置文件并移除其对应的 shell 别名。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;name&gt;` | 要删除的配置文件名称。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例:**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
此操作将永久删除该配置文件的整个目录，包括所有配置、记忆、会话和技能。无法删除当前正在使用的配置文件。
:::

<a id="hermes-profile-show"></a>
## `hermes profile show`

```bash
hermes profile show <name>
```

显示配置文件的详细信息，包括其主目录、配置的模型、网关状态、技能数量和配置文件状态。

这里显示的是配置文件的 Hermes 主目录，而非终端工作目录。终端命令从 `terminal.cwd`（或在本地后端启动时，当 `cwd: "."` 时则为启动目录）开始执行。

| 参数 | 描述 |
|----------|-------------|
| `&lt;name&gt;` | 要检查的配置文件名称。 |

**示例:**

```bash
$ hermes profile show work
配置文件: work
路径:    ~/.hermes/profiles/work
模型:   anthropic/claude-sonnet-4 (anthropic)
网关:   已停止
技能:  12
.env:    存在
SOUL.md: 存在
别名:   ~/.local/bin/work
```

<a id="hermes-profile-alias"></a>
## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

在 `~/.local/bin/&lt;name&gt;` 处重新生成 shell 别名脚本。如果别名被意外删除，或者在移动 Hermes 安装位置后需要更新它，这个命令很有用。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;name&gt;` | 要为其创建/更新别名的配置文件名称。 |
| `--remove` | 移除包装脚本，而不是创建它。 |
| `--name &lt;alias&gt;` | 自定义别名名称（默认：配置文件名称）。 |

**示例:**

```bash
hermes profile alias work
# 创建/更新 ~/.local/bin/work

hermes profile alias work --name mywork
# 创建 ~/.local/bin/mywork

hermes profile alias work --remove
# 移除包装脚本
```

<a id="hermes-profile-rename"></a>
## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

重命名一个配置文件。更新目录和 shell 别名。

| 参数 | 描述 |
|----------|-------------|
| `&lt;old-name&gt;` | 当前配置文件名称。 |
| `&lt;new-name&gt;` | 新的配置文件名称。 |

**示例:**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

<a id="hermes-profile-export"></a>
## `hermes profile export`

```bash
hermes profile export <name> [options]
```
将配置文件导出为压缩的 tar.gz 存档。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;name&gt;` | 要导出的配置文件名称。 |
| `-o`, `--output &lt;path&gt;` | 输出文件路径（默认：`&lt;name&gt;.tar.gz`）。 |

**示例：**

```bash
hermes profile export work
# 在当前目录创建 work.tar.gz

hermes profile export work -o ./work-2026-03-29.tar.gz
```

<a id="hermes-profile-import"></a>
## `hermes profile import`

```bash
hermes profile import <archive> [options]
```

从 tar.gz 存档导入配置文件。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;archive&gt;` | 要导入的 tar.gz 存档路径。 |
| `--name &lt;name&gt;` | 导入的配置文件名称（默认：从存档推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从存档推断配置文件名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

<a id="hermes-p-hermes-profile"></a>
## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

全局标志，用于在特定配置文件下运行任何 Hermes 命令，而无需更改粘性默认值。此操作会在命令执行期间覆盖当前活跃的配置文件。

| 选项 | 描述 |
|--------|-------------|
| `-p &lt;name&gt;`, `--profile &lt;name&gt;` | 用于此命令的配置文件。 |

**示例：**

```bash
hermes -p work chat -q "Check the server status"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

<a id="hermes-completion"></a>
## `hermes completion`

```bash
hermes completion <shell>
```

生成 shell 自动补全脚本。包含对配置文件名称和配置文件子命令的补全。

| 参数 | 描述 |
|----------|-------------|
| `&lt;shell&gt;` | 为其生成补全的 shell：`bash` 或 `zsh`。 |

**示例：**

```bash
# 安装补全脚本
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc

# 重新加载 shell
source ~/.bashrc
```

安装后，Tab 补全适用于：
- `hermes profile &lt;TAB&gt;` — 子命令（list、use、create 等）
- `hermes profile use &lt;TAB&gt;` — 配置文件名称
- `hermes -p &lt;TAB&gt;` — 配置文件名称

<a id="see-also"></a>
## 另请参阅

- [配置文件用户指南](../user-guide/profiles.md)
- [CLI 命令参考](./cli-commands.md)
- [FAQ — 配置文件部分](./faq.md#profiles)
