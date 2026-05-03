---
title: "Huggingface Hub — HuggingFace hf CLI：搜索/下载/上传模型、数据集"
sidebar_label: "Huggingface Hub"
description: "HuggingFace hf CLI：搜索/下载/上传模型、数据集"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Huggingface Hub {#huggingface-hub}

HuggingFace hf CLI：搜索/下载/上传模型、数据集。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/huggingface-hub` |
| 版本 | `1.0.0` |
| 作者 | Hugging Face |
| 许可证 | MIT |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Hugging Face CLI（`hf`）参考指南 {#hugging-face-cli-hf-reference-guide}

`hf` 命令是与 Hugging Face Hub 交互的现代命令行界面，提供管理仓库、模型、数据集和 Spaces 的工具。

> **重要提示：** `hf` 命令已取代现已弃用的 `huggingface-cli` 命令。

## 快速开始 {#quick-start}
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助：** 使用 `hf --help` 查看所有可用函数和实际示例。
*   **身份验证：** 推荐通过 `HF_TOKEN` 环境变量或 `--token` 标志进行。

---

## 核心命令 {#core-commands}

### 常规操作 {#general-operations}
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件/文件夹（推荐用于单次提交）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：推荐用于大目录的可恢复上传。
*   `hf sync`：在本地目录和存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境和版本详情。

### 身份验证（`hf auth`） {#authentication-hf-auth}
*   `login` / `logout`：使用来自 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 的令牌管理会话。
*   `list` / `switch`：管理和切换多个存储的访问令牌。
*   `whoami`：识别当前登录的账户。

### 仓库管理（`hf repos`） {#repository-management-hf-repos}
*   `create` / `delete`：创建或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆到新 ID。
*   `move`：在命名空间之间转移仓库。
*   `branch` / `tag`：管理类似 Git 的引用。
*   `delete-files`：使用模式删除特定文件。

---

## 专门的 Hub 交互 {#specialized-hub-interactions}

### 数据集与模型 {#datasets-models}
*   **数据集：** `hf datasets list`、`info` 和 `parquet`（列出 parquet URL）。
*   **SQL 查询：** `hf datasets sql SQL` — 通过 DuckDB 对数据集 parquet URL 执行原始 SQL。
*   **模型：** `hf models list` 和 `info`。
*   **论文：** `hf papers list` — 查看每日论文。

### 讨论与拉取请求（`hf discussions`） {#discussions-pull-requests-hf-discussions}
*   管理 Hub 贡献的生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 和 `rename`。
*   `diff`：查看 PR 中的更改。
*   `merge`：完成拉取请求。

### 基础设施与计算 {#infrastructure-compute}
*   **端点：** 部署和管理推理端点（`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`）。
*   **任务：** 在 HF 基础设施上运行计算任务。包括用于运行带有内联依赖项的 Python 脚本的 `hf jobs uv` 和用于资源监控的 `stats`。
*   **Spaces：** 管理交互式应用。包括无需完全重启即可对 Python 文件进行 `dev-mode` 和 `hot-reload`。
### 存储与自动化 {#storage-automation}
*   **存储桶（Buckets）：** 完整的类 S3 存储桶管理（`create`、`cp`、`mv`、`rm`、`sync`）。
*   **缓存（Cache）：** 使用 `list`、`prune`（移除分离的修订版本）和 `verify`（校验和检查）管理本地存储。
*   **Webhooks：** 通过管理 Hub 的 Webhooks（`create`、`watch`、`enable`/`disable`）自动化工作流。
*   **集合（Collections）：** 将 Hub 中的项目组织到集合中（`add-item`、`update`、`list`）。

---

## 高级用法与技巧 {#advanced-usage-tips}

### 全局标志 {#global-flags}
*   `--format json`：生成机器可读的输出，便于自动化。
*   `-q` / `--quiet`：仅输出 ID。

### 扩展与技能 {#extensions-skills}
*   **扩展（Extensions）：** 通过 GitHub 仓库使用 `hf extensions install REPO_ID` 扩展 CLI 功能。
*   **技能（Skills）：** 使用 `hf skills add` 管理 AI 助手技能。
