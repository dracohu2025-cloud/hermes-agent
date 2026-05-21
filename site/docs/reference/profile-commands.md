---
sidebar_position: 7
---

<a id="profile-commands-reference"></a>
# Profile 命令参考

本文档涵盖所有与 [Hermes profiles](../user-guide/profiles.md) 相关的命令。关于通用 CLI 命令，请参见 [CLI 命令参考](./cli-commands.md)。

<a id="hermes-profile"></a>
## `hermes profile`

```bash
hermes profile <子命令>
```

用于管理 profile 的顶级命令。直接运行 `hermes profile`（不带子命令）会显示帮助信息。

| 子命令 | 说明 |
|--------|------|
| `list` | 列出所有 profile。 |
| `use` | 设置当前生效（默认）的 profile。 |
| `create` | 创建一个新的 profile。 |
| `delete` | 删除一个 profile。 |
| `show` | 显示某个 profile 的详细信息。 |
| `alias` | 重新生成某个 profile 的 shell 别名。 |
| `rename` | 重命名一个 profile。 |
| `export` | 将一个 profile 导出为 tar.gz 存档。 |
| `import` | 从 tar.gz 存档导入一个 profile。 |
| `install` | 从 Git URL 或本地目录安装一个 profile 发行版。参见 [Profile 发行版](../user-guide/profile-distributions.md)。 |
| `update` | 重新拉取由发行版管理的 profile 并重新应用其 bundle。 |
| `info` | 显示某个 profile 的发行版元数据（源 URL、commit、最后更新时间）。 |

<a id="hermes-profile-list"></a>
## `hermes profile list`

```bash
hermes profile list
```

列出所有 profile。当前生效的 profile 会以 `*` 标记。

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

将 `<名称>` 设置为当前生效的 profile。之后所有 `hermes` 命令（不带 `-p` 参数）都将使用该 profile。

| 参数 | 说明 |
|------|------|
| `<名称>` | 要激活的 profile 名称。使用 `default` 可返回基础 profile。 |

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

创建一个新的 profile。

| 参数 / 选项 | 说明 |
|--------------|------|
| `<名称>` | 新 profile 的名称。必须是合法的目录名（字母数字、连字符、下划线）。 |
| `--clone` | 从当前 profile 复制 `config.yaml`、`.env` 和 `SOUL.md`。 |
| `--clone-all` | 从当前 profile 复制所有内容（配置、记忆、技能、会话、状态）。 |
| `--clone-from &lt;profile&gt;` | 从指定 profile 克隆，而不是从当前 profile。需与 `--clone` 或 `--clone-all` 一起使用。 |
| `--no-alias` | 跳过包装脚本的创建。 |
| `--description "<文本>"` | 一两句话描述该 profile 擅长什么。看板编排器会使用此描述根据角色（而非仅 profile 名称）来路由任务。可以跳过，之后通过 `hermes profile describe` 添加。会持久化存储在 `&lt;profile_dir&gt;/profile.yaml` 中。 |
| `--no-skills` | 创建一个**空的** profile，不启用任何捆绑技能。会在 profile 中写入一个 `.no-skills` 标记，这样后续的 `hermes update` 就不会重新注入捆绑的技能集。该选项不能与 `--clone` / `--clone-all` 一起使用（因为后者无论如何都会复制技能）。适用于狭窄的编排器 profile 或沙箱 profile，这些 profile 不应继承完整的技能目录。 |
创建 profile 并**不会**使该 profile 目录成为终端命令的默认项目/工作区目录。如果你希望某个 profile 从一个特定项目开始，请在该 profile 的 `config.yaml` 中设置 `terminal.cwd`。

**示例：**

```bash
# 空白 profile —— 需要完整设置
hermes profile create mybot

# 仅从当前 profile 克隆配置
hermes profile create work --clone

# 从当前 profile 克隆所有内容
hermes profile create backup --clone-all

# 从特定 profile 克隆配置
hermes profile create work2 --clone --clone-from work
```

<a id="hermes-profile-describe"></a>
## `hermes profile describe`

```bash
hermes profile describe [<name>] [options]
```

读取或设置 profile 的描述。看板编排器会使用该描述，根据每个 profile 擅长的内容来路由任务，而不是仅靠 profile 名称猜测。描述会持久化保存在 `&lt;profile_dir&gt;/profile.yaml` 中，因此重启后依然保留，并且会与网关共享。

不带任何标志时，会打印当前的描述（如果为空则显示 `(no description set for '&lt;name&gt;')`）。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;name&gt;` | 要描述的 profile。除非使用了 `--all --auto`，否则必填。 |
| `--text "&lt;text&gt;"` | 将描述设置为这段精确文本（用户编写）。会覆盖任何现有描述。 |
| `--auto` | 通过辅助 LLM，根据 profile 已安装的技能、配置的模型和名称，自动生成一条 1-2 句话的描述。在 `config.yaml` 的 `auxiliary.profile_describer` 下配置模型。自动生成的描述会被标记为 `description_auto: true`，以便仪表盘将其标记为待审核。 |
| `--overwrite` | 与 `--auto` 一起使用时，也会替换用户编写的描述（默认：跳过那些描述被显式设置的 profile）。 |
| `--all` | 与 `--auto` 一起使用时，扫描所有缺少描述的 profile。 |

**示例：**

```bash
# 读取当前描述
hermes profile describe researcher

# 显式设置描述
hermes profile describe researcher --text "Reads source code and writes findings."

# 让 LLM 生成描述
hermes profile describe researcher --auto

# 为所有没有描述的 profile 填充描述
hermes profile describe --all --auto
```

<a id="hermes-profile-delete"></a>
## `hermes profile delete`

```bash
hermes profile delete <name> [options]
```

删除一个 profile 并移除其 shell 别名。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `&lt;name&gt;` | 要删除的 profile。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例：**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
这将永久删除该 profile 的整个目录，包括所有配置、记忆、会话和技能。不能删除当前活跃的 profile。
:::

<a id="hermes-profile-show"></a>
## `hermes profile show`

```bash
hermes profile show <name>
```

显示 profile 的详细信息，包括其主目录、配置的模型、网关状态、技能数量以及配置文件状态。

这里显示的是该 profile 的 Hermes 主目录，而不是终端工作目录。终端命令从 `terminal.cwd` 启动（当 `cwd: "."` 时，则是本地后端上的启动目录）。
| 参数 | 说明 |
|----------|-------------|
| `&lt;name&gt;` | 要查看的 Profile 名称。 |

**示例：**

```bash
$ hermes profile show work
Profile: work
Path:    ~/.hermes/profiles/work
Model:   anthropic/claude-sonnet-4 (anthropic)
Gateway: stopped
Skills:  12
.env:    exists
SOUL.md: exists
Alias:   ~/.local/bin/work
```

<a id="hermes-profile-alias"></a>
## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

重新生成 `~/.local/bin/&lt;name&gt;` 下的 shell 别名脚本。当别名被意外删除，或移动 Hermes 安装位置后需要更新别名时，这个命令很有用。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `&lt;name&gt;` | 要创建/更新别名的 Profile 名称。 |
| `--remove` | 删除包装脚本，而不是创建它。 |
| `--name &lt;alias&gt;` | 自定义别名名称（默认：Profile 名称）。 |

**示例：**

```bash
hermes profile alias work
# 创建/更新 ~/.local/bin/work

hermes profile alias work --name mywork
# 创建 ~/.local/bin/mywork

hermes profile alias work --remove
# 删除包装脚本
```

<a id="hermes-profile-rename"></a>
## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

重命名一个 Profile。会同时更新目录和 shell 别名。

| 参数 | 说明 |
|----------|-------------|
| `&lt;old-name&gt;` | 当前 Profile 名称。 |
| `&lt;new-name&gt;` | 新的 Profile 名称。 |

**示例：**

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

将 Profile 导出为压缩的 tar.gz 归档文件。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `&lt;name&gt;` | 要导出的 Profile 名称。 |
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

从 tar.gz 归档文件导入一个 Profile。

| 参数 / 选项 | 说明 |
|-------------------|-------------|
| `&lt;archive&gt;` | 要导入的 tar.gz 归档文件路径。 |
| `--name &lt;name&gt;` | 导入后的 Profile 名称（默认：从归档文件推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# 从归档文件推断 Profile 名称

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

<a id="distribution-commands"></a>
## 分发命令

:::tip
**刚接触分发？** 请先阅读 [Profile 分发用户指南](../user-guide/profile-distributions.md)——它通过完整示例介绍了为什么、何时以及如何使用。以下部分是一个简洁的 CLI 参考，适合你已经明确需求时查阅。
:::

分发功能将 Profile 转换为一个可分享、带版本号的制品，并以 **git 仓库**的形式发布。接收方只需一条命令即可安装该分发，之后还可以原地更新，而无需触碰本地的记忆、会话或凭据。
`auth.json` 和 `.env` 永远不会被打包分发——它们只保留在安装用户的机器上。

接收方的用户数据（记忆、会话、认证信息、他们对 `.env` 的编辑）在初始安装及后续更新中都会始终保留。

:::info
`hermes profile export` / `import` 仍然是在本地机器上进行 **本地备份与恢复** 的正确命令。分发（`install` / `update` / `info`）是一个独立的概念：通过 git 发布一个配置，以便其他人可以安装它。
:::

<a id="hermes-profile-install"></a>
### `hermes profile install`

```bash
hermes profile install <source> [--name <name>] [--alias] [--force] [--yes]
```

从 Git URL 或本地目录安装一个配置分发。

| 选项 | 说明 |
|--------|-------------|
| `&lt;source&gt;` | Git URL（`github.com/user/repo`、`https://...`、`git@...`、`ssh://`、`git://`）或根目录下包含 `distribution.yaml` 的本地目录。 |
| `--name NAME` | 覆盖清单中的配置名称。 |
| `--alias` | 同时创建一个 Shell 包装器（例如 `telemetry` → `hermes -p telemetry`）。 |
| `--force` | 覆盖已存在的同名配置。用户数据仍然保留。 |
| `-y`, `--yes` | 跳过清单预览确认提示。 |

安装程序会在请求确认前显示清单、列出所需的环境变量，并警告 cron 任务。所需的环境变量会写入一个 `.env.EXAMPLE` 文件，你需要将其复制为 `.env` 并填写。

**示例：**

```bash
# 从 GitHub 仓库安装（简写）
hermes profile install github.com/kyle/telemetry-distribution --alias

# 从完整的 HTTPS Git URL 安装
hermes profile install https://github.com/kyle/telemetry-distribution.git

# 通过 SSH 安装
hermes profile install git@github.com:kyle/telemetry-distribution.git

# 在开发期间从本地目录安装
hermes profile install ./telemetry/
```

<a id="hermes-profile-update"></a>
### `hermes profile update`

```bash
hermes profile update <name> [--force-config] [--yes]
```

从记录的源地址重新克隆分发并应用更新。分发所拥有的文件（SOUL.md、skills/、cron/、mcp.json）会被覆盖；用户数据（记忆、会话、认证信息、.env）则不会被触及。

默认情况下会保留 `config.yaml`，以保持你的本地覆盖配置。如果使用 `--force-config`，则会将其重置为分发自带的配置。

<a id="hermes-profile-info"></a>
### `hermes profile info`

```bash
hermes profile info <name>
```

打印配置的分发清单——包括名称、版本、所需的 Hermes 版本、作者、环境变量需求、源 URL/路径，以及最后一次 `install` 或 `update` 分发时记录的 `Installed:` 时间戳。这对于在安装共享配置前检查其需求，以及发现“这个配置是 6 个月前安装的且从未更新过”很有用。

`hermes profile list` 也会在 `Distribution` 列中显示分发名称和版本，而 `hermes profile show &lt;name&gt;` / `delete &lt;name&gt;` 会显示源 URL，让你一眼就能看出哪些配置来自 git 仓库，哪些是本地创建的。
<a id="private-distributions"></a>
### 私有分发

私有 Git 仓库无需额外配置即可作为分发源使用——安装时 Hermes 会调用你本地的 `git` 二进制文件，因此你的 shell 已经配置好的认证方式（SSH 密钥、`git credential` helper、GitHub CLI 存储的 HTTPS 凭据）都会透明生效。

```bash
# 使用你的 SSH 密钥，和普通的 `git clone` 一样
hermes profile install git@github.com:your-org/internal-assistant.git

# 使用你的 git credential helper
hermes profile install https://github.com/your-org/internal-assistant.git
```

如果在安装过程中克隆操作在终端中交互式地要求提供凭据，这些提示会直接显示。请先像平常使用 `git clone` 克隆同一仓库那样设置好认证，然后再执行安装。

<a id="distribution-manifest-distribution-yaml"></a>
### 分发清单 (`distribution.yaml`)

每个分发版本的仓库根目录下都有一个 `distribution.yaml`：

```yaml
name: telemetry
version: 0.1.0
description: "Compliance monitoring harness"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "Memory graph URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
distribution_owned:   # 可选；默认值为 SOUL.md, config.yaml,
                      #   mcp.json, skills/, cron/, distribution.yaml
  - SOUL.md
  - skills/compliance/
  - cron/
```

`hermes_requires` 支持 `>=`、`<=`、`==`、`!=`、`>`、`<`，或一个裸版本号（视为 `>=`）。如果当前 Hermes 版本不满足此约束，安装会失败并显示清晰的错误信息。

`distribution_owned` 是可选的。如果设置了此字段，则更新时只会替换这些路径；配置文件中其余部分仍归用户所有。如果省略，则应用上述默认值。

<a id="publishing-a-distribution"></a>
### 发布一个分发

编写一个分发版本只需要执行一次 git push：

1. 在你的配置文件目录中创建 `distribution.yaml`，至少包含 `name` 和 `version`。
2. 初始化一个 Git 仓库（或使用现有的），然后推送到 GitHub / GitLab / 任何 Hermes 能够克隆的主机。
3. 告诉接收者运行 `hermes profile install <你的仓库地址>`。

使用 Git 标签进行版本化发布——克隆 `HEAD` 的接收者会得到你的最新状态，你随时可以更新清单中的 `version:`。

<a id="hermes-p-hermes-profile"></a>
## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

全局标志，用于在特定配置文件下运行任何 Hermes 命令，而不更改粘性默认值。该标志在命令执行期间覆盖当前激活的配置文件。

| 选项 | 描述 |
|--------|-------------|
| `-p &lt;name&gt;`, `--profile &lt;name&gt;` | 为此命令使用的配置文件。 |

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

生成 shell 补全脚本。包括配置文件名称以及配置文件子命令的补全。
| 参数 | 描述 |
|----------|-------------|
| `&lt;shell&gt;` | 为其生成补全的 Shell：`bash`、`zsh` 或 `fish`。 |

**示例：**

```bash
# 安装补全
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc
hermes completion fish > ~/.config/fish/completions/hermes.fish

# 重新加载 Shell
source ~/.bashrc
```

安装后，Tab 补全可用于：
- `hermes profile &lt;TAB&gt;` — 子命令（list、use、create 等）
- `hermes profile use &lt;TAB&gt;` — 配置文件名称
- `hermes -p &lt;TAB&gt;` — 配置文件名称

<a id="see-also"></a>
## 另请参阅

- [配置文件用户指南](../user-guide/profiles.md)
- [CLI 命令参考](./cli-commands.md)
- [常见问题 — 配置文件部分](./faq.md#profiles)
