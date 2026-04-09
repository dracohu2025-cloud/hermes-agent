---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和自定义皮肤自定义 Hermes CLI"
---

# 皮肤与主题

皮肤控制着 Hermes CLI 的**视觉呈现**：横幅颜色、加载动画（spinner）的表情与动词、响应框标签、品牌文本以及工具活动前缀。

对话风格与视觉风格是两个独立的概念：

- **个性（Personality）**：改变 Agent 的语气和措辞。
- **皮肤（Skin）**：改变 CLI 的外观。

## 切换皮肤

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换到内置的 ares 皮肤
/skin mytheme        # 切换到 ~/.hermes/skins/mytheme.yaml 中的自定义皮肤
```

或者在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置皮肤

| 皮肤 | 描述 | Agent 品牌名称 | 视觉特征 |
|------|-------------|----------------|------------------|
| `default` | 经典 Hermes — 金色与可爱风 | `Hermes Agent` | 温暖的金色边框，奶油色文本，加载动画中带有可爱的表情。熟悉的双蛇杖横幅。简洁且引人入胜。 |
| `ares` | 战神主题 — 深红与青铜色 | `Ares Agent` | 深红色边框配青铜色点缀。激进的加载动词（“锻造中”、“行军中”、“淬火中”）。自定义的剑盾 ASCII 艺术横幅。 |
| `mono` | 单色 — 简洁的灰度风格 | `Hermes Agent` | 全灰色 — 无色彩。边框为 `#555555`，文本为 `#c9d1d9`。非常适合极简终端设置或屏幕录制。 |
| `slate` | 冷蓝色 — 开发者导向 | `Hermes Agent` | 宝蓝色边框（`#4169e1`），柔和的蓝色文本。冷静且专业。无自定义加载动画 — 使用默认表情。 |
| `poseidon` | 海神主题 — 深蓝与海沫色 | `Poseidon Agent` | 从深蓝到海沫色的渐变。海洋主题的加载动画（“绘制洋流”、“探测深度”）。三叉戟 ASCII 艺术横幅。 |
| `sisyphus` | 西西弗斯主题 — 带有坚持感的严谨灰度 | `Sisyphus Agent` | 浅灰色，对比鲜明。巨石主题的加载动画（“推石上山”、“重置巨石”、“忍受循环”）。巨石与山丘 ASCII 艺术横幅。 |
| `charizard` | 火山主题 — 焦橙色与余烬色 | `Charizard Agent` | 从温暖的焦橙色到余烬色的渐变。火焰主题的加载动画（“切入气流”、“测量燃烧”）。龙影 ASCII 艺术横幅。 |

## 可配置键完整列表

### 颜色 (`colors:`)

控制 CLI 中所有的颜色值。值均为十六进制颜色字符串。

| 键 | 描述 | 默认值 (`default` 皮肤) |
|-----|-------------|--------------------------|
| `banner_border` | 启动横幅周围的面板边框 | `#CD7F32` (青铜色) |
| `banner_title` | 横幅中的标题文本颜色 | `#FFD700` (金色) |
| `banner_accent` | 横幅中的部分标题（可用工具等） | `#FFBF00` (琥珀色) |
| `banner_dim` | 横幅中的静音文本（分隔符、次要标签） | `#B8860B` (深金菊色) |
| `banner_text` | 横幅中的正文文本（工具名称、技能名称） | `#FFF8DC` (奶油色) |
| `ui_accent` | 通用 UI 强调色（高亮、活动元素） | `#FFBF00` |
| `ui_label` | UI 标签和标记 | `#4dd0e1` (青色) |
| `ui_ok` | 成功指示器（勾选标记、完成） | `#4caf50` (绿色) |
| `ui_error` | 错误指示器（失败、阻塞） | `#ef5350` (红色) |
| `ui_warn` | 警告指示器（注意、批准提示） | `#ffa726` (橙色) |
| `prompt` | 交互式提示符文本颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的水平线 | `#CD7F32` |
| `response_border` | Agent 响应框周围的边框（ANSI 转义） | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话 ID 的暗边框颜色 | `#8B8682` |

### 加载动画 (`spinner:`)

控制等待 API 响应时显示的动画加载器。

| 键 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的表情 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理期间循环显示的表情 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 加载消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | [左, 右] 对列表 | 加载器周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当加载动画值为空时（如 `default` 和 `mono` 皮肤），将使用 `display.py` 中硬编码的默认值。

### 品牌信息 (`branding:`)

在整个 CLI 界面中使用的文本字符串。

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 横幅标题和状态显示中显示的名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框标题上的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示符前的符号 | `❯ ` |
| `help_header` | `/help` 命令输出的标题文本 | `(^_^)? Available Commands` |

### 其他顶级键

| 键 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前缀的字符 | `┊` |
| `tool_emojis` | 字典 | 每个工具的表情符号覆盖（用于加载动画和进度）(`{tool_name: emoji}`) | `{}` |
| `banner_logo` | 字符串 | 富文本标记的 ASCII 艺术 Logo（替换默认的 HERMES_AGENT 横幅） | `""` |
| `banner_hero` | 字符串 | 富文本标记的英雄艺术图（替换默认的双蛇杖艺术图） | `""` |

## 自定义皮肤

在 `~/.hermes/skins/` 下创建 YAML 文件。用户皮肤会从内置的 `default` 皮肤继承缺失的值，因此你只需要指定想要更改的键即可。

### 完整自定义皮肤 YAML 模板

```yaml
# ~/.hermes/skins/mytheme.yaml
# 完整的皮肤模板 — 显示所有键。删除你不需要的任何键；
# 缺失的值将自动从 'default' 皮肤继承。

name: mytheme
description: My custom theme

colors:
  banner_border: "#CD7F32"
  banner_title: "#FFD700"
  banner_accent: "#FFBF00"
  banner_dim: "#B8860B"
  banner_text: "#FFF8DC"
  ui_accent: "#FFBF00"
  ui_label: "#4dd0e1"
  ui_ok: "#4caf50"
  ui_error: "#ef5350"
  ui_warn: "#ffa726"
  prompt: "#FFF8DC"
  input_rule: "#CD7F32"
  response_border: "#FFD700"
  session_label: "#DAA520"
  session_border: "#8B8682"

spinner:
  waiting_faces:
    - "(⚔)"
    - "(⛨)"
    - "(▲)"
  thinking_faces:
    - "(⚔)"
    - "(⌁)"
    - "(<>)"
  thinking_verbs:
    - "processing"
    - "analyzing"
    - "computing"
    - "evaluating"
  wings:
    - ["⟪⚡", "⚡⟫"]
    - ["⟪●", "●⟫"]

branding:
  agent_name: "My Agent"
  welcome: "Welcome to My Agent! Type your message or /help for commands."
  goodbye: "See you later! ⚡"
  response_label: " ⚡ My Agent "
  prompt_symbol: "⚡ ❯ "
  help_header: "(⚡) Available Commands"

tool_prefix: "┊"

# 每个工具的表情符号覆盖（可选）
tool_emojis:
  terminal: "⚔"
  web_search: "🔮"
  read_file: "📄"

# 自定义 ASCII 艺术横幅（可选，支持 Rich 标记）
# banner_logo: |
#   [bold #FFD700] MY AGENT [/]
# banner_hero: |
#   [#FFD700]  Custom art here  [/]
```

### 最小化自定义皮肤示例

由于所有内容都继承自 `default`，最小化的皮肤只需要更改不同的部分：

```yaml
name: cyberpunk
description: Neon terminal theme

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["jacking in", "decrypting", "uploading"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "

tool_prefix: "▏"
```

## Hermes Mod — 可视化皮肤编辑器

[Hermes Mod](https://github.com/cocktailpeanut/hermes-mod) 是一个社区构建的 Web UI，用于可视化地创建和管理皮肤。你无需手动编写 YAML，而是可以使用带有实时预览功能的点击式编辑器。

![Hermes Mod 皮肤编辑器](https://raw.githubusercontent.com/cocktailpeanut/hermes-mod/master/nous.png)

**功能特点：**

- 列出所有内置和自定义皮肤
- 在可视化编辑器中打开任何皮肤，包含所有 Hermes 皮肤字段（颜色、加载动画、品牌信息、工具前缀、工具表情）
- 根据文本提示生成 `banner_logo` 文本艺术
- 将上传的图像（PNG、JPG、GIF、WEBP）转换为带有多种渲染风格（盲文、ASCII 渐变、块、点）的 `banner_hero` ASCII 艺术
- 直接保存到 `~/.hermes/skins/`
- 通过更新 `~/.hermes/config.yaml` 来激活皮肤
- 显示生成的 YAML 和实时预览
### 安装

**选项 1 — Pinokio（一键安装）：**

在 [pinokio.computer](https://pinokio.computer) 上找到它并一键安装。

**选项 2 — npx（终端最快方式）：**

```bash
npx -y hermes-mod
```

**选项 3 — 手动安装：**

```bash
git clone https://github.com/cocktailpeanut/hermes-mod.git
cd hermes-mod/app
npm install
npm start
```

### 使用方法

1. 启动应用（通过 Pinokio 或终端）。
2. 打开 **Skin Studio**。
3. 选择一个内置或自定义的皮肤进行编辑。
4. 通过文本生成 Logo 和/或上传一张 Hero Art 图片。选择渲染风格和宽度。
5. 编辑颜色、加载动画（spinner）、品牌标识及其他字段。
6. 点击 **Save** 将皮肤 YAML 文件写入 `~/.hermes/skins/`。
7. 点击 **Activate** 将其设置为当前皮肤（这会更新 `config.yaml` 中的 `display.skin`）。

Hermes Mod 支持 `HERMES_HOME` 环境变量，因此它也适用于 [profiles](/user-guide/profiles)。

## 操作说明

- 内置皮肤从 `hermes_cli/skin_engine.py` 加载。
- 未知的皮肤会自动回退到 `default`。
- `/skin` 命令会立即更新当前会话的 CLI 主题。
- `~/.hermes/skins/` 中的用户皮肤优先级高于同名的内置皮肤。
- 通过 `/skin` 进行的皮肤更改仅在当前会话有效。若要将皮肤设为永久默认，请在 `config.yaml` 中进行设置。
- `banner_logo` 和 `banner_hero` 字段支持 Rich 控制台标记（例如 `[bold #FF0000]text[/]`），可用于彩色 ASCII 艺术。
