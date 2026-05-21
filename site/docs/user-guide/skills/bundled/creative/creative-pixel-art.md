---
title: "像素艺术 — 带有时代调色板的像素艺术（NES、Game Boy、PICO-8）"
sidebar_label: "像素艺术"
description: "带有时代调色板的像素艺术（NES、Game Boy、PICO-8）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="pixel-art"></a>
# 像素艺术

带有时代调色板的像素艺术（NES、Game Boy、PICO-8）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pixel-art` |
| 版本 | `2.0.0` |
| 作者 | dodo-reach |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `pixel-art`, `arcade`, `snes`, `nes`, `gameboy`, `retro`, `image`, `video` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 像素艺术

将任何图像转换为复古像素艺术，然后可选择将其制作成带有时代特色效果（雨、萤火虫、雪、余烬）的短 MP4 或 GIF 动画。

此技能附带两个脚本：

- `scripts/pixel_art.py` — 照片 → 像素艺术 PNG（Floyd-Steinberg 抖动）
- `scripts/pixel_art_video.py` — 像素艺术 PNG → 动画 MP4（+ 可选 GIF）

每个脚本都可直接导入或运行。当你想要时代精确的颜色（NES、Game Boy、PICO-8 等）时，预设会锁定硬件调色板，或者使用自适应 N 色量化来实现街机/SNES 风格的外观。

<a id="when-to-use"></a>
## 何时使用

- 用户想要从源图像生成复古像素艺术
- 用户要求 NES / Game Boy / PICO-8 / C64 / 街机 / SNES 风格
- 用户想要一个短的循环动画（雨景、夜空、雪等）
- 海报、专辑封面、社交媒体帖子、精灵图、角色、头像

<a id="workflow"></a>
## 工作流程

在生成之前，先和用户确认风格。不同的预设会产生非常不同的输出，重新生成成本很高。

<a id="step-1-offer-a-style"></a>
### 步骤 1 — 提供一种风格

用 4 个代表性预设调用 `clarify`。根据用户要求的内容选择一组——不要一次性抛出全部 14 个。

当用户意图不明确时的默认菜单：

```python
clarify(
    question="你想要哪种像素艺术风格？",
    choices=[
        "街机 — 大胆、厚实的 80 年代机台风格（16 色，8px）",
        "nes — 任天堂 8 位硬件调色板（54 色，8px）",
        "gameboy — 4 种绿色的 Game Boy DMG 色调",
        "snes — 更清晰的 16 位外观（32 色，4px）",
    ],
)
```

当用户已经提到某个时代（例如“80 年代街机”、“Gameboy”）时，跳过 `clarify`，直接使用匹配的预设。

<a id="step-2-offer-animation-optional"></a>
### 步骤 2 — 提供动画（可选）

如果用户要求视频/GIF，或者输出可能因动态效果而更好，询问场景：

```python
clarify(
    question="想要让它动起来吗？选择一个场景或跳过。",
    choices=[
        "夜晚 — 星星 + 萤火虫 + 树叶",
        "都市 — 雨 + 霓虹脉冲",
        "雪 — 飘落的雪花",
        "跳过 — 仅图像",
    ],
)
```

不要连续调用 `clarify` 超过两次。一次用于风格，如果考虑动画则一次用于场景。如果用户在其消息中明确要求了特定风格和场景，则完全跳过 `clarify`。

<a id="step-3-generate"></a>
### 步骤 3 — 生成
先运行 `pixel_art()`；如果需要动画，则在其结果上链式调用 `pixel_art_video()`。

<a id="preset-catalog"></a>
## 预设目录

| 预设 | 时代 | 调色板 | 像素块 | 最佳用途 |
|--------|-----|---------|-------|----------|
| `arcade` | 80年代街机 | 自适应16色 | 8px | 粗体海报、主角艺术 |
| `snes` | 16位 | 自适应32色 | 4px | 角色、精细场景 |
| `nes` | 8位 | NES (54色) | 8px | 纯正NES风格 |
| `gameboy` | DMG掌机 | 4种绿色调 | 8px | 单色Game Boy |
| `gameboy_pocket` | Pocket掌机 | 4种灰色调 | 8px | 单色GB Pocket |
| `pico8` | PICO-8 | 16种固定色 | 6px | 幻想主机风格 |
| `c64` | Commodore 64 | 16种固定色 | 8px | 8位家用电脑 |
| `apple2` | Apple II高分辨率 | 6种固定色 | 10px | 极致复古，6色 |
| `teletext` | BBC图文电视 | 8种纯色 | 10px | 粗犷原色 |
| `mspaint` | Windows MS Paint | 24种固定色 | 8px | 怀旧桌面 |
| `mono_green` | CRT荧光粉 | 2种绿色 | 6px | 终端/CRT美学 |
| `mono_amber` | CRT琥珀色 | 2种琥珀色 | 6px | 琥珀色显示器风格 |
| `neon` | 赛博朋克 | 10种霓虹色 | 6px | 蒸汽波/赛博 |
| `pastel` | 柔和粉彩 | 10种粉彩色 | 6px | 可爱/温柔 |

命名调色板位于 `scripts/palettes.py` 中（完整列表见 `references/palettes.md` —— 共28个命名调色板）。任何预设都可以被覆盖：

```python
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
```

<a id="scene-catalog-for-video"></a>
## 场景目录（用于视频）

| 场景 | 效果 |
|-------|---------|
| `night` | 闪烁星星 + 萤火虫 + 飘落的叶子 |
| `dusk` | 萤火虫 + 闪光 |
| `tavern` | 尘埃微粒 + 温暖闪光 |
| `indoor` | 尘埃微粒 |
| `urban` | 雨 + 霓虹脉冲 |
| `nature` | 叶子 + 萤火虫 |
| `magic` | 闪光 + 萤火虫 |
| `storm` | 雨 + 闪电 |
| `underwater` | 气泡 + 柔和闪光 |
| `fire` | 余烬 + 闪光 |
| `snow` | 雪花 + 闪光 |
| `desert` | 热浪 + 尘土 |

<a id="invocation-patterns"></a>
## 调用模式

<a id="python-import"></a>
### Python（导入）

```python
import sys
sys.path.insert(0, "/home/teknium/.hermes/skills/creative/pixel-art/scripts")
from pixel_art import pixel_art
from pixel_art_video import pixel_art_video

# 1. 转换为像素艺术
pixel_art("/path/to/photo.jpg", "/tmp/pixel.png", preset="nes")

# 2. 动画（可选）
pixel_art_video(
    "/tmp/pixel.png",
    "/tmp/pixel.mp4",
    scene="night",
    duration=6,
    fps=15,
    seed=42,
    export_gif=True,
)
```

<a id="cli"></a>
### CLI

```bash
cd /home/teknium/.hermes/skills/creative/pixel-art/scripts

python pixel_art.py in.jpg out.png --preset gameboy
python pixel_art.py in.jpg out.png --preset snes --palette PICO_8 --block 6

python pixel_art_video.py out.png out.mp4 --scene night --duration 6 --gif
```

<a id="pipeline-rationale"></a>
## 流水线原理

**像素转换：**
1. 增强对比度/色彩/锐度（调色板越小，增强越强）
2. 色调分离，简化量化前的色调区域
3. 使用 `Image.NEAREST` 按 `block` 缩小（硬像素，无插值）
4. 使用 Floyd-Steinberg 抖动进行量化 —— 针对自适应 N 色调色板或命名硬件调色板
5. 使用 `Image.NEAREST` 放大回原尺寸
Quantizing AFTER downscale keeps dithering aligned with the final pixel grid.
Quantizing before would waste error-diffusion on detail that disappears.

**视频叠加：**
- 每帧复制基础画布（静态背景）
- 叠加每帧无状态粒子绘制（每个效果对应一个函数）
- 通过 ffmpeg `libx264 -pix_fmt yuv420p -crf 18` 编码
- 可选 GIF 方案：`palettegen` + `paletteuse`

<a id="dependencies"></a>
## 依赖

- Python 3.9+
- Pillow（`pip install Pillow`）
- ffmpeg 需在 PATH 中（仅视频需要——Hermes 会自动安装该包）

<a id="pitfalls"></a>
## 注意事项

- 调色板键名区分大小写（`"NES"`、`"PICO_8"`、`"GAMEBOY_ORIGINAL"`）
- 非常小的源图像（宽度 < 100px）会在 8-10px 的块下崩溃。如果源图像太小，请先放大。
- 小数形式的 `block` 或 `palette` 会破坏量化——请确保它们为正整数。
- 动画粒子数量针对 ~640x480 的画布调整。对于非常大的图像，可能需要使用不同的种子进行第二次传递以获得足够密度。
- `mono_green` / `mono_amber` 会强制 `color=0.0`（去饱和度）。如果覆盖并保留色度，双色调色板会在平滑区域产生条纹。
- `clarify` 循环：每轮最多调用两次（先样式，后场景）。不要让用户重复选择。

<a id="verification"></a>
## 验证

- 在输出路径生成 PNG
- 在预设的块大小下观察到清晰的方形像素块
- 颜色数量与预设匹配（目测图像或运行 `Image.open(p).getcolors()`）
- 视频是有效的 MP4（`ffprobe` 可打开）且体积非零

<a id="attribution"></a>
##  Attribution（归属说明）

`pixel_art_video.py` 中的命名硬件调色板和程序化动画循环移植自 [pixel-art-studio](https://github.com/Synero/pixel-art-studio)（MIT 协议）。详情请参见该技能目录下的 `ATTRIBUTION.md`。
