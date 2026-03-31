---
sidebar_position: 9
title: "上下文引用"
description: "使用内联的 @ 语法，将文件、文件夹、git diff 和 URL 直接附加到你的消息中"
---

# 上下文引用

输入 `@` 后跟一个引用，即可将内容直接注入到你的消息中。Hermes 会内联展开该引用，并将内容附加在 `--- 附加上下文 ---` 部分下。

## 支持的引用类型

| 语法 | 描述 |
|--------|-------------|
| `@file:path/to/file.py` | 注入文件内容 |
| `@file:path/to/file.py:10-25` | 注入指定行范围（从1开始计数，包含首尾行） |
| `@folder:path/to/dir` | 注入目录树列表及文件元数据 |
| `@diff` | 注入 `git diff`（未暂存的工作区变更） |
| `@staged` | 注入 `git diff --staged`（已暂存的变更） |
| `@git:5` | 注入最近 N 次提交及其补丁（最多 10 次） |
| `@url:https://example.com` | 获取并注入网页内容 |

## 使用示例

```text
Review @file:src/main.py and suggest improvements

What changed? @diff

Compare @file:old_config.yaml and @file:new_config.yaml

What's in @folder:src/components?

Summarize this article @url:https://arxiv.org/abs/2301.00001
```

单个消息中可以使用多个引用：

```text
Check @file:main.py, and also @file:test.py.
```

引用值末尾的标点符号（`,`, `.`, `;`, `!`, `?`）会被自动移除。

## CLI 标签补全

在交互式 CLI 中，输入 `@` 会触发自动补全：

- `@` 显示所有引用类型（`@diff`, `@staged`, `@file:`, `@folder:`, `@git:`, `@url:`）
- `@file:` 和 `@folder:` 触发文件系统路径补全，并显示文件大小元数据
- 单独的 `@` 后跟部分文本，会显示当前目录下匹配的文件和文件夹

## 行范围

`@file:` 引用支持行范围，用于精确注入内容：

```text
@file:src/main.py:42        # 仅第 42 行
@file:src/main.py:10-25     # 第 10 行到第 25 行（包含首尾）
```

行号从 1 开始计数。无效的范围会被静默忽略（返回整个文件）。

## 大小限制

上下文引用有大小限制，以防止超出模型的上下文窗口：

| 阈值 | 值 | 行为 |
|-----------|-------|----------|
| 软限制 | 上下文长度的 25% | 附加警告，继续展开 |
| 硬限制 | 上下文长度的 50% | 拒绝展开，返回未修改的原始消息 |
| 文件夹条目 | 最多 200 个文件 | 超出条目替换为 `- ...` |
| Git 提交 | 最多 10 个 | `@git:N` 被限制在 [1, 10] 范围内 |

## 安全性

### 敏感路径拦截

以下路径在 `@file:` 引用中始终被拦截，以防止凭证泄露：

- SSH 密钥和配置：`~/.ssh/id_rsa`, `~/.ssh/id_ed25519`, `~/.ssh/authorized_keys`, `~/.ssh/config`
- Shell 配置文件：`~/.bashrc`, `~/.zshrc`, `~/.profile`, `~/.bash_profile`, `~/.zprofile`
- 凭证文件：`~/.netrc`, `~/.pgpass`, `~/.npmrc`, `~/.pypirc`
- Hermes 环境文件：`$HERMES_HOME/.env`

以下目录被完全拦截（其中的任何文件）：
- `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `~/.kube/`, `$HERMES_HOME/skills/.hub/`

### 路径遍历保护

所有路径都相对于工作目录进行解析。解析后位于允许的工作空间根目录之外的引用将被拒绝。

### 二进制文件检测

通过 MIME 类型和空字节扫描来检测二进制文件。已知的文本扩展名（`.py`, `.md`, `.json`, `.yaml`, `.toml`, `.js`, `.ts` 等）会绕过基于 MIME 的检测。二进制文件会被拒绝并显示警告。

## 错误处理

无效的引用会产生内联警告，而不是导致整个操作失败：

| 条件 | 行为 |
|-----------|----------|
| 文件未找到 | 警告："file not found" |
| 二进制文件 | 警告："binary files are not supported" |
| 文件夹未找到 | 警告："folder not found" |
| Git 命令失败 | 警告并附带 git stderr 输出 |
| URL 未返回内容 | 警告："no content extracted" |
| 敏感路径 | 警告："path is a sensitive credential file" |
| 路径在工作空间外 | 警告："path is outside the allowed workspace" |
