---
title: "Manim 视频 — Manim CE 动画：3Blue1Brown 数学/算法视频"
sidebar_label: "Manim 视频"
description: "Manim CE 动画：3Blue1Brown 数学/算法视频"
---

{/* 本页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Manim 视频 {#manim-video}

Manim CE 动画：3Blue1Brown 数学/算法视频。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/manim-video` |
| 版本 | `1.0.0` |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。当技能激活时，Agent 看到的就是这些指令。
:::

# Manim 视频制作流程 {#manim-video-production-pipeline}

## 何时使用 {#when-to-use}

当用户请求：动画讲解、数学动画、概念可视化、算法演示、技术解说、3Blue1Brown 风格视频，或任何与几何/数学内容相关的程序化动画时使用。使用 Manim Community Edition 制作 3Blue1Brown 风格的讲解视频、算法可视化、公式推导、架构图和数据叙事。

## 创作标准 {#creative-standard}

这是教育影院。每一帧都在教学。每一个动画都在揭示结构。

**在写任何一行代码之前**，先阐述叙事弧线。这个动画纠正了什么误解？"恍然大悟"的时刻在哪？什么样的视觉故事能带领观众从困惑走向理解？用户的提示是一个起点——要以教学抱负来诠释它。

**先几何后代数。** 先展示形状，再给出方程。视觉记忆比符号记忆编码更快。当观众在看到公式之前先看到几何模式时，这个方程就显得水到渠成。

**首次渲染即达完美，不容妥协。** 输出结果必须在视觉上清晰、美学上协调，无需反复修改。如果看起来杂乱、节奏不当，或者像"AI 生成的幻灯片"，那就是错的。

**不透明度分层引导注意力。** 永远不要把所有元素都以全亮度显示。主要元素为 1.0，上下文元素为 0.4，结构元素（坐标轴、网格）为 0.15。大脑会分层处理视觉显著性。

**呼吸空间。** 每个动画之后都需要 `self.wait()`。观众需要时间来吸收刚刚出现的内容。永远不要让动画一个接一个地匆忙进行。在关键揭示之后停顿 2 秒绝不会浪费。

**一致的视觉语言。** 所有场景共享统一的配色方案、一致的字体大小、匹配的动画速度。一个技术上正确但每个场景都使用随机颜色的视频，在美学上是失败的。

## 先决条件 {#prerequisites}

运行 `scripts/setup.sh` 验证所有依赖项。需要：Python 3.10+、Manim Community Edition v0.20+（`pip install manim`）、LaTeX（Linux 上为 `texlive-full`，macOS 上为 `mactex`）和 ffmpeg。参考文档针对 Manim CE v0.20.1 进行了测试。

## 模式 {#modes}

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **概念讲解** | 主题/概念 | 带有几何直觉的动画讲解 | `references/scene-planning.md` |
| **公式推导** | 数学表达式 | 逐步动画证明 | `references/equations.md` |
| **算法可视化** | 算法描述 | 带数据结构的逐步执行过程 | `references/graphs-and-data.md` |
| **数据故事** | 数据/指标 | 动画图表、比较、计数器 | `references/graphs-and-data.md` |
| **架构图** | 系统描述 | 组件逐步构建并建立连接 | `references/mobjects.md` |
| **论文讲解** | 研究论文 | 关键发现和方法动画演示 | `references/scene-planning.md` |
| **3D 可视化** | 3D 概念 | 旋转曲面、参数曲线、空间几何 | `references/camera-and-3d.md` |
## 技术栈 {#stack}

每个项目一个独立的 Python 脚本。无需浏览器、Node.js 或 GPU。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | Manim Community Edition | 场景渲染、动画引擎 |
| 数学 | LaTeX（texlive/MiKTeX） | 通过 `MathTex` 渲染公式 |
| 视频 I/O | ffmpeg | 场景拼接、格式转换、音频混流 |
| TTS | ElevenLabs / Qwen3-TTS（可选） | 旁白配音 |

## 工作流 {#pipeline}

```
规划 --> 编码 --> 渲染 --> 拼接 --> 音频（可选）--> 审阅
```

1. **规划** — 编写 `plan.md`，包含叙事弧线、场景列表、视觉元素、配色方案、旁白脚本
2. **编码** — 编写 `script.py`，每个场景一个类，每个类可独立渲染
3. **渲染** — 草稿用 `manim -ql script.py Scene1 Scene2 ...`，正式版用 `-qh`
4. **拼接** — 使用 ffmpeg 将场景片段拼接为 `final.mp4`
5. **音频**（可选）— 通过 ffmpeg 添加旁白和/或背景音乐。参见 `references/rendering.md`
6. **审阅** — 渲染预览静帧，对照规划检查，调整

## 项目结构 {#project-structure}

```
project-name/
  plan.md                # 叙事弧线、场景分解
  script.py              # 所有场景写在一个文件中
  concat.txt             # ffmpeg 场景列表
  final.mp4              # 拼接后的输出
  media/                 # 由 Manim 自动生成
    videos/script/480p15/
```

## 创意方向 {#creative-direction}

### 配色方案 {#color-palettes}

| 配色 | 背景色 | 主色 | 辅色 | 强调色 | 适用场景 |
|---------|-----------|---------|-----------|--------|----------|
| **经典 3B1B** | `#1C1C1C` | `#58C4DD`（蓝） | `#83C167`（绿） | `#FFFF00`（黄） | 通用数学/计算机科学 |
| **温暖学术** | `#2D2B55` | `#FF6B6B` | `#FFD93D` | `#6BCB77` | 亲和力强 |
| **霓虹科技** | `#0A0A0A` | `#00F5FF` | `#FF00FF` | `#39FF14` | 系统、架构 |
| **单色** | `#1A1A2E` | `#EAEAEA` | `#888888` | `#FFFFFF` | 极简风格 |

### 动画速度 {#animation-speed}

| 场景 | run_time | 之后的 self.wait() |
|---------|----------|-------------------|
| 标题/开场出现 | 1.5s | 1.0s |
| 关键公式揭示 | 2.0s | 2.0s |
| 变换/变形 | 1.5s | 1.5s |
| 辅助标签 | 0.8s | 0.5s |
| 淡出清理 | 0.5s | 0.3s |
| “顿悟时刻”揭示 | 2.5s | 3.0s |

### 字体大小层级 {#typography-scale}

| 角色 | 字号 | 用途 |
|------|-----------|-------|
| 标题 | 48 | 场景标题、开场文字 |
| 标题 | 36 | 场景内章节标题 |
| 正文 | 30 | 解释性文字 |
| 标签 | 24 | 注释、坐标轴标签 |
| 说明 | 20 | 字幕、小字 |

### 字体 {#fonts}

**所有文字使用等宽字体。** Manim 的 Pango 渲染器在使用比例字体时，所有字号下都会产生错误的字距。完整建议参见 `references/visual-design.md`。

```python
MONO = "Menlo"  # 在文件顶部定义一次

Text("Fourier Series", font_size=48, font=MONO, weight=BOLD)  # 标题
Text("n=1: sin(x)", font_size=20, font=MONO)                  # 标签
MathTex(r"\nabla L")                                            # 数学公式（使用 LaTeX）
```

最小 `font_size=18` 以保证可读性。
### 每场变化 {#per-scene-variation}

不要对所有场景使用相同的配置。每个场景应：
- **不同的主色调**（从调色板中选取）
- **不同的布局**——不要总是把所有内容居中
- **不同的动画入场方式**——在 Write、FadeIn、GrowFromCenter、Create 之间变化
- **不同的视觉重量**——有些场景密集，有些稀疏

## 工作流程 {#workflow}

### 步骤 1：规划（plan.md） {#step-1-plan-plan-md}

在编写任何代码之前，先写 `plan.md`。完整模板请参考 `references/scene-planning.md`。

### 步骤 2：编码（script.py） {#step-2-code-script-py}

每个场景一个类。每个场景都可以独立渲染。

```python
from manim import *

BG = "#1C1C1C"
PRIMARY = "#58C4DD"
SECONDARY = "#83C167"
ACCENT = "#FFFF00"
MONO = "Menlo"

class Scene1_Introduction(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Why Does This Work?", font_size=48, color=PRIMARY, weight=BOLD, font=MONO)
        self.add_subcaption("Why does this work?", duration=2)
        self.play(Write(title), run_time=1.5)
        self.wait(1.0)
        self.play(FadeOut(title), run_time=0.5)
```

关键模式：
- **每个动画都加字幕**：`self.add_subcaption("text", duration=N)` 或在 `self.play()` 中使用 `subcaption="text"`
- **文件顶部共享颜色常量**，保证跨场景一致性
- **每个场景都设置 `self.camera.background_color`**
- **干净退出**——场景结束时用 `FadeOut` 清除所有 mobject：`self.play(FadeOut(Group(*self.mobjects)))`

### 步骤 3：渲染 {#step-3-render}

```bash
manim -ql script.py Scene1_Introduction Scene2_CoreConcept  # 草稿
manim -qh script.py Scene1_Introduction Scene2_CoreConcept  # 正式
```

### 步骤 4：拼接 {#step-4-stitch}

```bash
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1_Introduction.mp4'
file 'media/videos/script/480p15/Scene2_CoreConcept.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

### 步骤 5：审查 {#step-5-review}

```bash
manim -ql --format=png -s script.py Scene2_CoreConcept  # 预览静态帧
```

## 关键实现说明 {#critical-implementation-notes}

### LaTeX 使用原始字符串 {#raw-strings-for-latex}
```python
# 错误：MathTex("\frac{1}{2}")
# 正确：
MathTex(r"\frac{1}{2}")
```

### 边缘文本的 buff >= 0.5 {#buff-0-5-for-edge-text}
```python
label.to_edge(DOWN, buff=0.5)  # 永远不要小于 0.5
```

### 替换文本前先 FadeOut {#fadeout-before-replacing-text}
```python
self.play(ReplacementTransform(note1, note2))  # 不要直接在原文本上 Write(note2)
```

### 永远不要对未添加的 mobject 做动画 {#never-animate-non-added-mobjects}
```python
self.play(Create(circle))  # 必须先 add
self.play(circle.animate.set_color(RED))  # 然后做动画
```

## 性能目标 {#performance-targets}

| 质量 | 分辨率 | 帧率 | 速度 |
|---------|-----------|-----|-------|
| `-ql`（草稿） | 854x480 | 15 | 5-15 秒/场景 |
| `-qm`（中等） | 1280x720 | 30 | 15-60 秒/场景 |
| `-qh`（正式） | 1920x1080 | 60 | 30-120 秒/场景 |

始终在 `-ql` 下迭代。只在最终输出时使用 `-qh` 渲染。

## 参考 {#references}

| 文件 | 内容 |
|------|----------|
| `references/animations.md` | 核心动画、速率函数、组合、`.animate` 语法、时间模式 |
| `references/mobjects.md` | 文本、形状、VGroup/Group、定位、样式、自定义 mobject |
| `references/visual-design.md` | 12 条设计原则、透明度分层、布局模板、调色板 |
| `references/equations.md` | Manim 中的 LaTeX、TransformMatchingTex、推导模式 |
| `references/graphs-and-data.md` | 坐标轴、绘图、BarChart、动画数据、算法可视化 |
| `references/camera-and-3d.md` | MovingCameraScene、ThreeDScene、3D 曲面、相机控制 |
| `references/scene-planning.md` | 叙事弧线、布局模板、场景过渡、规划模板 |
| `references/rendering.md` | CLI 参考、质量预设、ffmpeg、配音工作流、GIF 导出 |
| `references/troubleshooting.md` | LaTeX 错误、动画错误、常见错误、调试 |
| `references/animation-design-thinking.md` | 何时使用动画 vs 静态展示、分解、节奏、旁白同步 |
| `references/updaters-and-trackers.md` | ValueTracker、add_updater、always_redraw、基于时间的 updater、模式 |
| `references/paper-explainer.md` | 将研究论文转化为动画——工作流、模板、领域模式 |
| `references/decorations.md` | SurroundingRectangle、Brace、箭头、DashedLine、Angle、注释生命周期 |
| `references/production-quality.md` | 编码前、渲染前、渲染后检查清单、空间布局、颜色、节奏 |
---

## 创意发散（仅在用户要求实验性/创意性/独特输出时使用） {#creative-divergence-use-only-when-user-requests-experimental-creative-unique-output}

如果用户要求采用创意性、实验性或非传统的解释方式，请在设计动画之前先选择一种策略并进行推理。

- **SCAMPER** — 当用户希望为标准解释提供全新视角时
- **假设反转** — 当用户希望挑战某主题的常规教学方式时

### SCAMPER 变换 {#scamper-transformation}
将标准的数学/技术可视化进行变换：
- **替代**：替换标准的视觉隐喻（数轴 → 蜿蜒路径，矩阵 → 城市网格）
- **组合**：合并两种解释方法（代数 + 几何同时进行）
- **逆向**：反向推导——从结果出发，解构到公理
- **修改**：夸大某个参数以显示其重要性（10 倍学习率，1000 倍样本量）
- **消除**：去除所有符号——仅通过动画和空间关系进行解释

### 假设反转 {#assumption-reversal}
1. 列出该主题可视化的“标准”方式（从左到右、二维、离散步骤、正式符号）
2. 选择最根本的假设
3. 将其反转（从右到左推导、将二维概念嵌入三维、连续变形代替步骤、零符号）
4. 探索反转揭示了哪些标准方式所隐藏的内容
