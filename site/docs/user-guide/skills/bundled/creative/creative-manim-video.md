---
title: "Manim Video — Manim CE 动画：3Blue1Brown 数学/算法视频"
sidebar_label: "Manim Video"
description: "Manim CE 动画：3Blue1Brown 数学/算法视频"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="manim-video"></a>
# Manim 视频

Manim CE 动画：3Blue1Brown 数学/算法视频。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/manim-video` |
| 版本 | `1.0.0` |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下就是 Hermes 在该技能被触发时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="manim-video-production-pipeline"></a>
# Manim 视频制作流水线

<a id="when-to-use"></a>
## 何时使用

当用户请求以下内容时使用：动画解释、数学动画、概念可视化、算法讲解、技术说明、3Blue1Brown 风格视频，或任何涉及几何/数学内容的编程动画。使用 Manim 社区版创建 3Blue1Brown 风格的讲解视频、算法可视化、方程推导、架构图和数据故事。

<a id="creative-standard"></a>
## 创作标准

这是教育电影。每一帧都在传授知识。每个动画都揭示结构。

**在写一行代码之前**，阐明叙事弧线。这个修正了什么误解？什么是“顿悟时刻”？什么视觉故事将观众从困惑引向理解？用户的提示只是一个起点——要用教学上的雄心去解读它。

**几何先于代数。** 先展示形状，再展示方程。视觉记忆编码比符号记忆更快。当观众在看到公式之前先看到几何图案时，方程就显得理所应当了。

**首版渲染的 excellence 不可妥协。** 输出必须在视觉上清晰且美观一致，无需修订迭代。如果内容看起来杂乱、节奏不佳，或者像是“AI 生成的幻灯片”，那就是错的。

**不透明度分层引导注意力。** 永远不要将所有元素都以全亮度显示。主要元素用 1.0，上下文元素用 0.4，结构元素（轴线、网格）用 0.15。大脑是按层处理视觉突显的。

**留出呼吸空间。** 每个动画之后都需要 `self.wait()`。观众需要时间来消化刚刚出现的内容。不要从一个动画急匆匆跳到下一个。关键揭示后停顿 2 秒从来不会浪费。

**一致的视觉语言。** 所有场景共享配色方案、一致的字体大小、匹配的动画速度。一个技术上正确但每个场景都用随机不同颜色的视频，在美学上是失败的。

<a id="prerequisites"></a>
## 前置条件

运行 `scripts/setup.sh` 来验证所有依赖。需要：Python 3.10+、Manim Community Edition v0.20+（`pip install manim`）、LaTeX（Linux 上为 `texlive-full`，macOS 上为 `mactex`）以及 ffmpeg。参考文档已针对 Manim CE v0.20.1 测试。

<a id="modes"></a>
## 模式

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **概念解释** | 主题/概念 | 带有几何直觉的动画解释 | `references/scene-planning.md` |
| **方程推导** | 数学表达式 | 逐步动画证明 | `references/equations.md` |
| **算法可视化** | 算法描述 | 利用数据结构逐步执行 | `references/graphs-and-data.md` |
| **数据故事** | 数据/指标 | 动画图表、对比、计数器 | `references/graphs-and-data.md` |
| **架构图** | 系统描述 | 组件逐步构建并显示连接 | `references/mobjects.md` |
| **论文讲解** | 研究论文 | 关键发现和方法动画 | `references/scene-planning.md` |
| **3D 可视化** | 3D 概念 | 旋转曲面、参数曲线、空间几何 | `references/camera-and-3d.md` |
<a id="stack"></a>
## 技术栈

每个项目一个独立的 Python 脚本。无需浏览器、无需 Node.js、无需 GPU。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | Manim Community Edition | 场景渲染、动画引擎 |
| 数学 | LaTeX（texlive/MiKTeX） | 通过 `MathTex` 渲染公式 |
| 视频 I/O | ffmpeg | 场景拼接、格式转换、音频混合 |
| 语音合成 | ElevenLabs / Qwen3-TTS（可选） | 旁白配音 |

<a id="pipeline"></a>
## 工作流程

```
PLAN --> CODE --> RENDER --> STITCH --> AUDIO (可选) --> REVIEW
```

1. **PLAN** — 编写 `plan.md`，包含叙事弧线、场景列表、视觉元素、配色方案、旁白脚本
2. **CODE** — 编写 `script.py`，每个场景一个类，可独立渲染
3. **RENDER** — `manim -ql script.py Scene1 Scene2 ...` 用于草稿，`-qh` 用于正式版
4. **STITCH** — 使用 ffmpeg 拼接场景片段，生成 `final.mp4`
5. **AUDIO**（可选）— 通过 ffmpeg 添加旁白和/或背景音乐。参见 `references/rendering.md`
6. **REVIEW** — 渲染预览静态图，对照计划检查并调整

<a id="project-structure"></a>
## 项目结构

```
project-name/
  plan.md                # 叙事弧线、场景分解
  script.py              # 所有场景在一个文件中
  concat.txt             # ffmpeg 场景列表
  final.mp4              # 拼接后的输出文件
  media/                 # Manim 自动生成
    videos/script/480p15/
```

<a id="creative-direction"></a>
## 创意方向

<a id="color-palettes"></a>
### 配色方案

| 配色 | 背景色 | 主色 | 辅色 | 强调色 | 使用场景 |
|---------|-----------|---------|-----------|--------|----------|
| **经典 3B1B** | `#1C1C1C` | `#58C4DD`（蓝色） | `#83C167`（绿色） | `#FFFF00`（黄色） | 通用数学/计算机科学 |
| **温暖学术** | `#2D2B55` | `#FF6B6B` | `#FFD93D` | `#6BCB77` | 亲切友好 |
| **霓虹科技** | `#0A0A0A` | `#00F5FF` | `#FF00FF` | `#39FF14` | 系统、架构 |
| **单色调** | `#1A1A2E` | `#EAEAEA` | `#888888` | `#FFFFFF` | 极简风格 |

<a id="animation-speed"></a>
### 动画速度

| 场景 | run_time | self.wait() 后停顿 |
|---------|----------|-------------------|
| 标题/开场出现 | 1.5s | 1.0s |
| 关键公式揭示 | 2.0s | 2.0s |
| 变换/变形 | 1.5s | 1.5s |
| 辅助标签 | 0.8s | 0.5s |
| 淡出清理 | 0.5s | 0.3s |
| “恍然大悟”时刻揭示 | 2.5s | 3.0s |

<a id="typography-scale"></a>
### 字号比例

| 角色 | 字号 | 用途 |
|------|-----------|-------|
| 标题 | 48 | 场景标题、开场文字 |
| 章节标题 | 36 | 场景内章节标题 |
| 正文 | 30 | 解释性文字 |
| 标签 | 24 | 注释、坐标轴标签 |
| 注释 | 20 | 副标题、小字 |

<a id="fonts"></a>
### 字体

**所有文字使用等宽字体。** Manim 的 Pango 渲染器在非等宽字体下会产生字距错误。完整推荐请参见 `references/visual-design.md`。

```python
MONO = "Menlo"  # 在文件顶部定义一次

Text("Fourier Series", font_size=48, font=MONO, weight=BOLD)  # 标题
Text("n=1: sin(x)", font_size=20, font=MONO)                  # 标签
MathTex(r"\nabla L")                                            # 数学公式（使用 LaTeX）
```

最小 `font_size=18` 以保证可读性。
<a id="per-scene-variation"></a>
### 每个场景的差异化

不要为所有场景使用完全相同的配置。每个场景应：

- **使用色板中的不同主色调**
- **采用不同的布局**——不要总是把所有内容居中
- **使用不同的动画入场方式**——在 Write、FadeIn、GrowFromCenter、Create 之间切换
- **体现不同的视觉密度**——有些场景密集，有些稀疏

<a id="workflow"></a>
## 工作流程

<a id="step-1-plan-plan-md"></a>
### 第一步：规划（plan.md）

在编写任何代码之前，先写 `plan.md`。完整模板请参考 `references/scene-planning.md`。

<a id="step-2-code-script-py"></a>
### 第二步：编码（script.py）

每个场景一个类。每个场景均可独立渲染。

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

- **每次动画添加字幕**：`self.add_subcaption("文本", duration=N)` 或 `self.play()` 中传入 `subcaption="文本"`
- **文件顶部共享颜色常量**，确保跨场景一致性
- **在每个场景中设置** `self.camera.background_color`
- **干净的退出**——场景结束时用 FadeOut 清除所有对象：`self.play(FadeOut(Group(*self.mobjects)))`

<a id="step-3-render"></a>
### 第三步：渲染

```bash
manim -ql script.py Scene1_Introduction Scene2_CoreConcept  # 草稿
manim -qh script.py Scene1_Introduction Scene2_CoreConcept  # 最终版
```

<a id="step-4-stitch"></a>
### 第四步：拼接

```bash
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1_Introduction.mp4'
file 'media/videos/script/480p15/Scene2_CoreConcept.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

<a id="step-5-review"></a>
### 第五步：审查

```bash
manim -ql --format=png -s script.py Scene2_CoreConcept  # 预览静帧
```

<a id="critical-implementation-notes"></a>
## 关键实现说明

<a id="raw-strings-for-latex"></a>
### LaTeX 必须使用原始字符串
```python
# 错误：MathTex("\frac{1}{2}")
# 正确：
MathTex(r"\frac{1}{2}")
```

<a id="buff-0-5-for-edge-text"></a>
### 边缘文本的 buff >= 0.5
```python
label.to_edge(DOWN, buff=0.5)  # 切勿小于 0.5
```

<a id="fadeout-before-replacing-text"></a>
### 替换文本前先淡出
```python
self.play(ReplacementTransform(note1, note2))  # 不要直接在原文本上 Write(note2)
```

<a id="never-animate-non-added-mobjects"></a>
### 切勿动画未添加的对象
```python
self.play(Create(circle))  # 必须先 add
self.play(circle.animate.set_color(RED))  # 然后才能动画
```

<a id="performance-targets"></a>
## 性能目标

| 质量 | 分辨率 | 帧率 | 速度 |
|---------|-----------|-----|-------|
| `-ql`（草稿） | 854×480 | 15 | 5-15 秒/场景 |
| `-qm`（中等） | 1280×720 | 30 | 15-60 秒/场景 |
| `-qh`（最终版） | 1920×1080 | 60 | 30-120 秒/场景 |

始终先用 `-ql` 迭代。仅在最终输出时使用 `-qh` 渲染。

<a id="references"></a>
## 参考资料

| 文件 | 内容 |
|------|----------|
| `references/animations.md` | 核心动画、速率函数、组合、`.animate` 语法、时间控制模式 |
| `references/mobjects.md` | 文本、形状、VGroup/Group、定位、样式、自定义对象 |
| `references/visual-design.md` | 12 条设计原则、不透明度分层、布局模板、色板 |
| `references/equations.md` | Manim 中的 LaTeX、TransformMatchingTex、推导模式 |
| `references/graphs-and-data.md` | 坐标轴、绘图、柱状图、动态数据、算法可视化 |
| `references/camera-and-3d.md` | MovingCameraScene、ThreeDScene、3D 曲面、相机控制 |
| `references/scene-planning.md` | 叙事弧线、布局模板、场景过渡、规划模板 |
| `references/rendering.md` | CLI 参考、质量预设、ffmpeg、配音工作流、GIF 导出 |
| `references/troubleshooting.md` | LaTeX 错误、动画错误、常见错误、调试 |
| `references/animation-design-thinking.md` | 何时使用动画 vs 静态展示、分解、节奏、解说同步 |
| `references/updaters-and-trackers.md` | ValueTracker、add_updater、always_redraw、基于时间的更新器、模式 |
| `references/paper-explainer.md` | 将研究论文转化为动画——工作流、模板、领域模式 |
| `references/decorations.md` | SurroundingRectangle、Brace、箭头、DashedLine、Angle、注解生命周期 |
| `references/production-quality.md` | 编码前、渲染前、渲染后检查清单、空间布局、颜色、节奏 |
---

<a id="creative-divergence-use-only-when-user-requests-experimental-creative-unique-output"></a>
## 创意发散（仅在用户要求实验性/创意性/独特输出时使用）

如果用户要求创意、实验性或非传统的解释方式，请在设计动画之前先选择一个策略并对其进行推理。

- **SCAMPER** — 当用户想要对标准解释进行全新演绎时
- **假设反转（Assumption Reversal）** — 当用户想要挑战某主题的常规教学方式时

<a id="scamper-transformation"></a>
### SCAMPER 变换
选取一个标准数学/技术可视化方法并进行变换：
- **替代（Substitute）**：替换标准视觉隐喻（数轴 → 蜿蜒路径，矩阵 → 城市网格）
- **组合（Combine）**：合并两种解释方式（同时使用代数和几何）
- **反向（Reverse）**：逆向推导——从结果出发，分解到公理
- **修改（Modify）**：夸大某个参数以展示其重要性（10 倍学习率，1000 倍样本量）
- **消除（Eliminate）**：去掉所有记号——仅通过动画和空间关系进行解释

<a id="assumption-reversal"></a>
### 假设反转（Assumption Reversal）
1. 列出该主题可视化中的“常规”要素（从左到右、2D、离散步骤、正式记号）
2. 选择其中最根本的假设
3. 将其反转（从右到左推导、将 2D 概念嵌入 3D、用连续变形替代离散步骤、零记号）
4. 探索反转后揭示了哪些常规方法所隐藏的东西
