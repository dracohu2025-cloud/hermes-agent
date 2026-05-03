---
title: "P5Js — p5"
sidebar_label: "P5Js"
description: "p5"
---

{/* 此页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# P5Js {#p5js}

p5.js 草图：生成艺术、着色器、交互、3D。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/p5js` |
| 版本 | `1.0.0` |
| 标签 | `creative-coding`, `generative-art`, `p5js`, `canvas`, `interactive`, `visualization`, `webgl`, `shaders`, `animation` |
| 相关技能 | [`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 看到的指令即为此内容。
:::

# p5.js 制作管线 {#p5-js-production-pipeline}

## 何时使用 {#when-to-use}

当用户需要以下内容时使用：p5.js 草图、创意编程、生成艺术、交互式可视化、画布动画、基于浏览器的视觉艺术、数据可视化、着色器效果，或任何 p5.js 项目。

## 包含什么 {#what-s-inside}

用于使用 p5.js 创建交互式与生成式视觉艺术的制作管线。可创建基于浏览器的草图、生成艺术、数据可视化、交互体验、3D 场景、音频响应式视觉以及动态图形——导出为 HTML、PNG、GIF、MP4 或 SVG 格式。涵盖：2D/3D 渲染、噪声与粒子系统、流场、着色器（GLSL）、像素操作、动态排版、WebGL 场景、音频分析、鼠标/键盘交互，以及无头高分辨率导出。

## 创意标准 {#creative-standard}

这是浏览器中呈现的视觉艺术。画布是媒介，算法是画笔。

**在写第一行代码之前**，请先阐述创意概念。这件作品传达了怎样的信息？是什么让观众停下滚动的动作？它与代码教程示例有何不同？用户的提示是一个起点——请带着创造性的抱负去诠释它。

**首帧即惊艳，没有商量余地。** 首次加载的输出必须在视觉上令人震撼。如果看起来像 p5.js 教程练习题、默认配置，或者是“AI 生成的创意编程”，那就错了。在交付前请重新思考。

**超越参考词汇。** 参考中的噪声函数、粒子系统、调色板和着色器效果只是入门词汇。对于每个项目，请组合、叠加并创造新内容。目录是颜料的调色板——你来创作画作。

**主动发挥创意。** 如果用户要求“一个粒子系统”，请交付一个具有涌现群集行为、拖尾幽灵残影、调色板深度雾效以及会呼吸的背景噪声场的粒子系统。至少包含一个用户没有要求但会欣赏的视觉细节。

**密集、有层次、经得起推敲。** 每一帧都应值得观看。绝不能使用平淡的白色背景。始终要有构图层次。始终有意图地使用颜色。始终有只会在近距离观察时才显现的微观细节。
**统一的美学胜过功能数量。** 所有元素必须服务于统一的视觉语言——共享色温、一致的描边粗细词汇、和谐的运动速度。一个包含十个无关效果的草图，不如一个只有三个但彼此协调的草图。

## 模式 {#modes}

| 模式 | 输入 | 输出 | 参考 |
|------|------|------|------|
| **生成艺术** | 种子 / 参数 | 程序化视觉构成（静态或动画） | `references/visual-effects.md` |
| **数据可视化** | 数据集 / API | 交互式图表、图形、自定义数据展示 | `references/interaction.md` |
| **交互式体验** | 无（用户驱动） | 鼠标/键盘/触控驱动的草图 | `references/interaction.md` |
| **动画 / 动态图形** | 时间线 / 故事板 | 定时序列、动态排版、过渡效果 | `references/animation.md` |
| **3D 场景** | 概念描述 | WebGL 几何体、光照、相机、材质 | `references/webgl-and-3d.md` |
| **图像处理** | 图像文件 | 像素操作、滤镜、马赛克、点彩画 | `references/visual-effects.md` § 像素操作 |
| **音频响应** | 音频文件 / 麦克风 | 声音驱动的生成式视觉 | `references/interaction.md` § 音频输入 |

## 技术栈 {#stack}

每个项目一个独立的 HTML 文件。无需构建步骤。

| 层 | 工具 | 用途 |
|----|------|------|
| 核心 | p5.js 1.11.3 (CDN) | 画布渲染、数学、变换、事件处理 |
| 3D | p5.js WebGL 模式 | 3D 几何体、相机、光照、GLSL 着色器 |
| 音频 | p5.sound.js (CDN) | FFT 分析、振幅、麦克风输入、振荡器 |
| 导出 | 内置 `saveCanvas()` / `saveGif()` / `saveFrames()` | PNG、GIF、帧序列输出 |
| 录制 | CCapture.js（可选） | 固定帧率视频录制（WebM、GIF） |
| 无头 | Puppeteer + Node.js（可选） | 自动高分辨率渲染，通过 ffmpeg 输出 MP4 |
| SVG | p5.js-svg 1.6.0（可选） | 用于打印的矢量输出——需要 p5.js 1.x |
| 自然媒介 | p5.brush（可选） | 水彩、炭笔、钢笔——需要 p5.js 2.x + WEBGL |
| 纹理 | p5.grain（可选） | 胶片颗粒、纹理叠加 |
| 字体 | Google Fonts / `loadFont()` | 通过 OTF/TTF/WOFF2 自定义排版 |

### 版本说明 {#version-note}

**p5.js 1.x**（1.11.3）是默认版本——稳定、文档完善、库兼容性最广。除非项目需要 2.x 的功能，否则使用此版本。

**p5.js 2.x**（2.2+）新增：`async setup()` 替代 `preload()`、OKLCH/OKLAB 颜色模式、`splineVertex()`、着色器 `.modify()` API、可变字体、`textToContours()`、指针事件。p5.brush 需要此版本。参见 `references/core-api.md` § p5.js 2.0。

## 流程 {#pipeline}

每个项目遵循相同的 6 阶段路径：

```
概念 → 设计 → 编码 → 预览 → 导出 → 验证
```

1. **概念** — 阐述创意愿景：情绪、色彩世界、运动词汇、独特之处
2. **设计** — 选择模式、画布尺寸、交互模型、色彩系统、导出格式。将概念映射到技术决策
3. **编码** — 编写包含内联 p5.js 的单个 HTML 文件。结构：全局变量 → `preload()` → `setup()` → `draw()` → 辅助函数 → 类 → 事件处理
4. **预览** — 在浏览器中打开，验证视觉质量。在目标分辨率下测试。检查性能
5. **导出** — 捕获输出：`saveCanvas()` 用于 PNG，`saveGif()` 用于 GIF，`saveFrames()` + ffmpeg 用于 MP4，Puppeteer 用于无头批量导出
6. **验证** — 输出是否符合概念？在预期的显示尺寸下是否视觉上引人注目？你会把它装裱起来吗？
## 创意方向 {#creative-direction}

### 美学维度 {#aesthetic-dimensions}

| 维度 | 选项 | 参考 |
|-----------|---------|-----------|
| **色彩系统** | HSB/HSL、RGB、命名调色板、程序化和谐、渐变插值 | `references/color-systems.md` |
| **噪声词汇** | Perlin噪声、单纯形噪声、分形（八度）噪声、域扭曲、旋度噪声 | `references/visual-effects.md` § 噪声 |
| **粒子系统** | 基于物理、群集、拖尾绘制、吸引子驱动、流场跟随 | `references/visual-effects.md` § 粒子 |
| **形状语言** | 几何图元、自定义顶点、贝塞尔曲线、SVG路径 | `references/shapes-and-geometry.md` |
| **运动风格** | 缓动、弹簧、噪声驱动、物理模拟、线性插值、步进 | `references/animation.md` |
| **排版** | 系统字体、加载的OTF、`textToPoints()` 粒子文字、动态 | `references/typography.md` |
| **着色器效果** | GLSL片段/顶点着色器、滤镜着色器、后处理、反馈循环 | `references/webgl-and-3d.md` § 着色器 |
| **构图** | 网格、径向、黄金比例、三分法、有机散布、平铺 | `references/core-api.md` § 构图 |
| **交互模型** | 鼠标跟随、点击生成、拖拽、键盘状态、滚动驱动、麦克风输入 | `references/interaction.md` |
| **混合模式** | `BLEND`、`ADD`、`MULTIPLY`、`SCREEN`、`DIFFERENCE`、`EXCLUSION`、`OVERLAY` | `references/color-systems.md` § 混合模式 |
| **分层** | `createGraphics()` 离屏缓冲区、Alpha合成、遮罩 | `references/core-api.md` § 离屏缓冲区 |
| **纹理** | Perlin表面、点画、影线、半色调、像素排序 | `references/visual-effects.md` § 纹理生成 |

### 每个项目的变体规则 {#per-project-variation-rules}

永远不要使用默认配置。对于每个项目：
- **自定义调色板** — 绝不使用原始的 `fill(255, 0, 0)`。始终使用包含 3-7 种颜色的设计调色板
- **自定义描边粗细词汇** — 细强调（0.5）、中等结构（1-2）、粗强调（3-5）
- **背景处理** — 绝不使用简单的 `background(0)` 或 `background(255)`。始终使用纹理、渐变或分层
- **运动多样性** — 不同元素使用不同速度。主要元素 1x，次要元素 0.3x，环境元素 0.1x
- **至少一个自创元素** — 自定义粒子行为、新颖的噪声应用、独特的交互响应

### 项目特定创新 {#project-specific-invention}

对于每个项目，至少自创以下一项：
- 与情绪匹配的自定义调色板（非预设）
- 新颖的噪声场组合（例如：旋度噪声 + 域扭曲 + 反馈）
- 独特的粒子行为（自定义力、自定义拖尾、自定义生成）
- 用户未要求但能提升作品档次的交互机制
- 能创造视觉层次的构图技巧

### 参数设计理念 {#parameter-design-philosophy}

参数应从算法中自然产生，而非来自通用菜单。问自己：“*这个*系统的哪些属性应该是可调的？”

**好的参数**能展现算法的特性：
- **数量** — 粒子数、分支数、细胞数（控制密度）
- **尺度** — 噪声频率、元素大小、间距（控制纹理）
- **速率** — 速度、生长率、衰减（控制能量）
- **阈值** — 行为何时改变？（控制戏剧性）
- **比例** — 比例、力之间的平衡（控制和谐）
**不良参数** 是与算法无关的通用控件：

- "color1"、"color2"、"size" —— 脱离上下文毫无意义
- 用于无关效果的开关按钮
- 只改变外观、不改变行为的参数

每个参数都应该改变算法的**思维方式**，而不仅仅是它的**外观**。一个能改变噪声倍频程的"湍流"参数是好的。一个只改变 `ellipse()` 半径的"粒子大小"滑块则过于浅薄。

## 工作流程 {#workflow}

### 第一步：创意构思 {#step-1-creative-vision}

在编写任何代码之前，先明确：

- **情绪/氛围**：观众应该感受到什么？沉思？精力充沛？不安？有趣？
- **视觉故事**：随时间推移（或与用户交互时）会发生什么？构建？衰退？变换？振荡？
- **色彩世界**：暖色/冷色？单色？互补色？主色调是什么？强调色是什么？
- **形态语言**：有机曲线？锐利几何形状？点？线？混合？
- **运动词汇**：缓慢漂移？爆炸式爆发？呼吸般的脉冲？机械式的精确？
- **独特之处**：是什么让这个草图与众不同？

将用户的提示映射到美学选择上。"放松的生成式背景"与"故障数据可视化"所需的一切都截然不同。

### 第二步：技术设计 {#step-2-technical-design}

- **模式** —— 上表 7 种模式中的哪一种
- **画布尺寸** —— 横屏 1920x1080、竖屏 1080x1920、方形 1080x1080，或响应式 `windowWidth/windowHeight`
- **渲染器** —— `P2D`（默认）或 `WEBGL`（用于 3D、着色器、高级混合模式）
- **帧率** —— 60fps（交互式）、30fps（环境动画），或 `noLoop()`（静态生成）
- **导出目标** —— 浏览器显示、PNG 静态图片、GIF 循环、MP4 视频、SVG 矢量
- **交互模型** —— 被动（无输入）、鼠标驱动、键盘驱动、音频响应、滚动驱动
- **查看器 UI** —— 对于交互式生成艺术，从 `templates/viewer.html` 开始，该模板提供种子导航、参数滑块和下载功能。对于简单草图或视频导出，使用纯 HTML

### 第三步：编写草图 {#step-3-code-the-sketch}

对于**交互式生成艺术**（种子探索、参数调优）：从 `templates/viewer.html` 开始。先阅读模板，保留固定部分（种子导航、操作），替换算法和参数控件。这将为用户提供种子上一个/下一个/随机/跳转、带实时更新的参数滑块以及 PNG 下载——均已接线完成。

对于**动画、视频导出或简单草图**：使用纯 HTML：

单个 HTML 文件。结构：

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
  <!-- <script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script> -->  <!-- 视频录制 -->
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

// === 预加载（字体、图片、数据） ===
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

// === 事件处理器 ===
function mousePressed() { /* ... */ }
function keyPressed() { /* ... */ }
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```
关键实现模式：
- **种子随机性**：始终使用 `randomSeed()` + `noiseSeed()` 以确保可复现性
- **色彩模式**：使用 `colorMode(HSB, 360, 100, 100, 100)` 实现直观的色彩控制
- **状态分离**：CONFIG 存放参数，PALETTE 存放颜色，全局变量存放可变状态
- **基于类的实体**：粒子、Agent、形状等作为类，包含 `update()` + `display()` 方法
- **离屏缓冲区**：使用 `createGraphics()` 实现分层合成、轨迹、遮罩

### 第 4 步：预览与迭代 {#step-4-preview-iterate}

- 直接在浏览器中打开 HTML 文件——基础草图无需服务器
- 如需从本地文件加载 `loadImage()`/`loadFont()`：使用 `scripts/serve.sh` 或 `python3 -m http.server`
- 使用 Chrome DevTools 的 Performance 面板验证 60fps
- 在目标导出分辨率下测试，而不仅仅是窗口大小
- 调整参数，直到视觉效果符合第 1 步的概念

### 第 5 步：导出 {#step-5-export}

| 格式 | 方法 | 命令 |
|--------|--------|---------|
| **PNG** | 在 `keyPressed()` 中调用 `saveCanvas('output', 'png')` | 按 's' 键保存 |
| **高分辨率 PNG** | Puppeteer 无头截图 | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| **GIF** | `saveGif('output', 5)` — 捕获 N 秒 | 按 'g' 键保存 |
| **帧序列** | `saveFrames('frame', 'png', 10, 30)` — 10 秒，30fps | 然后 `ffmpeg -i frame-%04d.png -c:v libx264 output.mp4` |
| **MP4** | Puppeteer 帧捕获 + ffmpeg | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| **SVG** | 使用 p5.js-svg 的 `createCanvas(w, h, SVG)` | `save('output.svg')` |

### 第 6 步：质量验证 {#step-6-quality-verification}

- **是否符合预期？** 将输出与创意概念对比。如果看起来平庸，返回第 1 步
- **分辨率检查**：在目标显示尺寸下是否清晰？有无锯齿伪影？
- **性能检查**：在浏览器中能否保持 60fps？（动画至少 30fps）
- **色彩检查**：颜色搭配是否协调？在亮色和暗色显示器上分别测试
- **边界情况**：画布边缘会发生什么？调整大小时？运行 10 分钟后？

## 关键实现说明 {#critical-implementation-notes}

### 性能——首先禁用 FES {#performance-disable-fes-first}

友好错误系统（FES）会带来高达 10 倍的开销。在每个生产草图中禁用它：

```javascript
p5.disableFriendlyErrors = true;  // 在 setup() 之前

function setup() {
  pixelDensity(1);  // 防止 retina 屏幕 2x-4x 过度绘制
  createCanvas(1920, 1080);
}
```

在热循环（粒子、像素操作）中，使用 `Math.*` 代替 p5 包装函数——速度明显更快：

```javascript
// 在 draw() 或 update() 的热路径中：
let a = Math.sin(t);          // 不要用 sin(t)
let r = Math.sqrt(dx*dx+dy*dy); // 不要用 dist()——或者更好：跳过 sqrt，比较 magSq
let v = Math.random();        // 不要用 random()——当不需要种子时
let m = Math.min(a, b);       // 不要用 min(a, b)
```

永远不要在 `draw()` 中调用 `console.log()`。永远不要在 `draw()` 中操作 DOM。参见 `references/troubleshooting.md` § 性能。

### 种子随机性——始终如此 {#seeded-randomness-always}

每个生成式草图都必须可复现。相同的种子，相同的输出。
```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  // 所有 random() 和 noise() 调用现在都是确定性的
}
```

对于生成式内容，永远不要使用 `Math.random()` —— 它只适用于非视觉的性能关键型代码。视觉元素始终使用 `random()`。如果需要随机种子：`CONFIG.seed = floor(random(99999))`。

### 生成式艺术平台支持（fxhash / Art Blocks） {#generative-art-platform-support-fxhash-art-blocks}

对于生成式艺术平台，将 p5 的伪随机数生成器替换为平台的确定性随机数生成器：

```javascript
// fxhash 约定
const SEED = $fx.hash;              // 每个铸造品唯一
const rng = $fx.rand;               // 确定性伪随机数生成器
$fx.features({ palette: 'warm', complexity: 'high' });

// 在 setup() 中：
randomSeed(SEED);   // 用于 p5 的 noise()
noiseSeed(SEED);

// 用 rng() 替换 random() 以实现平台确定性
let x = rng() * width;  // 替代 random(width)
```

参见 `references/export-pipeline.md` § 平台导出。

### 色彩模式 —— 使用 HSB {#color-mode-use-hsb}

对于生成式艺术，HSB（色相、饱和度、明度）比 RGB 容易处理得多：

```javascript
colorMode(HSB, 360, 100, 100, 100);
// 现在：fill(色相, 饱和度, 明度, 透明度)
// 旋转色相：fill((baseHue + offset) % 360, 80, 90)
// 降低饱和度：fill(色相, 饱和度 * 0.3, 明度)
// 变暗：fill(色相, 饱和度, 明度 * 0.5)
```

永远不要硬编码原始 RGB 值。定义一个调色板对象，通过程序化方式派生变体。参见 `references/color-systems.md`。

### 噪声 —— 多倍频程，而非原始值 {#noise-multi-octave-not-raw}

原始的 `noise(x, y)` 看起来像平滑的斑点。叠加倍频程以获得自然纹理：

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

对于流动的有机形态，使用**域扭曲**：将噪声输出作为噪声输入坐标反馈回去。参见 `references/visual-effects.md`。

### createGraphics() 用于图层 —— 非可选 {#creategraphics-for-layers-not-optional}

单次平铺渲染看起来平淡无奇。使用离屏缓冲区进行合成：

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
  renderTrails(trailLayer);   // 持久，渐隐
  renderForeground(fgLayer);  // 每帧清除
  image(bgLayer, 0, 0);
  image(trailLayer, 0, 0);
  image(fgLayer, 0, 0);
}
```

### 性能 —— 尽可能向量化 {#performance-vectorize-where-possible}

p5.js 的绘制调用开销很大。对于数千个粒子：

```javascript
// 慢：逐个形状
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// 快：使用 beginShape() 的单个形状
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// 最快：用于大量计数的像素缓冲区
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 255;
}
updatePixels();
```
参见 `references/troubleshooting.md` § 性能。

### 多草图实例模式 {#instance-mode-for-multiple-sketches}

全局模式会污染 `window`。生产环境请使用实例模式：

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

当在一个页面中嵌入多个草图或与框架集成时需要使用此模式。

### WebGL 模式注意事项 {#webgl-mode-gotchas}

- `createCanvas(w, h, WEBGL)` — 原点在中心，而非左上角
- Y 轴是反向的（在 WEBGL 中 Y 轴正方向向上，在 P2D 中向下）
- 使用 `translate(-width/2, -height/2)` 获得类似 P2D 的坐标
- 每次变换都要使用 `push()`/`pop()` — 矩阵栈会静默溢出
- `texture()` 必须在 `rect()`/`plane()` 之前调用 — 不能之后
- 自定义着色器：`createShader(vert, frag)` — 在多个浏览器上测试

### 导出 — 按键绑定约定 {#export-key-bindings-convention}

每个草图都应在 `keyPressed()` 中包含以下内容：

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === 'r' || key === 'R') { randomSeed(millis()); noiseSeed(millis()); }
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

### 无头视频导出 — 使用 noLoop() {#headless-video-export-use-noloop}

对于通过 Puppeteer 进行的无头渲染，草图**必须**在 setup 中使用 `noLoop()`。如果不这样做，p5 的 draw 循环会自由运行，而截图速度很慢 — 草图会超前运行，导致帧被跳过或重复。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // 捕获脚本控制帧推进
  window._p5Ready = true;      // 向捕获脚本发出就绪信号
}
```

捆绑的 `scripts/export-frames.js` 会检测 `_p5Ready`，并在每次捕获时调用一次 `redraw()`，以实现精确的 1:1 帧对应。参见 `references/export-pipeline.md` § 确定性捕获。

对于多场景视频，请使用每片段架构：每个场景一个 HTML，独立渲染，使用 `ffmpeg -f concat` 拼接。参见 `references/export-pipeline.md` § 每片段架构。

### Agent 工作流程 {#agent-workflow}

在构建 p5.js 草图时：

1. **编写 HTML 文件** — 单个自包含文件，所有代码内联
2. **在浏览器中打开** — `open sketch.html`（macOS）或 `xdg-open sketch.html`（Linux）
3. **本地资源**（字体、图片）需要服务器：在项目目录中运行 `python3 -m http.server 8080`，然后打开 `http://localhost:8080/sketch.html`
4. **导出 PNG/GIF** — 添加上面所示的 `keyPressed()` 快捷键，并告知用户按哪个键
5. **无头导出** — `node scripts/export-frames.js sketch.html --frames 300` 用于自动帧捕获（草图必须使用 `noLoop()` + `_p5Ready`）
6. **MP4 渲染** — `bash scripts/render.sh sketch.html output.mp4 --duration 30`
7. **迭代优化** — 编辑 HTML 文件，用户刷新浏览器即可看到更改
8. **按需加载参考** — 在实现过程中使用 `skill_view(name="p5js", file_path="references/...")` 按需加载特定的参考文件
## 性能目标 {#performance-targets}

| 指标 | 目标 |
|--------|--------|
| 帧率（交互式） | 持续 60fps |
| 帧率（动画导出） | 最低 30fps |
| 粒子数量（P2D 形状） | 60fps 下 5,000–10,000 |
| 粒子数量（像素缓冲区） | 60fps 下 50,000–100,000 |
| 画布分辨率 | 最高 3840×2160（导出），1920×1080（交互式） |
| 文件大小（HTML） | &lt; 100KB（不含 CDN 库） |
| 加载时间 | 首帧 &lt; 2s |

## 参考文件 {#references}

| 文件 | 内容 |
|------|------|
| `references/core-api.md` | 画布设置、坐标系、绘制循环、`push()`/`pop()`、离屏缓冲区、合成模式、`pixelDensity()`、响应式设计 |
| `references/shapes-and-geometry.md` | 2D 基本图形、`beginShape()`/`endShape()`、贝塞尔/ Catmull-Rom 曲线、`vertex()` 系统、自定义形状、`p5.Vector`、有符号距离场、SVG 路径转换 |
| `references/visual-effects.md` | 噪声（Perlin、分形、域扭曲、旋度）、流场、粒子系统（物理、群集、轨迹）、像素操作、纹理生成（点画、影线、半色调）、反馈循环、反应扩散 |
| `references/animation.md` | 基于帧的动画、缓动函数、`lerp()`/`map()`、弹簧物理、状态机、时间线序列、基于 `millis()` 的计时、过渡模式 |
| `references/typography.md` | `text()`、`loadFont()`、`textToPoints()`、动态排版、文字遮罩、字体度量、响应式文字大小 |
| `references/color-systems.md` | `colorMode()`、HSB/HSL/RGB、`lerpColor()`、`paletteLerp()`、程序化调色板、色彩和谐、`blendMode()`、渐变渲染、精选调色板库 |
| `references/webgl-and-3d.md` | WEBGL 渲染器、3D 基本图形、相机、光照、材质、自定义几何体、GLSL 着色器（`createShader()`、`createFilterShader()`）、帧缓冲区、后期处理 |
| `references/interaction.md` | 鼠标事件、键盘状态、触摸输入、DOM 元素、`createSlider()`/`createButton()`、音频输入（p5.sound FFT/振幅）、滚动驱动动画、响应式事件 |
| `references/export-pipeline.md` | `saveCanvas()`、`saveGif()`、`saveFrames()`、确定性无头捕获、ffmpeg 帧转视频、CCapture.js、SVG 导出、逐片段架构、平台导出（fxhash）、视频注意事项 |
| `references/troubleshooting.md` | 性能分析、每像素预算、常见错误、浏览器兼容性、WebGL 调试、字体加载问题、像素密度陷阱、内存泄漏、CORS |
| `templates/viewer.html` | 交互式查看器模板：种子导航（上一个/下一个/随机/跳转）、参数滑块、下载 PNG、响应式画布。从该模板开始制作可探索的生成艺术 |

---

## 创意发散（仅在用户要求实验性/创意性/独特输出时使用） {#creative-divergence-use-only-when-user-requests-experimental-creative-unique-output}

如果用户要求创意性、实验性、令人惊喜或非传统的输出，请先选择最适合的策略，并在生成代码之前逐步推理其步骤。

- **概念融合** — 当用户提出两个要结合的事物或希望获得混合美学时
- **SCAMPER** — 当用户希望在一个已知的生成艺术模式上做出变体时
- **远距离联想** — 当用户给出单一概念并希望进行探索时（例如“做点关于时间的东西”）
### 概念融合（Conceptual Blending） {#conceptual-blending}
1. 命名两个不同的视觉系统（例如，粒子物理 + 手写）
2. 映射对应关系（粒子 = 墨滴，力 = 笔压，场 = 字形）
3. 选择性融合——只保留能产生有趣涌现视觉的映射
4. 将融合编码为一个统一的系统，而非两个系统并列

### SCAMPER 变换 {#scamper-transformation}
选取一个已知的生成模式（流场、粒子系统、L系统、细胞自动机），并系统性地对其进行变换：
- **替代（Substitute）**：用文字字符替换圆形，用渐变替换线条
- **组合（Combine）**：合并两种模式（流场 + Voronoi）
- **适配（Adapt）**：将二维模式应用于三维投影
- **修改（Modify）**：夸张比例，扭曲坐标空间
- **另作他用（Purpose）**：用物理模拟做排版，用排序算法做色彩
- **消除（Eliminate）**：移除网格，移除颜色，移除对称
- **反转（Reverse）**：反向运行模拟，反转参数空间

### 远距离联想（Distance Association） {#distance-association}
1. 锚定在用户的概念上（例如，“孤独”）
2. 在三个距离上生成联想：
   - 近（明显）：空房间、单独的人物、寂静
   - 中（有趣）：鱼群中一条游错方向的鱼、没有通知的手机、地铁车厢之间的缝隙
   - 远（抽象）：质数、渐近线、凌晨三点的颜色
3. 发展中等距离的联想——它们足够具体以可视化，但又足够意外而有趣
