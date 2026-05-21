---
title: "Llama Cpp — llama"
sidebar_label: "Llama Cpp"
description: "llama"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

<a id="llama-cpp"></a>
# Llama Cpp

llama.cpp 本地 GGUF 推理 + HF Hub 模型发现。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/llama-cpp` |
| 版本 | `2.1.2` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `llama-cpp-python>=0.2.0` |
| 支持平台 | linux, macos, windows |
| 标签 | `llama.cpp`, `GGUF`, `Quantization`, `Hugging Face Hub`, `CPU Inference`, `Apple Silicon`, `Edge Deployment`, `AMD GPUs`, `Intel GPUs`, `NVIDIA`, `URL-first` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。这就是技能激活时 Agent 看到的指令。
:::

<a id="llama-cpp-gguf"></a>
# llama.cpp + GGUF

在需要时使用此技能进行本地 GGUF 推理、量化选择或针对 llama.cpp 的 Hugging Face 仓库发现。

<a id="when-to-use"></a>
## 使用时机

- 在 CPU、Apple Silicon、CUDA、ROCm 或 Intel GPU 上运行本地模型
- 为特定 Hugging Face 仓库找到合适的 GGUF 文件
- 基于 Hub 构建 `llama-server` 或 `llama-cli` 命令
- 在 Hub 上搜索已支持 llama.cpp 的模型
- 枚举某个仓库中可用的 `.gguf` 文件及其大小
- 根据用户的 RAM 或 VRAM 在 Q4/Q5/Q6/IQ 变体之间做选择

<a id="model-discovery-workflow"></a>
## 模型发现工作流

在请求使用 `hf`、Python 或自定义脚本之前，优先使用 URL 工作流。

1. 在 Hub 上搜索候选仓库：
   - 基础：`https://huggingface.co/models?apps=llama.cpp&sort=trending`
   - 添加 `search=&lt;term&gt;` 以限定模型家族
   - 当用户有大小限制时，添加 `num_parameters=min:0,max:24B` 等参数
2. 使用 llama.cpp 本地应用视图打开仓库：
   - `https://huggingface.co/&lt;repo&gt;?local-app=llama.cpp`
3. 当本地应用片段可见时，将其视为信息来源：
   - 复制准确的 `llama-server` 或 `llama-cli` 命令
   - 按 HF 显示的内容报告推荐的量化方式
4. 以页面文本或 HTML 方式读取相同的 `?local-app=llama.cpp` URL，并提取 `Hardware compatibility`（硬件兼容性）部分：
   - 优先使用该部分给出的精确量化标签和大小，而非通用表格
   - 保留仓库特有的标签，如 `UD-Q4_K_M` 或 `IQ4_NL_XL`
   - 如果该部分在抓取的页面源码中不可见，则说明情况并回退到树 API 加上通用量化指导
5. 查询树 API 以确认实际存在的内容：
   - `https://huggingface.co/api/models/&lt;repo&gt;/tree/main?recursive=true`
   - 仅保留 `type` 为 `file` 且 `path` 以 `.gguf` 结尾的条目
   - 使用 `path` 和 `size` 作为文件名和字节大小的真实来源
   - 将量化检查点与 `mmproj-*.gguf` 投影文件以及 `BF16/` 分片文件分开
   - 仅将 `https://huggingface.co/&lt;repo&gt;/tree/main` 作为人工备选方案
6. 如果本地应用片段不可见文本，则根据仓库及所选量化方式重建命令：
   - 简写量化选择：`llama-server -hf &lt;repo&gt;:&lt;QUANT&gt;`
   - 精确文件回退：`llama-server --hf-repo &lt;repo&gt; --hf-file &lt;filename.gguf&gt;`
7. 只有当仓库尚未暴露 GGUF 文件时，才建议从 Transformers 权重进行转换。
<a id="quick-start"></a>
## 快速开始

<a id="install-llama-cpp"></a>
### 安装 llama.cpp

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

<a id="run-directly-from-the-hugging-face-hub"></a>
### 直接从 Hugging Face Hub 运行

```bash
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

```bash
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

<a id="run-an-exact-gguf-file-from-the-hub"></a>
### 从 Hub 运行确切的 GGUF 文件

当树形 API 显示自定义文件命名或缺少确切的 HF 片段时使用此方式。

```bash
llama-server \
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf \
    -c 4096
```

<a id="openai-compatible-server-check"></a>
### OpenAI 兼容服务器检查

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "写一首关于 Python 异常的打油诗"}
    ]
  }'
```

<a id="python-bindings-llama-cpp-python"></a>
## Python 绑定（llama-cpp-python）

`pip install llama-cpp-python`（CUDA：`CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir`；Metal：`CMAKE_ARGS="-DGGML_METAL=on" ...`）。

<a id="basic-generation"></a>
### 基本生成

```python
from llama_cpp import Llama

llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,     # CPU 设为 0，全部卸载到 GPU 设为 99
    n_threads=8,
)

out = llm("什么是机器学习？", max_tokens=256, temperature=0.7)
print(out["choices"][0]["text"])
```

<a id="chat-streaming"></a>
### 聊天 + 流式输出

```python
llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    chat_format="llama-3",   # 或 "chatml"、"mistral" 等
)

resp = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "什么是 Python？"},
    ],
    max_tokens=256,
)
print(resp["choices"][0]["message"]["content"])

# 流式输出
for chunk in llm("解释一下量子计算：", max_tokens=256, stream=True):
    print(chunk["choices"][0]["text"], end="", flush=True)
```

<a id="embeddings"></a>
### 嵌入向量

```python
llm = Llama(model_path="./model-q4_k_m.gguf", embedding=True, n_gpu_layers=35)
vec = llm.embed("这是一个测试句子。")
print(f"嵌入向量维度：{len(vec)}")
```

你也可以直接从 Hub 加载 GGUF：

```python
llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf",
    n_gpu_layers=35,
)
```

<a id="choosing-a-quant"></a>
## 选择量化版本

先参考 Hub 页面，再使用通用启发式规则。

- 优先选择 HF 上标记为与用户硬件配置兼容的精确量化版本。
- 对于常规聊天，从 `Q4_K_M` 开始。
- 对于代码或技术类工作，如果内存允许，优先选择 `Q5_K_M` 或 `Q6_K`。
- 对于极紧的内存预算，考虑 `Q3_K_M`、`IQ` 变体，或仅当用户明确优先考虑容量而非质量时才使用 `Q2` 变体。
- 对于多模态仓库，需单独提及 `mmproj-*.gguf`。投影文件不是主模型文件。
- 不要标准化仓库自带的标签。如果页面显示 `UD-Q4_K_M`，就报告 `UD-Q4_K_M`。
<a id="extracting-available-ggufs-from-a-repo"></a>
## 从仓库中提取可用的 GGUF 文件

当用户询问存在哪些 GGUF 文件时，返回：

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

对于像 `unsloth/Qwen3.6-35B-A3B-GGUF` 这样的仓库，本地应用页面可以显示诸如 `UD-Q4_K_M`、`UD-Q5_K_M`、`UD-Q6_K` 和 `Q8_0` 这样的量化芯片，而 tree API 则暴露了确切的文件路径，例如 `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` 和 `Qwen3.6-35B-A3B-Q8_0.gguf` 及其字节大小。使用 tree API 将量化标签转换为确切的文件名。

<a id="search-patterns"></a>
## 搜索模式

直接使用以下 URL 格式：

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
https://huggingface.co/<repo>/tree/main
```

<a id="output-format"></a>
## 输出格式

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

<a id="references"></a>
## 参考资料

- **[hub-discovery.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/hub-discovery.md)** - 仅 URL 的 Hugging Face 工作流、搜索模式、GGUF 提取和命令重构
- **[advanced-usage.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/advanced-usage.md)** — 推测解码、批量推理、语法约束生成、LoRA、多 GPU、自定义构建、基准测试脚本
- **[quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/quantization.md)** — 量化质量权衡、何时使用 Q4/Q5/Q6/IQ、模型大小缩放、imatrix
- **[server.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/server.md)** — 直接从 Hub 启动服务器、OpenAI API 端点、Docker 部署、NGINX 负载均衡、监控
- **[optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/optimization.md)** — CPU 线程、BLAS、GPU 卸载启发式、批处理调优、基准测试
- **[troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/llama-cpp/references/troubleshooting.md)** — 安装/转换/量化/推理/服务器问题、Apple Silicon、调试

<a id="resources"></a>
## 资源

- **GitHub**: https://github.com/ggml-org/llama.cpp
- **Hugging Face GGUF + llama.cpp 文档**: https://huggingface.co/docs/hub/gguf-llamacpp
- **Hugging Face 本地应用文档**: https://huggingface.co/docs/hub/main/local-apps
- **Hugging Face 本地 Agent 文档**: https://huggingface.co/docs/hub/agents-local
- **本地应用页面示例**: https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF?local-app=llama.cpp
- **tree API 示例**: https://huggingface.co/api/models/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main?recursive=true
- **llama.cpp 搜索示例**: https://huggingface.co/models?num_parameters=min:0,max:24B&apps=llama.cpp&sort=trending
- **许可证**: MIT
