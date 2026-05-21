---
title: "P5Js — p5"
sidebar_label: "P5Js"
description: "p5"
---

{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="p5js"></a>
# P5Js

p5.js 草图：生成艺术、着色器、交互、3D。

<a id="skill-metadata"></a>
## Skill 元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/p5js` |
| 版本 | `1.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `creative-coding`, `generative-art`, `p5js`, `canvas`, `interactive`, `visualization`, `webgl`, `shaders`, `animation` |
| 相关技能 | [`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时所看到的指令。
:::

<a id="p5-js-production-pipeline"></a>
# p5.js 生产管线

<a id="when-to-use"></a>
## 何时使用

当用户请求以下内容时使用：p5.js 草图、创意编程、生成艺术、交互式可视化、Canvas 动画、基于浏览器的视觉艺术、数据可视化、着色器效果，或任何 p5.js 项目。

<a id="what-s-inside"></a>
## 内部包含什么

使用 p5.js 实现交互式和生成式视觉艺术的生产管线。创建基于浏览器的草图、生成艺术、数据可视化、交互体验、3D 场景、音频响应式视觉特效以及动态图形——导出为 HTML、PNG、GIF、MP4 或 SVG。涵盖：2D/3D 渲染、噪声与粒子系统、流场、着色器（GLSL）、像素操作、动感文字、WebGL 场景、音频分析、鼠标/键盘交互，以及无头高分辨率导出。

<a id="creative-standard"></a>
## 创意标准

这是渲染在浏览器中的视觉艺术。画布是媒介，算法是画笔。

**在编写任何代码之前**，先阐述清楚创意概念。这件作品传达了什么？是什么让观众停下滚动？它与一个代码教程示例的区别在哪里？用户的提示只是一个起点——要用创意抱负去诠释它。

**首次渲染的卓越不容妥协。** 输出必须在首次加载时就视觉上引人注目。如果它看起来像 p5.js 教程练习、默认配置或“AI 生成的创意编程”，那它就是错的。在交付之前重新思考。

**超越参考词汇表。** 参考资料中的噪声函数、粒子系统、调色板和着色器效果只是一个起点词汇表。每个项目都要进行组合、叠加和创造。参考目录是颜料的调色板——由你来创作画作。

**主动发挥创意。** 如果用户要求“一个粒子系统”，那就交付一个具有涌现群聚行为、拖尾幽灵回声、调色板偏移景深雾效，以及背景呼吸噪声场的粒子系统。至少要包含一个用户没有要求但会欣赏的视觉细节。

**丰富、层次分明、经过深思熟虑。** 每一帧都值得观看。永远不要用纯白背景。永远要有构图层次。永远要有意图明确的颜色。永远要有只有凑近观察才能发现的微小细节。
**功能数量服从于美学统一性。** 所有元素必须服务于统一的视觉语言——共享色温、一致的描边粗细体系、协调的运动速度。一个有十种无关特效的草图，远不如三个彼此融合的效果来得精彩。

<a id="modes"></a>
## 模式

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **生成艺术** | 种子 / 参数 | 程序化视觉构图（静态或动画） | `references/visual-effects.md` |
| **数据可视化** | 数据集 / API | 交互式图表、图形、自定义数据展示 | `references/interaction.md` |
| **交互式体验** | 无（用户驱动） | 鼠标/键盘/触摸驱动的草图 | `references/interaction.md` |
| **动画 / 动态图形** | 时间线 / 分镜 | 时序动画、动态排版、转场 | `references/animation.md` |
| **3D 场景** | 概念描述 | WebGL 几何体、灯光、摄像机、材质 | `references/webgl-and-3d.md` |
| **图像处理** | 图像文件 | 像素操作、滤镜、马赛克、点彩画 | `references/visual-effects.md` § 像素操作 |
| **音频响应** | 音频文件 / 麦克风 | 声音驱动的生成式视觉 | `references/interaction.md` § 音频输入 |

<a id="stack"></a>
## 技术栈

每个项目一个独立的 HTML 文件，无需构建步骤。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | p5.js 1.11.3 (CDN) | 画布渲染、数学、变换、事件处理 |
| 3D | p5.js WebGL 模式 | 3D 几何体、摄像机、灯光、GLSL 着色器 |
| 音频 | p5.sound.js (CDN) | FFT 分析、振幅、麦克风输入、振荡器 |
| 导出 | 内置 `saveCanvas()` / `saveGif()` / `saveFrames()` | PNG、GIF、帧序列输出 |
| 捕获 | CCapture.js（可选） | 固定帧率视频捕获（WebM、GIF） |
| 无头 | Puppeteer + Node.js（可选） | 自动化高分辨率渲染，通过 ffmpeg 输出 MP4 |
| SVG | p5.js-svg 1.6.0（可选） | 适用于印刷的矢量输出——需要 p5.js 1.x |
| 自然媒介 | p5.brush（可选） | 水彩、炭笔、钢笔——需要 p5.js 2.x + WEBGL |
| 纹理 | p5.grain（可选） | 胶片颗粒、纹理叠加 |
| 字体 | Google Fonts / `loadFont()` | 通过 OTF/TTF/WOFF2 自定义字体 |

<a id="version-note"></a>
### 版本说明

**p5.js 1.x**（1.11.3）为默认版本——稳定、文档齐全、库兼容性最广。除非项目需要 2.x 功能，否则使用此版本。

**p5.js 2.x**（2.2+）新增：`async setup()` 替代 `preload()`、OKLCH/OKLAB 色彩模式、`splineVertex()`、着色器 `.modify()` API、可变字体、`textToContours()`、指针事件。p5.brush 需要此版本。参见 `references/core-api.md` § p5.js 2.0。

<a id="pipeline"></a>
## 流程

每个项目遵循相同的 6 个阶段：

```
CONCEPT → DESIGN → CODE → PREVIEW → EXPORT → VERIFY
```

1. **概念**——阐述创意愿景：情绪、色彩世界、运动词汇、独特之处
2. **设计**——选择模式、画布尺寸、交互模型、色彩系统、导出格式。将概念映射为技术决策
3. **编码**——编写单个 HTML 文件，内联 p5.js。结构：全局变量 → `preload()` → `setup()` → `draw()` → 辅助函数 → 类 → 事件处理程序
4. **预览**——在浏览器中打开，验证视觉质量。以目标分辨率测试。检查性能
5. **导出**——捕获输出：使用 `saveCanvas()` 导出 PNG，`saveGif()` 导出 GIF，`saveFrames()` + ffmpeg 导出 MP4，Puppeteer 用于无头批量导出
6. **验证**——输出是否与概念匹配？在预期的显示尺寸下是否具有视觉冲击力？你会将它装裱起来吗？
<a id="creative-direction"></a>
## 创意方向

<a id="aesthetic-dimensions"></a>
### 美学维度

| 维度 | 选项 | 参考 |
|-----------|---------|-----------|
| **色彩系统** | HSB/HSL, RGB, 命名调色板, 程序化和谐, 渐变插值 | `references/color-systems.md` |
| **噪声词汇** | Perlin 噪声, 单纯形噪声, 分形 (八度叠加), 域扭曲, 旋度噪声 | `references/visual-effects.md` § 噪声 |
| **粒子系统** | 基于物理, 集群, 拖尾绘制, 吸引子驱动, 流场跟随 | `references/visual-effects.md` § 粒子 |
| **形状语言** | 几何图元, 自定义顶点, 贝塞尔曲线, SVG 路径 | `references/shapes-and-geometry.md` |
| **运动风格** | 缓动, 弹簧式, 噪声驱动, 物理模拟, 线性插值, 步进式 | `references/animation.md` |
| **字体排版** | 系统字体, 加载的 OTF, `textToPoints()` 粒子文字, 动态 | `references/typography.md` |
| **着色器效果** | GLSL 片元/顶点着色器, 滤镜着色器, 后处理, 反馈循环 | `references/webgl-and-3d.md` § 着色器 |
| **构图** | 网格, 径向, 黄金比例, 三分法, 有机散落, 平铺 | `references/core-api.md` § 构图 |
| **交互模式** | 鼠标跟随, 点击生成, 拖拽, 键盘状态, 滚动驱动, 麦克风输入 | `references/interaction.md` |
| **混合模式** | `BLEND`, `ADD`, `MULTIPLY`, `SCREEN`, `DIFFERENCE`, `EXCLUSION`, `OVERLAY` | `references/color-systems.md` § 混合模式 |
| **分层** | `createGraphics()` 离屏缓冲区, Alpha 合成, 遮罩 | `references/core-api.md` § 离屏缓冲区 |
| **纹理** | Perlin 表面, 点画法, 排线法, 半色调, 像素排序 | `references/visual-effects.md` § 纹理生成 |

<a id="per-project-variation-rules"></a>
### 单个项目的变异规则

永远不要使用默认配置。对于每个项目：
- **自定义调色板** —— 不要直接写 `fill(255, 0, 0)`。始终使用设计好的 3–7 色调色板
- **自定义描边粗细词汇表** —— 细线强调 (0.5), 中等结构 (1–2), 粗体强调 (3–5)
- **背景处理** —— 不要直接写 `background(0)` 或 `background(255)`。始终使用纹理、渐变或分层背景
- **运动多样性** —— 不同元素使用不同速度。主要元素 1x, 次要元素 0.3x, 环境元素 0.1x
- **至少一个自创元素** —— 自定义粒子行为、新颖的噪声应用、独特的交互响应

<a id="project-specific-invention"></a>
### 项目专属创新

对于每个项目，至少创新以下内容之一：
- 与氛围匹配的自定义调色板（非预设）
- 新颖的噪声场组合（例如，旋度噪声 + 域扭曲 + 反馈）
- 独特的粒子行为（自定义力、自定义拖尾、自定义生成）
- 用户未要求但能提升作品档次的交互机制
- 能创造视觉层次感的构图技巧

<a id="parameter-design-philosophy"></a>
### 参数设计哲学

参数应从算法中自然产生，而不是来自通用菜单。提问：“这个系统的哪些属性应该可调？”

**好的参数**能够展现算法的特色：
- **数量** —— 粒子数、分支数、网格数（控制密度）
- **尺度** —— 噪声频率、元素大小、间距（控制纹理）
- **速率** —— 速度、生长速率、衰减（控制能量）
- **阈值** —— 行为何时改变？（控制戏剧性）
- **比例** —— 各元素的比例、力之间的平衡（控制和谐）
**坏参数** 是与算法无关的通用控件：
- `"color1"`、`"color2"`、`"size"`——没有上下文则毫无意义
- 与效果无关的开关切换
- 仅改变视觉效果而不改变行为的参数

每个参数都应该改变算法的思维*方式*，而不仅仅是它的*外观*。一个改变噪声倍频程的“湍流”参数是好的。一个只改变 `ellipse()` 半径的“粒子大小”滑块则是浅层的。

<a id="workflow"></a>
## 工作流

<a id="step-1-creative-vision"></a>
### 第 1 步：创意愿景

在任何代码之前，先明确：

- **情绪 / 氛围**：观看者应该感受到什么？沉思？充满活力？不安？有趣？
- **视觉故事**：随着时间的推移（或交互）会发生什么？构建？衰退？变换？振荡？
- **色彩世界**：暖色/冷色？单色？互补？主色调是什么？强调色是什么？
- **形状语言**：有机曲线？锐利几何？点？线？混合？
- **动词语汇**：缓慢漂移？爆发式扩散？呼吸脉冲？机械精确？
- **什么让这个作品与众不同**：是什么让这个草图独一无二？

将用户的提示映射到审美选择。“放松的生成背景”和“故障数据可视化”的要求完全不同。

<a id="step-2-technical-design"></a>
### 第 2 步：技术设计

- **模式** —— 上表中 7 种模式中的哪一种
- **画布大小** —— 横向 1920×1080、纵向 1080×1920、方形 1080×1080 或响应式 `windowWidth/windowHeight`
- **渲染器** —— `P2D`（默认）或 `WEBGL`（用于 3D、着色器、高级混合模式）
- **帧率** —— 60fps（交互式）、30fps（环境动画）或 `noLoop()`（静态生成）
- **导出目标** —— 浏览器显示、PNG 截图、GIF 循环、MP4 视频、SVG 矢量
- **交互模型** —— 被动（无输入）、鼠标驱动、键盘驱动、音频响应、滚动驱动
- **观众 UI** —— 对于交互式生成艺术，从 `templates/viewer.html` 开始，它提供种子导航、参数滑块和下载。对于简单草图或视频导出，使用纯 HTML

<a id="step-3-code-the-sketch"></a>
### 第 3 步：编写草图代码

对于**交互式生成艺术**（种子探索、参数调整）：从 `templates/viewer.html` 开始。先阅读模板，保留固定部分（种子导航、操作），替换算法和参数控件。这将为用户提供种子前后/随机/跳转导航、带实时更新的参数滑块以及 PNG 下载——全部已连接好。

对于**动画、视频导出或简单草图**：使用纯 HTML：

单个 HTML 文件。结构如下：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>项目名称</title>
  <script>p5.disableFriendlyErrors = true;</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/addons/p5.sound.min.js"></script> -->
  <!-- <script src="https://unpkg.com/p5.js-svg@1.6.0"></script> -->  <!-- SVG 导出 -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script> -->  <!-- 视频捕获 -->
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
// === 配置 ===
const CONFIG = {
  seed: 42,
  // ... 项目特定参数
};

// === 调色板 ===
const PALETTE = {
  bg: '#0a0a0f',
  primary: '#e8d5b7',
  // ...
};

// === 全局状态 ===
let particles = [];

// === 预加载（字体、图像、数据） ===
function preload() {
  // font = loadFont('...');
}

// === 设置 ===
function setup() {
  createCanvas(1920, 1080);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  colorMode(HSB, 360, 100, 100, 100);
  // 初始化状态...
}

// === 绘制循环 ===
function draw() {
  // 渲染帧...
}

// === 辅助函数 ===
// ...

// === 类 ===
class Particle {
  // ...
}

// === 事件处理 ===
function mousePressed() { /* ... */ }
function keyPressed() { /* ... */ }
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```
关键实现模式：
- **种子随机性**：始终使用 `randomSeed()` + `noiseSeed()` 保证可复现性
- **色彩模式**：使用 `colorMode(HSB, 360, 100, 100, 100)` 实现直观的颜色控制
- **状态分离**：用 CONFIG 管理参数，PALETTE 管理颜色，全局变量管理可变状态
- **基于类的实体**：粒子、Agent、形状等作为类，包含 `update()` + `display()` 方法
- **离屏缓冲区**：使用 `createGraphics()` 实现分层合成、拖尾和遮罩

<a id="step-4-preview-iterate"></a>
### 步骤 4：预览与迭代

- 直接在浏览器中打开 HTML 文件 —— 基础草图无需服务器
- 从本地文件加载 `loadImage()`/`loadFont()` 时，使用 `scripts/serve.sh` 或 `python3 -m http.server`
- 使用 Chrome 开发者工具 Performance 面板验证 60fps
- 在目标导出分辨率下测试，而非仅窗口大小
- 调整参数直到视觉效果符合步骤 1 中的构思

<a id="step-5-export"></a>
### 步骤 5：导出

| 格式 | 方法 | 命令 |
|--------|--------|---------|
| **PNG** | 在 `keyPressed()` 中使用 `saveCanvas('output', 'png')` | 按 's' 保存 |
| **高分辨率 PNG** | Puppeteer 无头截图 | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| **GIF** | `saveGif('output', 5)` —— 捕获 N 秒 | 按 'g' 保存 |
| **帧序列** | `saveFrames('frame', 'png', 10, 30)` —— 10 秒 30fps | 然后 `ffmpeg -i frame-%04d.png -c:v libx264 output.mp4` |
| **MP4** | Puppeteer 帧捕获 + ffmpeg | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| **SVG** | 使用 p5.js-svg 的 `createCanvas(w, h, SVG)` | `save('output.svg')` |

<a id="step-6-quality-verification"></a>
### 步骤 6：质量验证

- **是否符合预期？** 将输出与创意构思对比。如果看起来过于普通，回到步骤 1
- **分辨率检查**：在目标显示尺寸下是否清晰？有无锯齿伪影？
- **性能检查**：在浏览器中能否保持 60fps？（动画至少 30fps）
- **色彩检查**：颜色是否协调？同时在亮色和暗色显示器上测试
- **边缘情况**：画布边缘会发生什么？调整大小时呢？运行 10 分钟后呢？

<a id="critical-implementation-notes"></a>
## 关键实现说明

<a id="performance-disable-fes-first"></a>
### 性能 —— 先禁用 FES

友好错误系统（FES）会带来最多 10 倍的开销。在每个生产用草图中禁用：

```javascript
p5.disableFriendlyErrors = true;  // 必须在 setup() 之前

function setup() {
  pixelDensity(1);  // 防止 retina 屏上 2x-4x 过度绘制
  createCanvas(1920, 1080);
}
```

在热点循环（粒子、像素运算）中，使用 `Math.*` 替代 p5 封装 —— 性能提升可测量：

```javascript
// 在 draw() 或 update() 热点路径中：
let a = Math.sin(t);          // 不要用 sin(t)
let r = Math.sqrt(dx*dx+dy*dy); // 不要用 dist() —— 或者更好：跳过 sqrt，比较 magSq
let v = Math.random();        // 不要用 random() —— 当不需要种子时
let m = Math.min(a, b);       // 不要用 min(a, b)
```

永远不要在 `draw()` 中使用 `console.log()`。永远不要在 `draw()` 中操作 DOM。参见 `references/troubleshooting.md` § 性能。

<a id="seeded-randomness-always"></a>
### 种子随机性 —— 必须始终使用

每个生成式草图都必须可复现。相同的种子，相同的输出。
```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  // 所有 random() 和 noise() 调用现在都是确定性的
}
```

永远不要为生成内容使用 `Math.random()` —— 仅在性能关键的非视觉代码中使用。始终对视觉元素使用 `random()`。如果需要随机种子：`CONFIG.seed = floor(random(99999))`。

<a id="generative-art-platform-support-fxhash-art-blocks"></a>
### 生成艺术平台支持（fxhash / Art Blocks）

对于生成艺术平台，将 p5 的 PRNG 替换为平台的确定性随机：

```javascript
// fxhash 惯例
const SEED = $fx.hash;              // 每个铸造唯一
const rng = $fx.rand;               // 确定性 PRNG
$fx.features({ palette: 'warm', complexity: 'high' });

// 在 setup() 中：
randomSeed(SEED);   // 用于 p5 的 noise()
noiseSeed(SEED);

// 用 rng() 替代 random() 以实现平台确定性
let x = rng() * width;  // 代替 random(width)
```

参见 `references/export-pipeline.md` § 平台导出。

<a id="color-mode-use-hsb"></a>
### 颜色模式 —— 使用 HSB

对于生成艺术来说，HSB（色相、饱和度、明度）比 RGB 容易使用得多：

```javascript
colorMode(HSB, 360, 100, 100, 100);
// 现在：fill(色相, 饱和度, 明度, 透明度)
// 旋转色相：fill((baseHue + offset) % 360, 80, 90)
// 降低饱和度：fill(色相, sat * 0.3, 明度)
// 变暗：fill(色相, 饱和度, bri * 0.5)
```

永远不要硬编码原始 RGB 值。定义一个调色板对象，通过程序化方式衍生变体。参见 `references/color-systems.md`。

<a id="noise-multi-octave-not-raw"></a>
### 噪声 —— 多倍频程，而非原始

原始 `noise(x, y)` 看起来像平滑的斑块。叠加倍频程以获得自然纹理：

```javascript
function fbm(x, y, octaves = 4) {
  let val = 0, amp = 1, freq = 1, sum = 0;
  for (let i = 0; i < octaves; i++) {
    val += noise(x * freq, y * freq) * amp;
    sum += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return val / sum;
}
```

对于流动的有机形态，使用 **域扭曲（domain warping）**：将噪声输出作为噪声输入坐标反馈回去。参见 `references/visual-effects.md`。

<a id="creategraphics-for-layers-not-optional"></a>
### createGraphics() 用于图层 —— 不是可选项

单次通渲染是扁平的。使用离屏缓冲区进行合成：

```javascript
let bgLayer, fgLayer, trailLayer;
function setup() {
  createCanvas(1920, 1080);
  bgLayer = createGraphics(width, height);
  fgLayer = createGraphics(width, height);
  trailLayer = createGraphics(width, height);
}
function draw() {
  renderBackground(bgLayer);
  renderTrails(trailLayer);   // 持久、淡出
  renderForeground(fgLayer);  // 每帧清除
  image(bgLayer, 0, 0);
  image(trailLayer, 0, 0);
  image(fgLayer, 0, 0);
}
```

<a id="performance-vectorize-where-possible"></a>
### 性能 —— 尽可能向量化

p5.js 的绘图调用开销很大。对于数千个粒子：

```javascript
// 慢：单独的形状
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// 快：使用 beginShape() 的单个形状
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// 最快：大量粒子时使用像素缓冲区
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 255;
}
updatePixels();
```
--- BEGIN TRANSLATED CHUNK ---

参见 `references/troubleshooting.md` § 性能。

<a id="instance-mode-for-multiple-sketches"></a>
### 多草稿的实例模式

全局模式会污染 `window`。生产环境应使用实例模式：

```javascript
const sketch = (p) => {
  p.setup = function() {
    p.createCanvas(800, 800);
  };
  p.draw = function() {
    p.background(0);
    p.ellipse(p.mouseX, p.mouseY, 50);
  };
};
new p5(sketch, 'canvas-container');
```

当需要在一页上嵌入多个草稿或与框架集成时必用。

<a id="webgl-mode-gotchas"></a>
### WebGL 模式注意事项

- `createCanvas(w, h, WEBGL)` —— 原点在中心，而非左上角
- Y 轴反转（WEBGL 中正 Y 向上，P2D 中正 Y 向下）
- 使用 `translate(-width/2, -height/2)` 获得类似 P2D 的坐标
- 每次变换都用 `push()`/`pop()` 包裹——矩阵栈会无声溢出
- `texture()` 必须在 `rect()`/`plane()` 之前调用，而非之后
- 自定义着色器：`createShader(vert, frag)` —— 在多个浏览器中测试

<a id="export-key-bindings-convention"></a>
### 导出——键绑定约定

每个草稿都应在 `keyPressed()` 中包含以下内容：

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === 'r' || key === 'R') { randomSeed(millis()); noiseSeed(millis()); }
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

<a id="headless-video-export-use-noloop"></a>
### 无头视频导出——使用 `noLoop()`

通过 Puppeteer 进行无头渲染时，草稿**必须**在 setup 中使用 `noLoop()`。若不加，p5 的 draw 循环会自由运行，而截图却缓慢——草稿会超前运行，导致跳过或重复帧。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // 捕获脚本控制帧前进
  window._p5Ready = true;      // 向捕获脚本发出就绪信号
}
```

附带的 `scripts/export-frames.js` 会检测 `_p5Ready`，并在每次捕获时调用 `redraw()`，实现精确的 1:1 帧对应。参见 `references/export-pipeline.md` § 确定性捕获。

对于多场景视频，请使用逐片段架构：每个场景一个 HTML，独立渲染，然后用 `ffmpeg -f concat` 拼接。参见 `references/export-pipeline.md` § 逐片段架构。

<a id="agent-workflow"></a>
### Agent 工作流

构建 p5.js 草稿时：

1. **编写 HTML 文件** —— 单个自包含文件，所有代码内联
2. **在浏览器中打开** —— `open sketch.html`（macOS）或 `xdg-open sketch.html`（Linux）
3. **本地资源**（字体、图片）需要服务器：在项目目录下运行 `python3 -m http.server 8080`，然后打开 `http://localhost:8080/sketch.html`
4. **导出 PNG/GIF** —— 添加上述 `keyPressed()` 快捷键，告知用户按哪个键
5. **无头导出** —— `node scripts/export-frames.js sketch.html --frames 300` 用于自动捕获帧（草稿必须使用 `noLoop()` + `_p5Ready`）
6. **MP4 渲染** —— `bash scripts/render.sh sketch.html output.mp4 --duration 30`
7. **迭代优化** —— 编辑 HTML 文件，用户刷新浏览器即可看到变化
8. **按需加载参考** —— 在实现过程中使用 `skill_view(name="p5js", file_path="references/...")` 加载特定的参考文件

--- END TRANSLATED CHUNK ---
<a id="performance-targets"></a>
## 性能目标

| 指标 | 目标 |
|------|------|
| 帧率（交互式） | 持续 60fps |
| 帧率（动画导出） | 最低 30fps |
| 粒子数量（P2D 形状） | 5000–10000 个，60fps |
| 粒子数量（像素缓冲区） | 50000–100000 个，60fps |
| 画布分辨率 | 高达 3840×2160（导出），1920×1080（交互式） |
| 文件大小（HTML） | < 100KB（不包括 CDN 库） |
| 加载时间 | < 2 秒显示第一帧 |

<a id="references"></a>
## 参考文档

| 文件 | 内容 |
|------|------|
| `references/core-api.md` | 画布设置、坐标系、绘制循环、`push()`/`pop()`、离屏缓冲区、组合模式、`pixelDensity()`、响应式设计 |
| `references/shapes-and-geometry.md` | 2D 图元、`beginShape()`/`endShape()`、贝塞尔/Catmull-Rom 曲线、`vertex()` 系统、自定义形状、`p5.Vector`、符号距离场、SVG 路径转换 |
| `references/visual-effects.md` | 噪声（Perlin、分形、域扭曲、旋度）、流场、粒子系统（物理、群集、轨迹）、像素操作、纹理生成（点画、影线、半色调）、反馈循环、反应扩散 |
| `references/animation.md` | 基于帧的动画、缓动函数、`lerp()`/`map()`、弹簧物理、状态机、时间轴序列、基于 `millis()` 的定时、过渡模式 |
| `references/typography.md` | `text()`、`loadFont()`、`textToPoints()`、动态文字、文字遮罩、字体度量、响应式文字大小 |
| `references/color-systems.md` | `colorMode()`、HSB/HSL/RGB、`lerpColor()`、`paletteLerp()`、程序化调色板、色彩和谐、`blendMode()`、渐变渲染、精选调色板库 |
| `references/webgl-and-3d.md` | WEBGL 渲染器、3D 图元、相机、光照、材质、自定义几何体、GLSL 着色器（`createShader()`、`createFilterShader()`）、帧缓冲、后处理 |
| `references/interaction.md` | 鼠标事件、键盘状态、触摸输入、DOM 元素、`createSlider()`/`createButton()`、音频输入（p5.sound FFT/振幅）、滚动驱动动画、响应式事件 |
| `references/export-pipeline.md` | `saveCanvas()`、`saveGif()`、`saveFrames()`、确定性无头捕获、ffmpeg 帧转视频、CCapture.js、SVG 导出、按片段架构、平台导出（fxhash）、视频注意事项 |
| `references/troubleshooting.md` | 性能剖析、每像素预算、常见错误、浏览器兼容性、WebGL 调试、字体加载问题、像素密度陷阱、内存泄漏、CORS |
| `templates/viewer.html` | 交互式查看器模板：种子导航（上一步/下一步/随机/跳转）、参数滑块、下载 PNG、响应式画布。可从该模板开始制作可探索的生成艺术 |

---

<a id="creative-divergence-use-only-when-user-requests-experimental-creative-unique-output"></a>
## 创意发散（仅当用户要求实验性/创意性/独特输出时使用）

如果用户要求创意、实验性、令人惊喜或非传统的输出，请先选择最合适的策略，并在生成代码之前逐步推理。

- **概念混合** — 当用户提到两个需要结合的事物，或希望获得混合美学时
- **SCAMPER** — 当用户希望在一个已知的生成艺术模式上做出改变时
- **远距离联想** — 当用户给出一个单一概念并希望进行探索时（例如“创作一些关于时间的东西”）
<a id="conceptual-blending"></a>
### 概念融合
1. 命名两个不同的视觉系统（例如，粒子物理 + 手写）
2. 映射对应关系（粒子 = 墨滴，力 = 笔压，场 = 字形）
3. 选择性融合——仅保留那些能产生有趣涌现视觉效果的映射
4. 将融合编码为一个统一的系统，而非两个系统并列

<a id="scamper-transformation"></a>
### SCAMPER 变换
选取一个已知的生成模式（流场、粒子系统、L-system、元胞自动机）并系统性地进行变换：
- **替代**：用文字字符替换圆形，用渐变替换线条
- **组合**：将两个模式合并（流场 + 沃罗诺伊）
- **调整**：将2D模式应用于3D投影
- **修改**：夸张尺寸，扭曲坐标空间
- **改变用途**：将物理模拟用于排版，将排序算法用于颜色
- **消除**：移除网格，移除颜色，移除对称
- **反转**：反向运行模拟，反转参数空间

<a id="distance-association"></a>
### 远距离联想
1. 锚定于用户的概念（例如，“孤独”）
2. 在三个距离上生成联想：
   - 近距离（显而易见的）：空房间、单个人影、寂静
   - 中距离（有趣的）：鱼群中一条游错方向的鱼、没有通知的手机、地铁车厢间的缝隙
   - 远距离（抽象的）：素数、渐近曲线、凌晨三点的颜色
3. 发展那些中距离联想——它们具体到足以可视化，但又出乎意料到足够有趣
