---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和用户自定义皮肤定制 Hermes CLI"
---

# 皮肤与主题 {#skins-themes}

皮肤控制 Hermes CLI 的**视觉呈现**：横幅颜色、旋转动画样式和动词、回复框标签、品牌文字以及工具活动前缀。

对话风格和视觉风格是两个独立的概念：

- **个性** 改变 Agent 的语气和措辞。
- **皮肤** 改变 CLI 的外观。

## 切换皮肤 {#change-skins}

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换到内置皮肤
/skin mytheme        # 切换到 ~/.hermes/skins/mytheme.yaml 中的自定义皮肤
```

或者在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置皮肤 {#built-in-skins}

| 皮肤 | 描述 | Agent 品牌 | 视觉特征 |
|------|------|------------|----------|
| `default` | 经典 Hermes — 金色与可爱风 | `Hermes Agent` | 暖金色边框，玉米丝色文字，旋转动画中的可爱表情。熟悉的双蛇杖横幅。干净且吸引人。 |
| `ares` | 战神主题 — 深红与古铜 | `Ares Agent` | 深红色边框配古铜色点缀。激进的旋转动画动词（"锻造"、"行军"、"淬炼钢铁"）。自定义剑盾 ASCII 艺术横幅。 |
| `mono` | 单色 — 干净灰度 | `Hermes Agent` | 全灰度 — 无颜色。边框为 `#555555`，文字为 `#c9d1d9`。适合极简终端设置或屏幕录制。 |
| `slate` | 冷蓝色 — 面向开发者 | `Hermes Agent` | 皇家蓝边框（`#4169e1`），柔和蓝色文字。冷静且专业。无自定义旋转动画 — 使用默认表情。 |
| `daylight` | 亮色主题，适用于明亮终端，深色文字配冷蓝色点缀 | `Hermes Agent` | 专为白色或明亮终端设计。深石板色文字配蓝色边框，浅色状态表面，以及一个在亮色终端配置下保持可读性的浅色补全菜单。 |
| `warm-lightmode` | 暖棕/金色文字，适用于浅色终端背景 | `Hermes Agent` | 适用于浅色终端的暖羊皮纸色调。深棕色文字配马鞍棕色点缀，奶油色状态表面。比冷色调的 daylight 主题更接地气的选择。 |
| `poseidon` | 海神主题 — 深蓝与海沫绿 | `Poseidon Agent` | 深蓝到海沫绿渐变。海洋主题旋转动画（"绘制洋流"、"探测深度"）。三叉戟 ASCII 艺术横幅。 |
| `sisyphus` | 西西弗斯主题 — 朴素灰度，强调坚持 | `Sisyphus Agent` | 浅灰色配强烈对比。巨石主题旋转动画（"推上山坡"、"重置巨石"、"忍受循环"）。巨石与山丘 ASCII 艺术横幅。 |
| `charizard` | 火山主题 — 焦橙色与余烬 | `Charizard Agent` | 暖焦橙色到余烬渐变。火焰主题旋转动画（"滑入上升气流"、"测量燃烧"）。龙形剪影 ASCII 艺术横幅。 |

## 可配置键的完整列表 {#complete-list-of-configurable-keys}

### 颜色（`colors:`） {#colors-colors}

控制 CLI 中所有颜色值。值为十六进制颜色字符串。

| 键 | 描述 | 默认值（`default` 皮肤） |
|----|------|--------------------------|
| `banner_border` | 启动横幅周围的面板边框 | `#CD7F32`（古铜色） |
| `banner_title` | 横幅中的标题文字颜色 | `#FFD700`（金色） |
| `banner_accent` | 横幅中的章节标题（可用工具等） | `#FFBF00`（琥珀色） |
| `banner_dim` | 横幅中的弱化文字（分隔符、次要标签） | `#B8860B`（深金菊色） |
| `banner_text` | 横幅中的正文文字（工具名称、技能名称） | `#FFF8DC`（玉米丝色） |
| `ui_accent` | 通用 UI 强调色（高亮、活动元素） | `#FFBF00` |
| `ui_label` | UI 标签和标记 | `#4dd0e1`（青色） |
| `ui_ok` | 成功指示器（勾选、完成） | `#4caf50`（绿色） |
| `ui_error` | 错误指示器（失败、阻塞） | `#ef5350`（红色） |
| `ui_warn` | 警告指示器（注意、批准提示） | `#ffa726`（橙色） |
| `prompt` | 交互式提示文字颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的水平分隔线 | `#CD7F32` |
| `response_border` | Agent 回复框的边框（ANSI 转义） | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话 ID 的弱化边框颜色 | `#8B8682` |
| `status_bar_bg` | TUI 状态/使用量栏的背景色 | `#1a1a2e` |
| `voice_status_bg` | 语音模式状态徽章的背景色 | `#1a1a2e` |
| `completion_menu_bg` | 补全菜单列表的背景色 | `#1a1a2e` |
| `completion_menu_current_bg` | 当前补全行的背景色 | `#333355` |
| `completion_menu_meta_bg` | 补全元数据列的背景色 | `#1a1a2e` |
| `completion_menu_meta_current_bg` | 当前补全元数据列的背景色 | `#333355` |
### Spinner（`spinner:`） {#spinner-spinner}

控制等待 API 响应时显示的动画旋转器。

| 键 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的面孔 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理时循环显示的面孔 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 旋转器消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | [左, 右] 对列表 | 旋转器周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当 spinner 值为空时（如 `default` 和 `mono` 皮肤），将使用 `display.py` 中的硬编码默认值。

### 品牌标识（`branding:`） {#branding-branding}

CLI 界面中使用的文本字符串。

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 横幅标题和状态显示中显示的名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框标题上的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示前的符号（裸 token，渲染器会添加尾随空格） | `❯` |
| `help_header` | `/help` 命令输出的标题文本 | `(^_^)? Available Commands` |

### 其他顶级键 {#other-top-level-keys}

| 键 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前添加的字符 | `┊` |
| `tool_emojis` | 字典 | 每个工具的 emoji 覆盖（用于旋转器和进度显示）（`{tool_name: emoji}`） | `{}` |
| `banner_logo` | 字符串 | Rich 标记的 ASCII 艺术标志（替换默认的 HERMES_AGENT 横幅） | `""` |
| `banner_hero` | 字符串 | Rich 标记的英雄艺术（替换默认的蛇杖艺术） | `""` |

## 自定义皮肤 {#custom-skins}

在 `~/.hermes/skins/` 下创建 YAML 文件。用户皮肤会从内置的 `default` 皮肤继承缺失的值，因此您只需指定要更改的键。

### 完整自定义皮肤 YAML 模板 {#full-custom-skin-yaml-template}

```yaml
# ~/.hermes/skins/mytheme.yaml
# 完整皮肤模板 — 显示所有键。删除任何不需要的键；
# 缺失的值会自动从 'default' 皮肤继承。

name: mytheme
description: 我的自定义主题

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
  status_bar_bg: "#1a1a2e"
  voice_status_bg: "#1a1a2e"
  completion_menu_bg: "#1a1a2e"
  completion_menu_current_bg: "#333355"
  completion_menu_meta_bg: "#1a1a2e"
  completion_menu_meta_current_bg: "#333355"

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
  prompt_symbol: "⚡"
  help_header: "(⚡) Available Commands"

tool_prefix: "┊"

# 每个工具的 emoji 覆盖（可选）
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
### 最小自定义皮肤示例 {#minimal-custom-skin-example}

由于所有皮肤都继承自 `default`，一个最小皮肤只需修改不同的部分：

```yaml
name: cyberpunk
description: 霓虹终端主题

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["正在接入", "正在解密", "正在上传"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "

tool_prefix: "▏"
```

## Hermes Mod — 可视化皮肤编辑器 {#hermes-mod-visual-skin-editor}

[Hermes Mod](https://github.com/cocktailpeanut/hermes-mod) 是一个社区构建的 Web UI，用于可视化创建和管理皮肤。无需手动编写 YAML，你只需使用一个带实时预览的点击式编辑器。

![Hermes Mod 皮肤编辑器](https://raw.githubusercontent.com/cocktailpeanut/hermes-mod/master/nous.png)

**功能：**

- 列出所有内置和自定义皮肤
- 将任何皮肤打开到可视化编辑器中，包含所有 Hermes 皮肤字段（颜色、spinner、品牌、工具前缀、工具表情符号）
- 根据文本提示生成 `banner_logo` 文字艺术
- 将上传的图片（PNG、JPG、GIF、WEBP）转换为 `banner_hero` ASCII 艺术，支持多种渲染样式（盲文、ASCII 斜坡、块、点）
- 直接保存到 `~/.hermes/skins/`
- 通过更新 `~/.hermes/config.yaml` 激活皮肤
- 显示生成的 YAML 和实时预览

### 安装 {#install}

**选项 1 — Pinokio（一键安装）：**

在 [pinokio.computer](https://pinokio.computer) 上找到它，一键安装。

**选项 2 — npx（终端中最快）：**

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

### 使用方法 {#usage}

1. 启动应用（通过 Pinokio 或终端）。
2. 打开 **Skin Studio**。
3. 选择一个内置或自定义皮肤进行编辑。
4. 从文本生成徽标和/或上传图片作为英雄艺术。选择渲染样式和宽度。
5. 编辑颜色、spinner、品牌和其他字段。
6. 点击 **保存** 将皮肤 YAML 写入 `~/.hermes/skins/`。
7. 点击 **激活** 将其设置为当前皮肤（更新 `config.yaml` 中的 `display.skin`）。

Hermes Mod 尊重 `HERMES_HOME` 环境变量，因此它也适用于 [配置文件](/user-guide/profiles)。

## 操作说明 {#operational-notes}

- 内置皮肤从 `hermes_cli/skin_engine.py` 加载。
- 未知皮肤会自动回退到 `default`。
- `/skin` 会立即更新当前会话的活动 CLI 主题。
- `~/.hermes/skins/` 中的用户皮肤优先于同名的内置皮肤。
- 通过 `/skin` 进行的皮肤更改仅限当前会话。要使皮肤成为永久默认，请在 `config.yaml` 中设置。
- `banner_logo` 和 `banner_hero` 字段支持 Rich 控制台标记（例如 `[bold #FF0000]text[/]`）用于彩色 ASCII 艺术。
