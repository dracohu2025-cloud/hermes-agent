---
title: "超帧 (Hyperframes)"
sidebar_label: "超帧"
description: "使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交媒体叠加层、带字幕的说话人头视频、音频响应式视觉效果以及着色器转场。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能 SKILL.md 自动生成。请编辑源 SKILL.md 而非此页面。 */}

<a id="hyperframes"></a>
# 超帧 (Hyperframes)

使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交媒体叠加层、带字幕的说话人头视频、音频响应式视觉效果以及着色器转场。HTML 是视频的真理来源。当用户需要从 HTML 合成渲染 MP4/WebM、需要为媒体制作文本/标志/图表动画、需要与音频同步的字幕、需要 TTS 旁白、或者需要将网站转换为视频时，使用此技能。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/hyperframes` 安装 |
| 路径 | `optional-skills/creative/hyperframes` |
| 版本 | `1.0.0` |
| 作者 | heygen-com |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `video`, `animation`, `html`, `gsap`, `motion-graphics` |
| 相关技能 | [`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video), [`meme-generation`](/user-guide/skills/optional/creative/creative-meme-generation) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这就是技能激活时 Agent 看到的指令。
:::

# HyperFrames

HTML 是视频的真理来源。合成是一个带有 `data-*` 属性（用于时间控制）、GSAP 时间线（用于动画）和 CSS（用于外观）的 HTML 文件。HyperFrames 引擎逐帧捕获页面，并使用 FFmpeg 编码为 MP4/WebM。

**与 `manim-video` 互补：** 使用 `manim-video` 制作数学/几何说明（方程、3B1B 风格）。使用 `hyperframes` 制作动态图形、带字幕的说话人头、产品导览、社交媒体叠加层、着色器转场以及任何由真实视频/音频媒体驱动的场景。

<a id="when-to-use"></a>
## 使用时机

- 用户要求根据文本、脚本或网站渲染视频
- 动画标题卡、下三分之一或排版简介
- 带字幕的旁白视频（TTS + 字幕与波形同步）
- 音频响应式视觉效果（节拍同步、频谱条、脉动发光）
- 场景到场景的转场（淡入淡出、擦除、着色器扭曲、闪白过渡）
- 社交媒体叠加层（Instagram/TikTok/YouTube 风格）
- 网站到视频的流程（捕获 URL，生成宣传片）
- 任何必须确定性渲染为视频文件的 HTML/CSS/JS 动画

**不要** 将此技能用于：
- 纯数学/方程动画（→ `manim-video`）
- 图像生成或梗图（→ `meme-generation`、图像模型）
- 实时视频会议或流媒体

<a id="quick-reference"></a>
## 快速参考

```bash
npx hyperframes init my-video               # 创建项目脚手架
cd my-video
npx hyperframes lint                        # 在预览/渲染前进行验证
npx hyperframes preview                     # 实时加载浏览器预览（端口 3002）
npx hyperframes render --output final.mp4   # 渲染为 MP4
npx hyperframes doctor                      # 诊断环境问题
```
渲染标志：`--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker`（可重现）· `--strict`。

完整 CLI 参考：[references/cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md)。

<a id="setup-one-time"></a>
## 一次性设置

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

该脚本会：
1. 检查是否已安装 Node.js >= 22 和 FFmpeg，若未安装则输出修复说明。
2. 全局安装 `hyperframes` CLI（`npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell` —— **必须**，用于通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获路径实现最佳品质渲染。
4. 运行 `npx hyperframes doctor` 并报告结果。

如果设置失败，请参见 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。

<a id="procedure"></a>
## 流程

<a id="1-plan-before-writing-html"></a>
### 1. 编写 HTML 之前的规划

在触碰代码之前，先在高层次上阐明：
- **内容**——叙事弧线、关键时刻、情感节奏
- **结构**——构图、轨道（视频/音频/叠加层）、时长
- **视觉识别**——颜色、字体、运动特征（爆发式 / 电影感 / 流畅 / 技术感）
- **关键帧**——每个场景中大多数元素同时可见的瞬间。这是你首先要构建的静态布局。

**视觉标识门（HARD-GATE）。** 在编写任何构图 HTML 之前，必须定义视觉标识。不要使用默认或通用颜色来编写构图（`#333`、`#3b82f6`、`Roboto` 是跳过此步骤的标志）。按顺序检查：

1. **项目根目录下有 `DESIGN.md`？** → 使用其中确切颜色、字体、运动规则以及“禁止操作”约束。
2. **用户指定了风格**（例如“Swiss Pulse”、“dark and techy”、“奢华品牌”）？ → 生成一个最小化的 `DESIGN.md`，包含 `## Style Prompt`、`## Colors`（3-5 个十六进制颜色及其角色）、`## Typography`（1-2 个字体族）、`## What NOT to Do`（3-5 个反模式）。
3. **以上都不是？** → 在编写任何 HTML 前询问 3 个问题：
   - 情绪？（爆发式 / 电影感 / 流畅 / 技术感 / 混乱 / 温暖）
   - 浅色还是深色画布？
   - 是否有品牌色、字体或视觉参考？

   然后根据答案生成一个 `DESIGN.md`。每个构图都必须将其调色板和字体族追溯回 `DESIGN.md` 或用户的明确指示。

<a id="2-scaffold"></a>
### 2. 项目初始化

```bash
npx hyperframes init my-video --non-interactive
```

模板：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。使用 `--example &lt;name&gt;` 选择一个，使用 `--video clip.mp4` 或 `--audio track.mp3` 通过媒体文件初始化。

<a id="3-layout-before-animation"></a>
### 3. 在动画前布局

首先编写关键帧的静态 HTML+CSS——暂不涉及 GSAP。`.scene-content` 容器必须填充场景（`width:100%; height:100%; padding:Npx`），使用 `display:flex` + `gap`。使用 padding 将内容向内推——永远不要在内容容器上使用 `position: absolute; top: Npx`（当内容高度超过剩余空间时会溢出）。
只有当英雄画面的布局看起来正确后，再添加 `gsap.from()` 入场动画（从CSS位置动画**到**指定状态）和 `gsap.to()` 出场动画（从指定状态动画**离开**）。

完整的数据属性（data-attribute）模式与组合规则请参见 [references/composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md)。

<a id="4-animate-with-gsap"></a>
### 4. 使用 GSAP 制作动画

每个组合（composition）必须：
- 注册其时间线：`window.__timelines["&lt;composition-id&gt;"] = tl`
- 以暂停状态开始：`gsap.timeline({ paused: true })` —— 播放器控制播放
- 使用有限的 `repeat` 值（不要用 `repeat: -1` —— 这会破坏捕获引擎）。计算方法：`repeat: Math.ceil(duration / cycleDuration) - 1`
- 具备确定性 —— 不要使用 `Math.random()`、`Date.now()` 或基于时钟的逻辑。如果需要伪随机，使用种子化的伪随机数生成器（seeded PRNG）
- 同步构建 —— 在时间线构建过程中不要使用 `async`/`await`、`setTimeout` 或 Promise

核心 GSAP API（补间、缓动、交错、时间线）请参见 [references/gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md)。

<a id="5-transitions-between-scenes"></a>
### 5. 场景之间的转场

多场景组合需要使用转场。规则：
1. **场景之间始终使用转场** —— 不要用跳切（jump cut）
2. **每个场景元素始终使用入场动画**（`gsap.from(...)`）
3. **除最后一个场景外，不要使用出场动画** —— 转场本身即为出场
4. 最后一个场景可以淡出

使用 `npx hyperframes add &lt;transition-name&gt;` 安装着色器转场（`flash-through-white`、`liquid-wipe` 等）。完整列表：`npx hyperframes add --list`。

<a id="6-audio-captions-tts-audio-reactive-highlighting"></a>
### 6. 音频、字幕、TTS、音频响应与高亮

- **音频：** 始终使用独立的 `&lt;audio&gt;` 元素（视频使用 `muted playsinline`）
- **TTS：** `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav`。使用 `--list` 列出可用语音。语音 ID 的第一个字母编码语言（`a`/`b`=英语, `e`=西班牙语, `f`=法语, `j`=日语, `z`=普通话等）—— CLI 会自动推断音素器（phonemizer）的区域设置；只有需要覆盖时才传入 `--lang`。非英语的音素化需要系统级别安装 `espeak-ng`
- **字幕：** `npx hyperframes transcribe narration.wav` → 逐词转录。根据转录的语气选择风格（ hype / corporate / tutorial / storytelling / social —— 参见 `references/features.md` 中的表格）。**语言规则：** 除非音频确认是英语，否则不要使用 `.en` 的 whisper 模型 —— `.en` 模型会翻译非英语音频而非转录。每个字幕组（caption group）**必须**在其出场补间结束后，使用硬性的 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 进行清理 —— 否则字幕组会可见地泄漏到后续字幕组中
- **音频响应视觉：** 预先提取音频频段（低音/中音/高音），并在时间线内部使用 `for` 循环配合 `tl.call(draw, [], f / fps)` 逐帧采样 —— 单个长补间无法响应音频。映射关系：低音 → `scale`（脉冲效果），高音 → `textShadow`/`boxShadow`（发光效果），整体幅度 → `opacity`/`y`/`backgroundColor`。避免均衡器条的老套效果 —— 让内容引导视觉，音频驱动其行为
- **标记式高亮：** 用于文字强调的高亮、圆圈、爆发、涂鸦、素描效果是确定性的 CSS+GSAP —— 参见 `references/features.md#marker-highlighting`。完全可定位，不使用动画 SVG 滤镜
- **场景转场：** 每个多场景组合**必须**使用转场（不能有跳切）。可从 CSS 基本转场（推拉滑动、模糊交叉淡变、缩放穿过、交错方块）或着色器转场（`flash-through-white`、`liquid-wipe`、`cross-warp-morph`、`chromatic-split` 等）中选择，通过 `npx hyperframes add` 安装。情绪与能量对照表位于 `references/features.md#transitions`。不要在同一个组合中混用 CSS 转场和着色器转场。
<a id="7-lint-validate-inspect-preview-render"></a>
### 7. Lint（代码检查）、validate（验证）、inspect（检查）、preview（预览）、render（渲染）

```bash
npx hyperframes lint              # 捕获缺少 data-composition-id、轨道重叠、未注册的时间线
npx hyperframes validate          # 在 5 个时间点进行 WCAG 对比度审计
npx hyperframes inspect           # 可视化布局检查 — 元素溢出、超出帧范围、被遮挡的文本
npx hyperframes preview           # 实时浏览器预览
npx hyperframes render --quality draft --output draft.mp4    # 快速迭代
npx hyperframes render --quality high --output final.mp4     # 最终输出
```

`hyperframes validate` 会采样每个文本元素背后的背景像素，并在对比度低于 4.5:1（大文本为 3:1）时发出警告。`hyperframes inspect` 是布局侧的配套工具——它在多个时间点运行页面，并标记静态 lint 无法发现的问题（例如仅在 4.5 秒时换行超出安全区域的字幕、标题为最长变体时溢出的卡片、最终出现在过渡着色器后面的元素）。对于包含对话气泡、卡片、字幕或紧凑排版的合成，尤其要运行 `inspect`。

<a id="8-website-to-video-if-the-user-gives-a-url"></a>
### 8. 网站转视频（如果用户提供了 URL）

使用 [references/website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) 中的 7 步捕获到视频工作流：捕获 → DESIGN.md → SCRIPT.md → 故事板 → 合成 → 渲染 → 交付。

<a id="pitfalls"></a>
## 常见陷阱

- **`HeadlessExperimental.beginFrame' wasn't found`** — Chromium 147+ 移除了此协议。请确保使用 `hyperframes@>=0.4.2`（自动检测并回退到截图模式）。逃生舱：`export PRODUCER_FORCE_SCREENSHOT=true`。参见 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 和 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。
- **系统 Chrome（而非 `chrome-headless-shell`）** — 渲染会挂起 120 秒然后超时。运行 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 会执行此操作）。`hyperframes doctor` 会报告将要使用的二进制文件。
- **任何地方的 `repeat: -1`** — 会破坏捕获引擎。始终计算一个有限的重复次数。
- **在稍后进入的剪辑元素上使用 `gsap.set()`** — 页面加载时该元素不存在。请改用时间线内的 `tl.set(selector, vars, timePosition)`，且时间位置在剪辑的 `data-start` 或之后。
- **内容文本中的 `&lt;br&gt;`** — 强制换行不知道渲染字体的宽度，因此自然换行加 `&lt;br&gt;` 会导致双重换行。使用 `max-width` 让文本自动换行。例外：每个单词刻意独占一行的短显示标题。
- **对 `visibility` 或 `display` 进行动画** — GSAP 无法对这些属性进行补间。请使用 `autoAlpha`（同时处理可见性和透明度）。
- **调用 `video.play()` 或 `audio.play()`** — 框架拥有播放控制权。切勿自行调用。
- **异步构建时间线** — 捕获引擎在页面加载后同步读取 `window.__timelines`。切勿将时间线构建包装在 `async`、`setTimeout` 或 Promise 中。
- **将独立的 `index.html` 包裹在 `&lt;template&gt;` 中** — 会向浏览器隐藏所有内容。只有通过 `data-composition-src` 加载的**子合成**才使用 `&lt;template&gt;`。
- **使用视频作为音频** — 始终使用静音 `&lt;video&gt;` + 单独的 `&lt;audio&gt;`。
<a id="verification"></a>
## 验证

渲染前后：

1. **Lint + 验证 + 检查通过：** `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（lint 检查结构问题，validate 检查对比度，inspect 检查视觉布局/溢出问题——如出现警告，参见 troubleshooting.md）。
2. **动画编排** —— 对于新合成或重大动画更改，运行动画映射。`npx hyperframes init` 将技能脚本复制到项目中，因此路径是项目本地的：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
   输出一个 `animation-map.json` 文件，包含每个补间的摘要、ASCII 甘特图时间线、交错检测、死区（>1秒无动画）、元素生命周期和标记（`offscreen`、`collision`、`invisible`、`paced-fast` &lt;0.2s、`paced-slow` >2s）。扫描摘要和标记——修复或说明每个标记。小改动可跳过此步骤。
3. **文件存在且非零：** `ls -lh final.mp4`。
4. **时长匹配 `data-duration`：** `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取合成中间帧：`ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **音频存在（如果期望）：** `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 失败，运行 `npx hyperframes doctor` 并在报告时附上其输出。

<a id="references"></a>
## 参考

- [composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md) —— 数据属性、时间线契约、不可协商的规则、排版/资源规则
- [cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md) —— 所有 CLI 命令（init、capture、lint、validate、inspect、preview、render、transcribe、tts、doctor、browser、info、upgrade、benchmark）
- [gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md) —— HyperFrames 的 GSAP 核心 API（补间、缓动、交错、时间线、matchMedia）
- [features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/features.md) —— 字幕、TTS、音频反应、标记高亮、过渡（按需加载）
- [website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) —— 7步捕获到视频的工作流
- [troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md) —— OpenClaw 修复、环境变量、常见渲染错误
