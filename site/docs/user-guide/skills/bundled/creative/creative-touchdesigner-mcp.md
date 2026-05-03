---
title: "Touchdesigner Mcp"
sidebar_label: "Touchdesigner Mcp"
description: "通过 twozero MCP 控制正在运行的 TouchDesigner 实例 — 创建操作器、设置参数、连接节点、执行 Python、构建实时视觉"
---

{/* 本页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Touchdesigner Mcp {#touchdesigner-mcp}

通过 twozero MCP 控制正在运行的 TouchDesigner 实例 — 创建操作器、设置参数、连接节点、执行 Python、构建实时视觉。内置 36 个原生工具。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/touchdesigner-mcp` |
| 版本 | `1.1.0` |
| 作者 | kshitijk4poor |
| 许可证 | MIT |
| 标签 | `TouchDesigner`, `MCP`, `twozero`, `creative-coding`, `real-time-visuals`, `generative-art`, `audio-reactive`, `VJ`, `installation`, `GLSL` |
| 相关技能 | [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp), [`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video), `hermes-video` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 所看到的指令。
:::

# TouchDesigner 集成（twozero MCP） {#touchdesigner-integration-twozero-mcp}

## 关键规则 {#critical-rules}

1. **切勿猜测参数名称。** 请先对操作器类型调用 `td_get_par_info`。你的训练数据对于 TD 2025.32 而言是错误的。
2. **如果 `tdAttributeError` 触发，立即停止。** 在继续之前，先对失败节点调用 `td_get_operator_info`。
3. **切勿在脚本回调中硬编码绝对路径。** 请使用 `me.parent()` / `scriptOp.parent()`。
4. **优先使用原生 MCP 工具而非 `td_execute_python`。** 使用 `td_create_operator`、`td_set_operator_pars`、`td_get_errors` 等。仅在需要复杂多步逻辑时退而使用 `td_execute_python`。
5. **在构建之前调用 `td_get_hints`。** 它会返回与你当前操作的 op 类型相关的模式。

## 架构 {#architecture}

```
Hermes Agent -> MCP（可流式 HTTP）-> twozero.tox（端口 40404）-> TD Python
```

36 个原生工具。免费插件（无需付费/许可证 — 2026 年 4 月确认）。
上下文感知（知道当前选中的 OP 和当前网络）。
中心健康检查：`GET http://localhost:40404/mcp` 返回包含实例 PID、项目名称、TD 版本的 JSON。

## 设置（自动化） {#setup-automated}

运行设置脚本以完成所有操作：

```bash
bash "${HERMES_HOME:-$HOME/.hermes}/skills/creative/touchdesigner-mcp/scripts/setup.sh"
```

脚本将：
1. 检查 TD 是否正在运行
2. 如果尚未缓存，则下载 twozero.tox
3. 将 `twozero_td` MCP 服务器添加到 Hermes 配置（如果缺失）
4. 测试端口 40404 上的 MCP 连接
5. 报告还需要手动执行哪些步骤（将 .tox 拖入 TD，启用 MCP 开关）

### 手动步骤（一次性，无法自动化） {#manual-steps-one-time-cannot-be-automated}

1. **将 `~/Downloads/twozero.tox` 拖入 TD 网络编辑器** → 点击 Install
2. **启用 MCP：** 点击 twozero 图标 → Settings → mcp → "auto start MCP" → Yes
3. **重启 Hermes 会话** 以加载新的 MCP 服务器

设置完成后，验证：
```bash
nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"
```

## 环境说明 {#environment-notes}
- **非商业版 TD** 将分辨率限制在 1280×1280。使用 `outputresolution = 'custom'` 并明确设置宽/高。
- **编码器：** 优先使用 `prores`（macOS 上推荐）或回退到 `mjpa`。H.264/H.265/AV1 需要商业许可。
- 设置参数前务必调用 `td_get_par_info`——参数名称因 TD 版本而异（参见关键规则 #1）。

## 工作流程 {#workflow}

### 第 0 步：探索（在构建任何东西之前） {#step-0-discover-before-building-anything}

```
为每种计划使用的运算符类型，调用 td_get_par_info 并传入 op_type。
调用 td_get_hints 并传入你正在构建的主题（例如 "glsl"、"audio reactive"、"feedback"）。
调用 td_get_focus 查看用户所在位置以及当前选择的内容。
调用 td_get_network 查看已有内容。
```

没有临时节点，无需清理。这将完全取代旧版的探索流程。

### 第 1 步：清理 + 构建 {#step-1-clean-build}

**重要提示：将清理和创建拆分为独立的 MCP 调用。** 如果在一个 `td_execute_python` 脚本中同时销毁和重建同名的节点，会导致“Invalid OP object”错误。参见常见陷阱 #11b。

为每个节点使用 `td_create_operator`（自动处理视口定位）：

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

### 第 2 步：设置参数 {#step-2-set-parameters}

优先使用原生工具（会验证参数，不会崩溃）：

```
td_set_operator_pars(path="/project1/bg", parameters={"roughness": 0.6, "monochrome": true})
```

对于表达式或模式，使用 `td_execute_python`：

```python
op('/project1/time_driver').par.colorr.expr = "absTime.seconds % 1000.0"
```

### 第 3 步：连线 {#step-3-wire}

使用 `td_execute_python`——没有原生连线工具：

```python
op('/project1/bg').outputConnectors[0].connect(op('/project1/fx').inputConnectors[0])
```

### 第 4 步：验证 {#step-4-verify}

```
td_get_errors(path="/project1", recursive=true)
td_get_perf()
td_get_operator_info(path="/project1/out", detail="full")
```

### 第 5 步：显示 / 捕获 {#step-5-display-capture}

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

## MCP 工具快速参考 {#mcp-tool-quick-reference}

**核心工具（尽量多用这些）：**
| 工具 | 功能 |
|------|------|
| `td_execute_python` | 在 TD 中运行任意 Python 代码。完全访问 API。 |
| `td_create_operator` | 创建节点并设置参数 + 自动定位 |
| `td_set_operator_pars` | 安全设置参数（会验证，不会崩溃） |
| `td_get_operator_info` | 检查单个节点：连接、参数、错误 |
| `td_get_operators_info` | 一次调用检查多个节点 |
| `td_get_network` | 查看指定路径的网络结构 |
| `td_get_errors` | 递归查找错误/警告 |
| `td_get_par_info` | 获取某个 OP 类型的参数名称（替代探索步骤） |
| `td_get_hints` | 构建前获取模式/技巧 |
| `td_get_focus` | 查看当前打开的网络以及选中的内容 |
**读/写：**
| 工具 | 功能 |
|------|------|
| `td_read_dat` | 读取 DAT 文本内容 |
| `td_write_dat` | 写入/修补 DAT 内容 |
| `td_read_chop` | 读取 CHOP 通道值 |
| `td_read_textport` | 读取 TD 控制台输出 |

**可视化：**
| 工具 | 功能 |
|------|------|
| `td_get_screenshot` | 将单个 OP 查看器捕获到文件 |
| `td_get_screenshots` | 同时捕获多个 OP |
| `td_get_screen_screenshot` | 通过 TD 捕获实际屏幕 |
| `td_navigate_to` | 将网络编辑器跳转到某个 OP |

**搜索：**
| 工具 | 功能 |
|------|------|
| `td_find_op` | 按名称/类型在整个项目中查找 OP |
| `td_search` | 搜索代码、表达式、字符串参数 |

**系统：**
| 工具 | 功能 |
|------|------|
| `td_get_perf` | 性能分析（FPS、慢 OP） |
| `td_list_instances` | 列出所有正在运行的 TD 实例 |
| `td_get_docs` | 获取某个 TD 主题的详细文档 |
| `td_agents_md` | 读取/写入每个 COMP 的 markdown 文档 |
| `td_reinit_extension` | 代码编辑后重新加载扩展 |
| `td_clear_textport` | 调试会话前清空控制台 |

**输入自动化：**
| 工具 | 功能 |
|------|------|
| `td_input_execute` | 向 TD 发送鼠标/键盘操作 |
| `td_input_status` | 查询输入队列状态 |
| `td_input_clear` | 停止输入自动化 |
| `td_op_screen_rect` | 获取节点的屏幕坐标 |
| `td_click_screen_point` | 在截图中点击某个点 |
| `td_screen_point_to_global` | 将截图像素坐标转换为绝对屏幕坐标 |

上表涵盖了典型创意工作流中使用的 32 个工具。其余 4 个工具（`td_project_quit`、`td_test_session`、`td_dev_log`、`td_clear_dev_log`）是管理/开发模式工具——完整 36 个工具的参考及参数模式请参见 `references/mcp-tools.md`。

## 关键实现规则 {#key-implementation-rules}

**GLSL 时间：** GLSL TOP 中不要使用 `uTDCurrentTime`。请使用 Values 页面：
```python
# 先调用 td_get_par_info(op_type="glslTOP") 确认参数名称
td_set_operator_pars(path="/project1/shader", parameters={"value0name": "uTime"})
# 然后通过脚本设置表达式：
# op('/project1/shader').par.value0.expr = "absTime.seconds"
# 在 GLSL 中：uniform float uTime;
```

回退方案：使用 `rgba32float` 格式的 Constant TOP（8 位会钳制到 0-1，导致着色器冻结）。

**Feedback TOP：** 使用 `top` 参数引用，而不是直接输入连线。第一次烹饪后“Not enough sources”会消失。“Cook dependency loop”警告是预期的。

**分辨率：** 非商业版限制为 1280×1280。请使用 `outputresolution = 'custom'`。

**大型着色器：** 将 GLSL 写入 `/tmp/file.glsl`，然后使用 `td_write_dat` 或 `td_execute_python` 加载。

**顶点/点访问（TD 2025.32）：** 使用 `point.P[0]`、`point.P[1]`、`point.P[2]`——而不是 `.x`、`.y`、`.z`。

**扩展：** `ext0object` 格式在 CONSTANT 模式下为 `"op('./datName').module.ClassName(me)"`。使用 `td_write_dat` 编辑扩展代码后，调用 `td_reinit_extension`。

**脚本回调：** 始终通过 `me.parent()` / `scriptOp.parent()` 使用相对路径。

**清理节点：** 在迭代前始终使用 `list(root.children)`，并检查 `child.valid`。
## 录制 / 导出视频 {#recording-exporting-video}

```python
# 通过 td_execute_python:
root = op('/project1')
rec = root.create(moviefileoutTOP, 'recorder')
op('/project1/out').outputConnectors[0].connect(rec.inputConnectors[0])
rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'prores'  # Apple ProRes — macOS 上无许可证限制
rec.par.record = True   # 开始录制
# rec.par.record = False  # 停止录制（稍后单独调用）
```

H.264/H.265/AV1 需要商业许可证。在 macOS 上使用 `prores`，或使用 `mjpa` 作为备选方案。
提取帧：`ffmpeg -i /tmp/output.mov -vframes 120 /tmp/frames/frame_%06d.png`

**TOP.save() 对动画无效** — 每次都会捕获相同的 GPU 纹理。请始终使用 MovieFileOut。

### 录制前：检查清单 {#before-recording-checklist}

1. **通过 `td_get_perf` 确认 FPS > 0**。如果 FPS=0，录制的视频将是空的。参见陷阱 #38-39。
2. **通过 `td_get_screenshot` 确认着色器输出不是黑色**。黑色输出 = 着色器错误或缺少输入。参见陷阱 #8、#40。
3. **如果录制带音频：** 先让音频开始播放，然后延迟 3 帧再开始录制。参见陷阱 #19。
4. **在开始录制前设置输出路径** — 在同一个脚本中同时设置两者可能会产生竞态条件。

## 音频响应式 GLSL（经过验证的配方） {#audio-reactive-glsl-proven-recipe}

### 正确的信号链（2026 年 4 月测试） {#correct-signal-chain-tested-april-2026}

```
AudioFileIn CHOP（播放模式=顺序）
  → AudioSpectrum CHOP（FFT=512，输出菜单=手动设置，输出长度=256，时间片=开启）
  → Math CHOP（增益=10）
  → CHOP 到 TOP（数据格式=r，布局=行裁剪）
  → GLSL TOP 输入 1（频谱纹理，256x2）

Constant TOP（rgba32float，时间）→ GLSL TOP 输入 0
GLSL TOP → Null TOP → MovieFileOut
```

### 关键的音频响应规则（经验证） {#critical-audio-reactive-rules-empirically-verified}

1. **AudioSpectrum 必须保持 TimeSlice 开启**。关闭 = 处理整个音频文件 → 24000+ 个采样 → CHOP 到 TOP 溢出。
2. **通过 `outputmenu='setmanually'` 和 `outlength=256` 手动设置输出长度为 256**。默认输出 22050 个采样。
3. **不要使用 Lag CHOP 进行频谱平滑。** Lag CHOP 在时间片模式下运行，会将 256 个采样扩展到 2400+，将所有值平均到接近零（~1e-06）。着色器将无法接收到可用数据。这是测试中音频同步失败的头号原因。
4. **也不要使用 Filter CHOP** — 对频谱数据存在相同的时间片扩展问题。
5. **如果需要平滑，应在 GLSL 着色器中完成**，通过使用反馈纹理进行时间线性插值：`mix(prevValue, newValue, 0.3)`。这能实现帧级完美同步，且零管线延迟。
6. **CHOP 到 TOP 的 dataformat = 'r'**，layout = 'rowscropped'。频谱输出为 256x2（立体声）。在 y=0.25 处采样第一个通道。
7. **Math 增益 = 10**（不是 5）。原始频谱值在低音范围内约为 ~0.19。增益为 10 可为着色器提供约 ~5.0 的可用值。
8. **不需要 Resample CHOP。** 直接通过 AudioSpectrum 的 `outlength` 参数控制输出大小。

### GLSL 频谱采样 {#glsl-spectrum-sampling}

```glsl
// 输入 0 = 时间（1x1 rgba32float），输入 1 = 频谱（256x2）
float iTime = texture(sTD2DInputs[0], vec2(0.5)).r;

// 每个频段采样多个点并取平均值以获得稳定性：
// 注意：y=0.25 用于第一个通道（立体声纹理为 256x2，第一行中心为 0.25）
float bass = (texture(sTD2DInputs[1], vec2(0.02, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.05, 0.25)).r) / 2.0;
float mid  = (texture(sTD2DInputs[1], vec2(0.2, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.35, 0.25)).r) / 2.0;
float hi   = (texture(sTD2DInputs[1], vec2(0.6, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.8, 0.25)).r) / 2.0;
```
参见 `references/network-patterns.md` 获取完整的构建脚本和着色器代码。

## 操作符速查表 {#operator-quick-reference}

| 家族 | 颜色 | Python 类 / MCP 类型 | 后缀 |
|--------|-------|-------------|--------|
| TOP | 紫色 | noiseTOP, glslTOP, compositeTOP, levelTop, blurTOP, textTOP, nullTOP | TOP |
| CHOP | 绿色 | audiofileinCHOP, audiospectrumCHOP, mathCHOP, lfoCHOP, constantCHOP | CHOP |
| SOP | 蓝色 | gridSOP, sphereSOP, transformSOP, noiseSOP | SOP |
| DAT | 白色 | textDAT, tableDAT, scriptDAT, webserverDAT | DAT |
| MAT | 黄色 | phongMAT, pbrMAT, glslMAT, constMAT | MAT |
| COMP | 灰色 | geometryCOMP, containerCOMP, cameraCOMP, lightCOMP, windowCOMP | COMP |

## 安全说明 {#security-notes}

- MCP 仅在 localhost（端口 40404）上运行。无身份验证——任何本地进程都可以发送命令。
- `td_execute_python` 对 TD Python 环境和文件系统拥有与 TD 进程用户相同的无限制访问权限。
- `setup.sh` 从官方 404zero.com 网址下载 twozero.tox。如有顾虑，请验证下载内容。
- 该技能不会将数据发送到 localhost 之外。所有 MCP 通信都是本地的。

## 参考资料 {#references}

| 文件 | 说明 |
|------|------|
| `references/pitfalls.md` | 实际使用中积累的宝贵经验教训 |
| `references/operators.md` | 所有操作符家族及其参数和用例 |
| `references/network-patterns.md` | 配方：音频响应、生成式、GLSL、实例化 |
| `references/mcp-tools.md` | 完整的 twozero MCP 工具参数模式 |
| `references/python-api.md` | TD Python：op()、脚本、扩展 |
| `references/troubleshooting.md` | 连接诊断、调试 |
| `references/glsl.md` | GLSL uniform、内置函数、着色器模板 |
| `references/postfx.md` | 后期特效：辉光、CRT、色差、反馈发光 |
| `references/layout-compositor.md` | HUD 布局模式、面板网格、BSP 风格布局 |
| `references/operator-tips.md` | 线框渲染、反馈 TOP 设置 |
| `references/geometry-comp.md` | Geometry COMP：实例化、POP 与 SOP、变形 |
| `references/audio-reactive.md` | 音频频段提取、节拍检测、包络跟随 |
| `references/animation.md` | LFO、定时器、关键帧、缓动、表达式驱动运动 |
| `references/midi-osc.md` | MIDI/OSC 控制器、TouchOSC、多机同步 |
| `references/particles.md` | POP 和旧版 particleSOP——发射、力、碰撞 |
| `references/projection-mapping.md` | 多窗口输出、角点定位、网格变形、边缘融合 |
| `references/external-data.md` | HTTP、WebSocket、MQTT、串口、TCP、webserverDAT |
| `references/panel-ui.md` | 自定义参数、面板 COMP、按钮/滑块/输入框、panelExecuteDAT |
| `references/replicator.md` | replicatorCOMP——数据驱动克隆、布局、回调 |
| `references/dat-scripting.md` | Execute DAT 家族——chop/dat/parameter/panel/op/executeDAT |
| `references/3d-scene.md` | 灯光系统、阴影、IBL/立方体贴图、多相机、PBR |
| `scripts/setup.sh` | 自动设置脚本 |

---

> 你不是在写代码。你是在指挥光。
