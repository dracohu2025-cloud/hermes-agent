---
title: "Ascii Video — ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF"
sidebar_label: "Ascii Video"
description: "ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Ascii Video {#ascii-video}

ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/ascii-video` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# ASCII 视频制作管线 {#ascii-video-production-pipeline}

## 使用时机 {#when-to-use}

当用户提出以下请求时使用：ASCII 视频、文字艺术视频、终端风格视频、字符艺术动画、复古文字可视化、ASCII 音频可视化、将视频转换为 ASCII 艺术、矩阵风格效果，或任何动画 ASCII 输出。

## 包含内容 {#what-s-inside}

ASCII 艺术视频的制作管线——支持任何格式。将视频/音频/图像/生成式输入转换为彩色 ASCII 字符视频输出（MP4、GIF、图像序列）。涵盖：视频到 ASCII 转换、音频响应式音乐可视化、生成式 ASCII 艺术动画、混合视频+音频响应、文字/歌词叠加、实时终端渲染。

## 创意标准 {#creative-standard}

这是视觉艺术。ASCII 字符是媒介，电影是标准。

**在写任何代码之前**，先阐述创意概念。情绪是什么？它讲述什么视觉故事？是什么让这个项目与其他所有 ASCII 视频不同？用户的提示是起点——要用创意野心去诠释，而不是逐字照搬。

**首次渲染的卓越性不容妥协。** 输出必须在视觉上引人注目，无需反复修改。如果某些内容看起来普通、平淡，或像“AI 生成的 ASCII 艺术”，那就是错的——在交付前重新思考创意概念。

**超越参考词汇表。** 参考中的效果目录、着色器预设和调色板库只是起点词汇。对于每个项目，都要组合、修改和创造新的模式。目录是颜料的调色板——你来创作画作。

**主动发挥创意。** 当项目需要时，扩展技能的词汇表。如果参考中没有实现愿景所需的内容，就自己构建。至少包含一个用户没有要求但会欣赏的视觉瞬间——一个过渡、一个效果、一个能提升整体作品的颜色选择。

**美学统一性优先于技术正确性。** 视频中的所有场景必须通过统一的视觉语言相互关联——共享的色温、相关的字符调色板、一致的运动词汇。一个技术正确但每个场景都使用随机不同效果的视频，在美学上是失败的。

**密集、有层次、经过深思熟虑。** 每一帧都值得细看。永远不要使用纯黑色背景。始终采用多网格构图。始终为每个场景提供变化。始终有意识地使用颜色。

## 模式 {#modes}

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **视频转 ASCII** | 视频文件 | 源素材的 ASCII 再现 | `references/inputs.md` § 视频采样 |
| **音频响应式** | 音频文件 | 由音频特征驱动的生成式视觉 | `references/inputs.md` § 音频分析 |
| **生成式** | 无（或种子参数） | 程序化 ASCII 动画 | `references/effects.md` |
| **混合式** | 视频 + 音频 | 带有音频响应式叠加的 ASCII 视频 | 两个输入参考 |
| **歌词/文字** | 音频 + 文本/SRT | 带有视觉效果的定时文字 | `references/inputs.md` § 文字/歌词 |
| **TTS 旁白** | 文本引用 + TTS API | 带有打字文本的旁白推荐/引用视频 | `references/inputs.md` § TTS 集成 |
## 技术栈 {#stack}

每个项目都是一个独立的 Python 脚本，无需 GPU。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | Python 3.10+, NumPy | 数学运算、数组操作、向量化特效 |
| 信号 | SciPy | FFT、峰值检测（音频模式） |
| 图像 | Pillow (PIL) | 字体光栅化、帧解码、图像 I/O |
| 视频 I/O | ffmpeg (CLI) | 解码输入、编码输出、混流音频 |
| 并行 | concurrent.futures | 用于批量/片段渲染的 N 个工作进程 |
| TTS | ElevenLabs API (可选) | 生成旁白片段 |
| 可选 | OpenCV | 视频帧采样、边缘检测 |

## 流水线架构 {#pipeline-architecture}

每种模式都遵循相同的 6 阶段流水线：

```
INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE
```

1. **INPUT** — 加载/解码源素材（视频帧、音频样本、图像，或空）
2. **ANALYZE** — 提取每帧特征（音频频段、视频亮度/边缘、运动向量）
3. **SCENE_FN** — 场景函数渲染到像素画布（`uint8 H,W,3`）。通过 `_render_vf()` + 像素混合模式组合多个字符网格。参见 `references/composition.md`
4. **TONEMAP** — 基于百分位数的自适应亮度归一化。参见 `references/composition.md` § 自适应色调映射
5. **SHADE** — 通过 `ShaderChain` + `FeedbackBuffer` 进行后处理。参见 `references/shaders.md`
6. **ENCODE** — 将原始 RGB 帧通过管道送入 ffmpeg 进行 H.264/GIF 编码

## 创意方向 {#creative-direction}

### 美学维度 {#aesthetic-dimensions}

| 维度 | 选项 | 参考 |
|-----------|---------|-----------|
| **字符调色板** | 密度渐变、块元素、符号、文字（片假名、希腊文、符文、盲文）、项目专用 | `architecture.md` § 调色板 |
| **色彩策略** | HSV、OKLAB/OKLCH、离散 RGB 调色板、自动生成和谐色、单色、色温 | `architecture.md` § 色彩系统 |
| **背景纹理** | 正弦场、fBM 噪声、域扭曲、沃罗诺伊图、反应扩散、元胞自动机、视频 | `effects.md` |
| **主要特效** | 环、螺旋、隧道、涡旋、波浪、干涉、极光、火焰、SDF、奇异吸引子 | `effects.md` |
| **粒子** | 火花、雪、雨、气泡、符文、轨道、群集模拟、流场跟随、拖尾 | `effects.md` § 粒子 |
| **着色器氛围** | 复古 CRT、干净现代、故障艺术、电影感、梦幻、工业、迷幻 | `shaders.md` |
| **网格密度** | xs(8px) 到 xxl(40px)，每层可混合 | `architecture.md` § 网格系统 |
| **坐标空间** | 笛卡尔、极坐标、平铺、旋转、鱼眼、莫比乌斯、域扭曲 | `effects.md` § 变换 |
| **反馈** | 缩放隧道、彩虹拖尾、鬼影回响、旋转曼陀罗、色彩演化 | `composition.md` § 反馈 |
| **遮罩** | 圆形、环形、渐变、文字模板、动画光圈/擦除/溶解 | `composition.md` § 遮罩 |
| **转场** | 交叉淡入淡出、擦除、溶解、故障切、光圈、基于遮罩的揭示 | `shaders.md` § 转场 |

### 每段变化 {#per-section-variation}

切勿在整个视频中使用相同的配置。对于每个段落/场景：
- **不同的背景特效**（或组合 2-3 种）
- **不同的字符调色板**（匹配氛围）
- **不同的色彩策略**（或至少不同的色相）
- **变化着色器强度**（高潮时更多泛光，安静时更多颗粒）
- **如果粒子处于激活状态，使用不同的粒子类型**
### 项目特定发明 {#project-specific-invention}

每个项目至少发明以下一项：
- 与主题匹配的自定义字符调色板
- 自定义背景效果（组合/修改现有构建块）
- 自定义颜色调色板（与品牌/氛围匹配的离散 RGB 集合）
- 自定义粒子字符集
- 新颖的场景过渡或视觉瞬间

不要只是从目录中挑选。目录是词汇——你用它写诗。

## 工作流程 {#workflow}

### 第一步：创意愿景 {#step-1-creative-vision}

在写任何代码之前，先阐明创意概念：

- **氛围/情绪**：观众应该感受到什么？充满活力、冥想、混乱、优雅、不祥？
- **视觉故事**：在持续时间内发生了什么？制造紧张？转变？溶解？
- **色彩世界**：暖色/冷色？单色？霓虹？大地色？主色调是什么？
- **字符质感**：密集数据？稀疏星星？有机点？几何块？
- **这个项目有何不同**：是什么让这个项目独一无二？
- **情感弧线**：场景如何推进？以能量开场，推向高潮，然后收尾？

将用户的提示映射到美学选择上。一个“chill lo-fi 可视化器”与“故障赛博朋克数据流”所需的一切都不同。

### 第二步：技术设计 {#step-2-technical-design}

- **模式**——上述 6 种模式中的哪一种
- **分辨率**——横屏 1920x1080（默认），竖屏 1080x1920，方形 1080x1080 @ 24fps
- **硬件检测**——自动检测核心数/内存，设置质量配置文件。参见 `references/optimization.md`
- **章节**——将时间戳映射到场景函数，每个函数有自己的效果/调色板/颜色/着色器配置
- **输出格式**——MP4（默认），GIF（640x360 @ 15fps），PNG 序列

### 第三步：构建脚本 {#step-3-build-the-script}

单个 Python 文件。组件（附参考）：

1. **硬件检测 + 质量配置文件**——`references/optimization.md`
2. **输入加载器**——依赖模式；`references/inputs.md`
3. **特征分析器**——音频 FFT、视频亮度或合成数据
4. **网格 + 渲染器**——带位图缓存的多密度网格；`references/architecture.md`
5. **字符调色板**——每个项目多个；`references/architecture.md` § 调色板
6. **颜色系统**——HSV + 离散 RGB + 和谐生成；`references/architecture.md` § 颜色
7. **场景函数**——每个返回 `canvas (uint8 H,W,3)`；`references/scenes.md`
8. **色调映射**——自适应亮度归一化；`references/composition.md`
9. **着色器管线**——`ShaderChain` + `FeedbackBuffer`；`references/shaders.md`
10. **场景表 + 调度器**——时间 → 场景函数 + 配置；`references/scenes.md`
11. **并行编码器**——使用 ffmpeg 管道的 N 工作线程片段渲染
12. **主函数**——编排整个管线

### 第四步：质量验证 {#step-4-quality-verification}

- **先测试帧**：在完整渲染之前，在关键时间戳渲染单帧
- **亮度检查**：所有 ASCII 内容的 `canvas.mean() > 8`。如果太暗，降低伽马值
- **视觉连贯性**：所有场景是否感觉属于同一个视频？
- **创意愿景检查**：输出是否与第一步的概念匹配？如果看起来太普通，返回重做
## 关键实现说明 {#critical-implementation-notes}

### 亮度 —— 使用 `tonemap()`，不要用线性乘数 {#brightness-use-tonemap-not-linear-multipliers}

这是排名第一的视觉问题。黑色背景上的 ASCII 本身就很暗。**绝对不要使用 `canvas * N` 乘数**——它们会裁切高光。请使用自适应色调映射：

```python
def tonemap(canvas, gamma=0.75):
    f = canvas.astype(np.float32)
    lo, hi = np.percentile(f[::4, ::4], [1, 99.5])
    if hi - lo < 10: hi = lo + 10
    f = np.clip((f - lo) / (hi - lo), 0, 1) ** gamma
    return (f * 255).astype(np.uint8)
```

处理流程：`scene_fn() → tonemap() → FeedbackBuffer → ShaderChain → ffmpeg`

每场景 gamma 值：默认 0.75，曝光过度 0.55，色调分离 0.50，明亮场景 0.85。对于暗色图层，使用 `screen` 混合模式（不要用 `overlay`）。

### 字体单元格高度 {#font-cell-height}

macOS 上的 Pillow：`textbbox()` 返回的高度不正确。请使用 `font.getmetrics()`：`cell_height = ascent + descent`。参见 `references/troubleshooting.md`。

### ffmpeg 管道死锁 {#ffmpeg-pipe-deadlock}

对于长时间运行的 ffmpeg，切勿使用 `stderr=subprocess.PIPE`——缓冲区在 64KB 时会填满并导致死锁。请重定向到文件。参见 `references/troubleshooting.md`。

### 字体兼容性 {#font-compatibility}

并非所有 Unicode 字符在所有字体中都能正确渲染。请在初始化时验证调色板——渲染每个字符，检查输出是否为空。参见 `references/troubleshooting.md`。

### 按片段架构 {#per-clip-architecture}

对于分段视频（引文、场景、章节），将每个片段渲染为独立的剪辑文件，以便并行渲染和选择性重新渲染。参见 `references/scenes.md`。

## 性能目标 {#performance-targets}

| 组件 | 预算 |
|-----------|--------|
| 特征提取 | 1-5ms |
| 效果函数 | 2-15ms |
| 字符渲染 | 80-150ms（瓶颈） |
| 着色器管线 | 5-25ms |
| **总计** | ~100-200ms/帧 |

## 参考文档 {#references}

| 文件 | 内容 |
|------|----------|
| `references/architecture.md` | 网格系统、分辨率预设、字体选择、字符调色板（20+）、色彩系统（HSV + OKLAB + 离散 RGB + 和谐生成）、`_render_vf()` 辅助函数、GridLayer 类 |
| `references/composition.md` | 像素混合模式（20 种）、`blend_canvas()`、多网格合成、自适应 `tonemap()`、`FeedbackBuffer`、`PixelBlendStack`、遮罩/模板系统 |
| `references/effects.md` | 效果构建块：值场生成器、色相场、噪声/fBM/域扭曲、沃罗诺伊图、反应扩散、元胞自动机、SDF、奇异吸引子、粒子系统、坐标变换、时间一致性 |
| `references/shaders.md` | `ShaderChain`、`_apply_shader_step()` 调度、38 种着色器目录、音频响应缩放、转场、色调预设、输出格式编码、终端渲染 |
| `references/scenes.md` | 场景协议、`Renderer` 类、`SCENES` 表、`render_clip()`、节拍同步剪辑、并行渲染、设计模式（图层层次、方向弧线、视觉隐喻、合成技巧）、各复杂度级别的完整场景示例、场景设计检查清单 |
| `references/inputs.md` | 音频分析（FFT、频带、节拍）、视频采样、图像转换、文本/歌词、TTS 集成（ElevenLabs、语音分配、音频混合） |
| `references/optimization.md` | 硬件检测、质量配置、向量化模式、并行渲染、内存管理、性能预算 |
| `references/troubleshooting.md` | NumPy 广播陷阱、混合模式陷阱、多进程/序列化、亮度诊断、ffmpeg 问题、字体问题、常见错误 |
---

## 创意发散（仅在用户要求实验性/创意性/独特输出时使用） {#creative-divergence-use-only-when-user-requests-experimental-creative-unique-output}

如果用户要求创意性、实验性、令人惊喜或非传统的输出，请先选择最合适的策略，并在生成代码之前逐步推理其步骤。

- **强制连接** — 当用户想要跨领域灵感时（"让它看起来有机"，"工业美学"）
- **概念融合** — 当用户指定两个事物进行组合时（"海洋遇见音乐"，"太空+书法"）
- **侧向策略** — 当用户完全开放时（"给我惊喜"，"我从未见过的东西"）

### 强制连接 {#forced-connections}
1. 选择一个与视觉目标无关的领域（天气系统、微生物学、建筑学、流体动力学、纺织编织）
2. 列出其核心视觉/结构元素（侵蚀→逐渐显现；有丝分裂→分裂复制；编织→互锁图案）
3. 将这些元素映射到 ASCII 字符和动画模式上
4. 综合思考——"侵蚀"或"结晶"在字符网格中看起来是什么样子？

### 概念融合 {#conceptual-blending}
1. 命名两个不同的视觉/概念空间（例如，海浪 + 乐谱）
2. 映射对应关系（波峰 = 高音，波谷 = 休止，泡沫 = 断奏）
3. 选择性融合——保留最有趣的映射，舍弃牵强的部分
4. 发展仅存在于融合中的涌现特性

### 侧向策略 {#oblique-strategies}
1. 抽取一条："将你的错误视为隐藏的意图" / "使用一个旧想法" / "你最亲密的朋友会怎么做？" / "强调缺陷" / "把它颠倒过来" / "只取一部分，而非全部" / "反转"
2. 根据当前的 ASCII 动画挑战解读该指令
3. 在编写代码之前，将侧向洞察应用于视觉设计
