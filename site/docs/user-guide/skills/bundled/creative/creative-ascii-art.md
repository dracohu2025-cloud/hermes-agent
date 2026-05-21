---
title: "Ascii Art — ASCII 艺术：pyfiglet、cowsay、boxes、图片转 ASCII"
sidebar_label: "Ascii Art"
description: "ASCII 艺术：pyfiglet、cowsay、boxes、图片转 ASCII"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="ascii-art"></a>
# Ascii Art

ASCII 艺术：pyfiglet、cowsay、boxes、图片转 ASCII。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/ascii-art` |
| 版本 | `4.0.0` |
| 作者 | 0xbyt4, Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `ASCII`, `Art`, `Banners`, `Creative`, `Unicode`, `Text-Art`, `pyfiglet`, `figlet`, `cowsay`, `boxes` |
| 相关技能 | [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="ascii-art-skill"></a>
# ASCII 艺术技能

多种工具满足不同的 ASCII 艺术需求。所有工具均为本地 CLI 程序或免费 REST API — 无需 API 密钥。

<a id="tool-1-text-banners-pyfiglet-local"></a>
## 工具 1：文字横幅（pyfiglet — 本地）

将文字渲染为大型 ASCII 艺术横幅。内置 571 种字体。

<a id="setup"></a>
### 安装

```bash
pip install pyfiglet --break-system-packages -q
```

<a id="usage"></a>
### 用法

```bash
python3 -m pyfiglet "你的文字" -f slant
python3 -m pyfiglet "文字" -f doom -w 80    # 设置宽度
python3 -m pyfiglet --list_fonts             # 列出所有 571 种字体
```

<a id="recommended-fonts"></a>
### 推荐字体

| 风格 | 字体 | 最佳用途 |
|-------|------|----------|
| 简洁现代 | `slant` | 项目名称、标题 |
| 粗体块状 | `doom` | 标题、标志 |
| 大而清晰 | `big` | 横幅 |
| 经典横幅 | `banner3` | 宽屏显示 |
| 紧凑 | `small` | 副标题 |
| 赛博朋克 | `cyberlarge` | 科技主题 |
| 3D 效果 | `3-d` | 启动画面 |
| 哥特风格 | `gothic` | 戏剧性文字 |

<a id="tips"></a>
### 提示

- 预览 2-3 种字体，让用户选择最喜欢的
- 短文本（1-8 个字符）使用 `doom` 或 `block` 等细节丰富的字体效果最佳
- 长文本使用 `small` 或 `mini` 等紧凑字体效果更好

<a id="tool-2-text-banners-asciified-api-remote-no-install"></a>
## 工具 2：文字横幅（asciified API — 远程，无需安装）

免费 REST API，可将文字转换为 ASCII 艺术。支持 250 多种 FIGlet 字体。直接返回纯文本 — 无需解析。当 pyfiglet 未安装或作为快速替代方案时使用。

<a id="usage-via-terminal-curl"></a>
### 用法（通过终端 curl）

```bash
# 基本文字横幅（默认字体）
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello+World"

# 使用特定字体
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Doom"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Star+Wars"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=3-D"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Banner3"

# 列出所有可用字体（返回 JSON 数组）
curl -s "https://asciified.thelicato.io/api/v2/fonts"
```

### 提示

- 在 text 参数中，将空格 URL 编码为 `+`
- 响应是纯文本 ASCII 艺术 — 无 JSON 包装，可直接显示
- 字体名称区分大小写；请使用 fonts 端点获取准确名称
- 任何带有 curl 的终端均可使用 — 无需 Python 或 pip
<a id="tool-3-cowsay-message-art"></a>
## Tool 3: Cowsay（文字气泡艺术）

将文字放入ASCII字符的对话气泡中的经典工具。

<a id="setup"></a>
### 安装

```bash
sudo apt install cowsay -y    # Debian/Ubuntu
# brew install cowsay         # macOS
```

<a id="usage"></a>
### 用法

```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"       # Tux the penguin
cowsay -f dragon "Rawr!"          # Dragon
cowsay -f stegosaurus "Roar!"     # Stegosaurus
cowthink "Hmm..."                  # 思考气泡
cowsay -l                          # 列出所有角色
```

<a id="available-characters-50"></a>
### 可用角色（50+）

`beavis.zen`, `bong`, `bunny`, `cheese`, `daemon`, `default`, `dragon`,
`dragon-and-cow`, `elephant`, `eyes`, `flaming-skull`, `ghostbusters`,
`hellokitty`, `kiss`, `kitty`, `koala`, `luke-koala`, `mech-and-cow`,
`meow`, `moofasa`, `moose`, `ren`, `sheep`, `skeleton`, `small`,
`stegosaurus`, `stimpy`, `supermilker`, `surgery`, `three-eyes`,
`turkey`, `turtle`, `tux`, `udder`, `vader`, `vader-koala`, `www`

<a id="eye-tongue-modifiers"></a>
### 眼睛/舌头修饰符

```bash
cowsay -b "Borg"       # =_= 眼睛
cowsay -d "Dead"       # x_x 眼睛
cowsay -g "Greedy"     # $_$ 眼睛
cowsay -p "Paranoid"   # @_@ 眼睛
cowsay -s "Stoned"     # *_* 眼睛
cowsay -w "Wired"      # O_O 眼睛
cowsay -e "OO" "Msg"   # 自定义眼睛
cowsay -T "U " "Msg"   # 自定义舌头
```

<a id="tool-4-boxes-decorative-borders"></a>
## Tool 4: Boxes（装饰边框）

为任意文本绘制装饰性ASCII艺术边框/框架。内置70多种设计。

### 安装

```bash
sudo apt install boxes -y    # Debian/Ubuntu
# brew install boxes         # macOS
```

### 用法

```bash
echo "Hello World" | boxes                    # 默认框
echo "Hello World" | boxes -d stone           # 石头边框
echo "Hello World" | boxes -d parchment       # 羊皮卷轴
echo "Hello World" | boxes -d cat             # 猫边框
echo "Hello World" | boxes -d dog             # 狗边框
echo "Hello World" | boxes -d unicornsay      # 独角兽
echo "Hello World" | boxes -d diamonds        # 钻石图案
echo "Hello World" | boxes -d c-cmt           # C风格注释
echo "Hello World" | boxes -d html-cmt        # HTML注释
echo "Hello World" | boxes -a c               # 居中文本
boxes -l                                       # 列出所有70+种设计
```

<a id="combine-with-pyfiglet-or-asciified"></a>
### 与 pyfiglet 或 asciified 结合使用

```bash
python3 -m pyfiglet "HERMES" -f slant | boxes -d stone
# 或者未安装 pyfiglet 时：
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=HERMES&font=Slant" | boxes -d stone
```

<a id="tool-5-toilet-colored-text-art"></a>
## Tool 5: TOIlet（彩色文字艺术）

类似 pyfiglet，但带有 ANSI 颜色效果和视觉滤镜。非常适合在终端中制造视觉亮点。

### 安装

```bash
sudo apt install toilet toilet-fonts -y    # Debian/Ubuntu
# brew install toilet                      # macOS
```

### 用法

```bash
toilet "Hello World"                    # 基本文字艺术
toilet -f bigmono12 "Hello"            # 指定字体
toilet --gay "Rainbow!"                 # 彩虹着色
toilet --metal "Metal!"                 # 金属效果
toilet -F border "Bordered"             # 添加边框
toilet -F border --gay "Fancy!"         # 组合效果
toilet -f pagga "Block"                 # 块状字体（toilet 独有）
toilet -F list                          # 列出可用滤镜
```
<a id="filters"></a>
### 过滤器

`crop`（裁剪）、`gay`（彩虹效果）、`metal`（金属效果）、`flip`（水平翻转）、`flop`（垂直翻转）、`180`（旋转 180°）、`left`（左旋 90°）、`right`（右旋 90°）、`border`（添加边框）

**注意**：toilet 命令输出的 ANSI 转义码带有颜色——在终端中有效，但在某些场景下（如纯文本文件、某些聊天平台）可能无法正常显示。

<a id="tool-6-image-to-ascii-art"></a>
## 工具 6：图片转 ASCII 艺术

将图片（PNG、JPEG、GIF、WEBP）转换为 ASCII 艺术。

<a id="option-a-ascii-image-converter-recommended-modern"></a>
### 选项 A：ascii-image-converter（推荐，现代化工具）

```bash
# 安装
sudo snap install ascii-image-converter
# 或：go install github.com/TheZoraiz/ascii-image-converter@latest
```

```bash
ascii-image-converter image.png                  # 基础用法
ascii-image-converter image.png -C               # 彩色输出
ascii-image-converter image.png -d 60,30         # 设置尺寸
ascii-image-converter image.png -b               # 使用盲文字符
ascii-image-converter image.png -n               # 反相/负片效果
ascii-image-converter https://url/image.jpg      # 直接使用 URL
ascii-image-converter image.png --save-txt out   # 保存为文本文件
```

<a id="option-b-jp2a-lightweight-jpeg-only"></a>
### 选项 B：jp2a（轻量级，仅支持 JPEG）

```bash
sudo apt install jp2a -y
jp2a --width=80 image.jpg
jp2a --colors image.jpg              # 彩色输出
```

<a id="tool-7-search-pre-made-ascii-art"></a>
## 工具 7：搜索现成的 ASCII 艺术

从网络中搜索精选的 ASCII 艺术。使用 `terminal` 配合 `curl`。

<a id="source-a-ascii-co-uk-recommended-for-pre-made-art"></a>
### 来源 A：ascii.co.uk（推荐用于获取现成作品）

庞大的经典 ASCII 艺术收藏库，按主题分类。艺术作品位于 HTML 的 `&lt;pre&gt;` 标签内。先用 curl 获取页面，再用一小段 Python 代码提取艺术作品。

**URL 模式：** `https://ascii.co.uk/art/{主题}`

**步骤 1 — 获取页面：**

```bash
curl -s 'https://ascii.co.uk/art/cat' -o /tmp/ascii_art.html
```

**步骤 2 — 从 pre 标签中提取艺术作品：**

```python
import re, html
with open('/tmp/ascii_art.html') as f:
    text = f.read()
arts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.DOTALL)
for art in arts:
    clean = re.sub(r'<[^>]+>', '', art)
    clean = html.unescape(clean).strip()
    if len(clean) > 30:
        print(clean)
        print('\n---\n')
```

**可用主题**（用作 URL 路径）：
- 动物：`cat`（猫）、`dog`（狗）、`horse`（马）、`bird`（鸟）、`fish`（鱼）、`dragon`（龙）、`snake`（蛇）、`rabbit`（兔子）、`elephant`（大象）、`dolphin`（海豚）、`butterfly`（蝴蝶）、`owl`（猫头鹰）、`wolf`（狼）、`bear`（熊）、`penguin`（企鹅）、`turtle`（乌龟）
- 物品：`car`（汽车）、`ship`（船）、`airplane`（飞机）、`rocket`（火箭）、`guitar`（吉他）、`computer`（电脑）、`coffee`（咖啡）、`beer`（啤酒）、`cake`（蛋糕）、`house`（房子）、`castle`（城堡）、`sword`（剑）、`crown`（王冠）、`key`（钥匙）
- 自然：`tree`（树）、`flower`（花）、`sun`（太阳）、`moon`（月亮）、`star`（星星）、`mountain`（山）、`ocean`（海洋）、`rainbow`（彩虹）
- 角色：`skull`（骷髅）、`robot`（机器人）、`angel`（天使）、`wizard`（巫师）、`pirate`（海盗）、`ninja`（忍者）、`alien`（外星人）
- 节日：`christmas`（圣诞节）、`halloween`（万圣节）、`valentine`（情人节）

**提示：**
- 保留艺术家的签名/缩写——这是重要的礼节
- 每页可能有多个艺术作品——为用户挑选最佳的一个
- 通过 curl 即可可靠获取，无需 JavaScript

<a id="source-b-github-octocat-api-fun-easter-egg"></a>
### 来源 B：GitHub Octocat API（有趣的彩蛋）

返回一个随机的 GitHub Octocat 形象并附带一句智慧名言。无需认证。

```bash
curl -s https://api.github.com/octocat
```

<a id="tool-8-fun-ascii-utilities-via-curl"></a>
## 工具 8：有趣的 ASCII 工具集（通过 curl 使用）

这些免费服务直接返回 ASCII 艺术——非常适合用来增添趣味。
<a id="qr-codes-as-ascii-art"></a>
### 二维码 ASCII 艺术

```bash
curl -s "qrenco.de/Hello+World"
curl -s "qrenco.de/https://example.com"
```

<a id="weather-as-ascii-art"></a>
### 天气 ASCII 艺术

```bash
curl -s "wttr.in/London"          # 带 ASCII 图形的完整天气预报
curl -s "wttr.in/Moon"            # ASCII 艺术月相
curl -s "v2.wttr.in/London"       # 详细版本
```

<a id="tool-9-llm-generated-custom-art-fallback"></a>
## 工具 9：LLM 生成的自定义艺术（备用方案）

当上述工具无法满足需求时，直接使用以下 Unicode 字符生成 ASCII 艺术：

<a id="character-palette"></a>
### 字符调色板

**框线字符：** `╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬ ┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯`

**块元素：** `░ ▒ ▓ █ ▄ ▀ ▌ ▐ ▖ ▗ ▘ ▝ ▚ ▞`

**几何与符号：** `◆ ◇ ◈ ● ○ ◉ ■ □ ▲ △ ▼ ▽ ★ ☆ ✦ ✧ ◀ ▶ ◁ ▷ ⬡ ⬢ ⌂`

<a id="rules"></a>
### 规则

- 最大宽度：每行 60 个字符（终端安全）
- 最大高度：横幅 15 行，场景 25 行
- 仅限等宽字体：输出必须在固定宽度字体中正确渲染

<a id="decision-flow"></a>
## 决策流程

1. **文本作为横幅** → 如果已安装 pyfiglet，则使用；否则通过 curl 调用 asciified API
2. **用有趣的字符艺术包装消息** → cowsay
3. **添加装饰性边框/框架** → boxes（可与 pyfiglet/asciified 组合使用）
4. **特定事物的艺术**（猫、火箭、龙）→ 通过 curl 调用 ascii.co.uk 并解析
5. **将图像转换为 ASCII** → ascii-image-converter 或 jp2a
6. **二维码** → 通过 curl 调用 qrenco.de
7. **天气/月相艺术** → 通过 curl 调用 wttr.in
8. **自定义/创意内容** → 使用 Unicode 调色板进行 LLM 生成
9. **任何未安装的工具** → 安装它，或回退到下一个选项
