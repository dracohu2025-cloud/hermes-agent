---
title: 供应商路由
description: 配置 OpenRouter 供应商偏好，以优化成本、速度或质量。
sidebar_label: 供应商路由
sidebar_position: 7
---

# 供应商路由

当使用 [OpenRouter](https://openrouter.ai) 作为你的 LLM 供应商时，Hermes Agent 支持**供应商路由**——即对底层 AI 供应商处理你的请求的方式及其优先级进行细粒度控制。

OpenRouter 会将请求路由到许多供应商（例如 Anthropic、Google、AWS Bedrock、Together AI）。供应商路由功能让你可以针对成本、速度、质量进行优化，或强制执行特定的供应商要求。

## 配置

在你的 `~/.hermes/config.yaml` 文件中添加一个 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "price"           # 如何对供应商进行排序
  only: []                # 白名单：仅使用这些供应商
  ignore: []              # 黑名单：永不使用这些供应商
  order: []               # 明确的供应商优先级顺序
  require_parameters: false  # 仅使用支持所有参数的供应商
  data_collection: null   # 控制数据收集（"allow" 或 "deny"）
```

:::info
供应商路由仅在通过 OpenRouter 使用时生效。对于直接连接供应商（例如直接连接 Anthropic API）的情况没有影响。
:::

## 选项

### `sort`

控制 OpenRouter 如何为你的请求对可用供应商进行排序。

| 值 | 描述 |
|-------|-------------|
| `"price"` | 最便宜的供应商优先 |
| `"throughput"` | 每秒令牌数最快的供应商优先 |
| `"latency"` | 首令牌时间最低的供应商优先 |

```yaml
provider_routing:
  sort: "price"
```

### `only`

供应商名称的白名单。设置后，**仅**使用这些供应商。所有其他供应商将被排除。

```yaml
provider_routing:
  only:
    - "Anthropic"
    - "Google"
```

### `ignore`

供应商名称的黑名单。这些供应商将**永不**被使用，即使它们提供了最便宜或最快的选项。

```yaml
provider_routing:
  ignore:
    - "Together"
    - "DeepInfra"
```

### `order`

明确的优先级顺序。列在前面的供应商优先使用。未列出的供应商作为后备使用。

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
    - "AWS Bedrock"
```

### `require_parameters`

当设置为 `true` 时，OpenRouter 将仅路由到支持你请求中**所有**参数（如 `temperature`、`top_p`、`tools` 等）的供应商。这可以避免参数被静默丢弃。

```yaml
provider_routing:
  require_parameters: true
```

### `data_collection`

控制供应商是否可以将你的提示用于训练。选项为 `"allow"` 或 `"deny"`。

```yaml
provider_routing:
  data_collection: "deny"
```

## 实用示例

### 优化成本

路由到最便宜的可用供应商。适用于高使用量和开发场景：

```yaml
provider_routing:
  sort: "price"
```

### 优化速度

为交互式使用优先选择低延迟供应商：

```yaml
provider_routing:
  sort: "latency"
```

### 优化吞吐量

最适合每秒令牌数很重要的长文本生成：

```yaml
provider_routing:
  sort: "throughput"
```

### 锁定特定供应商

确保所有请求都通过特定供应商以获得一致性：

```yaml
provider_routing:
  only:
    - "Anthropic"
```

### 避免特定供应商

排除你不想使用的供应商（例如，出于数据隐私考虑）：

```yaml
provider_routing:
  ignore:
    - "Together"
    - "Lepton"
  data_collection: "deny"
```

### 带后备的优先顺序

首先尝试你首选的供应商，如果不可用则回退到其他供应商：

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
  require_parameters: true
```

## 工作原理

供应商路由偏好通过每次 API 调用时 `extra_body.provider` 字段传递给 OpenRouter API。这适用于以下两种模式：

- **CLI 模式** — 在 `~/.hermes/config.yaml` 中配置，启动时加载
- **网关模式** — 相同的配置文件，网关启动时加载

路由配置从 `config.yaml` 中读取，并在创建 `AIAgent` 时作为参数传递：

```
providers_allowed  ← 来自 provider_routing.only
providers_ignored  ← 来自 provider_routing.ignore
providers_order    ← 来自 provider_routing.order
provider_sort      ← 来自 provider_routing.sort
provider_require_parameters ← 来自 provider_routing.require_parameters
provider_data_collection    ← 来自 provider_routing.data_collection
```

:::tip
你可以组合多个选项。例如，按价格排序，但排除某些供应商并要求参数支持：

```yaml
provider_routing:
  sort: "price"
  ignore: ["Together"]
  require_parameters: true
  data_collection: "deny"
```
:::

## 默认行为

当没有配置 `provider_routing` 部分时（默认情况），OpenRouter 使用其自身的默认路由逻辑，通常会自动平衡成本和可用性。

:::tip 供应商路由 vs. 后备模型
供应商路由控制 OpenRouter 内部的**子供应商**处理你的请求。关于当你的主模型失败时自动故障转移到完全不同的供应商，请参阅[后备供应商](/docs/user-guide/features/fallback-providers)。
:::
