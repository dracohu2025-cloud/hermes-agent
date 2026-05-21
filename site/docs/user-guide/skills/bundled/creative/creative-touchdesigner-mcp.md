---
title: "Touchdesigner Mcp"
sidebar_label: "Touchdesigner Mcp"
description: "通过 twozero MCP 控制正在运行的 TouchDesigner 实例——创建算子、设置参数、连接线路、执行 Python、构建实时视觉。包含 36 个原生工具。"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 从技能文件 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="touchdesigner-mcp"></a>
# Touchdesigner Mcp

通过 twozero MCP 控制正在运行的 TouchDesigner 实例——创建算子、设置参数、连接线路、执行 Python、构建实时视觉。包含 36 个原生工具。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/touchdesigner-mcp` |
| 版本 | `1.1.0` |
| 作者 | kshitijk4poor |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `TouchDesigner`、`MCP`、`twozero`、`creative-coding`、`real-time-visuals`、`generative-art`、`audio-reactive`、`VJ`、`installation`、`GLSL` |
| 相关技能 | [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp)、[`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video)、[`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video)、`hermes-video` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下为 Hermes 在触发该技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令内容。
:::

<a id="touchdesigner-integration-twozero-mcp"></a>
# TouchDesigner 集成（twozero MCP）

<a id="critical-rules"></a>
## 关键规则

1. **切勿猜测参数名。** 请针对算子类型首先调用 `td_get_par_info`。你的训练数据对 TD 2025.32 来说已过时。
2. **如果触发了 `tdAttributeError`，立即停止。** 在继续之前，先对出错的节点调用 `td_get_operator_info`。
3. **切勿在脚本回调中硬编码绝对路径。** 应使用 `me.parent()` / `scriptOp.parent()`。
4. **优先使用原生 MCP 工具，而非 `td_execute_python`。** 使用 `td_create_operator`、`td_set_operator_pars`、`td_get_errors` 等工具。仅在进行复杂的多步逻辑时，才退而使用 `td_execute_python`。
5. **在构建之前先调用 `td_get_hints`。** 它会返回与你当前操作算子类型相关的特定模式。

<a id="architecture"></a>
## 架构

```
Hermes Agent -> MCP（可流式 HTTP）-> twozero.tox（端口 40404）-> TD Python
```

36 个原生工具。免费插件（无需付费/许可——已于 2026 年 4 月确认）。
上下文感知（知道当前选中的 OP、当前网络）。
Hub 健康检查：`GET http://localhost:40404/mcp` 返回包含实例 PID、项目名称、TD 版本的 JSON。

<a id="setup-automated"></a>
## 设置（自动化）

运行设置脚本即可处理所有事项：

```bash
bash "${HERMES_HOME:-$HOME/.hermes}/skills/creative/touchdesigner-mcp/scripts/setup.sh"
```

该脚本将：
1. 检查 TD 是否正在运行
2. 如果尚未缓存，则下载 twozero.tox
3. 将 `twozero_td` MCP 服务器添加到 Hermes 配置中（如果缺少）
4. 测试端口 40404 上的 MCP 连接
5. 报告仍需手动完成的步骤（将 .tox 拖入 TD，启用 MCP 开关）

<a id="manual-steps-one-time-cannot-be-automated"></a>
### 手动步骤（一次性操作，无法自动化）

1. **将 `~/Downloads/twozero.tox` 拖入 TD 网络编辑器** → 点击 Install
2. **启用 MCP：** 点击 twozero 图标 → Settings → mcp → “auto start MCP” → Yes
3. **重启 Hermes 会话** 以加载新的 MCP 服务器

设置完成后，验证：

```bash
nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"
```
<a id="environment-notes"></a>
## 环境说明

- **非商业版 TD** 将分辨率限制在 1280×1280。请使用 `outputresolution = 'custom'` 并显式设置宽高。
- **编码器：** `prores`（macOS 上首选）或 `mjpa` 作为备选。H.264/H.265/AV1 需要商业许可证。
- 设置参数前务必先调用 `td_get_par_info`——参数名称因 TD 版本而异（参见关键规则 #1）。

<a id="workflow"></a>
## 工作流程

<a id="step-0-discover-before-building-anything"></a>
### 第 0 步：探查（在构建任何内容之前）

```
为计划使用的每种类型调用 td_get_par_info，传入 op_type。
针对正在构建的主题（例如 "glsl"、"audio reactive"、"feedback"）调用 td_get_hints。
调用 td_get_focus 查看用户当前所在位置以及选中了什么。
调用 td_get_network 查看已有内容。
```

无需临时节点，无需清理。这完全取代了旧式的探查步骤。

<a id="step-1-clean-build"></a>
### 第 1 步：清理 + 构建

**重要提示：将清理和创建操作拆分为独立的 MCP 调用。** 在同一个 `td_execute_python` 脚本中销毁并重新创建同名节点会导致"无效 OP 对象"错误。参见陷阱 #11b。

使用 `td_create_operator` 创建每个节点（自动处理视口定位）：

```
td_create_operator(type="noiseTOP", parent="/project1", name="bg", parameters={"resolutionw": 1280, "resolutionh": 720})
td_create_operator(type="levelTOP", parent="/project1", name="brightness")
td_create_operator(type="nullTOP", parent="/project1", name="out")
```

对于批量创建或连线，使用 `td_execute_python`：

```python
# td_execute_python 脚本：
root = op('/project1')
nodes = []
for name, optype in [('bg', noiseTOP), ('fx', levelTOP), ('out', nullTOP)]:
    n = root.create(optype, name)
    nodes.append(n.path)
# 连线链
for i in range(len(nodes)-1):
    op(nodes[i]).outputConnectors[0].connect(op(nodes[i+1]).inputConnectors[0])
result = {'created': nodes}
```

<a id="step-2-set-parameters"></a>
### 第 2 步：设置参数

优先使用原生工具（会验证参数，不会崩溃）：

```
td_set_operator_pars(path="/project1/bg", parameters={"roughness": 0.6, "monochrome": true})
```

对于表达式或模式，使用 `td_execute_python`：

```python
op('/project1/time_driver').par.colorr.expr = "absTime.seconds % 1000.0"
```

<a id="step-3-wire"></a>
### 第 3 步：连线

使用 `td_execute_python`——没有原生的连线工具：

```python
op('/project1/bg').outputConnectors[0].connect(op('/project1/fx').inputConnectors[0])
```

<a id="step-4-verify"></a>
### 第 4 步：验证

```
td_get_errors(path="/project1", recursive=true)
td_get_perf()
td_get_operator_info(path="/project1/out", detail="full")
```

<a id="step-5-display-capture"></a>
### 第 5 步：显示 / 截图

```
td_get_screenshot(path="/project1/out")
```

或通过脚本打开窗口：

```python
win = op('/project1').create(windowCOMP, 'display')
win.par.winop = op('/project1/out').path
win.par.winw = 1280; win.par.winh = 720
win.par.winopen.pulse()
```

<a id="mcp-tool-quick-reference"></a>
## MCP 工具快速参考

**核心工具（最常用）：**
| 工具 | 功能 |
|------|------|
| `td_execute_python` | 在 TD 中运行任意 Python 代码。完整 API 访问权限。 |
| `td_create_operator` | 创建节点，支持参数设置和自动定位 |
| `td_set_operator_pars` | 安全设置参数（会验证，不会崩溃） |
| `td_get_operator_info` | 检查单个节点：连接、参数、错误 |
| `td_get_operators_info` | 一次调用检查多个节点 |
| `td_get_network` | 查看指定路径的网络结构 |
| `td_get_errors` | 递归查找错误/警告 |
| `td_get_par_info` | 获取某 OP 类型的参数名称（替代探查步骤） |
| `td_get_hints` | 构建前获取模式/提示 |
| `td_get_focus` | 查看当前打开的网络以及选中的内容 |
**读/写：**
| 工具 | 用途 |
|------|------|
| `td_read_dat` | 读取DAT文本内容 |
| `td_write_dat` | 写入/修补DAT内容 |
| `td_read_chop` | 读取CHOP通道值 |
| `td_read_textport` | 读取TD控制台输出 |

**可视化：**
| 工具 | 用途 |
|------|------|
| `td_get_screenshot` | 捕获一个OP查看器到文件 |
| `td_get_screenshots` | 一次捕获多个OP |
| `td_get_screen_screenshot` | 通过TD捕获实际屏幕 |
| `td_navigate_to` | 将网络编辑器跳转至某个OP |

**搜索：**
| 工具 | 用途 |
|------|------|
| `td_find_op` | 按名称/类型在整个项目中查找OP |
| `td_search` | 搜索代码、表达式、字符串参数 |

**系统：**
| 工具 | 用途 |
|------|------|
| `td_get_perf` | 性能分析（FPS，慢OP） |
| `td_list_instances` | 列出所有正在运行的TD实例 |
| `td_get_docs` | 获取某个TD主题的深入文档 |
| `td_agents_md` | 读写每个COMP的Markdown文档 |
| `td_reinit_extension` | 代码编辑后重新加载扩展 |
| `td_clear_textport` | 调试会话前清空控制台 |

**输入自动化：**
| 工具 | 用途 |
|------|------|
| `td_input_execute` | 向TD发送鼠标/键盘 |
| `td_input_status` | 查询输入队列状态 |
| `td_input_clear` | 停止输入自动化 |
| `td_op_screen_rect` | 获取节点的屏幕坐标 |
| `td_click_screen_point` | 在截图中点击某点 |
| `td_screen_point_to_global` | 将截图像素转换为绝对屏幕坐标 |

上表涵盖了典型创意工作流中使用的32个工具。其余4个工具（`td_project_quit`、`td_test_session`、`td_dev_log`、`td_clear_dev_log`）是管理员/开发模式实用工具——完整36个工具的参考（含完整参数模式）请参见 `references/mcp-tools.md`。

<a id="key-implementation-rules"></a>
## 关键实现规则

**GLSL时间：** GLSL TOP中不要使用 `uTDCurrentTime`。应使用 Values 页面：
```python
# 先调用 td_get_par_info(op_type="glslTOP") 确认参数名称
td_set_operator_pars(path="/project1/shader", parameters={"value0name": "uTime"})
# 然后通过脚本设置表达式：
# op('/project1/shader').par.value0.expr = "absTime.seconds"
# 在 GLSL 中：uniform float uTime;
```

回退方案：使用 `rgba32float` 格式的 Constant TOP（8位会钳位到0-1，导致着色器冻结）。

**Feedback TOP：** 使用 `top` 参数引用，而非直接输入连线。第一次烹饪后“Not enough sources”错误会解决。“Cook dependency loop”警告是预期的。

**分辨率：** Non-Commercial 版本限制为1280×1280。使用 `outputresolution = 'custom'`。

**大型着色器：** 将GLSL写入 `/tmp/file.glsl`，然后使用 `td_write_dat` 或 `td_execute_python` 加载。

**顶点/点访问（TD 2025.32）：** `point.P[0]`、`point.P[1]`、`point.P[2]` —— 而不是 `.x`、`.y`、`.z`。

**扩展：** 在 CONSTANT 模式下，`ext0object` 格式为 `"op('./datName').module.ClassName(me)"`。使用 `td_write_dat` 编辑扩展代码后，调用 `td_reinit_extension`。

**脚本回调：** 始终通过 `me.parent()` / `scriptOp.parent()` 使用相对路径。

**清理节点：** 在迭代前始终 `list(root.children)`，并加上 `child.valid` 检查。
<a id="recording-exporting-video"></a>
## 录制/导出视频

```python
# via td_execute_python:
root = op('/project1')
rec = root.create(moviefileoutTOP, 'recorder')
op('/project1/out').outputConnectors[0].connect(rec.inputConnectors[0])
rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'prores'  # Apple ProRes — NOT license-restricted on macOS
rec.par.record = True   # start
# rec.par.record = False  # stop (call separately later)
```

H.264/H.265/AV1 需要商业许可证。在 macOS 上使用 `prores`，或使用 `mjpa` 作为后备方案。
提取帧：`ffmpeg -i /tmp/output.mov -vframes 120 /tmp/frames/frame_%06d.png`

**TOP.save() 对动画无效** — 每次都会捕获相同的 GPU 纹理。始终使用 MovieFileOut。

<a id="before-recording-checklist"></a>
### 录制前的检查清单

1. **通过 `td_get_perf` 确认 FPS > 0**。如果 FPS=0，录制内容将为空。参见陷阱 #38-39。
2. **通过 `td_get_screenshot` 确认着色器输出不为黑色**。黑色输出意味着着色器错误或缺少输入。参见陷阱 #8, #40。
3. **如果录制带音频：** 先触发音频开始，然后将录制延迟 3 帧。参见陷阱 #19。
4. **在开始录制前设置输出路径** — 如果在同一个脚本中同时设置两者可能会导致竞态条件。

<a id="audio-reactive-glsl-proven-recipe"></a>
## 音频响应式 GLSL（经过验证的方案）

<a id="correct-signal-chain-tested-april-2026"></a>
### 正确的信号链（2026年4月测试）

```
AudioFileIn CHOP (playmode=sequential)
  → AudioSpectrum CHOP (FFT=512, outputmenu=setmanually, outlength=256, timeslice=ON)
  → Math CHOP (gain=10)
  → CHOP to TOP (dataformat=r, layout=rowscropped)
  → GLSL TOP input 1 (spectrum texture, 256x2)

Constant TOP (rgba32float, time) → GLSL TOP input 0
GLSL TOP → Null TOP → MovieFileOut
```

<a id="critical-audio-reactive-rules-empirically-verified"></a>
### 关键的音频响应规则（经验证）

1. **TimeSlice 必须保持 ON** 对 AudioSpectrum。OFF 会处理整个音频文件 → 24000+ 样本 → CHOP to TOP 溢出。
2. **手动设置 Output Length** 为 256，通过 `outputmenu='setmanually'` 和 `outlength=256`。默认输出 22050 个样本。
3. **不要使用 Lag CHOP 进行频谱平滑。** Lag CHOP 在 timeslice 模式下工作，将 256 个样本扩展到 2400+，将所有值平均到接近零（~1e-06）。着色器接收不到可用数据。这是测试中排名第一的音频同步失败原因。
4. **也不要使用 Filter CHOP** — 与频谱数据存在相同的 timeslice 扩展问题。
5. **平滑处理应在 GLSL 着色器中完成** 如果需要，通过带有反馈纹理的时间插值：`mix(prevValue, newValue, 0.3)`。这可以实现逐帧完美同步，零管道延迟。
6. **CHOP to TOP 的 dataformat = 'r'**，layout = 'rowscropped'。频谱输出为 256x2（立体声）。在第一通道的 y=0.25 处采样。
7. **Math 增益 = 10**（不是 5）。原始频谱值在低频范围内约为 0.19。增益 10 可提供着色器可用的 ~5.0 值。
8. **不需要 Resample CHOP。** 直接通过 AudioSpectrum 的 `outlength` 参数控制输出大小。

<a id="glsl-spectrum-sampling"></a>
### GLSL 频谱采样

```glsl
// Input 0 = time (1x1 rgba32float), Input 1 = spectrum (256x2)
float iTime = texture(sTD2DInputs[0], vec2(0.5)).r;

// Sample multiple points per band and average for stability:
// NOTE: y=0.25 for first channel (stereo texture is 256x2, first row center is 0.25)
float bass = (texture(sTD2DInputs[1], vec2(0.02, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.05, 0.25)).r) / 2.0;
float mid  = (texture(sTD2DInputs[1], vec2(0.2, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.35, 0.25)).r) / 2.0;
float hi   = (texture(sTD2DInputs[1], vec2(0.6, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.8, 0.25)).r) / 2.0;
```
参见 `references/network-patterns.md` 了解完整构建脚本和着色器代码。

<a id="operator-quick-reference"></a>
## 算子快速参考

| 系列 | 颜色 | Python 类 / MCP 类型 | 后缀 |
|--------|-------|-------------|--------|
| TOP | 紫色 | noiseTOP, glslTOP, compositeTOP, levelTop, blurTOP, textTOP, nullTOP | TOP |
| CHOP | 绿色 | audiofileinCHOP, audiospectrumCHOP, mathCHOP, lfoCHOP, constantCHOP | CHOP |
| SOP | 蓝色 | gridSOP, sphereSOP, transformSOP, noiseSOP | SOP |
| DAT | 白色 | textDAT, tableDAT, scriptDAT, webserverDAT | DAT |
| MAT | 黄色 | phongMAT, pbrMAT, glslMAT, constMAT | MAT |
| COMP | 灰色 | geometryCOMP, containerCOMP, cameraCOMP, lightCOMP, windowCOMP | COMP |

<a id="security-notes"></a>
## 安全注意事项

- MCP 仅在 localhost（端口 40404）上运行。无身份验证——任何本地进程都可以发送命令。
- `td_execute_python` 可以无限制访问 TD Python 环境和文件系统，权限与 TD 进程用户相同。
- `setup.sh` 从官方 404zero.com URL 下载 `twozero.tox`。如有顾虑，请验证下载内容。
- 该技能绝不会将数据发送到 localhost 之外。所有 MCP 通信均为本地通信。

<a id="references"></a>
## 参考资料

| 文件 | 说明 |
|------|------|
| `references/pitfalls.md` | 从实际会话中获得的宝贵经验 |
| `references/operators.md` | 所有算子系列及其参数和用例 |
| `references/network-patterns.md` | 配方：音频响应、生成式、GLSL、实例化 |
| `references/mcp-tools.md` | 完整的 twozero MCP 工具参数模式 |
| `references/python-api.md` | TD Python：op()、脚本、扩展 |
| `references/troubleshooting.md` | 连接诊断、调试 |
| `references/glsl.md` | GLSL uniform、内置函数、着色器模板 |
| `references/postfx.md` | 后期特效：辉光、CRT、色差、反馈发光 |
| `references/layout-compositor.md` | HUD 布局模式、面板网格、BSP 风格布局 |
| `references/operator-tips.md` | 线框渲染、反馈 TOP 设置 |
| `references/geometry-comp.md` | Geometry COMP：实例化、POP vs SOP、变形 |
| `references/audio-reactive.md` | 音频频段提取、节拍检测、包络跟踪 |
| `references/animation.md` | LFO、计时器、关键帧、缓动、表达式驱动运动 |
| `references/midi-osc.md` | MIDI/OSC 控制器、TouchOSC、多机同步 |
| `references/particles.md` | POP 和旧版 particleSOP——发射、力、碰撞 |
| `references/projection-mapping.md` | 多窗口输出、边角定位、网格扭曲、边缘融合 |
| `references/external-data.md` | HTTP、WebSocket、MQTT、串口、TCP、webserverDAT |
| `references/panel-ui.md` | 自定义参数、panel COMP、按钮/滑块/字段、panelExecuteDAT |
| `references/replicator.md` | replicatorCOMP——数据驱动克隆、布局、回调 |
| `references/dat-scripting.md` | Execute DAT 系列——chop/dat/parameter/panel/op/executeDAT |
| `references/3d-scene.md` | 照明系统、阴影、IBL/立方体贴图、多相机、PBR |
| `scripts/setup.sh` | 自动设置脚本 |

---

> 你不是在写代码。你是在驾驭光。
