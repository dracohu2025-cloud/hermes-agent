---
title: "Weights And Biases — W&B：记录 ML 实验、超参数搜索、模型注册表、仪表盘"
sidebar_label: "Weights And Biases"
description: "W&B：记录 ML 实验、超参数搜索、模型注册表、仪表盘"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Weights And Biases {#weights-and-biases}

W&B：记录 ML 实验、超参数搜索、模型注册表、仪表盘。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/evaluation/weights-and-biases` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `wandb` |
| 标签 | `MLOps`、`Weights And Biases`、`WandB`、`Experiment Tracking`、`Hyperparameter Tuning`、`Model Registry`、`Collaboration`、`Real-Time Visualization`、`PyTorch`、`TensorFlow`、`HuggingFace` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Weights & Biases：ML 实验跟踪与 MLOps {#weights-biases-ml-experiment-tracking-mlops}

## 何时使用此技能 {#when-to-use-this-skill}

当你需要以下功能时，请使用 Weights & Biases (W&B)：
- **跟踪 ML 实验**，自动记录指标
- **实时仪表盘**可视化训练过程
- **跨超参数和配置**比较运行结果
- **自动超参数搜索**优化模型
- **管理模型注册表**，支持版本控制和血缘追踪
- **团队工作区**协作 ML 项目
- **跟踪工件**（数据集、模型、代码）及其血缘关系

**用户**：200,000+ ML 从业者 | **GitHub Stars**：10.5k+ | **集成**：100+

## 安装 {#installation}

```bash
# 安装 W&B
pip install wandb

# 登录（创建 API 密钥）
wandb login

# 或以编程方式设置 API 密钥
export WANDB_API_KEY=your_api_key_here
```

## 快速开始 {#quick-start}

### 基础实验跟踪 {#basic-experiment-tracking}

```python
import wandb

# 初始化一次运行
run = wandb.init(
    project="my-project",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "ResNet50"
    }
)

# 训练循环
for epoch in range(run.config.epochs):
    # 你的训练代码
    train_loss = train_epoch()
    val_loss = validate()

    # 记录指标
    wandb.log({
        "epoch": epoch,
        "train/loss": train_loss,
        "val/loss": val_loss,
        "train/accuracy": train_acc,
        "val/accuracy": val_acc
    })

# 结束运行
wandb.finish()
```

### 与 PyTorch 配合使用 {#with-pytorch}

```python
import torch
import wandb

# 初始化
wandb.init(project="pytorch-demo", config={
    "lr": 0.001,
    "epochs": 10
})

# 访问配置
config = wandb.config

# 训练循环
for epoch in range(config.epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        # 前向传播
        output = model(data)
        loss = criterion(output, target)

        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 每 100 个 batch 记录一次
        if batch_idx % 100 == 0:
            wandb.log({
                "loss": loss.item(),
                "epoch": epoch,
                "batch": batch_idx
            })

# 保存模型
torch.save(model.state_dict(), "model.pth")
wandb.save("model.pth")  # 上传到 W&B

wandb.finish()
```
## 核心概念 {#core-concepts}

### 1. 项目与运行 {#1-projects-and-runs}

**项目**：相关实验的集合  
**运行**：训练脚本的单个执行

```python
# 创建/使用项目
run = wandb.init(
    project="image-classification",
    name="resnet50-experiment-1",  # 可选的运行名称
    tags=["baseline", "resnet"],    # 用标签组织
    notes="First baseline run"      # 添加备注
)

# 每个运行都有唯一 ID
print(f"Run ID: {run.id}")
print(f"Run URL: {run.url}")
```

### 2. 配置追踪 {#2-configuration-tracking}

自动追踪超参数：

```python
config = {
    # 模型架构
    "model": "ResNet50",
    "pretrained": True,

    # 训练参数
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 50,
    "optimizer": "Adam",

    # 数据参数
    "dataset": "ImageNet",
    "augmentation": "standard"
}

wandb.init(project="my-project", config=config)

# 训练过程中访问配置
lr = wandb.config.learning_rate
batch_size = wandb.config.batch_size
```

### 3. 指标记录 {#3-metric-logging}

```python
# 记录标量
wandb.log({"loss": 0.5, "accuracy": 0.92})

# 记录多个指标
wandb.log({
    "train/loss": train_loss,
    "train/accuracy": train_acc,
    "val/loss": val_loss,
    "val/accuracy": val_acc,
    "learning_rate": current_lr,
    "epoch": epoch
})

# 使用自定义 x 轴记录
wandb.log({"loss": loss}, step=global_step)

# 记录媒体（图像、音频、视频）
wandb.log({"examples": [wandb.Image(img) for img in images]})

# 记录直方图
wandb.log({"gradients": wandb.Histogram(gradients)})

# 记录表格
table = wandb.Table(columns=["id", "prediction", "ground_truth"])
wandb.log({"predictions": table})
```

### 4. 模型检查点 {#4-model-checkpointing}

```python
import torch
import wandb

# 保存模型检查点
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}

torch.save(checkpoint, 'checkpoint.pth')

# 上传到 W&B
wandb.save('checkpoint.pth')

# 或使用 Artifacts（推荐）
artifact = wandb.Artifact('model', type='model')
artifact.add_file('checkpoint.pth')
wandb.log_artifact(artifact)
```

## 超参数扫描 {#hyperparameter-sweeps}

自动搜索最优超参数。

### 定义扫描配置 {#define-sweep-configuration}

```python
sweep_config = {
    'method': 'bayes',  # 或 'grid'、'random'
    'metric': {
        'name': 'val/accuracy',
        'goal': 'maximize'
    },
    'parameters': {
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        'batch_size': {
            'values': [16, 32, 64, 128]
        },
        'optimizer': {
            'values': ['adam', 'sgd', 'rmsprop']
        },
        'dropout': {
            'distribution': 'uniform',
            'min': 0.1,
            'max': 0.5
        }
    }
}

# 初始化扫描
sweep_id = wandb.sweep(sweep_config, project="my-project")
```

### 定义训练函数 {#define-training-function}

```python
def train():
    # 初始化运行
    run = wandb.init()

    # 访问扫描参数
    lr = wandb.config.learning_rate
    batch_size = wandb.config.batch_size
    optimizer_name = wandb.config.optimizer

    # 使用扫描配置构建模型
    model = build_model(wandb.config)
    optimizer = get_optimizer(optimizer_name, lr)

    # 训练循环
    for epoch in range(NUM_EPOCHS):
        train_loss = train_epoch(model, optimizer, batch_size)
        val_acc = validate(model)

        # 记录指标
        wandb.log({
            "train/loss": train_loss,
            "val/accuracy": val_acc
        })

# 运行扫描
wandb.agent(sweep_id, function=train, count=50)  # 运行 50 次试验
```
### 扫描策略 {#sweep-strategies}

```python
# 网格搜索 - 穷举
sweep_config = {
    'method': 'grid',
    'parameters': {
        'lr': {'values': [0.001, 0.01, 0.1]},
        'batch_size': {'values': [16, 32, 64]}
    }
}

# 随机搜索
sweep_config = {
    'method': 'random',
    'parameters': {
        'lr': {'distribution': 'uniform', 'min': 0.0001, 'max': 0.1},
        'dropout': {'distribution': 'uniform', 'min': 0.1, 'max': 0.5}
    }
}

# 贝叶斯优化（推荐）
sweep_config = {
    'method': 'bayes',
    'metric': {'name': 'val/loss', 'goal': 'minimize'},
    'parameters': {
        'lr': {'distribution': 'log_uniform', 'min': 1e-5, 'max': 1e-1}
    }
}
```

## 工件（Artifacts） {#artifacts}

追踪数据集、模型及其他文件，并记录其来源。

### 记录工件 {#log-artifacts}

```python
# 创建工件
artifact = wandb.Artifact(
    name='training-dataset',
    type='dataset',
    description='ImageNet 训练集',
    metadata={'size': '1.2M images', 'split': 'train'}
)

# 添加文件
artifact.add_file('data/train.csv')
artifact.add_dir('data/images/')

# 记录工件
wandb.log_artifact(artifact)
```

### 使用工件 {#use-artifacts}

```python
# 下载并使用工件
run = wandb.init(project="my-project")

# 下载工件
artifact = run.use_artifact('training-dataset:latest')
artifact_dir = artifact.download()

# 使用数据
data = load_data(f"{artifact_dir}/train.csv")
```

### 模型注册表 {#model-registry}

```python
# 将模型记录为工件
model_artifact = wandb.Artifact(
    name='resnet50-model',
    type='model',
    metadata={'architecture': 'ResNet50', 'accuracy': 0.95}
)

model_artifact.add_file('model.pth')
wandb.log_artifact(model_artifact, aliases=['best', 'production'])

# 链接到模型注册表
run.link_artifact(model_artifact, 'model-registry/production-models')
```

## 集成示例 {#integration-examples}

### HuggingFace Transformers {#huggingface-transformers}

```python
from transformers import Trainer, TrainingArguments
import wandb

# 初始化 W&B
wandb.init(project="hf-transformers")

# 带 W&B 的训练参数
training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",  # 启用 W&B 日志记录
    run_name="bert-finetuning",
    logging_steps=100,
    save_steps=500
)

# Trainer 自动记录到 W&B
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
```

### PyTorch Lightning {#pytorch-lightning}

```python
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import WandbLogger
import wandb

# 创建 W&B 日志器
wandb_logger = WandbLogger(
    project="lightning-demo",
    log_model=True  # 记录模型检查点
)

# 与 Trainer 一起使用
trainer = Trainer(
    logger=wandb_logger,
    max_epochs=10
)

trainer.fit(model, datamodule=dm)
```

### Keras/TensorFlow {#keras-tensorflow}

```python
import wandb
from wandb.keras import WandbCallback

# 初始化
wandb.init(project="keras-demo")

# 添加回调
model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=10,
    callbacks=[WandbCallback()]  # 自动记录指标
)
```
## 可视化与分析 {#visualization-analysis}

### 自定义图表 {#custom-charts}

```python
# Log custom visualizations
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
wandb.log({"custom_plot": wandb.Image(fig)})

# Log confusion matrix
wandb.log({"conf_mat": wandb.plot.confusion_matrix(
    probs=None,
    y_true=ground_truth,
    preds=predictions,
    class_names=class_names
)})
```

### 报告 {#reports}

在 W&B UI 中创建可分享的报告：
- 组合运行、图表和文本
- 支持 Markdown
- 可嵌入的可视化
- 团队协作

## 最佳实践 {#best-practices}

### 1. 使用标签和分组进行组织 {#1-organize-with-tags-and-groups}

```python
wandb.init(
    project="my-project",
    tags=["baseline", "resnet50", "imagenet"],
    group="resnet-experiments",  # 对相关运行进行分组
    job_type="train"             # 任务类型
)
```

### 2. 记录所有相关数据 {#2-log-everything-relevant}

```python
# Log system metrics
wandb.log({
    "gpu/util": gpu_utilization,
    "gpu/memory": gpu_memory_used,
    "cpu/util": cpu_utilization
})

# Log code version
wandb.log({"git_commit": git_commit_hash})

# Log data splits
wandb.log({
    "data/train_size": len(train_dataset),
    "data/val_size": len(val_dataset)
})
```

### 3. 使用描述性名称 {#3-use-descriptive-names}

```python
# ✅ 好：描述性的运行名称
wandb.init(
    project="nlp-classification",
    name="bert-base-lr0.001-bs32-epoch10"
)

# ❌ 差：通用名称
wandb.init(project="nlp", name="run1")
```

### 4. 保存重要工件 {#4-save-important-artifacts}

```python
# Save final model
artifact = wandb.Artifact('final-model', type='model')
artifact.add_file('model.pth')
wandb.log_artifact(artifact)

# Save predictions for analysis
predictions_table = wandb.Table(
    columns=["id", "input", "prediction", "ground_truth"],
    data=predictions_data
)
wandb.log({"predictions": predictions_table})
```

### 5. 网络不稳定时使用离线模式 {#5-use-offline-mode-for-unstable-connections}

```python
import os

# Enable offline mode
os.environ["WANDB_MODE"] = "offline"

wandb.init(project="my-project")
# ... your code ...

# Sync later
# wandb sync <run_directory>
```

## 团队协作 {#team-collaboration}

### 分享运行 {#share-runs}

```python
# Runs are automatically shareable via URL
run = wandb.init(project="team-project")
print(f"Share this URL: {run.url}")
```

### 团队项目 {#team-projects}

- 在 wandb.ai 创建团队账号
- 添加团队成员
- 设置项目可见性（私有/公开）
- 使用团队级别的工件和模型注册表

## 定价 {#pricing}

- **免费版**：无限公共项目，100GB 存储
- **学术版**：学生/研究人员免费
- **团队版**：$50/席位/月，私有项目，无限存储
- **企业版**：自定义定价，支持本地部署

## 资源 {#resources}

- **文档**：https://docs.wandb.ai
- **GitHub**：https://github.com/wandb/wandb（10.5k+ 星标）
- **示例**：https://github.com/wandb/examples
- **社区**：https://wandb.ai/community
- **Discord**：https://wandb.me/discord

## 另请参阅 {#see-also}

- `references/sweeps.md` - 全面的超参数优化指南
- `references/artifacts.md` - 数据和模型版本管理模式
- `references/integrations.md` - 框架特定示例
