---
title: "Songsee — 通过 CLI 生成音频频谱图/特征（mel、chroma、MFCC）"
sidebar_label: "Songsee"
description: "通过 CLI 生成音频频谱图/特征（mel、chroma、MFCC）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Songsee {#songsee}

通过 CLI 生成音频频谱图/特征（mel、chroma、MFCC）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/songsee` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `Audio`, `Visualization`, `Spectrogram`, `Music`, `Analysis` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="songsee"></a>
# songsee

从音频文件生成频谱图和多面板音频特征可视化图。

## 前置条件 {#prerequisites}

需要安装 [Go](https://go.dev/doc/install)：
```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

可选：对于 WAV/MP3 之外的格式，需要 `ffmpeg`。

## 快速开始 {#quick-start}

```bash
# 基础频谱图
songsee track.mp3

# 保存到指定文件
songsee track.mp3 -o spectrogram.png

# 多面板可视化网格
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# 时间切片（从 12.5 秒开始，持续 8 秒）
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg

# 从标准输入读取
cat track.mp3 | songsee - --format png -o out.png
```

## 可视化类型 {#visualization-types}

使用 `--viz` 参数，以逗号分隔多个值：

| 类型 | 描述 |
|------|------|
| `spectrogram` | 标准频率频谱图 |
| `mel` | Mel 刻度频谱图 |
| `chroma` | 音级分布 |
| `hpss` | 谐波/打击乐分离 |
| `selfsim` | 自相似矩阵 |
| `loudness` | 随时间变化的响度 |
| `tempogram` | 节奏估计 |
| `mfcc` | 梅尔频率倒谱系数 |
| `flux` | 频谱通量（起始检测） |

多个 `--viz` 类型会在单张图片中渲染为网格。

## 常用标志 {#common-flags}

| 标志 | 描述 |
|------|------|
| `--viz` | 可视化类型（逗号分隔） |
| `--style` | 调色板：`classic`、`magma`、`inferno`、`viridis`、`gray` |
| `--width` / `--height` | 输出图像尺寸 |
| `--window` / `--hop` | FFT 窗口和跳跃大小 |
| `--min-freq` / `--max-freq` | 频率范围过滤 |
| `--start` / `--duration` | 音频的时间切片 |
| `--format` | 输出格式：`jpg` 或 `png` |
| `-o` | 输出文件路径 |

## 注意事项 {#notes}

- WAV 和 MP3 原生解码；其他格式需要 `ffmpeg`
- 输出图像可通过 `vision_analyze` 进行检查，用于自动化音频分析
- 适用于比较音频输出、调试合成或记录音频处理流程
