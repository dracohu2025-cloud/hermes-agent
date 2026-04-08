---
sidebar_position: 99
title: "Honcho 记忆"
description: "通过 Honcho 实现 AI 原生持久化记忆 —— 辩证推理、多 Agent 用户建模以及深度个性化"
---

# Honcho 记忆

[Honcho](https://github.com/plastic-labs/honcho) 是一个 AI 原生记忆后端，它在 Hermes 内置记忆系统的基础上增加了辩证推理和深度用户建模功能。Honcho 不仅仅是简单的键值存储，它通过在对话结束后对内容进行推理，维护一个关于用户是谁的动态模型 —— 包括他们的偏好、沟通风格、目标和行为模式。

:::info Honcho 是一个记忆提供商插件
Honcho 已集成到 [Memory Providers](./memory-providers.md) 系统中。以下所有功能均可通过统一的记忆提供商接口使用。
:::

## Honcho 带来的提升

| 能力 | 内置记忆 | Honcho |
|-----------|----------------|--------|
| 跨会话持久化 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 带 API 的服务端存储 |
| 用户画像 | ✔ 手动 Agent 维护 | ✔ 自动辩证推理 |
| 多 Agent 隔离 | — | ✔ 每个 Peer（节点）画像分离 |
| 观察模式 | — | ✔ 统一或定向观察 |
| 结论（衍生洞察） | — | ✔ 服务端对模式的推理 |
| 历史记录搜索 | ✔ FTS5 会话搜索 | ✔ 对结论进行语义搜索 |

**辩证推理 (Dialectic reasoning)**：在每次对话之后，Honcho 会分析交流内容并得出“结论” —— 即关于用户偏好、习惯和目标的洞察。这些结论会随着时间推移不断积累，使 Agent 能够产生超越用户显式表达内容的深度理解。

**多 Agent 画像**：当多个 Hermes 实例与同一个用户交谈时（例如一个编程助手和一个私人助手），Honcho 会维护独立的“Peer”画像。每个 Peer 只能看到自己的观察结果和结论，防止上下文交叉污染。

## 安装设置

```bash
hermes memory setup    # 从提供商列表中选择 "honcho"
```

或者手动配置：

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo "HONCHO_API_KEY=your-key" >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

## 配置选项

```yaml
# ~/.hermes/config.yaml
honcho:
  observation: directional    # "unified"（新安装默认值）或 "directional"
  peer_name: ""               # 从平台自动检测，或手动设置
```

**观察模式：**
- `unified` — 所有观察结果都进入同一个池。更简单，适合单 Agent 设置。
- `directional` — 观察结果会标记方向（用户→Agent，Agent→用户）。可以对对话动态进行更丰富的分析。

## 工具 (Tools)

当 Honcho 作为记忆提供商激活时，将提供四个额外的工具：

| 工具 | 用途 |
|------|---------|
| `honcho_conclude` | 对最近的对话触发服务端辩证推理 |
| `honcho_context` | 从 Honcho 记忆中检索与当前对话相关的上下文 |
| `honcho_profile` | 查看或更新用户的 Honcho 画像 |
| `honcho_search` | 对所有存储的结论和观察结果进行语义搜索 |

## CLI 命令

```bash
hermes honcho status          # 显示连接状态和配置
hermes honcho peer            # 为多 Agent 设置更新 Peer 名称
```

## 从 `hermes honcho` 迁移

如果你之前使用过独立的 `hermes honcho setup`：

1. 你现有的配置（`honcho.json` 或 `~/.honcho/config.json`）会被保留。
2. 你的服务端数据（记忆、结论、用户画像）完好无损。
3. 在 config.yaml 中设置 `memory.provider: honcho` 即可重新激活。

无需重新登录或重新设置。运行 `hermes memory setup` 并选择 "honcho" —— 向导会自动检测你现有的配置。

## 完整文档

请参阅 [Memory Providers — Honcho](./memory-providers.md#honcho) 获取完整参考指南。
