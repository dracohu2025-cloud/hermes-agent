---
title: "Modal Serverless Gpu — 用于运行 ML 工作负载的无服务器 GPU 云平台"
sidebar_label: "Modal Serverless Gpu"
description: "用于运行 ML 工作负载的无服务器 GPU 云平台"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Modal Serverless Gpu {#modal-serverless-gpu}

用于运行 ML 工作负载的无服务器 GPU 云平台。当你需要按需使用 GPU 而无需管理基础设施、将 ML 模型部署为 API、或运行自动扩缩容的批处理作业时，可以使用它。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/modal` 安装 |
| 路径 | `optional-skills/mlops/modal` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `modal>=0.64.0` |
| 标签 | `Infrastructure`, `Serverless`, `GPU`, `Cloud`, `Deployment`, `Modal` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="modal-serverless-gpu"></a>
# Modal Serverless GPU

在 Modal 的无服务器 GPU 云平台上运行 ML 工作负载的全面指南。

## 何时使用 Modal {#when-to-use-modal}

**在以下情况下使用 Modal：**
- 运行 GPU 密集型 ML 工作负载，无需管理基础设施
- 将 ML 模型部署为自动扩缩容的 API
- 运行批处理作业（训练、推理、数据处理）
- 需要按秒计费的 GPU 定价，无闲置成本
- 快速原型化 ML 应用
- 运行定时任务（类似 cron 的工作负载）

**主要特性：**
- **无服务器 GPU**：按需使用 T4、L4、A10G、L40S、A100、H100、H200、B200
- **Python 原生**：用 Python 代码定义基础设施，无需 YAML
- **自动扩缩容**：缩容到零，瞬间扩容到 100+ GPU
- **亚秒级冷启动**：基于 Rust 的基础设施，实现快速容器启动
- **容器缓存**：镜像层缓存，支持快速迭代
- **Web 端点**：将函数部署为 REST API，零停机更新

**替代方案：**
- **RunPod**：用于需要持久化状态的长时间运行 Pod
- **Lambda Labs**：用于预留 GPU 实例
- **SkyPilot**：用于多云编排和成本优化
- **Kubernetes**：用于复杂的多服务架构

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
pip install modal
modal setup  # 打开浏览器进行身份验证
```

### 带 GPU 的 Hello World {#hello-world-with-gpu}

```python
import modal

app = modal.App("hello-gpu")

@app.function(gpu="T4")
def gpu_info():
    import subprocess
    return subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout

@app.local_entrypoint()
def main():
    print(gpu_info.remote())
```

运行：`modal run hello_gpu.py`

### 基本推理端点 {#basic-inference-endpoint}

```python
import modal

app = modal.App("text-generation")
image = modal.Image.debian_slim().pip_install("transformers", "torch", "accelerate")

@app.cls(gpu="A10G", image=image)
class TextGenerator:
    @modal.enter()
    def load_model(self):
        from transformers import pipeline
        self.pipe = pipeline("text-generation", model="gpt2", device=0)

    @modal.method()
    def generate(self, prompt: str) -> str:
        return self.pipe(prompt, max_length=100)[0]["generated_text"]

@app.local_entrypoint()
def main():
    print(TextGenerator().generate.remote("Hello, world"))
```
## 核心概念 {#core-concepts}

### 关键组件 {#key-components}

| 组件 | 用途 |
|-----------|---------|
| `App` | 函数和资源的容器 |
| `Function` | 带计算规格的无服务器函数 |
| `Cls` | 基于类的函数，支持生命周期钩子 |
| `Image` | 容器镜像定义 |
| `Volume` | 模型/数据的持久化存储 |
| `Secret` | 安全凭据存储 |

### 执行模式 {#execution-modes}

| 命令 | 描述 |
|---------|-------------|
| `modal run script.py` | 执行并退出 |
| `modal serve script.py` | 开发模式，支持热重载 |
| `modal deploy script.py` | 持久化云端部署 |

## GPU 配置 {#gpu-configuration}

### 可用 GPU {#available-gpus}

| GPU | 显存 | 最佳用途 |
|-----|------|----------|
| `T4` | 16GB | 预算推理、小模型 |
| `L4` | 24GB | 推理、Ada Lovelace 架构 |
| `A10G` | 24GB | 训练/推理，比 T4 快 3.3 倍 |
| `L40S` | 48GB | 推荐用于推理（最佳性价比） |
| `A100-40GB` | 40GB | 大模型训练 |
| `A100-80GB` | 80GB | 超大模型 |
| `H100` | 80GB | 最快，支持 FP8 + Transformer Engine |
| `H200` | 141GB | 从 H100 自动升级，带宽 4.8TB/s |
| `B200` | 最新 | Blackwell 架构 |

### GPU 规格模式 {#gpu-specification-patterns}

```python
# 单 GPU
@app.function(gpu="A100")

# 指定显存变体
@app.function(gpu="A100-80GB")

# 多 GPU（最多 8 块）
@app.function(gpu="H100:4")

# 带降级策略的 GPU
@app.function(gpu=["H100", "A100", "L40S"])

# 任意可用 GPU
@app.function(gpu="any")
```

## 容器镜像 {#container-images}

```python
# 基础镜像 + pip 安装
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.0", "transformers==4.36.0", "accelerate"
)

# 基于 CUDA 基础镜像
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
    add_python="3.11"
).pip_install("torch", "transformers")

# 带系统包
image = modal.Image.debian_slim().apt_install("git", "ffmpeg").pip_install("whisper")
```

## 持久化存储 {#persistent-storage}

```python
volume = modal.Volume.from_name("model-cache", create_if_missing=True)

@app.function(gpu="A10G", volumes={"/models": volume})
def load_model():
    import os
    model_path = "/models/llama-7b"
    if not os.path.exists(model_path):
        model = download_model()
        model.save_pretrained(model_path)
        volume.commit()  # 持久化变更
    return load_from_path(model_path)
```

## Web 端点 {#web-endpoints}

### FastAPI 端点装饰器 {#fastapi-endpoint-decorator}

```python
@app.function()
@modal.fastapi_endpoint(method="POST")
def predict(text: str) -> dict:
    return {"result": model.predict(text)}
```

### 完整 ASGI 应用 {#full-asgi-app}

```python
from fastapi import FastAPI
web_app = FastAPI()

@web_app.post("/predict")
async def predict(text: str):
    return {"result": await model.predict.remote.aio(text)}

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app
```

### Web 端点类型 {#web-endpoint-types}

| 装饰器 | 适用场景 |
|-----------|----------|
| `@modal.fastapi_endpoint()` | 简单函数 → API |
| `@modal.asgi_app()` | 完整的 FastAPI/Starlette 应用 |
| `@modal.wsgi_app()` | Django/Flask 应用 |
| `@modal.web_server(port)` | 任意 HTTP 服务器 |
## 动态批处理 {#dynamic-batching}

```python
@app.function()
@modal.batched(max_batch_size=32, wait_ms=100)
async def batch_predict(inputs: list[str]) -> list[dict]:
    # 输入会自动分批
    return model.batch_predict(inputs)
```

## 密钥管理 {#secrets-management}

```bash
# 创建密钥
modal secret create huggingface HF_TOKEN=hf_xxx
```

```python
@app.function(secrets=[modal.Secret.from_name("huggingface")])
def download_model():
    import os
    token = os.environ["HF_TOKEN"]
```

## 任务调度 {#scheduling}

```python
@app.function(schedule=modal.Cron("0 0 * * *"))  # 每天午夜
def daily_job():
    pass

@app.function(schedule=modal.Period(hours=1))
def hourly_job():
    pass
```

## 性能优化 {#performance-optimization}

### 冷启动缓解 {#cold-start-mitigation}

```python
@app.function(
    container_idle_timeout=300,  # 保持热启动 5 分钟
    allow_concurrent_inputs=10,  # 处理并发请求
)
def inference():
    pass
```

### 模型加载最佳实践 {#model-loading-best-practices}

```python
@app.cls(gpu="A100")
class Model:
    @modal.enter()  # 在容器启动时运行一次
    def load(self):
        self.model = load_model()  # 在预热期间加载

    @modal.method()
    def predict(self, x):
        return self.model(x)
```

## 并行处理 {#parallel-processing}

```python
@app.function()
def process_item(item):
    return expensive_computation(item)

@app.function()
def run_parallel():
    items = list(range(1000))
    # 分发到并行容器
    results = list(process_item.map(items))
    return results
```

## 常见配置 {#common-configuration}

```python
@app.function(
    gpu="A100",
    memory=32768,              # 32GB 内存
    cpu=4,                     # 4 个 CPU 核心
    timeout=3600,              # 最长 1 小时
    container_idle_timeout=120,# 保持热启动 2 分钟
    retries=3,                 # 失败时重试
    concurrency_limit=10,      # 最大并发容器数
)
def my_function():
    pass
```

## 调试 {#debugging}

```python
# 本地测试
if __name__ == "__main__":
    result = my_function.local()

# 查看日志
# modal app logs my-app
```

## 常见问题 {#common-issues}

| 问题 | 解决方案 |
|-------|----------|
| 冷启动延迟 | 增加 `container_idle_timeout`，使用 `@modal.enter()` |
| GPU 内存不足 | 使用更大的 GPU（`A100-80GB`），启用梯度检查点 |
| 镜像构建失败 | 固定依赖版本，检查 CUDA 兼容性 |
| 超时错误 | 增加 `timeout`，添加检查点 |

## 参考文档 {#references}

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/modal/references/advanced-usage.md)** - 多 GPU、分布式训练、成本优化
- **[故障排除](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/modal/references/troubleshooting.md)** - 常见问题及解决方案

## 资源 {#resources}

- **文档**: https://modal.com/docs
- **示例**: https://github.com/modal-labs/modal-examples
- **定价**: https://modal.com/pricing
- **Discord**: https://discord.gg/modal
