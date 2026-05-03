---
title: "Pixel Art — Pixel art w/ era palettes (NES, Game Boy, PICO-8)"
sidebar_label: "Pixel Art"
description: "使用时代调色板生成像素画（NES、Game Boy、PICO-8）"
---

{/* 此页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pixel Art {#pixel-art}

使用时代调色板生成像素画（NES、Game Boy、PICO-8）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pixel-art` |
| 版本 | `2.0.0` |
| 作者 | dodo-reach |
| 许可证 | MIT |
| 标签 | `creative`, `pixel-art`, `arcade`, `snes`, `nes`, `gameboy`, `retro`, `image`, `video` |

## 完整 SKILL.md 参考 {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 将看到这些指令。
:::

<a id="pixel-art"></a>
# Pixel Art

将任意图片转换为复古像素画，并可选地将其制作成带有时代风格特效（雨、萤火虫、雪、余烬）的短 MP4 或 GIF。

此技能附带两个脚本：

- `scripts/pixel_art.py` — 照片 → 像素画 PNG（Floyd-Steinberg 抖动）
- `scripts/pixel_art_video.py` — 像素画 PNG → 动画 MP4（可选 GIF）

每个脚本均可直接导入或运行。当你需要时代准确的色彩（NES、Game Boy、PICO-8 等）时，预设会锁定到硬件调色板；或者使用自适应 N 色量化实现街机/SNES 风格。

## 何时使用 {#when-to-use}

- 用户想要从源图片生成复古像素画
- 用户要求 NES / Game Boy / PICO-8 / C64 / 街机 / SNES 风格
- 用户想要一个短循环动画（雨景、夜空、雪景等）
- 海报、专辑封面、社交媒体帖子、精灵图、角色、头像

## 工作流程 {#workflow}

在生成之前，与用户确认风格。不同的预设会产生截然不同的输出，重新生成成本较高。

### 步骤 1 — 提供风格 {#step-1-offer-a-style}

使用 4 个代表性预设调用 `clarify`。根据用户的需求选择一组——不要一次性列出全部 14 个。

当用户意图不明确时的默认菜单：

```python
clarify(
    question="你想要哪种像素画风格？",
    choices=[
        "街机 —— 粗犷、厚重的 80 年代街机柜体感（16 色，8px）",
        "nes —— 任天堂 8 位硬件调色板（54 色，8px）",
        "gameboy —— 4 阶绿色 Game Boy DMG",
        "snes —— 更清晰的 16 位外观（32 色，4px）",
    ],
)
```

当用户已经提到某个时代（例如“80 年代街机”、“Gameboy”）时，跳过 `clarify` 直接使用匹配的预设。

### 步骤 2 — 提供动画（可选） {#step-2-offer-animation-optional}

如果用户要求视频/GIF，或者输出可能因运动效果更好，询问场景：

```python
clarify(
    question="想要制作动画吗？选择一个场景或跳过。",
    choices=[
        "night —— 星星 + 萤火虫 + 树叶",
        "urban —— 雨 + 霓虹脉冲",
        "snow —— 飘落的雪花",
        "skip —— 仅生成图片",
    ],
)
```

不要连续调用 `clarify` 超过两次。一次用于风格，一次用于场景（如果需要动画）。如果用户明确在消息中指定了风格和场景，完全跳过 `clarify`。

### 步骤 3 — 生成 {#step-3-generate}

首先运行 `pixel_art()`；如果请求了动画，则在其结果上链式调用 `pixel_art_video()`。
## 预设目录 {#preset-catalog}

| 预设 | 时代 | 调色板 | 像素块 | 最佳用途 |
|--------|-----|---------|-------|----------|
| `arcade` | 80年代街机 | 自适应16色 | 8px | 大胆的海报、英雄艺术 |
| `snes` | 16位 | 自适应32色 | 4px | 角色、精细场景 |
| `nes` | 8位 | NES (54色) | 8px | 纯正NES风格 |
| `gameboy` | DMG掌机 | 4种绿色调 | 8px | 单色Game Boy |
| `gameboy_pocket` | Pocket掌机 | 4种灰色调 | 8px | 单色GB Pocket |
| `pico8` | PICO-8 | 16种固定色 | 6px | 幻想主机风格 |
| `c64` | Commodore 64 | 16种固定色 | 8px | 8位家用电脑 |
| `apple2` | Apple II高分辨率 | 6种固定色 | 10px | 极致复古，6色 |
| `teletext` | BBC图文电视 | 8种纯色 | 10px | 粗犷原色 |
| `mspaint` | Windows画图 | 24种固定色 | 8px | 怀旧桌面 |
| `mono_green` | CRT荧光粉 | 2种绿色 | 6px | 终端/CRT美学 |
| `mono_amber` | CRT琥珀色 | 2种琥珀色 | 6px | 琥珀色显示器风格 |
| `neon` | 赛博朋克 | 10种霓虹色 | 6px | 蒸汽波/赛博 |
| `pastel` | 柔和粉彩 | 10种粉彩色 | 6px | 可爱/温柔 |

命名调色板位于 `scripts/palettes.py` 中（完整列表见 `references/palettes.md` —— 共28个命名调色板）。任何预设都可以被覆盖：

```python
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
```

## 场景目录（用于视频） {#scene-catalog-for-video}

| 场景 | 效果 |
|-------|---------|
| `night` | 闪烁的星星 + 萤火虫 + 飘落的树叶 |
| `dusk` | 萤火虫 + 闪光 |
| `tavern` | 灰尘颗粒 + 温暖闪光 |
| `indoor` | 灰尘颗粒 |
| `urban` | 雨 + 霓虹脉冲 |
| `nature` | 树叶 + 萤火虫 |
| `magic` | 闪光 + 萤火虫 |
| `storm` | 雨 + 闪电 |
| `underwater` | 气泡 + 柔和闪光 |
| `fire` | 余烬 + 闪光 |
| `snow` | 雪花 + 闪光 |
| `desert` | 热浪 + 灰尘 |

## 调用模式 {#invocation-patterns}

### Python（导入） {#python-import}

```python
import sys
sys.path.insert(0, "/home/teknium/.hermes/skills/creative/pixel-art/scripts")
from pixel_art import pixel_art
from pixel_art_video import pixel_art_video

# 1. 转换为像素艺术
pixel_art("/path/to/photo.jpg", "/tmp/pixel.png", preset="nes")

# 2. 制作动画（可选）
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

### CLI {#cli}

```bash
cd /home/teknium/.hermes/skills/creative/pixel-art/scripts

python pixel_art.py in.jpg out.png --preset gameboy
python pixel_art.py in.jpg out.png --preset snes --palette PICO_8 --block 6

python pixel_art_video.py out.png out.mp4 --scene night --duration 6 --gif
```

## 流程原理 {#pipeline-rationale}

**像素转换：**
1. 增强对比度/色彩/锐度（调色板越小，增强越强）
2. 色调分离，在量化前简化色调区域
3. 使用 `Image.NEAREST` 按 `block` 缩小（硬像素，无插值）
4. 使用 Floyd-Steinberg 抖动进行量化 —— 针对自适应 N 色调色板或命名硬件调色板
5. 使用 `Image.NEAREST` 放大回原尺寸

在缩小之后进行量化，可确保抖动与最终像素网格对齐。如果在缩小之前量化，误差扩散会浪费在最终消失的细节上。
**Video overlay:**
- 每帧复制基础画面（静态背景）
- 叠加每帧无状态粒子绘制（每个效果一个函数）
- 通过 ffmpeg 编码 `libx264 -pix_fmt yuv420p -crf 18`
- 可选 GIF 通过 `palettegen` + `paletteuse`

## Dependencies {#dependencies}

- Python 3.9+
- Pillow（`pip install Pillow`）
- ffmpeg 在 PATH 中（仅视频需要 — Hermes 会安装此包）

## Pitfalls {#pitfalls}

- 调色板键区分大小写（`"NES"`、`"PICO_8"`、`"GAMEBOY_ORIGINAL"`）。
- 非常小的源（&lt;100px wide）会在 8-10 像素块下崩溃。如果源很小，请先放大。
- 小数 `block` 或 `palette` 会破坏量化 — 请保持为正整数。
- 动画粒子计数针对 ~640x480 画布调整。在非常大的图像上，你可能需要第二次传递，使用不同的种子来调整密度。
- `mono_green` / `mono_amber` 强制 `color=0.0`（去饱和）。如果你覆盖并保留色度，2 色调色板会在平滑区域产生条纹。
- `clarify` 循环：每轮最多调用两次（先风格，后场景）。不要用更多选择来烦扰用户。

## Verification {#verification}

- PNG 在输出路径创建
- 在预设的块大小下可见清晰的方形像素块
- 颜色数量与预设匹配（目测图像或运行 `Image.open(p).getcolors()`）
- 视频是有效的 MP4（`ffprobe` 可以打开）且大小非零

## Attribution {#attribution}

`pixel_art_video.py` 中的命名硬件调色板和程序化动画循环移植自 [pixel-art-studio](https://github.com/Synero/pixel-art-studio)（MIT）。详情请参阅此技能目录中的 `ATTRIBUTION.md`。
