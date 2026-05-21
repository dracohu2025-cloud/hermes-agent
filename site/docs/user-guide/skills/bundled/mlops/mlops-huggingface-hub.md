---
title: "Huggingface Hub — HuggingFace hf CLI：搜索/下载/上传模型与数据集"
sidebar_label: "Huggingface Hub"
description: "HuggingFace hf CLI：搜索/下载/上传模型与数据集"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能描述文件 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="huggingface-hub"></a>
# Huggingface Hub

HuggingFace hf CLI：搜索/下载/上传模型与数据集。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/huggingface-hub` |
| 版本 | `1.0.0` |
| 作者 | Hugging Face |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下为当此技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到以下指令。
:::

<a id="hugging-face-cli-hf-reference-guide"></a>
# Hugging Face CLI (`hf`) 参考指南

`hf` 命令是与 Hugging Face Hub 交互的现代命令行界面，提供管理仓库、模型、数据集和 Spaces 的工具。

> **重要提示：** `hf` 命令已取代现已废弃的 `huggingface-cli` 命令。

<a id="quick-start"></a>
## 快速开始
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助：** 使用 `hf --help` 查看所有可用功能及真实示例。
*   **身份验证：** 推荐通过 `HF_TOKEN` 环境变量或 `--token` 标志进行。

---

<a id="core-commands"></a>
## 核心命令

<a id="general-operations"></a>
### 通用操作
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件/文件夹（推荐用于单次提交）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：推荐用于大目录的可断点续传上传。
*   `hf sync`：在本地目录与存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境和版本详情。

<a id="authentication-hf-auth"></a>
### 身份验证 (`hf auth`)
*   `login` / `logout`：使用来自 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 的令牌管理会话。
*   `list` / `switch`：管理和切换多个已存储的访问令牌。
*   `whoami`：识别当前登录的账户。

<a id="repository-management-hf-repos"></a>
### 仓库管理 (`hf repos`)
*   `create` / `delete`：创建或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆到新的 ID。
*   `move`：在不同命名空间之间转移仓库。
*   `branch` / `tag`：管理类似 Git 的引用。
*   `delete-files`：使用模式删除特定文件。

---

<a id="specialized-hub-interactions"></a>
## 专用 Hub 交互

<a id="datasets-models"></a>
### 数据集与模型
*   **数据集：** `hf datasets list`、`info` 和 `parquet`（列出 parquet URL）。
*   **SQL 查询：** `hf datasets sql SQL` — 通过 DuckDB 对数据集 parquet URL 执行原始 SQL。
*   **模型：** `hf models list` 和 `info`。
*   **论文：** `hf papers list` — 查看每日论文。

<a id="discussions-pull-requests-hf-discussions"></a>
### 讨论与拉取请求 (`hf discussions`)
*   管理 Hub 贡献的生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 和 `rename`。
*   `diff`：查看 PR 中的变更。
*   `merge`：最终合并拉取请求。

<a id="infrastructure-compute"></a>
### 基础设施与计算
*   **Endpoints：** 部署和管理推理端点（`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`）。
*   **Jobs：** 在 HF 基础设施上运行计算任务。包括用于运行带有内联依赖的 Python 脚本的 `hf jobs uv` 以及用于资源监控的 `stats`。
*   **Spaces：** 管理交互式应用。包括无需完全重启即可对 Python 文件进行热重载的 `dev-mode` 和 `hot-reload`。
<a id="storage-automation"></a>
### 存储与自动化
*   **存储桶（Buckets）：** 完整的类 S3 存储桶管理（`create`、`cp`、`mv`、`rm`、`sync`）。
*   **缓存：** 使用 `list`（列出）、`prune`（移除已分离的修订版本）和 `verify`（校验和检查）管理本地存储。
*   **Webhooks：** 通过管理 Hub 的 Webhook（`create`、`watch`、`enable`/`disable`）自动化工作流。
*   **集合（Collections）：** 将 Hub 中的项目组织成集合（`add-item`、`update`、`list`）。

---

<a id="advanced-usage-tips"></a>
## 高级用法与技巧

<a id="global-flags"></a>
### 全局标志
*   `--format json`：输出机器可读的 JSON 格式，便于自动化处理。
*   `-q` / `--quiet`：限制输出，仅显示 ID。

<a id="extensions-skills"></a>
### 扩展与技能
*   **扩展（Extensions）：** 使用 `hf extensions install REPO_ID` 通过 GitHub 仓库扩展 CLI 功能。
*   **技能（Skills）：** 使用 `hf skills add` 管理 AI 助手技能。
