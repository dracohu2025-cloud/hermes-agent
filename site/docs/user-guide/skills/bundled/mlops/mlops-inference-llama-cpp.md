---
title: "Llama Cpp — llama"
sidebar_label: "Llama Cpp"
description: "llama"
---

{/* 此页面由 skills 目录下的 SKILL.md 经 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Llama Cpp {#llama-cpp}

llama.cpp 本地 GGUF 推理 + HF Hub 模型搜索。

## 技能元信息 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/llama-cpp` |
| 版本 | `2.1.2` |
| 作者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖 | `llama-cpp-python>=0.2.0` |
| 标签 | `llama.cpp`、`GGUF`、`量化`、`Hugging Face Hub`、`CPU 推理`、`Apple Silicon`、`边缘部署`、`AMD GPU`、`Intel GPU`、`NVIDIA`、`URL优先` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活后 Agent 看到的指令。
:::

# llama.cpp + GGUF {#llama-cpp-gguf}

使用此技能进行本地 GGUF 推理、量化选择或为 llama.cpp 搜索 Hugging Face 仓库。

## 何时使用 {#when-to-use}

- 在 CPU、Apple Silicon、CUDA、ROCm 或 Intel GPU 上运行本地模型
- 为特定的 Hugging Face 仓库找到合适的 GGUF
- 从 Hub 构建 `llama-server` 或 `llama-cli` 命令
- 在 Hub 中搜索已支持 llama.cpp 的模型
- 枚举仓库中可用的 `.gguf` 文件及其大小
- 根据用户的 RAM 或 VRAM 决定使用 Q4/Q5/Q6/IQ 变体

## 模型搜索工作流 {#model-discovery-workflow}

在询问 `hf`、Python 或自定义脚本之前，优先使用 URL 工作流。

1. 在 Hub 上搜索候选仓库：
   - 基础链接：`https://huggingface.co/models?apps=llama.cpp&sort=trending`
   - 添加 `search=&lt;term&gt;` 来搜索特定模型家族
   - 当用户有大小限制时，添加 `num_parameters=min:0,max:24B` 等参数
2. 使用 llama.cpp 本地应用视图打开仓库：
   - `https://huggingface.co/&lt;repo&gt;?local-app=llama.cpp`
3. 当本地应用代码段可见时，将其视为权威来源：
   - 复制准确的 `llama-server` 或 `llama-cli` 命令
   - 报告 Hub 显示的推荐量化类型
4. 以页面文本或 HTML 形式读取相同的 `?local-app=llama.cpp` URL，提取 `硬件兼容性` 部分：
   - 优先使用其确切的量化标签和大小，而非通用表格
   - 保留仓库特有的标签，如 `UD-Q4_K_M` 或 `IQ4_NL_XL`
   - 如果在获取的页面源码中该部分不可见，则说明情况并回退到树 API 加上通用量化指导
5. 查询树 API 以确认实际存在的文件：
   - `https://huggingface.co/api/models/&lt;repo&gt;/tree/main?recursive=true`
   - 保留 `type` 为 `file` 且 `path` 以 `.gguf` 结尾的条目
   - 以 `path` 和 `size` 作为文件名和字节大小的权威来源
   - 将量化的检查点与 `mmproj-*.gguf` 投影文件及 `BF16/` 分片文件分开
   - 仅将 `https://huggingface.co/&lt;repo&gt;/tree/main` 作为人工回退手段
6. 如果本地应用代码段不可见为文本，则根据仓库和所选量化重建命令：
   - 简写量化选择：`llama-server -hf &lt;repo&gt;:&lt;QUANT&gt;`
   - 精确文件回退：`llama-server --hf-repo &lt;repo&gt; --hf-file &lt;filename.gguf&gt;`
7. 仅当仓库尚未暴露 GGUF 文件时，才建议从 Transformers 权重进行转换。
## 快速开始 {#quick-start}

### 安装 llama.cpp {#install-llama-cpp}

```bash
# macOS / Linux（最简单）
brew install llama.cpp
```

```bash
winget install llama.cpp
```

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

### 直接从 Hugging Face Hub 运行 {#run-directly-from-the-hugging-face-hub}

```bash
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

```bash
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

### 从 Hub 运行指定的 GGUF 文件 {#run-an-exact-gguf-file-from-the-hub}

当树形 API 显示自定义文件名或缺少准确的 HF 代码片段时，使用此方式。

```bash
llama-server \
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf \
    -c 4096
```

### 检查 OpenAI 兼容服务器 {#openai-compatible-server-check}

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "写一首关于 Python 异常的打油诗"}
    ]
  }'
```

## Python 绑定（llama-cpp-python） {#python-bindings-llama-cpp-python}

`pip install llama-cpp-python`（CUDA：`CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir`；Metal：`CMAKE_ARGS="-DGGML_METAL=on" ...`）。

### 基础生成 {#basic-generation}

```python
from llama_cpp import Llama

llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,     # 0 表示 CPU，99 表示全部卸载到 GPU
    n_threads=8,
)

out = llm("什么是机器学习？", max_tokens=256, temperature=0.7)
print(out["choices"][0]["text"])
```

### 对话 + 流式输出 {#chat-streaming}

```python
llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    chat_format="llama-3",   # 或 "chatml"、"mistral" 等
)

resp = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "你是一个乐于助人的助手。"},
        {"role": "user", "content": "什么是 Python？"},
    ],
    max_tokens=256,
)
print(resp["choices"][0]["message"]["content"])

# 流式输出
for chunk in llm("解释量子计算：", max_tokens=256, stream=True):
    print(chunk["choices"][0]["text"], end="", flush=True)
```

### 嵌入向量 {#embeddings}

```python
llm = Llama(model_path="./model-q4_k_m.gguf", embedding=True, n_gpu_layers=35)
vec = llm.embed("这是一个测试句子。")
print(f"嵌入维度：{len(vec)}")
```

你也可以直接从 Hub 加载 GGUF 文件：

```python
llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf",
    n_gpu_layers=35,
)
```

## 选择量化版本 {#choosing-a-quant}

优先使用 Hub 页面，其次使用通用启发式规则。

- 优先选择 HF 标记为与用户硬件配置兼容的精确量化版本。
- 对于通用对话，从 `Q4_K_M` 开始。
- 对于代码或技术工作，如果内存允许，优先选择 `Q5_K_M` 或 `Q6_K`。
- 对于内存非常紧张的情况，考虑 `Q3_K_M`、`IQ` 变体，或仅在用户明确优先考虑适配而非质量时使用 `Q2` 变体。
- 对于多模态仓库，单独提及 `mmproj-*.gguf`。投影文件不是主模型文件。
- 不要规范化仓库自带的标签。如果页面显示 `UD-Q4_K_M`，就报告 `UD-Q4_K_M`。
## 从仓库中提取可用的 GGUF 文件 {#extracting-available-ggufs-from-a-repo}

当用户询问存在哪些 GGUF 时，返回：

- 文件名
- 文件大小
- 量化标签
- 是主模型还是辅助投影模型

除非被要求，否则忽略：

- README
- BF16 分片文件
- imatrix 数据块或校准产物

此步骤使用 tree API：

- `https://huggingface.co/api/models/&lt;repo&gt;/tree/main?recursive=true`

对于像 `unsloth/Qwen3.6-35B-A3B-GGUF` 这样的仓库，本地应用页面可以显示诸如 `UD-Q4_K_M`、`UD-Q5_K_M`、`UD-Q6_K` 和 `Q8_0` 的量化芯片，而 tree API 则暴露精确的文件路径，例如 `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` 和 `Qwen3.6-35B-A3B-Q8_0.gguf` 及其字节大小。使用 tree API 将量化标签转换为精确的文件名。

## 搜索模式 {#search-patterns}

直接使用以下 URL 格式：

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
https://huggingface.co/<repo>/tree/main
```

## 输出格式 {#output-format}

在回答发现请求时，优先使用紧凑的结构化结果，例如：

```text
Repo: <repo>
Recommended quant from HF: <label> (<size>)
llama-server: <command>
Other GGUFs:
- <filename> - <size>
- <filename> - <size>
Source URLs:
- <local-app URL>
- <tree API URL>
```

## 参考 {#references}

- **[hub-discovery.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/hub-discovery.md)** — 仅 URL 的 Hugging Face 工作流、搜索模式、GGUF 提取和命令重构
- **[advanced-usage.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/advanced-usage.md)** — 推测解码、批量推理、语法约束生成、LoRA、多 GPU、自定义构建、基准脚本
- **[quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/quantization.md)** — 量化质量权衡、何时使用 Q4/Q5/Q6/IQ、模型大小缩放、imatrix
- **[server.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/server.md)** — 直接从 Hub 启动服务器、OpenAI API 端点、Docker 部署、NGINX 负载均衡、监控
- **[optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/optimization.md)** — CPU 线程、BLAS、GPU 卸载启发式、批量调优、基准测试
- **[troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/troubleshooting.md)** — 安装/转换/量化/推理/服务器问题、Apple Silicon、调试

## 资源 {#resources}

- **GitHub**：https://github.com/ggml-org/llama.cpp
- **Hugging Face GGUF + llama.cpp 文档**：https://huggingface.co/docs/hub/gguf-llamacpp
- **Hugging Face 本地应用文档**：https://huggingface.co/docs/hub/main/local-apps
- **Hugging Face 本地 Agent 文档**：https://huggingface.co/docs/hub/agents-local
- **本地应用页面示例**：https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF?local-app=llama.cpp
- **tree API 示例**：https://huggingface.co/api/models/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main?recursive=true
- **llama.cpp 搜索示例**：https://huggingface.co/models?num_parameters=min:0,max:24B&apps=llama.cpp&sort=trending
- **许可证**：MIT
