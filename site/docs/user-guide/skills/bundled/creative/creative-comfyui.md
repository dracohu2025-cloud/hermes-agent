---
title: "Comfyui"
sidebar_label: "Comfyui"
description: "使用 ComfyUI 生成图像、视频和音频 — 安装、启动、管理节点/模型、通过参数注入运行工作流"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Comfyui {#comfyui}

使用 ComfyUI 生成图像、视频和音频 — 安装、启动、管理节点/模型、通过参数注入运行工作流。使用官方 comfy-cli 进行生命周期管理，并通过直接 REST/WebSocket API 执行。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/comfyui` |
| 版本 | `5.0.0` |
| 作者 | ['kshitijk4poor', 'alt-glitch'] |
| 许可证 | MIT |
| 平台 | macos, linux, windows |
| 标签 | `comfyui`, `image-generation`, `stable-diffusion`, `flux`, `sd3`, `wan-video`, `hunyuan-video`, `creative`, `generative-ai`, `video-generation` |
| 相关技能 | [`stable-diffusion-image-generation`](/user-guide/skills/optional/mlops/mlops-stable-diffusion), `image_gen` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="comfyui"></a>
# ComfyUI

通过 ComfyUI 生成图像、视频、音频和 3D 内容，使用官方 `comfy-cli` 进行设置/生命周期管理，并通过直接 REST/WebSocket API 执行工作流。

## 此技能包含的内容 {#what-s-in-this-skill}

**参考文档（`references/`）：**

- `official-cli.md` — 所有 `comfy ...` 命令及其标志
- `rest-api.md` — REST + WebSocket 端点（本地 + 云端），负载模式
- `workflow-format.md` — API 格式的 JSON，常见节点类型，参数映射

**脚本（`scripts/`）：**

| 脚本 | 用途 |
|--------|---------|
| `_common.py` | 共享 HTTP、云端路由、节点目录（不要直接运行） |
| `hardware_check.py` | 探测 GPU/VRAM/磁盘 → 推荐本地还是 Comfy Cloud |
| `comfyui_setup.sh` | 硬件检查 + comfy-cli + ComfyUI 安装 + 启动 + 验证 |
| `extract_schema.py` | 读取工作流 → 列出可控参数 + 模型依赖 |
| `check_deps.py` | 对照运行中的服务器检查工作流 → 列出缺失的节点/模型 |
| `auto_fix_deps.py` | 运行 check_deps 然后执行 `comfy node install` / `comfy model download` |
| `run_workflow.py` | 注入参数、提交、监控、下载输出（HTTP 或 WS） |
| `run_batch.py` | 使用扫描参数提交工作流 N 次，根据你的层级并行执行 |
| `ws_monitor.py` | 实时 WebSocket 查看器，用于监控正在执行的作业（实时进度） |
| `health_check.py` | 验证检查清单运行器 — comfy-cli + 服务器 + 模型 + 冒烟测试 |
| `fetch_logs.py` | 拉取指定 prompt_id 的回溯/状态消息 |

**示例工作流（`workflows/`）：** SD 1.5、SDXL、Flux Dev、SDXL img2img、SDXL inpaint、ESRGAN 放大、AnimateDiff 视频、Wan T2V。详见 `workflows/README.md`。

## 何时使用 {#when-to-use}

- 用户要求使用 Stable Diffusion、SDXL、Flux、SD3 等生成图像
- 用户想要运行特定的 ComfyUI 工作流文件
- 用户想要串联生成步骤（txt2img → 放大 → 面部修复）
- 用户需要 ControlNet、inpainting、img2img 或其他高级管线
- 用户要求管理 ComfyUI 队列、检查模型或安装自定义节点
- 用户想要通过 AnimateDiff、Hunyuan、Wan、AudioCraft 等生成视频/音频/3D 内容
## 架构：两层 {#architecture-two-layers}

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────┐
│ 第一层：comfy-cli（官方生命周期工具）                  │
│   安装、服务器生命周期、自定义节点、模型               │
│   → comfy install / launch / stop / node / model    │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│ 第二层：REST/WebSocket API + 技能脚本                │
│   工作流执行、参数注入、监控                          │
│   POST /api/prompt, GET /api/view, WS /ws           │
│   → run_workflow.py, run_batch.py, ws_monitor.py    │
└─────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

**为什么是两层？** 官方 CLI 在安装和服务器管理方面表现出色，但工作流执行支持非常有限。REST/WS API 正好填补了这个空白——这些脚本处理了 CLI 无法完成的参数注入、执行监控和输出下载。

## 快速开始 {#quick-start}

### 检测环境 {#detect-environment}

```bash
# 检查可用的工具
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: 已安装"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "服务器: 运行中"

# 这台机器能否本地运行 ComfyUI？（检查 GPU/VRAM/磁盘）
python3 scripts/hardware_check.py
```

如果什么都没安装，请参考下面的 **安装与上手** 部分——但务必先运行硬件检查。

### 一行命令健康检查 {#one-line-health-check}

```bash
python3 scripts/health_check.py
# → JSON 格式：comfy_cli 是否在 PATH 中？服务器是否可达？至少有一个 checkpoint？冒烟测试是否通过？
```

## 核心工作流 {#core-workflow}

### 第一步：获取 API 格式的工作流 JSON {#step-1-get-a-workflow-json-in-api-format}

工作流必须是 API 格式（每个节点都有 `class_type`）。可以从以下途径获取：

- ComfyUI 网页界面 → **工作流 → 导出（API）**（新版 UI）或
  旧版 UI 的 "保存（API 格式）" 按钮
- 本技能的 `workflows/` 目录（可直接运行的示例）
- 社区下载（civitai、Reddit、Discord）——通常是编辑器格式，
  必须加载到 ComfyUI 中然后重新导出

编辑器格式（顶层 `nodes` 和 `links` 数组）**不能直接执行**。脚本会检测到这种情况并提示你重新导出。

### 第二步：查看可控制的参数 {#step-2-see-what-s-controllable}

```bash
python3 scripts/extract_schema.py workflow_api.json --summary-only
# → {"parameter_count": 12, "has_negative_prompt": true, "has_seed": true, ...}

python3 scripts/extract_schema.py workflow_api.json
# → 完整 schema，包含参数、模型依赖、embedding 引用
```

### 第三步：带参数运行 {#step-3-run-with-parameters}

```bash
# 本地运行（默认使用 http://127.0.0.1:8188）
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": -1, "steps": 30}' \
  --output-dir ./outputs

# 云端运行（只需导出一次 API key；自动使用正确的 /api 路由）
export COMFY_CLOUD_API_KEY="comfyui-..."
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "..."}' \
  --host https://cloud.comfy.org \
  --output-dir ./outputs

# 通过 WebSocket 实时查看进度（需要 `pip install websocket-client`）
python3 scripts/run_workflow.py \
  --workflow flux_dev.json \
  --args '{"prompt": "..."}' \
  --ws

# img2img / inpaint：传入 --input-image 自动上传并引用
python3 scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}'

# 批量 / 扫描：8 个随机种子，并行数不超过云端层级限制
python3 scripts/run_batch.py \
  --workflow sdxl.json \
  --args '{"prompt": "abstract"}' \
  --count 8 --randomize-seed --parallel 3 \
  --output-dir ./outputs/batch
```
`-1` 作为 `seed` 值（或使用 `--randomize-seed` 省略该参数）会在每次运行时生成新的随机种子。

### 步骤 4：展示结果 {#step-4-present-results}

脚本会向标准输出打印 JSON，描述每个输出文件：

```json
{
  "status": "success",
  "prompt_id": "abc-123",
  "outputs": [
    {"file": "./outputs/sdxl_00001_.png", "node_id": "9",
     "type": "image", "filename": "sdxl_00001_.png"}
  ]
}
```

## 决策树 {#decision-tree}

| 用户说 | 工具 | 命令 |
|--------|------|------|
| **生命周期（使用 comfy-cli）** | | |
| "安装 ComfyUI" | comfy-cli | `bash scripts/comfyui_setup.sh` |
| "启动 ComfyUI" | comfy-cli | `comfy launch --background` |
| "停止 ComfyUI" | comfy-cli | `comfy stop` |
| "安装 X 节点" | comfy-cli | `comfy node install &lt;name&gt;` |
| "下载 X 模型" | comfy-cli | `comfy model download --url &lt;url&gt; --relative-path models/checkpoints` |
| "列出已安装的模型" | comfy-cli | `comfy model list` |
| "列出已安装的节点" | comfy-cli | `comfy node show installed` |
| **执行（使用脚本）** | | |
| "一切就绪了吗？" | script | `health_check.py`（可选加 `--workflow X --smoke-test`） |
| "这个工作流里我能改什么？" | script | `extract_schema.py W.json` |
| "检查 W 的依赖是否满足" | script | `check_deps.py W.json` |
| "修复缺失的依赖" | script | `auto_fix_deps.py W.json` |
| "生成一张图片" | script | `run_workflow.py --workflow W --args '{...}'` |
| "使用这张图片"（img2img） | script | `run_workflow.py --input-image image=./x.png ...` |
| "用随机种子生成 8 个变体" | script | `run_batch.py --count 8 --randomize-seed ...` |
| "给我看实时进度" | script | `ws_monitor.py --prompt-id &lt;id&gt;` |
| "从任务 X 获取错误信息" | script | `fetch_logs.py &lt;prompt_id&gt;` |
| **直接 REST** | | |
| "队列里有什么？" | REST | `curl http://HOST:8188/queue`（本地）或 `--host https://cloud.comfy.org` |
| "取消那个" | REST | `curl -X POST http://HOST:8188/interrupt` |
| "释放 GPU 内存" | REST | `curl -X POST http://HOST:8188/free` |

## 安装与上手 {#setup-onboarding}

当用户要求设置 ComfyUI 时，**第一件事是询问他们想要 Comfy Cloud（托管、零安装、API 密钥）还是本地（在自己的机器上安装 ComfyUI）**。在用户回答之前，不要开始运行安装命令或硬件检查。

**官方文档：** https://docs.comfy.org/installation
**CLI 文档：** https://docs.comfy.org/comfy-cli/getting-started
**Cloud 文档：** https://docs.comfy.org/get_started/cloud
**Cloud API：** https://docs.comfy.org/development/cloud/overview

### 步骤 0：询问本地还是 Cloud（始终优先） {#step-0-ask-local-vs-cloud-always-first}

建议的对话脚本：

> "您想在本地机器上运行 ComfyUI，还是使用 Comfy Cloud？
>
> - **Comfy Cloud** — 托管在 RTX 6000 Pro GPU 上，所有常见模型已预装，零设置。需要 API 密钥（实际运行工作流需要付费订阅；免费版只读）。如果您没有合适的 GPU，这是最佳选择。
> - **本地** — 免费，但您的机器必须满足硬件要求：
>   - NVIDIA GPU，**≥6 GB 显存**（SDXL 需要 ≥8 GB，Flux/视频需要 ≥12 GB），或者
>   - AMD GPU，支持 ROCm（Linux），或者
>   - Apple Silicon Mac（M1+），**≥16 GB 统一内存**（推荐 ≥32 GB）。
>   - Intel Mac 和没有 GPU 的机器无法使用——请改用 Cloud。
>
> 您想要哪种？"
路由：

- **云端** → 跳转到**路径 A**。
- **本地** → 先运行硬件检查，然后根据判定结果从路径 B–E 中选择一条。
- **不确定** → 运行硬件检查，让判定结果决定。

### 步骤 1：验证硬件（仅当用户选择本地时） {#step-1-verify-hardware-only-if-user-chose-local}

```bash
python3 scripts/hardware_check.py --json
# 可选：同时探测 `torch` 以获取实际的 CUDA/MPS：
python3 scripts/hardware_check.py --json --check-pytorch
```

| 判定结果      | 含义                                                         | 操作 |
|------------|---------------------------------------------------------------|--------|
| `ok`       | ≥8 GB 显存（独立）或 ≥32 GB 统一内存（Apple Silicon）       | 本地安装 — 使用报告中的 `comfy_cli_flag` |
| `marginal` | SD1.5 可用；SDXL 紧张；Flux/视频不太可能                  | 本地可用于轻量工作流，否则走**路径 A（云端）** |
| `cloud`    | 无可用 GPU、&lt;6 GB 显存、&lt;16 GB Apple 统一内存、Intel Mac、Rosetta Python | **切换到云端**，除非用户明确强制本地 |

脚本还会输出 `wsl: true`（WSL2 带 NVIDIA 直通）和
`rosetta: true`（Apple Silicon 上运行 x86_64 Python — 必须重新安装为 ARM64）。

如果判定结果为 `cloud` 但用户想要本地安装，不要静默继续。
逐字显示 `notes` 数组，并询问用户是否要 (a) 切换到
云端，或 (b) 强制本地安装（在现代模型上会 OOM 或慢到无法使用）。

### 选择安装路径 {#choosing-an-installation-path}

先使用硬件检查。下表是当用户已经告知你硬件信息时的备用方案：

| 情况 | 推荐路径 |
|-----------|------------------|
| 硬件检查结果为 `verdict: cloud` | **路径 A：Comfy Cloud** |
| 无 GPU / 想先试试不承诺 | **路径 A：Comfy Cloud** |
| Windows + NVIDIA + 非技术用户 | **路径 B：ComfyUI Desktop** |
| Windows + NVIDIA + 技术用户 | **路径 C：Portable** 或 **路径 D：comfy-cli** |
| Linux + 任意 GPU | **路径 D：comfy-cli**（最简单） |
| macOS + Apple Silicon | **路径 B：Desktop** 或 **路径 D：comfy-cli** |
| 无头 / 服务器 / CI / Agents | **路径 D：comfy-cli** |

对于全自动路径（硬件检查 → 安装 → 启动 → 验证）：

```bash
bash scripts/comfyui_setup.sh
# 或带覆盖参数：
bash scripts/comfyui_setup.sh --m-series --port=8190 --workspace=/data/comfy
```

它内部会运行 `hardware_check.py`，当判定结果为 `cloud` 时拒绝本地安装（除非使用 `--force-cloud-override`），选择正确的
`comfy-cli` 标志，并优先使用 `pipx`/`uvx` 而非全局 `pip`，以避免污染系统 Python。

---

### 路径 A：Comfy Cloud（无需本地安装） {#path-a-comfy-cloud-no-local-install}

适用于没有合适 GPU 或希望零设置的用户。托管在 RTX 6000 Pro 上。

**文档：** https://docs.comfy.org/get_started/cloud

1. 在 https://comfy.org/cloud 注册
2. 在 https://platform.comfy.org/login 生成 API 密钥
3. 设置密钥：
   ```bash
   export COMFY_CLOUD_API_KEY="comfyui-xxxxxxxxxxxx"
   ```
4. 运行工作流：
   ```bash
   python3 scripts/run_workflow.py \
     --workflow workflows/flux_dev_txt2img.json \
     --args '{"prompt": "..."}' \
     --host https://cloud.comfy.org \
     --output-dir ./outputs
   ```
**定价：** https://www.comfy.org/cloud/pricing  
**并发任务：** 免费/标准版 1 个，创作者版 3 个，专业版 5 个。免费版  
**无法通过 API 运行工作流**——只能浏览模型。需要付费订阅  
才能使用 `/api/prompt`、`/api/upload/*`、`/api/view` 等接口。

---

### 路径 B：ComfyUI Desktop（Windows / macOS） {#path-b-comfyui-desktop-windows-macos}

面向非技术用户的一键安装程序。目前为 Beta 版。

**文档：** https://docs.comfy.org/installation/desktop  
- **Windows（NVIDIA）：** https://download.comfy.org/windows/nsis/x64  
- **macOS（Apple Silicon）：** https://comfy.org  

Linux **不支持** Desktop 版——请使用路径 D。

---

### 路径 C：ComfyUI Portable（仅限 Windows） {#path-c-comfyui-portable-windows-only}

**文档：** https://docs.comfy.org/installation/comfyui_portable_windows  

从 https://github.com/comfyanonymous/ComfyUI/releases 下载，解压，  
运行 `run_nvidia_gpu.bat`。通过 `update/update_comfyui_stable.bat` 更新。

---

### 路径 D：comfy-cli（全平台——推荐用于 Agent） {#path-d-comfy-cli-all-platforms-recommended-for-agents}

官方 CLI 是无头/自动化设置的最佳路径。

**文档：** https://docs.comfy.org/comfy-cli/getting-started  

#### 安装 comfy-cli {#install-comfy-cli}

```bash
# 推荐：
pipx install comfy-cli
# 或者使用 uvx 无需安装：
uvx --from comfy-cli comfy --help
# 或者（如果 pipx/uvx 不可用）：
pip install --user comfy-cli
```

以非交互方式禁用分析：
```bash
comfy --skip-prompt tracking disable
```

#### 安装 ComfyUI {#install-comfyui}

```bash
comfy --skip-prompt install --nvidia              # NVIDIA（CUDA）
comfy --skip-prompt install --amd                 # AMD（ROCm，Linux）
comfy --skip-prompt install --m-series            # Apple Silicon（MPS）
comfy --skip-prompt install --cpu                 # 仅 CPU（较慢）
comfy --skip-prompt install --nvidia --fast-deps  # 基于 uv 的依赖解析
```

默认位置：`~/comfy/ComfyUI`（Linux），`~/Documents/comfy/ComfyUI`  
（macOS/Win）。可通过 `comfy --workspace /custom/path install` 覆盖。

#### 启动 / 验证 {#launch-verify}

```bash
comfy launch --background                       # 后台守护进程，端口 :8188
comfy launch -- --listen 0.0.0.0 --port 8190    # 局域网可访问的自定义端口
curl -s http://127.0.0.1:8188/system_stats      # 健康检查
```

---

### 路径 E：手动安装（高级 / 不支持的硬件） {#path-e-manual-install-advanced-unsupported-hardware}

适用于 Ascend NPU、Cambricon MLU、Intel Arc 或其他不支持的硬件。

**文档：** https://docs.comfy.org/installation/manual_install  

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

---

### 安装后：下载模型 {#post-install-download-models}

```bash
# SDXL（通用，约 6.5 GB）
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5（更轻量，约 4 GB，适合 6 GB 显存显卡）
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8（较小变体，约 12 GB）
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI（先设置 token）：
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```
列出已安装的模型：`comfy model list`。

### 安装后：安装自定义节点 {#post-install-install-custom-nodes}

```bash
comfy node install comfyui-impact-pack             # 常用工具包
comfy node install comfyui-animatediff-evolved     # 视频生成
comfy node install comfyui-controlnet-aux          # ControlNet 预处理器
comfy node install comfyui-essentials              # 常用辅助工具
comfy node update all
comfy node install-deps --workflow=workflow.json   # 安装工作流所需的所有依赖
```

### 安装后：验证 {#post-install-verify}

```bash
python3 scripts/health_check.py
# → comfy_cli 是否在 PATH 中？服务器是否可达？检查点？冒烟测试？

python3 scripts/check_deps.py my_workflow.json
# → 该工作流的节点/模型/嵌入是否已安装？

python3 scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```

## 图片上传（img2img / Inpainting） {#image-upload-img2img-inpainting}

最简单的方式是使用 `run_workflow.py` 的 `--input-image` 参数：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it cyberpunk", "denoise": 0.6}'
```

该标志会上传 `photo.png`，然后将其服务端文件名注入到名为 `image` 的 schema 参数中。对于 inpainting，需要同时传入两个参数：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_inpaint.json \
  --input-image image=./photo.png \
  --input-image mask_image=./mask.png \
  --args '{"prompt": "fill with flowers"}'
```

通过 REST 手动上传：
```bash
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# 返回：{"name": "photo.png", "subfolder": "", "type": "input"}

# 云端等效命令：
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```

## 云端细节 {#cloud-specifics}

- **基础 URL：** `https://cloud.comfy.org`
- **认证：** `X-API-Key` 请求头（WebSocket 也可用 `?token=KEY`）
- **API 密钥：** 设置 `$COMFY_CLOUD_API_KEY` 一次，脚本会自动读取
- **输出下载：** `/api/view` 返回一个 302 重定向到签名 URL；脚本会跟随该重定向，并在从存储后端获取之前剥离 `X-API-Key`（不要将 API 密钥泄露给 S3/CloudFront）。
- **与本地 ComfyUI 的端点差异：**
  - `/api/object_info`、`/api/queue`、`/api/userdata` — **免费套餐返回 403**；仅付费套餐可用。
  - `/history` 在云端重命名为 `/history_v2`（脚本会自动路由）。
  - `/models/&lt;folder&gt;` 在云端重命名为 `/experiment/models/&lt;folder&gt;`（脚本会自动路由）。
  - WebSocket 中的 `clientId` 当前被忽略——同一用户的所有连接会收到相同的广播。请在客户端按 `prompt_id` 过滤。
  - 上传时接受 `subfolder` 但会被忽略——云端使用扁平命名空间。
- **并发任务：** 免费/标准：1，创作者：3，专业：5。额外任务会自动排队。使用 `run_batch.py --parallel N` 来充分利用你的套餐。
## 队列与系统管理 {#queue-system-management}

```bash
# 本地
curl -s http://127.0.0.1:8188/queue | python3 -m json.tool
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'    # 取消待处理任务
curl -X POST http://127.0.0.1:8188/interrupt                      # 取消正在运行的任务
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# 云端 — 路径相同，位于 /api/ 下，另加：
python3 scripts/fetch_logs.py --tail-queue --host https://cloud.comfy.org
```

## 注意事项 {#pitfalls}

1. **需要 API 格式** — 所有脚本和 `/api/prompt` 端点都要求使用 API 格式的工作流 JSON。脚本会检测编辑器格式（顶层包含 `nodes` 和 `links` 数组），并提示你通过“Workflow → Export (API)”（新版 UI）或“Save (API Format)”（旧版 UI）重新导出。

2. **服务器必须运行** — 所有执行都需要一个正在运行的服务器。`comfy launch --background` 会启动一个。用 `curl http://127.0.0.1:8188/system_stats` 验证。

3. **模型名称必须精确** — 区分大小写，包含文件扩展名。`check_deps.py` 会进行模糊匹配（带/不带扩展名和文件夹前缀），但工作流本身必须使用规范名称。用 `comfy model list` 查看已安装的模型。

4. **缺少自定义节点** — 出现“class_type not found”表示所需的节点未安装。`check_deps.py` 会报告需要安装哪个包；`auto_fix_deps.py` 会为你自动安装。

5. **工作目录** — `comfy-cli` 会自动检测 ComfyUI 工作区。如果命令失败并提示“no workspace found”，请使用 `comfy --workspace /path/to/ComfyUI &lt;command&gt;` 或 `comfy set-default /path/to/ComfyUI`。

6. **云免费版 API 限制** — 免费账户下，`/api/prompt`、`/api/view`、`/api/upload/*`、`/api/object_info` 都会返回 403。`health_check.py` 和 `check_deps.py` 会优雅处理并给出明确提示。

7. **视频/音频工作流超时** — 当输出节点为 `VHS_VideoCombine`、`SaveVideo` 等时，会自动检测；默认超时从 300 秒提升到 900 秒。可以用 `--timeout 1800` 显式覆盖。

8. **输出文件名中的路径遍历** — 服务器提供的文件名会经过 `safe_path_join` 处理，拒绝任何试图逃逸 `--output-dir` 的内容。请保持此保护开启——带有自定义保存节点的工作流可能产生任意路径。

9. **工作流 JSON 是任意代码** — 自定义节点会运行 Python，因此提交未知工作流与 `eval` 具有相同的信任风险。在运行前请检查来自不可信来源的工作流。

10. **自动随机种子** — 在 `--args` 中传递 `seed: -1`（或使用 `--randomize-seed` 并省略 seed）即可每次运行获得新种子。实际种子会记录到 stderr。

11. **`tracking` 提示** — 首次运行 `comfy` 时可能会弹出分析统计提示。使用 `comfy --skip-prompt tracking disable` 以非交互方式跳过。`comfyui_setup.sh` 会自动为你处理。

## 验证清单 {#verification-checklist}

使用 `python3 scripts/health_check.py` 一次性运行所有检查。手动检查：
- [ ] `hardware_check.py` 的判定结果为 `ok`，或者用户明确选择了 Comfy Cloud
- [ ] `comfy --version` 命令可正常执行（或 `uvx --from comfy-cli comfy --help`）
- [ ] `curl http://HOST:PORT/system_stats` 返回 JSON
- [ ] `comfy model list` 显示至少一个检查点（本地）或 `/api/experiment/models/checkpoints` 返回模型（云端）
- [ ] 工作流 JSON 为 API 格式
- [ ] `check_deps.py` 报告 `is_ready: true`（或在云端免费套餐中仅报告 `node_check_skipped`）
- [ ] 使用小型工作流进行测试运行并成功完成；输出文件位于 `--output-dir` 目录中
