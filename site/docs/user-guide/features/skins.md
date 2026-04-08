---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和用户定义的皮肤自定义 Hermes CLI"
---

# 皮肤与主题

皮肤控制 Hermes CLI 的**视觉呈现**：横幅颜色、加载动画（spinner）的面部和动词、响应框标签、品牌文本以及工具活动前缀。

对话风格和视觉风格是两个独立的概念：

- **性格 (Personality)** 改变 Agent 的语气和措辞。
- **皮肤 (Skin)** 改变 CLI 的外观。

## 切换皮肤

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换到内置皮肤
/skin mytheme        # 切换到位于 ~/.hermes/skins/mytheme.yaml 的自定义皮肤
```

或者在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置皮肤

| 皮肤 | 描述 | Agent 品牌 | 视觉特征 |
|------|-------------|----------------|------------------|
| `default` | 经典 Hermes — 金色且可爱 | `Hermes Agent` | 温暖的金色边框，玉米丝色文本，加载动画中使用可爱表情。熟悉的商神杖横幅。整洁且亲切。 |
| `ares` | 战神主题 — 深红与青铜 | `Ares Agent` | 深红边框搭配青铜点缀。激进的加载动词（"forging", "marching", "tempering steel"）。自定义剑与盾 ASCII 艺术横幅。 |
| `mono` | 单色 — 纯净灰阶 | `Hermes Agent` | 全灰色 — 无彩色。边框为 `#555555`，文本为 `#c9d1d9`。非常适合极简终端设置或屏幕录制。 |
| `slate` | 冷蓝 — 开发者导向 | `Hermes Agent` | 皇室蓝边框 (`#4169e1`)，柔和的蓝色文本。冷静且专业。无自定义加载动画 — 使用默认面部。 |
| `poseidon` | 海神主题 — 深蓝与海泡绿 | `Poseidon Agent` | 深蓝到海泡绿的渐变。海洋主题加载动画（"charting currents", "sounding the depth"）。三叉戟 ASCII 艺术横幅。 |
| `sisyphus` | 西西弗斯主题 — 朴素灰阶与坚持 | `Sisyphus Agent` | 浅灰色，对比鲜明。巨石主题加载动画（"pushing uphill", "resetting the boulder", "enduring the loop"）。巨石与山丘 ASCII 艺术横幅。 |
| `charizard` | 火山主题 — 焦橙与余烬 | `Charizard Agent` | 温暖的焦橙到余烬渐变。火焰主题加载动画（"banking into the draft", "measuring burn"）。龙影 ASCII 艺术横幅。 |

## 可配置键完整列表

### 颜色 (`colors:`)

控制整个 CLI 的所有颜色值。值为十六进制颜色字符串。

| 键名 | 描述 | 默认值 (`default` 皮肤) |
|-----|-------------|--------------------------|
| `banner_border` | 启动横幅周围的面板边框 | `#CD7F32` (青铜色) |
| `banner_title` | 横幅中的标题文本颜色 | `#FFD700` (金色) |
| `banner_accent` | 横幅中的部分标题（可用工具等） | `#FFBF00` (琥珀色) |
| `banner_dim` | 横幅中的暗淡文本（分隔符、次要标签） | `#B8860B` (暗金菊色) |
| `banner_text` | 横幅中的正文文本（工具名、技能名） | `#FFF8DC` (玉米丝色) |
| `ui_accent` | 通用 UI 强调色（高亮、活动元素） | `#FFBF00` |
| `ui_label` | UI 标签和标记 | `#4dd0e1` (青色) |
| `ui_ok` | 成功指示器（打勾、完成） | `#4caf50` (绿色) |
| `ui_error` | 错误指示器（失败、阻塞） | `#ef5350` (红色) |
| `ui_warn` | 警告指示器（注意、审批提示） | `#ffa726` (橙色) |
| `prompt` | 交互式提示符文本颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的水平分割线 | `#CD7F32` |
| `response_border` | Agent 响应框周围的边框 (ANSI 转义) | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话 ID 暗淡边框颜色 | `#8B8682` |

### 加载动画 (`spinner:`)

控制等待 API 响应时显示的动画加载器。

| 键名 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的面部 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理期间循环显示的面部 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 加载动画消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | [左, 右] 配对列表 | 加载动画周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当加载动画值为空时（如在 `default` 和 `mono` 中），将使用 `display.py` 中硬编码的默认值。

### 品牌化 (`branding:`)

在整个 CLI 界面中使用的文本字符串。

| 键名 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 横幅标题和状态显示中显示的名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框顶部的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示符前的符号 | `❯ ` |
| `help_header` | `/help` 命令输出的标题文本 | `(^_^)? Available Commands` |

### 其他顶级键名

| 键名 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前缀字符 | `┊` |
| `tool_emojis` | 字典 | 针对每个工具的加载动画和进度 Emoji 覆盖 (`{tool_name: emoji}`) | `{}` |
| `banner_logo` | 字符串 | Rich 标记格式的 ASCII 艺术 Logo（替换默认的 HERMES_AGENT 横幅） | `""` |
| `banner_hero` | 字符串 | Rich 标记格式的主视觉艺术（替换默认的商神杖艺术） | `""` |

## 自定义皮肤

在 `~/.hermes/skins/` 下创建 YAML 文件。用户皮肤会从内置的 `default` 皮肤继承缺失的值，因此你只需要指定想要更改的键。

### 完整自定义皮肤 YAML 模板

```yaml
# ~/.hermes/skins/mytheme.yaml
# 完整的皮肤模板 — 显示所有键。删除任何你不需要的；
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

# 针对每个工具的 Emoji 覆盖（可选）
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

### 极简自定义皮肤示例

由于所有内容都继承自 `default`，极简皮肤只需更改不同的部分：

```yaml
name: cyberpunk
description: 霓虹终端主题

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
- `~/.hermes/skins/` 中的用户皮肤优先级高于同名的内置皮肤。
- 通过 `/skin` 进行的皮肤更改仅限当前会话。要将皮肤设为永久默认，请在 `config.yaml` 中进行设置。
- `banner_logo` 和 `banner_hero` 字段支持 Rich 控制台标记（例如 `[bold #FF0000]text[/]`）以实现彩色 ASCII 艺术。
