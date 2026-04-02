---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和用户自定义的皮肤来定制 Hermes CLI 的外观"
---

# 皮肤与主题

皮肤控制着 Hermes CLI 的**视觉呈现**：横幅颜色、旋转器表情和动词、响应框标签、品牌文本以及工具活动前缀。

对话风格和视觉风格是两个独立的概念：

- **个性** 改变 Agent 的语气和措辞。
- **皮肤** 改变 CLI 的外观。

## 更换皮肤

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换到内置皮肤
/skin mytheme        # 切换到自定义皮肤（来自 ~/.hermes/skins/mytheme.yaml）
```

或者在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置皮肤

| 皮肤 | 描述 | Agent 品牌 | 视觉特征 |
|------|-------------|----------------|------------------|
| `default` | 经典 Hermes — 金色与可爱风 | `Hermes Agent` | 温暖的金色边框，米色文本，旋转器中的可爱表情。熟悉的双蛇杖横幅。干净且吸引人。 |
| `ares` | 战神主题 — 深红与青铜色 | `Ares Agent` | 深红色边框配青铜色点缀。激进的旋转器动词（"锻造"、"行军"、"淬炼钢铁"）。自定义剑与盾 ASCII 艺术横幅。 |
| `mono` | 单色 — 干净的灰度 | `Hermes Agent` | 全灰度 — 无颜色。边框为 `#555555`，文本为 `#c9d1d9`。适合极简终端设置或屏幕录制。 |
| `slate` | 冷蓝色 — 面向开发者 | `Hermes Agent` | 宝蓝色边框 (`#4169e1`)，柔和的蓝色文本。冷静且专业。无自定义旋转器 — 使用默认表情。 |
| `poseidon` | 海神主题 — 深蓝与海沫色 | `Poseidon Agent` | 深蓝到海沫色的渐变。海洋主题的旋转器（"绘制洋流"、"探测深度"）。三叉戟 ASCII 艺术横幅。 |
| `sisyphus` | 西西弗斯主题 — 朴素灰度与持久感 | `Sisyphus Agent` | 浅灰色，对比鲜明。巨石主题的旋转器（"推石上山"、"重置巨石"、"承受循环"）。巨石与山丘 ASCII 艺术横幅。 |
| `charizard` | 火山主题 — 焦橙色与余烬色 | `Charizard Agent` | 温暖的焦橙色到余烬色的渐变。火焰主题的旋转器（"顺风滑翔"、"测量燃烧"）。龙形剪影 ASCII 艺术横幅。 |

## 可配置键的完整列表

### 颜色 (`colors:`)

控制 CLI 中的所有颜色值。值为十六进制颜色字符串。

| 键 | 描述 | 默认值 (`default` 皮肤) |
|-----|-------------|--------------------------|
| `banner_border` | 启动横幅周围的面板边框 | `#CD7F32` (青铜色) |
| `banner_title` | 横幅中的标题文本颜色 | `#FFD700` (金色) |
| `banner_accent` | 横幅中的章节标题颜色（可用工具等） | `#FFBF00` (琥珀色) |
| `banner_dim` | 横幅中的次要文本颜色（分隔符、次要标签） | `#B8860B` (暗金黄色) |
| `banner_text` | 横幅中的正文文本颜色（工具名、技能名） | `#FFF8DC` (米色) |
| `ui_accent` | 通用 UI 强调色（高亮、活动元素） | `#FFBF00` |
| `ui_label` | UI 标签和标记 | `#4dd0e1` (青色) |
| `ui_ok` | 成功指示器（对勾、完成） | `#4caf50` (绿色) |
| `ui_error` | 错误指示器（失败、阻止） | `#ef5350` (红色) |
| `ui_warn` | 警告指示器（注意、确认提示） | `#ffa726` (橙色) |
| `prompt` | 交互式提示文本颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的水平分隔线颜色 | `#CD7F32` |
| `response_border` | Agent 响应框周围的边框颜色 (ANSI 转义) | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话 ID 暗淡边框颜色 | `#8B8682` |

### 旋转器 (`spinner:`)

控制等待 API 响应时显示的动画旋转器。

| 键 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的表情 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理期间循环显示的表情 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 旋转器消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | [左, 右] 对列表 | 旋转器周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当旋转器值为空时（如 `default` 和 `mono`），将使用 `display.py` 中的硬编码默认值。

### 品牌 (`branding:`)

整个 CLI 界面中使用的文本字符串。

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 横幅标题和状态显示中显示的名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框标题上的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示前的符号 | `❯ ` |
| `help_header` | `/help` 命令输出的标题文本 | `(^_^)? Available Commands` |

### 其他顶级键

| 键 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前的前缀字符 | `┊` |
| `tool_emojis` | 字典 | 针对特定工具的旋转器和进度表情符号覆盖 (`{工具名: 表情符号}`) | `{}` |
| `banner_logo` | 字符串 | 富标记 ASCII 艺术徽标（替换默认的 HERMES_AGENT 横幅） | `""` |
| `banner_hero` | 字符串 | 富标记英雄艺术图（替换默认的双蛇杖艺术图） | `""` |

## 自定义皮肤

在 `~/.hermes/skins/` 下创建 YAML 文件。用户皮肤会从内置的 `default` 皮肤继承缺失的值，因此你只需要指定想要更改的键。

### 完整的自定义皮肤 YAML 模板

```yaml
# ~/.hermes/skins/mytheme.yaml
# 完整的皮肤模板 — 显示所有键。删除任何不需要的键；
# 缺失的值会自动从 'default' 皮肤继承。

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

# 针对特定工具的表情符号覆盖（可选）
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

由于所有内容都从 `default` 继承，一个最小化的皮肤只需要更改不同的部分：

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

## 操作说明

- 内置皮肤从 `hermes_cli/skin_engine.py` 加载。
- 未知皮肤会自动回退到 `default`。
- `/skin` 会立即更新当前会话的活动 CLI 主题。
- `~/.hermes/skins/` 中的用户皮肤优先于同名的内置皮肤。
- 通过 `/skin` 进行的皮肤更改仅对当前会话有效。要将某个皮肤设为永久默认值，请在 `config.yaml` 中设置。
- `banner_logo` 和 `banner_hero` 字段支持 Rich 控制台标记（例如 `[bold #FF0000]text[/]`）以创建彩色 ASCII 艺术。
