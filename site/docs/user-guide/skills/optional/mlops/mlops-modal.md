---
title: "Modal Serverless Gpu — 用于运行机器学习工作负载的无服务器 GPU 云平台"
sidebar_label: "Modal Serverless Gpu"
description: "用于运行机器学习工作负载的无服务器 GPU 云平台"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

<a id="modal-serverless-gpu"></a>
# Modal Serverless Gpu

用于运行机器学习工作负载的无服务器 GPU 云平台。当您需要按需 GPU 访问而无需管理基础设施、将 ML 模型部署为 API，或运行具有自动扩缩能力的批量任务时，使用此平台。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/modal` 安装 |
| 路径 | `optional-skills/mlops/modal` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `modal>=0.64.0` |
| 支持平台 | linux, macos, windows |
| 标签 | `Infrastructure`, `Serverless`, `GPU`, `Cloud`, `Deployment`, `Modal` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Modal Serverless GPU

在 Modal 的无服务器 GPU 云平台上运行机器学习工作负载的全面指南。

<a id="when-to-use-modal"></a>
## 何时使用 Modal

**使用 Modal 的场景：**
- 运行 GPU 密集型 ML 工作负载，无需管理基础设施
- 将 ML 模型部署为自动扩缩的 API
- 运行批量处理任务（训练、推理、数据处理）
- 需要按秒计费的 GPU 定价，无需承担空闲成本
- 快速原型化 ML 应用
- 运行定时任务（类似 cron 的工作负载）

**关键特性：**
- **无服务器 GPU**：按需使用 T4、L4、A10G、L40S、A100、H100、H200、B200
- **Python 原生**：用 Python 代码定义基础设施，无需 YAML
- **自动扩缩**：缩到零，瞬间扩到 100+ GPU
- **亚秒级冷启动**：基于 Rust 的基础设施，实现快速容器启动
- **容器缓存**：镜像层被缓存，支持快速迭代
- **Web 端点**：将函数部署为 REST API，零停机更新

**替代方案：**
- **RunPod**：用于长时间运行的、带有持久状态的 Pod
- **Lambda Labs**：用于预留 GPU 实例
- **SkyPilot**：用于多云编排和成本优化
- **Kubernetes**：用于复杂的多服务架构

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
pip install modal
modal setup  # 打开浏览器进行身份认证
```

<a id="hello-world-with-gpu"></a>
### Hello World with GPU

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

<a id="basic-inference-endpoint"></a>
### 基础推理端点

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
<a id="core-concepts"></a>
## 核心概念

<a id="key-components"></a>
### 主要组件

| 组件 | 用途 |
|-----------|---------|
| `App` | 函数和资源的容器 |
| `Function` | 带计算规格的无服务器函数 |
| `Cls` | 基于类的函数，支持生命周期钩子 |
| `Image` | 容器镜像定义 |
| `Volume` | 模型/数据的持久化存储 |
| `Secret` | 安全凭据存储 |

<a id="execution-modes"></a>
### 执行模式

| 命令 | 描述 |
|---------|-------------|
| `modal run script.py` | 执行并退出 |
| `modal serve script.py` | 开发模式，支持热重载 |
| `modal deploy script.py` | 持久化云端部署 |

<a id="gpu-configuration"></a>
## GPU 配置

<a id="available-gpus"></a>
### 可用的 GPU

| GPU | 显存 | 最佳用途 |
|-----|------|----------|
| `T4` | 16GB | 预算推理、小型模型 |
| `L4` | 24GB | 推理，Ada Lovelace 架构 |
| `A10G` | 24GB | 训练/推理，速度比 T4 快 3.3 倍 |
| `L40S` | 48GB | 推荐用于推理（最佳性价比） |
| `A100-40GB` | 40GB | 大型模型训练 |
| `A100-80GB` | 80GB | 超大型模型 |
| `H100` | 80GB | 最快，支持 FP8 + Transformer Engine |
| `H200` | 141GB | 从 H100 自动升级，带宽 4.8TB/s |
| `B200` | 最新 | Blackwell 架构 |

<a id="gpu-specification-patterns"></a>
### GPU 规格模式

```python
# 单块 GPU
@app.function(gpu="A100")

# 指定显存版本
@app.function(gpu="A100-80GB")

# 多块 GPU（最多 8 块）
@app.function(gpu="H100:4")

# GPU 带降级方案
@app.function(gpu=["H100", "A100", "L40S"])

# 任意可用 GPU
@app.function(gpu="any")
```

<a id="container-images"></a>
## 容器镜像

```python
# 带 pip 的基础镜像
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.0", "transformers==4.36.0", "accelerate"
)

# 基于 CUDA 基础镜像
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
    add_python="3.11"
).pip_install("torch", "transformers")

# 带系统软件包
image = modal.Image.debian_slim().apt_install("git", "ffmpeg").pip_install("whisper")
```

<a id="persistent-storage"></a>
## 持久化存储

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

<a id="web-endpoints"></a>
## Web 端点

<a id="fastapi-endpoint-decorator"></a>
### FastAPI 端点装饰器

```python
@app.function()
@modal.fastapi_endpoint(method="POST")
def predict(text: str) -> dict:
    return {"result": model.predict(text)}
```

<a id="full-asgi-app"></a>
### 完整 ASGI 应用

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

<a id="web-endpoint-types"></a>
### Web 端点类型

| 装饰器 | 使用场景 |
|-----------|----------|
| `@modal.fastapi_endpoint()` | 简单函数 → API |
| `@modal.asgi_app()` | 完整的 FastAPI/Starlette 应用 |
| `@modal.wsgi_app()` | Django/Flask 应用 |
| `@modal.web_server(port)` | 任意 HTTP 服务器 |
<a id="dynamic-batching"></a>
## 动态批处理

```python
@app.function()
@modal.batched(max_batch_size=32, wait_ms=100)
async def batch_predict(inputs: list[str]) -> list[dict]:
    # 输入会自动进行批处理
    return model.batch_predict(inputs)
```

<a id="secrets-management"></a>
## 密钥管理

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

<a id="scheduling"></a>
## 任务调度

```python
@app.function(schedule=modal.Cron("0 0 * * *"))  # 每天午夜执行
def daily_job():
    pass

@app.function(schedule=modal.Period(hours=1))
def hourly_job():
    pass
```

<a id="performance-optimization"></a>
## 性能优化

<a id="cold-start-mitigation"></a>
### 冷启动缓解

```python
@app.function(
    container_idle_timeout=300,  # 保持热启动 5 分钟
    allow_concurrent_inputs=10,  # 处理并发请求
)
def inference():
    pass
```

<a id="model-loading-best-practices"></a>
### 模型加载最佳实践

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

<a id="parallel-processing"></a>
## 并行处理

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

<a id="common-configuration"></a>
## 常见配置

```python
@app.function(
    gpu="A100",
    memory=32768,              # 32GB 内存
    cpu=4,                     # 4 个 CPU 核心
    timeout=3600,              # 最长 1 小时
    container_idle_timeout=120,# 保持热启动 2 分钟
    retries=3,                 # 失败时重试 3 次
    concurrency_limit=10,      # 最大并发容器数
)
def my_function():
    pass
```

<a id="debugging"></a>
## 调试

```python
# 本地测试
if __name__ == "__main__":
    result = my_function.local()

# 查看日志
# modal app logs my-app
```

<a id="common-issues"></a>
## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 冷启动延迟 | 增加 `container_idle_timeout`，使用 `@modal.enter()` |
| GPU 内存不足 | 使用更大的 GPU（`A100-80GB`），启用梯度检查点 |
| 镜像构建失败 | 固定依赖版本，检查 CUDA 兼容性 |
| 超时错误 | 增加 `timeout`，添加检查点 |

<a id="references"></a>
## 参考文档

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/modal/references/advanced-usage.md)** - 多 GPU、分布式训练、成本优化
- **[故障排除](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/modal/references/troubleshooting.md)** - 常见问题及解决方案

<a id="resources"></a>
## 资源

- **文档**: https://modal.com/docs
- **示例**: https://github.com/modal-labs/modal-examples
- **定价**: https://modal.com/pricing
- **Discord**: https://discord.gg/modal
