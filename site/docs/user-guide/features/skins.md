---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和用户自定义的皮肤来定制 Hermes CLI"
---

<a id="skins-themes"></a>
# 皮肤与主题

皮肤控制 Hermes CLI 的**视觉呈现**：横幅颜色、加载动画图标与动作动词、回复框标签、品牌文字以及工具活动前缀。

对话风格和视觉风格是两个独立的概念：

- **人格** 改变 Agent 的语气和措辞。
- **皮肤** 改变 CLI 的外观。

<a id="change-skins"></a>
## 更换皮肤

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换为内置皮肤
/skin mytheme        # 切换到 ~/.hermes/skins/mytheme.yaml 中的自定义皮肤
```

也可以在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

<a id="built-in-skins"></a>
## 内置皮肤

| 皮肤 | 描述 | Agent 品牌名 | 视觉特征 |
|------|------|--------------|----------|
| `default` | 经典 Hermes — 金色与可爱风 | `Hermes Agent` | 温暖金色边框、玉米须色文字、加载动画中的可爱表情。熟悉的双蛇杖横幅。干净且友好。 |
| `ares` | 战神主题 — 深红与青铜色 | `Ares Agent` | 深红边框配青铜色点缀。激进的加载动画动词（“锻造”、“行军”、“淬炼钢铁”）。自定义剑盾 ASCII 艺术横幅。 |
| `mono` | 单色 — 干净灰度 | `Hermes Agent` | 全灰色 — 无彩色。边框为 `#555555`，文字为 `#c9d1d9`。适合极简终端环境或屏幕录制。 |
| `slate` | 冷静蓝 — 面向开发者 | `Hermes Agent` | 皇家蓝边框（`#4169e1`），柔和蓝色文字。冷静且专业。无自定义加载动画 — 使用默认表情。 |
| `daylight` | 浅色主题，适合亮色终端，深色文字和冷蓝色点缀 | `Hermes Agent` | 专为白色或亮色终端设计。深石板色文字配蓝色边框，浅色状态面板，补全菜单在浅色终端配置下保持可读。 |
| `warm-lightmode` | 温暖棕色/金色文字，适合浅色终端背景 | `Hermes Agent` | 温暖羊皮纸色调，适合浅色终端。深棕色文字配马鞍棕色点缀，奶油色状态面板。比冷淡的 daylight 主题更接地气的选择。 |
| `poseidon` | 海神主题 — 深蓝与海沫绿 | `Poseidon Agent` | 深蓝到海沫绿渐变。海洋主题加载动画（“绘制洋流”、“探测深度”）。三叉戟 ASCII 艺术横幅。 |
| `sisyphus` | 西西弗斯主题 — 简朴灰度，强调坚持 | `Sisyphus Agent` | 浅灰色配强烈对比。巨石主题加载动画（“向上推”、“重置巨石”、“承受循环”）。巨石与山坡 ASCII 艺术横幅。 |
| `charizard` | 火山主题 — 焦橙色与余烬色 | `Charizard Agent` | 温暖焦橙到余烬色渐变。火焰主题加载动画（“俯冲进入气流”、“测量燃烧”）。龙形剪影 ASCII 艺术横幅。 |

<a id="complete-list-of-configurable-keys"></a>
## 可配置键的完整列表

<a id="colors-colors"></a>
### 颜色（`colors:`）

控制 CLI 中所有颜色值。值为十六进制颜色字符串。

| 键名 | 说明 | 默认值（`default` 皮肤） |
|------|------|--------------------------|
| `banner_border` | 启动横幅面板边框 | `#CD7F32`（青铜色） |
| `banner_title` | 横幅标题文字颜色 | `#FFD700`（金色） |
| `banner_accent` | 横幅中的章节标题（可用工具等） | `#FFBF00`（琥珀色） |
| `banner_dim` | 横幅中柔和的文字（分隔符、次要标签） | `#B8860B`（深金菊色） |
| `banner_text` | 横幅正文文字（工具名、技能名） | `#FFF8DC`（玉米须色） |
| `ui_accent` | 通用界面强调色（高亮、活动元素） | `#FFBF00` |
| `ui_label` | 界面标签和标记 | `#4dd0e1`（青色） |
| `ui_ok` | 成功指示符（勾号、完成） | `#4caf50`（绿色） |
| `ui_error` | 错误指示符（失败、阻塞） | `#ef5350`（红色） |
| `ui_warn` | 警告指示符（注意、确认提示） | `#ffa726`（橙色） |
| `prompt` | 交互提示文字颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的水平分割线 | `#CD7F32` |
| `response_border` | Agent 回复框的边框（ANSI 转义） | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话 ID 的暗淡边框颜色 | `#8B8682` |
| `status_bar_bg` | TUI 状态/使用量栏的背景色 | `#1a1a2e` |
| `voice_status_bg` | 语音模式状态徽章背景色 | `#1a1a2e` |
| `selection_bg` | TUI 鼠标选择高亮背景色。未设置时回退为 `completion_menu_current_bg` | `#333355` |
| `completion_menu_bg` | 补全菜单列表背景色 | `#1a1a2e` |
| `completion_menu_current_bg` | 当前补全行背景色 | `#333355` |
| `completion_menu_meta_bg` | 补全菜单元数据列背景色 | `#1a1a2e` |
| `completion_menu_meta_current_bg` | 当前补全元数据列背景色 | `#333355` |
<a id="spinner-spinner"></a>
### 旋转加载动画（`spinner:`）

控制等待 API 响应时显示的旋转加载动画。

| 键 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的面孔 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理时循环显示的面孔 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 旋转动画消息中显示的动词 | `["锻造", "策划", "敲定计划"]` |
| `wings` | [左, 右] 对列表 | 旋转动画周围的装饰括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当 spinner 值为空时（如在 `default` 和 `mono` 皮肤中），会使用 `display.py` 中硬编码的默认值。

<a id="branding-branding"></a>
### 品牌标识（`branding:`）

CLI 界面中使用的文本字符串。

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 横幅标题和状态显示中显示的名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `欢迎使用 Hermes Agent！输入消息或 /help 查看命令。` |
| `goodbye` | 退出时显示的消息 | `再见！⚕` |
| `response_label` | 响应框标题上的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示前的符号（仅符号本身，渲染器会添加尾随空格） | `❯` |
| `help_header` | `/help` 命令输出的标题文本 | `(^_^)? 可用命令` |

<a id="other-top-level-keys"></a>
### 其他顶级键

| 键 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前缀的字符 | `┊` |
| `tool_emojis` | 字典 | 每个工具在旋转动画和进度中使用的表情符号覆盖（`{工具名称: 表情符号}`） | `{}` |
| `banner_logo` | 字符串 | 富标记 ASCII 艺术标志（替换默认的 HERMES_AGENT 横幅） | `""` |
| `banner_hero` | 字符串 | 富标记英雄艺术图（替换默认的蛇杖艺术图） | `""` |

<a id="custom-skins"></a>
## 自定义皮肤

在 `~/.hermes/skins/` 下创建 YAML 文件。用户皮肤中缺失的值会从内置的 `default` 皮肤继承，因此你只需指定要修改的键即可。

<a id="full-custom-skin-yaml-template"></a>
### 完整的自定义皮肤 YAML 模板

```yaml
# ~/.hermes/skins/mytheme.yaml
# 完整皮肤模板——显示所有键。删除不需要的键；
# 缺失值会自动从 'default' 皮肤继承。

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
  selection_bg: "#333355"
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
    - "处理中"
    - "分析中"
    - "计算中"
    - "评估中"
  wings:
    - ["⟪⚡", "⚡⟫"]
    - ["⟪●", "●⟫"]

branding:
  agent_name: "我的 Agent"
  welcome: "欢迎使用我的 Agent！输入消息或 /help 查看命令。"
  goodbye: "下次见！⚡"
  response_label: " ⚡ 我的 Agent "
  prompt_symbol: "⚡"
  help_header: "(⚡) 可用命令"

tool_prefix: "┊"

# 每个工具的表情符号覆盖（可选）
tool_emojis:
  terminal: "⚔"
  web_search: "🔮"
  read_file: "📄"

# 自定义 ASCII 艺术横幅（可选，支持 Rich 标记）
# banner_logo: |
#   [bold #FFD700] 我的 AGENT [/]
# banner_hero: |
#   [#FFD700]  在此处放置自定义艺术  [/]
```
<a id="minimal-custom-skin-example"></a>
### 最小自定义皮肤示例

由于所有皮肤都继承自 `default`，一个最小皮肤只需要修改不同的部分：

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

<a id="hermes-mod-visual-skin-editor"></a>
## Hermes Mod — 可视化皮肤编辑器

[Hermes Mod](https://github.com/cocktailpeanut/hermes-mod) 是一个社区构建的 Web UI，用于可视化创建和管理皮肤。无需手动编写 YAML，你只需使用一个带实时预览的点击式编辑器。

![Hermes Mod 皮肤编辑器](https://raw.githubusercontent.com/cocktailpeanut/hermes-mod/master/nous.png)

**功能：**

- 列出所有内置和自定义皮肤
- 将任何皮肤在可视化编辑器中打开，包含所有 Hermes 皮肤字段（颜色、spinner、品牌信息、工具前缀、工具表情符号）
- 根据文本提示生成 `banner_logo` 文字艺术
- 将上传的图片（PNG、JPG、GIF、WEBP）转换为 `banner_hero` ASCII 艺术，支持多种渲染样式（盲文、ASCII 渐变、块、点）
- 直接保存到 `~/.hermes/skins/`
- 通过更新 `~/.hermes/config.yaml` 激活皮肤
- 显示生成的 YAML 和实时预览

<a id="install"></a>
### 安装

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

<a id="usage"></a>
### 使用方法

1. 启动应用（通过 Pinokio 或终端）。
2. 打开 **Skin Studio**。
3. 选择一个内置或自定义皮肤进行编辑。
4. 从文本生成 Logo 和/或上传图片作为英雄艺术。选择渲染样式和宽度。
5. 编辑颜色、spinner、品牌信息和其他字段。
6. 点击 **保存** 将皮肤 YAML 写入 `~/.hermes/skins/`。
7. 点击 **激活** 将其设置为当前皮肤（更新 `config.yaml` 中的 `display.skin`）。

Hermes Mod 会尊重 `HERMES_HOME` 环境变量，因此它也适用于[配置文件](/user-guide/profiles)。

<a id="operational-notes"></a>
## 操作说明

- 内置皮肤从 `hermes_cli/skin_engine.py` 加载。
- 未知皮肤会自动回退到 `default`。
- `/skin` 会立即更新当前会话的活动 CLI 主题。
- `~/.hermes/skins/` 中的用户皮肤会优先于同名的内置皮肤。
- 通过 `/skin` 进行的皮肤更改仅限当前会话。要使皮肤成为永久默认设置，请在 `config.yaml` 中设置。
- `banner_logo` 和 `banner_hero` 字段支持 Rich 控制台标记（例如 `[bold #FF0000]text[/]`）用于彩色 ASCII 艺术。
