---
title: "Lambda Labs Gpu Cloud — 面向机器学习训练与推理的预留及按需GPU云实例"
sidebar_label: "Lambda Labs Gpu Cloud"
description: "用于机器学习训练和推理的预留及按需GPU云实例"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="lambda-labs-gpu-cloud"></a>
# Lambda Labs Gpu Cloud

用于机器学习训练和推理的预留及按需GPU云实例。当您需要专用GPU实例，支持简单SSH访问、持久化文件系统或高性能多节点集群用于大规模训练时使用。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/lambda-labs` 安装 |
| 路径 | `optional-skills/mlops/lambda-labs` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `lambda-cloud-client>=1.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `Infrastructure`, `GPU Cloud`, `Training`, `Inference`, `Lambda Labs` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。当技能激活时，Agent 将此视为指令。
:::

# Lambda Labs GPU Cloud

在 Lambda Labs GPU 云上运行机器学习工作负载的全面指南，支持按需实例和一鍵集群。

<a id="when-to-use-lambda-labs"></a>
## 何时使用 Lambda Labs

**在以下情况使用 Lambda Labs：**
- 需要具有完整 SSH 访问权限的专用 GPU 实例
- 运行长时间训练任务（数小时到数天）
- 想要简单定价且无出站流量费用
- 需要跨会话的持久化存储
- 需要高性能多节点集群（16-512 GPU）
- 需要预装的 ML 堆栈（包含 PyTorch、CUDA、NCCL 的 Lambda Stack）

**主要特性：**
- **GPU 种类**：B200, H100, GH200, A100, A10, A6000, V100
- **Lambda Stack**：预装 PyTorch、TensorFlow、CUDA、cuDNN、NCCL
- **持久化文件系统**：在实例重启间保留数据
- **一鍵集群**：16-512 GPU Slurm 集群，配备 InfiniBand
- **简单定价**：按分钟计费，无出站流量费用
- **全球区域**：覆盖全球 12+ 个区域

**其他替代方案：**
- **Modal**：适用于无服务器、自动扩缩的工作负载
- **SkyPilot**：用于多云编排和成本优化
- **RunPod**：用于更便宜的竞价实例和无服务器端点
- **Vast.ai**：用于 GPU 市场最低价

<a id="quick-start"></a>
## 快速开始

<a id="account-setup"></a>
### 账户设置

1. 在 https://lambda.ai 注册账户
2. 添加支付方式
3. 从控制面板生成 API 密钥
4. 添加 SSH 密钥（启动实例前必须操作）

<a id="launch-via-console"></a>
### 通过控制台启动

1. 访问 https://cloud.lambda.ai/instances
2. 点击“Launch instance”
3. 选择 GPU 类型和区域
4. 选择 SSH 密钥
5. 可选：附加文件系统
6. 启动并等待 3-15 分钟

<a id="connect-via-ssh"></a>
### 通过 SSH 连接

```bash
# 从控制台获取实例 IP
ssh ubuntu@<INSTANCE-IP>

# 或使用指定密钥
ssh -i ~/.ssh/lambda_key ubuntu@<INSTANCE-IP>
```

<a id="gpu-instances"></a>
## GPU 实例

<a id="available-gpus"></a>
### 可用 GPU

| GPU | 显存 | 价格/GPU/小时 | 最佳用途 |
|-----|------|--------------|----------|
| B200 SXM6 | 180 GB | $4.99 | 最大模型，最快训练 |
| H100 SXM | 80 GB | $2.99-3.29 | 大模型训练 |
| H100 PCIe | 80 GB | $2.49 | 性价比 H100 |
| GH200 | 96 GB | $1.49 | 单 GPU 大模型 |
| A100 80GB | 80 GB | $1.79 | 生产训练 |
| A100 40GB | 40 GB | $1.29 | 标准训练 |
| A10 | 24 GB | $0.75 | 推理，微调 |
| A6000 | 48 GB | $0.80 | 高显存性价比 |
| V100 | 16 GB | $0.55 | 预算训练 |
<a id="instance-configurations"></a>
### 实例配置

```
8x GPU：最适合分布式训练（DDP、FSDP）
4x GPU：大模型、多GPU训练
2x GPU：中等负载
1x GPU：微调、推理、开发
```

<a id="launch-times"></a>
### 启动时间

- 单GPU：3-5分钟
- 多GPU：10-15分钟

<a id="lambda-stack"></a>
## Lambda Stack

所有实例均预装 Lambda Stack：

```bash
# 预装软件
- Ubuntu 22.04 LTS
- NVIDIA 驱动（最新版）
- CUDA 12.x
- cuDNN 8.x
- NCCL（适用于多GPU）
- PyTorch（最新版）
- TensorFlow（最新版）
- JAX
- JupyterLab
```

<a id="verify-installation"></a>
### 验证安装

```bash
# 检查GPU
nvidia-smi

# 检查PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# 检查CUDA版本
nvcc --version
```

<a id="python-api"></a>
## Python API

<a id="installation"></a>
### 安装

```bash
pip install lambda-cloud-client
```

<a id="authentication"></a>
### 认证

```python
import os
import lambda_cloud_client

# 用API密钥配置
configuration = lambda_cloud_client.Configuration(
    host="https://cloud.lambdalabs.com/api/v1",
    access_token=os.environ["LAMBDA_API_KEY"]
)
```

<a id="list-available-instances"></a>
### 列出可用实例

```python
with lambda_cloud_client.ApiClient(configuration) as api_client:
    api = lambda_cloud_client.DefaultApi(api_client)

    # 获取可用实例类型
    types = api.instance_types()
    for name, info in types.data.items():
        print(f"{name}: {info.instance_type.description}")
```

<a id="launch-instance"></a>
### 启动实例

```python
from lambda_cloud_client.models import LaunchInstanceRequest

request = LaunchInstanceRequest(
    region_name="us-west-1",
    instance_type_name="gpu_1x_h100_sxm5",
    ssh_key_names=["my-ssh-key"],
    file_system_names=["my-filesystem"],  # 可选
    name="training-job"
)

response = api.launch_instance(request)
instance_id = response.data.instance_ids[0]
print(f"已启动：{instance_id}")
```

<a id="list-running-instances"></a>
### 列出正在运行的实例

```python
instances = api.list_instances()
for instance in instances.data:
    print(f"{instance.name}: {instance.ip} ({instance.status})")
```

<a id="terminate-instance"></a>
### 终止实例

```python
from lambda_cloud_client.models import TerminateInstanceRequest

request = TerminateInstanceRequest(
    instance_ids=[instance_id]
)
api.terminate_instance(request)
```

<a id="ssh-key-management"></a>
### SSH密钥管理

```python
from lambda_cloud_client.models import AddSshKeyRequest

# 添加SSH密钥
request = AddSshKeyRequest(
    name="my-key",
    public_key="ssh-rsa AAAA..."
)
api.add_ssh_key(request)

# 列出密钥
keys = api.list_ssh_keys()

# 删除密钥
api.delete_ssh_key(key_id)
```

<a id="cli-with-curl"></a>
## 使用curl的CLI

<a id="list-instance-types"></a>
### 列出实例类型

```bash
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instance-types | jq
```

### 启动实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/launch \
  -H "Content-Type: application/json" \
  -d '{
    "region_name": "us-west-1",
    "instance_type_name": "gpu_1x_h100_sxm5",
    "ssh_key_names": ["my-key"]
  }' | jq
```

### 终止实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/terminate \
  -H "Content-Type: application/json" \
  -d '{"instance_ids": ["<INSTANCE-ID>"]}' | jq
```
<a id="persistent-storage"></a>
## 持久化存储

<a id="filesystems"></a>
### 文件系统

文件系统可以在实例重启后持久保存数据：

```bash
# Mount location
/lambda/nfs/<FILESYSTEM_NAME>

# Example: save checkpoints
python train.py --checkpoint-dir /lambda/nfs/my-storage/checkpoints
```

<a id="create-filesystem"></a>
### 创建文件系统

1. 在 Lambda 控制台中进入 Storage
2. 点击 “Create filesystem”
3. 选择区域（必须与实例区域匹配）
4. 命名并创建

<a id="attach-to-instance"></a>
### 挂载到实例

文件系统必须在实例启动时挂载：
- 通过控制台：启动时选择文件系统
- 通过 API：在启动请求中包含 `file_system_names`

<a id="best-practices"></a>
### 最佳实践

<!-- ascii-guard-ignore -->
```bash
# Store on filesystem (persists)
/lambda/nfs/storage/
  ├── datasets/
  ├── checkpoints/
  ├── models/
  └── outputs/

# Local SSD (faster, ephemeral)
/home/ubuntu/
  └── working/  # Temporary files
```
<!-- ascii-guard-ignore-end -->

<a id="ssh-configuration"></a>
## SSH 配置

<a id="add-ssh-key"></a>
### 添加 SSH 密钥

```bash
# Generate key locally
ssh-keygen -t ed25519 -f ~/.ssh/lambda_key

# Add public key to Lambda console
# Or via API
```

<a id="multiple-keys"></a>
### 多个密钥

```bash
# On instance, add more keys
echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys
```

<a id="import-from-github"></a>
### 从 GitHub 导入

```bash
# On instance
ssh-import-id gh:username
```

<a id="ssh-tunneling"></a>
### SSH 隧道

```bash
# Forward Jupyter
ssh -L 8888:localhost:8888 ubuntu@<IP>

# Forward TensorBoard
ssh -L 6006:localhost:6006 ubuntu@<IP>

# Multiple ports
ssh -L 8888:localhost:8888 -L 6006:localhost:6006 ubuntu@<IP>
```

<a id="jupyterlab"></a>
## JupyterLab

<a id="launch-from-console"></a>
### 从控制台启动

1. 进入 Instances 页面
2. 点击 Cloud IDE 列中的 “Launch”
3. JupyterLab 会在浏览器中打开

<a id="manual-access"></a>
### 手动访问

```bash
# On instance
jupyter lab --ip=0.0.0.0 --port=8888

# From local machine with tunnel
ssh -L 8888:localhost:8888 ubuntu@<IP>
# Open http://localhost:8888
```

<a id="training-workflows"></a>
## 训练工作流

<a id="single-gpu-training"></a>
### 单 GPU 训练

```bash
# SSH to instance
ssh ubuntu@<IP>

# Clone repo
git clone https://github.com/user/project
cd project

# Install dependencies
pip install -r requirements.txt

# Train
python train.py --epochs 100 --checkpoint-dir /lambda/nfs/storage/checkpoints
```

<a id="multi-gpu-training-single-node"></a>
### 多 GPU 训练（单节点）

```python
# train_ddp.py
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def main():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    device = rank % torch.cuda.device_count()

    model = MyModel().to(device)
    model = DDP(model, device_ids=[device])

    # Training loop...

if __name__ == "__main__":
    main()
```

```bash
# Launch with torchrun (8 GPUs)
torchrun --nproc_per_node=8 train_ddp.py
```

<a id="checkpoint-to-filesystem"></a>
### 检查点保存到文件系统

```python
import os

checkpoint_dir = "/lambda/nfs/my-storage/checkpoints"
os.makedirs(checkpoint_dir, exist_ok=True)

# Save checkpoint
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, f"{checkpoint_dir}/checkpoint_{epoch}.pt")
```

<a id="1-click-clusters"></a>
## 一键集群

<a id="overview"></a>
### 概述
高性能 Slurm 集群，配备：
- 16-512 块 NVIDIA H100 或 B200 GPU
- NVIDIA Quantum-2 400 Gb/s InfiniBand
- 3200 Gb/s 的 GPUDirect RDMA
- 预装分布式机器学习栈

<a id="included-software"></a>
### 包含的软件

- Ubuntu 22.04 LTS + Lambda Stack
- NCCL、Open MPI
- 支持 DDP 和 FSDP 的 PyTorch
- TensorFlow
- OFED 驱动

<a id="storage"></a>
### 存储

- 每个计算节点 24 TB NVMe（临时存储）
- 用于持久化数据的 Lambda 文件系统

<a id="multi-node-training"></a>
### 多节点训练

```bash
# 在 Slurm 集群上
srun --nodes=4 --ntasks-per-node=8 --gpus-per-node=8 \
  torchrun --nnodes=4 --nproc_per_node=8 \
  --rdzv_backend=c10d --rdzv_endpoint=$MASTER_ADDR:29500 \
  train.py
```

<a id="networking"></a>
## 网络

<a id="bandwidth"></a>
### 带宽

- 实例间（同区域）：最高 200 Gbps
- 互联网出站：最高 20 Gbps

<a id="firewall"></a>
### 防火墙

- 默认：仅开放 22 端口（SSH）
- 在 Lambda 控制台中配置其他端口
- 默认允许 ICMP 流量

<a id="private-ips"></a>
### 私有 IP

```bash
# 查找私有 IP
ip addr show | grep 'inet '
```

<a id="common-workflows"></a>
## 常见工作流

<a id="workflow-1-fine-tuning-llm"></a>
### 工作流 1：微调 LLM

```bash
# 1. 启动 8x H100 实例并挂载文件系统

# 2. SSH 连接并设置环境
ssh ubuntu@<IP>
pip install transformers accelerate peft

# 3. 将模型下载到文件系统
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-hf')
model.save_pretrained('/lambda/nfs/storage/models/llama-2-7b')
"

# 4. 在文件系统上使用检查点进行微调
accelerate launch --num_processes 8 train.py \
  --model_path /lambda/nfs/storage/models/llama-2-7b \
  --output_dir /lambda/nfs/storage/outputs \
  --checkpoint_dir /lambda/nfs/storage/checkpoints
```

<a id="workflow-2-batch-inference"></a>
### 工作流 2：批量推理

```bash
# 1. 启动 A10 实例（推理场景性价比高）

# 2. 运行推理
python inference.py \
  --model /lambda/nfs/storage/models/fine-tuned \
  --input /lambda/nfs/storage/data/inputs.jsonl \
  --output /lambda/nfs/storage/data/outputs.jsonl
```

<a id="cost-optimization"></a>
## 成本优化

<a id="choose-right-gpu"></a>
### 选择合适的 GPU

| 任务 | 推荐 GPU |
|------|----------|
| LLM 微调（7B） | A100 40GB |
| LLM 微调（70B） | 8x H100 |
| 推理 | A10、A6000 |
| 开发 | V100、A10 |
| 最高性能 | B200 |

<a id="reduce-costs"></a>
### 降低成本

1. **使用文件系统**：避免重复下载数据
2. **频繁保存检查点**：可恢复中断的训练
3. **合理配置**：不要过度分配 GPU
4. **终止闲置实例**：无自动停止，需手动终止

<a id="monitor-usage"></a>
### 监控使用情况

- 仪表盘显示实时 GPU 利用率
- 提供 API 用于程序化监控

<a id="common-issues"></a>
## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 实例无法启动 | 检查区域可用性，尝试不同 GPU |
| SSH 连接被拒绝 | 等待实例初始化完成（3-15 分钟） |
| 终止后数据丢失 | 使用持久化文件系统 |
| 数据传输慢 | 使用同区域的文件系统 |
| 未检测到 GPU | 重启实例，检查驱动 |

<a id="references"></a>
## 参考

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/advanced-usage.md)** - 多节点训练、API 自动化
- **[故障排除](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/troubleshooting.md)** - 常见问题及解决方案
<a id="resources"></a>
## 资源

- **文档**：https://docs.lambda.ai
- **控制台**：https://cloud.lambda.ai
- **定价**：https://lambda.ai/instances
- **支持**：https://support.lambdalabs.com
- **博客**：https://lambda.ai/blog
