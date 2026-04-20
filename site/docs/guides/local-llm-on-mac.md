---
sidebar_position: 2
title: "在 Mac 上运行本地 LLM"
description: "通过 llama.cpp 或 MLX 在 macOS 上设置兼容 OpenAI 的本地 LLM 服务器，包括模型选择、内存优化以及 Apple Silicon 上的真实基准测试"
---

# 在 Mac 上运行本地 LLM {#run-local-llms-on-mac}

本指南将引导你通过兼容 OpenAI 的 API 在 macOS 上运行本地 LLM 服务器。你将获得完全的隐私保护、零 API 成本，并在 Apple Silicon 上获得出色的性能。

我们涵盖了两种后端：

| 后端 | 安装 | 优势 | 格式 |
|---------|---------|---------|--------|
| **llama.cpp** | `brew install llama.cpp` | 首字响应速度最快，量化 KV 缓存以节省内存 | GGUF |
| **omlx** | [omlx.ai](https://omlx.ai) | 生成速度最快，原生 Metal 优化 | MLX (safetensors) |

两者都提供兼容 OpenAI 的 `/v1/chat/completions` 端点。Hermes 可以与其中任何一个配合使用——只需将其指向 `http://localhost:8080` 或 `http://localhost:8000` 即可。

:::info 仅限 Apple Silicon
本指南针对搭载 Apple Silicon（M1 及更高版本）的 Mac。Intel Mac 可以使用 llama.cpp，但没有 GPU 加速——性能会显著降低。
:::

---

## 选择模型 {#choosing-a-model}

对于入门，我们推荐 **Qwen3.5-9B**——它是一个强大的推理模型，在 8GB 以上统一内存的设备上，配合量化技术可以轻松运行。

| 变体 | 磁盘占用 | 所需内存 (128K 上下文) | 后端 |
|---------|-------------|---------------------------|---------|
| Qwen3.5-9B-Q4_K_M (GGUF) | 5.3 GB | ~10 GB（含量化 KV 缓存） | llama.cpp |
| Qwen3.5-9B-mlx-lm-mxfp4 (MLX) | ~5 GB | ~12 GB | omlx |
<a id="apple-silicon-only"></a>

**内存经验法则：** 模型大小 + KV 缓存。9B Q4 模型约为 5 GB。在 128K 上下文且使用 Q4 量化时，KV 缓存会增加约 4-5 GB。如果使用默认的 (f16) KV 缓存，内存占用会激增至约 16 GB。llama.cpp 中的量化 KV 缓存标志是内存受限系统的关键技巧。

对于更大的模型（27B、35B），你需要 32 GB 以上的统一内存。9B 模型是 8-16 GB 内存机器的最佳选择。

---

## 选项 A：llama.cpp {#option-a-llama-cpp}

llama.cpp 是最通用的本地 LLM 运行时。在 macOS 上，它开箱即用，利用 Metal 进行 GPU 加速。

### 安装 {#install}

```bash
brew install llama.cpp
```

这将在全局安装 `llama-server` 命令。

### 下载模型 {#download-the-model}

你需要 GGUF 格式的模型。最简单的方法是通过 `huggingface-cli` 从 Hugging Face 下载：

```bash
brew install huggingface-cli
```

然后下载：

```bash
huggingface-cli download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf --local-dir ~/models
```

:::tip 受限模型
Hugging Face 上的某些模型需要身份验证。如果遇到 401 或 404 错误，请先运行 `huggingface-cli login`。
:::

### 启动服务器 {#start-the-server}

```bash
llama-server -m ~/models/Qwen3.5-9B-Q4_K_M.gguf \
  -ngl 99 \
  -c 131072 \
<a id="gated-models"></a>
  -np 1 \
  -fa on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --host 0.0.0.0
```

以下是各标志的作用：

| 标志 | 用途 |
|------|---------|
| `-ngl 99` | 将所有层卸载到 GPU (Metal)。使用较大的数值以确保模型完全在 GPU 上运行。 |
| `-c 131072` | 上下文窗口大小（128K token）。如果内存不足，请减小此值。 |
| `-np 1` | 并行槽位数量。单用户使用时保持为 1——更多的槽位会瓜分你的内存预算。 |
| `-fa on` | Flash attention。减少内存使用并加速长上下文推理。 |
| `--cache-type-k q4_0` | 将 Key 缓存量化为 4-bit。**这是节省内存的大杀器。** |
| `--cache-type-v q4_0` | 将 Value 缓存量化为 4-bit。与上述配合，相比 f16 可减少约 75% 的 KV 缓存内存占用。 |
| `--host 0.0.0.0` | 监听所有接口。如果不需要网络访问，请使用 `127.0.0.1`。 |

当看到以下输出时，服务器即已就绪：

```
main: server is listening on http://0.0.0.0:8080
srv  update_slots: all slots are idle
```

### 针对受限系统的内存优化 {#memory-optimization-for-constrained-systems}

`--cache-type-k q4_0 --cache-type-v q4_0` 标志是内存受限系统最重要的优化手段。以下是 128K 上下文下的影响：

| KV 缓存类型 | KV 缓存内存 (128K 上下文, 9B 模型) |
|---------------|--------------------------------------|
| f16 (默认) | ~16 GB |
| q8_0 | ~8 GB |
| **q4_0** | **~4 GB** |

在 8 GB 内存的 Mac 上，请使用 `q4_0` KV 缓存并将上下文减小至 `-c 32768` (32K)。在 16 GB 内存的机器上，你可以轻松运行 128K 上下文。在 32 GB 以上的机器上，你可以运行更大的模型或多个并行槽位。

如果仍然内存不足，请先减小上下文大小 (`-c`)，然后尝试更小的量化版本（例如使用 Q3_K_M 代替 Q4_K_M）。

### 测试 {#test-it}

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 获取模型名称 {#get-the-model-name}

如果你忘记了模型名称，可以查询模型端点：

```bash
curl -s http://localhost:8080/v1/models | jq '.data[].id'
```

---

## 选项 B：通过 omlx 使用 MLX {#option-b-mlx-via-omlx}

[omlx](https://omlx.ai) 是一款 macOS 原生应用，用于管理和运行 MLX 模型。MLX 是苹果自家的机器学习框架，专门针对 Apple Silicon 的统一内存架构进行了优化。

<a id="install"></a>
### 安装

从 [omlx.ai](https://omlx.ai) 下载并安装。它提供了用于模型管理的图形界面和内置服务器。

<a id="download-the-model"></a>
### 下载模型

使用 omlx 应用浏览并下载模型。搜索 `Qwen3.5-9B-mlx-lm-mxfp4` 并下载。模型存储在本地（通常位于 `~/.omlx/models/`）。

<a id="start-the-server"></a>
### 启动服务器

omlx 默认在 `http://127.0.0.1:8000` 上提供服务。通过应用界面启动服务，或者在可用时使用 CLI。

<a id="test-it"></a>
### 测试

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-mlx-lm-mxfp4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 列出可用模型 {#list-available-models}

omlx 可以同时运行多个模型：

```bash
curl -s http://127.0.0.1:8000/v1/models | jq '.data[].id'
```

---

## 基准测试：llama.cpp vs MLX {#benchmarks-llama-cpp-vs-mlx}

两个后端均在同一台机器（Apple M5 Max，128 GB 统一内存）上进行测试，运行相同的模型 (Qwen3.5-9B) 和相当的量化级别（GGUF 使用 Q4_K_M，MLX 使用 mxfp4）。测试包含五个不同的提示词，每个运行三次，后端依次测试以避免资源争用。

### 结果 {#results}

| 指标 | llama.cpp (Q4_K_M) | MLX (mxfp4) | 胜出者 |
|--------|-------------------|-------------|--------|
| **TTFT (平均)** | **67 ms** | 289 ms | llama.cpp (快 4.3 倍) |
| **TTFT (p50)** | **66 ms** | 286 ms | llama.cpp (快 4.3 倍) |
| **生成速度 (平均)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **生成速度 (p50)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **总耗时 (512 tokens)** | 7.3s | **5.5s** | MLX (快 25%) |

### 结论 {#what-this-means}

- **llama.cpp** 在提示词处理方面表现出色——其 Flash attention + 量化 KV 缓存流水线能让你在约 66ms 内获得第一个 token。如果你正在构建注重交互响应的应用（如聊天机器人、自动补全），这是一个显著的优势。

- **MLX** 一旦开始生成，速度比 llama.cpp 快约 37%。对于批处理任务、长文本生成或任何总完成时间比初始延迟更重要的任务，MLX 完成得更快。

- 两个后端的表现都**极其稳定**——多次运行之间的差异微乎其微。你可以信赖这些数据。

### 你应该选择哪一个？ {#which-one-should-you-pick}

| 使用场景 | 推荐 |
|----------|---------------|
| 交互式聊天、低延迟工具 | llama.cpp |
| 长文本生成、批量处理 | MLX (omlx) |
| 内存受限 (8-16 GB) | llama.cpp (量化 KV 缓存无可匹敌) |
| 同时运行多个模型 | omlx (内置多模型支持) |
| 最大兼容性 (包括 Linux) | llama.cpp |

---

## 连接到 Hermes {#connect-to-hermes}

本地服务器运行后：

```bash
hermes model
```

选择 **Custom endpoint** 并按照提示操作。它会要求输入基础 URL 和模型名称——使用你在上面设置的任何后端对应的值即可。

---

## 超时设置 {#timeouts}

Hermes 会自动检测本地端点（localhost、局域网 IP）并放宽其流式传输超时限制。对于大多数设置，无需进行任何配置。

---
如果你仍然遇到超时错误（例如在慢速硬件上处理超大上下文时），你可以覆盖流式读取的超时设置：

```bash
# 在你的 .env 文件中 — 将默认的 120 秒提升至 30 分钟
HERMES_STREAM_READ_TIMEOUT=1800
```

| 超时类型 | 默认值 | 本地自动调整 | 环境变量覆盖 |
|---------|---------|----------------------|------------------|
| 流式读取 (Socket 级别) | 120s | 提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 过期流检测 | 180s | 完全禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API 调用 (非流式) | 1800s | 无需更改 | `HERMES_API_TIMEOUT` |

流式读取超时是最容易引发问题的设置——它是接收下一个数据块的 Socket 级别截止时间。在处理大上下文的预填充（prefill）阶段，本地模型在处理提示词时可能会有几分钟不输出任何内容。自动检测功能可以透明地处理这种情况。
