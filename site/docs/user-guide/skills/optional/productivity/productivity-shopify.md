---
title: "Shopify — 通过 curl 使用 Shopify Admin & Storefront GraphQL API"
sidebar_label: "Shopify"
description: "通过 curl 使用 Shopify Admin & Storefront GraphQL API"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="shopify"></a>
# Shopify

通过 curl 使用 Shopify Admin & Storefront GraphQL API。支持商品、订单、客户、库存、元字段。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/productivity/shopify` 安装 |
| 路径 | `optional-skills/productivity/shopify` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Shopify`、`E-commerce`、`Commerce`、`API`、`GraphQL` |
| 相关技能 | [`airtable`](/user-guide/skills/bundled/productivity/productivity-airtable)、[`xurl`](/user-guide/skills/bundled/social-media/social-media-xurl) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，这就是 agent 看到的指令内容。
:::

<a id="shopify-admin-storefront-graphql-apis"></a>
# Shopify — Admin & Storefront GraphQL API

直接通过 `curl` 与 Shopify 店铺交互：列举商品、管理库存、拉取订单、更新客户、读取元字段。无需 SDK，无需应用框架——仅需 GraphQL 端点和一个自定义应用访问令牌。

REST Admin API 自 2024-04 起已弃用，仅接收安全修复。**请使用 GraphQL Admin** 进行所有管理工作。对于只读的客户面向查询（商品、分类、购物车），请使用 **Storefront GraphQL**。

<a id="prerequisites"></a>
## 前提条件

1. 在 Shopify 后台中：**设置 → 应用和销售渠道 → 开发应用 → 创建应用**。
2. 点击 **配置 Admin API 权限**，根据需要选择（示例如下），然后保存。
3. **安装应用** → Admin API 访问令牌将**一次性**显示。请立即复制——Shopify 不会再显示它。令牌以 `shpat_` 开头。
4. 保存到 `~/.hermes/.env`：
   ```
   SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx
   SHOPIFY_STORE_DOMAIN=my-store.myshopify.com
   SHOPIFY_API_VERSION=2026-01
   ```

> **注意：** 自 2026 年 1 月 1 日起，在 Shopify 后台创建新的“旧版自定义应用”功能已移除。新设置应使用 **Dev Dashboard**（`shopify.dev/docs/apps/build/dev-dashboard`）。已有的后台创建的应用继续有效。如果用户的店铺没有现有的自定义应用且时间在 2026-01-01 之后，请引导他们使用 Dev Dashboard 而非后台流程。

常见任务对应的权限范围：
- 商品 / 分类：`read_products`、`write_products`
- 库存：`read_inventory`、`write_inventory`、`read_locations`
- 订单：`read_orders`、`write_orders`（未授予 `read_all_orders` 时仅最近 30 条）
- 客户：`read_customers`、`write_customers`
- 草稿订单：`read_draft_orders`、`write_draft_orders`
- 履行：`read_fulfillments`、`write_fulfillments`
- 元字段 / 元对象：由对应资源的权限范围覆盖

<a id="api-basics"></a>
## API 基础

- **端点：** `https://$SHOPIFY_STORE_DOMAIN/admin/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头：** `X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN`（**不是** `Authorization: Bearer`）
- **方法：** 始终为 `POST`，始终设置 `Content-Type: application/json`，请求体为 `{"query": "...", "variables": {...}}`
- **HTTP 200 不代表成功。** GraphQL 会在顶层 `errors` 数组和每个字段的 `userErrors` 中返回错误。请务必同时检查两者。
- **ID 是 GID 字符串：** `gid://shopify/Product/10079467700516`、`gid://shopify/Variant/...`、`gid://shopify/Order/...`。请原样传递——不要去掉前缀。
- **速率限制：** 通过查询成本（漏桶算法）计算。每个响应都包含 `extensions.cost`，其中有 `requestedQueryCost`、`actualQueryCost`、`throttleStatus.{currentlyAvailable, maximumAvailable, restoreRate}`。当 `currentlyAvailable` 低于下一次查询的成本时，应主动降低频率。标准店铺 = 100 点桶容量，每秒恢复 50 点；Plus 店铺 = 1000 点 / 100 恢复。
基础 curl 模式（可复用）：

```bash
shop_gql() {
  local query="$1"
  local variables="${2:-{}}"
  curl -sS -X POST \
    "https://${SHOPIFY_STORE_DOMAIN}/admin/api/${SHOPIFY_API_VERSION:-2026-01}/graphql.json" \
    -H "Content-Type: application/json" \
    -H "X-Shopify-Access-Token: ${SHOPIFY_ACCESS_TOKEN}" \
    --data "$(jq -nc --arg q "$query" --argjson v "$variables" '{query: $q, variables: $v}')"
}
```

通过 `jq` 管道输出可读结果。`-sS` 参数会保留错误信息，但隐藏进度条。

<a id="discovery"></a>
## 发现

<a id="shop-info-current-api-version"></a>
### 店铺信息 + 当前 API 版本
```bash
shop_gql '{ shop { name myshopifyDomain primaryDomain { url } currencyCode plan { displayName } } }' | jq
```

<a id="list-all-supported-api-versions"></a>
### 列出所有支持的 API 版本
```bash
shop_gql '{ publicApiVersions { handle supported } }' | jq '.data.publicApiVersions[] | select(.supported)'
```

<a id="products"></a>
## 产品

<a id="search-products-first-20-matching-query"></a>
### 搜索产品（前 20 个匹配结果）
```bash
shop_gql '
query($q: String!) {
  products(first: 20, query: $q) {
    edges { node { id title handle status totalInventory variants(first: 5) { edges { node { id sku price inventoryQuantity } } } } }
    pageInfo { hasNextPage endCursor }
  }
}' '{"q":"hoodie status:active"}' | jq
```

查询语法支持 `title:`、`sku:`、`vendor:`、`product_type:`、`status:active`、`tag:`、`created_at:>2025-01-01`。完整语法：https://shopify.dev/docs/api/usage/search-syntax

<a id="paginate-products-cursor"></a>
### 分页查询产品（使用游标）
```bash
shop_gql '
query($cursor: String) {
  products(first: 100, after: $cursor) {
    edges { cursor node { id handle } }
    pageInfo { hasNextPage endCursor }
  }
}' '{"cursor":null}'
# 后续调用：传入上一次的 endCursor
```

<a id="get-a-product-with-variants-metafields"></a>
### 获取产品详情（含变体 + 元字段）
```bash
shop_gql '
query($id: ID!) {
  product(id: $id) {
    id title handle descriptionHtml tags status
    variants(first: 20) { edges { node { id sku price compareAtPrice inventoryQuantity selectedOptions { name value } } } }
    metafields(first: 20) { edges { node { namespace key type value } } }
  }
}' '{"id":"gid://shopify/Product/10079467700516"}' | jq
```

<a id="create-a-product-with-one-variant"></a>
### 创建一个带变体的产品
```bash
shop_gql '
mutation($input: ProductCreateInput!) {
  productCreate(product: $input) {
    product { id handle }
    userErrors { field message }
  }
}' '{"input":{"title":"Test Hoodie","status":"DRAFT","vendor":"Hermes","productType":"Apparel","tags":["test"]}}'
```

在较新版本中，变体现在有独立的变更操作：

```bash
# 创建产品后添加变体
shop_gql '
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}' '{"productId":"gid://shopify/Product/...","variants":[{"optionValues":[{"optionName":"Size","name":"M"}],"price":"49.00","inventoryItem":{"sku":"HD-M","tracked":true}}]}'
```

<a id="update-price-sku"></a>
### 更新价格 / SKU
```bash
shop_gql '
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}' '{"productId":"gid://shopify/Product/...","variants":[{"id":"gid://shopify/ProductVariant/...","price":"55.00"}]}'
```
<a id="orders"></a>
## 订单

<a id="list-recent-orders-last-30-by-default-without-readallorders"></a>
### 列出最近订单（默认最近30个，如果不使用 `read_all_orders`）
```bash
shop_gql '
{
  orders(first: 20, reverse: true, query: "financial_status:paid") {
    edges { node {
      id name createdAt displayFinancialStatus displayFulfillmentStatus
      totalPriceSet { shopMoney { amount currencyCode } }
      customer { id displayName email }
      lineItems(first: 10) { edges { node { title quantity sku } } }
    } }
  }
}' | jq
```

有用的订单查询筛选条件：`financial_status:paid|pending|refunded`, `fulfillment_status:unfulfilled|fulfilled`, `created_at:>2025-01-01`, `tag:gift`, `email:foo@example.com`。

<a id="fetch-a-single-order-with-shipping-address"></a>
### 获取单个订单（含收货地址）
```bash
shop_gql '
query($id: ID!) {
  order(id: $id) {
    id name email
    shippingAddress { name address1 address2 city province country zip phone }
    lineItems(first: 50) { edges { node { title quantity variant { sku } originalUnitPriceSet { shopMoney { amount currencyCode } } } } }
    transactions { id kind status amountSet { shopMoney { amount currencyCode } } }
  }
}' '{"id":"gid://shopify/Order/...."}' | jq
```

<a id="customers"></a>
## 客户

```bash
# Search
shop_gql '
{
  customers(first: 10, query: "email:*@example.com") {
    edges { node { id email displayName numberOfOrders amountSpent { amount currencyCode } } }
  }
}'

# Create
shop_gql '
mutation($input: CustomerInput!) {
  customerCreate(input: $input) {
    customer { id email }
    userErrors { field message }
  }
}' '{"input":{"email":"test@example.com","firstName":"Test","lastName":"User","tags":["api-created"]}}'
```

<a id="inventory"></a>
## 库存

库存存在于与变体关联的**库存项目**上，数量按**位置**追踪。

```bash
# Get inventory for a variant across all locations
shop_gql '
query($id: ID!) {
  productVariant(id: $id) {
    id sku
    inventoryItem {
      id tracked
      inventoryLevels(first: 10) {
        edges { node { location { id name } quantities(names: ["available","on_hand","committed"]) { name quantity } } }
      }
    }
  }
}' '{"id":"gid://shopify/ProductVariant/..."}'
```

调整库存（差值）——使用 `inventoryAdjustQuantities`：

```bash
shop_gql '
mutation($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    inventoryAdjustmentGroup { reason changes { name delta } }
    userErrors { field message }
  }
}' '{
  "input": {
    "reason": "correction",
    "name": "available",
    "changes": [{"delta": 5, "inventoryItemId": "gid://shopify/InventoryItem/...", "locationId": "gid://shopify/Location/..."}]
  }
}'
```

设置绝对库存（不是差值）—— `inventorySetQuantities`：

```bash
shop_gql '
mutation($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { id }
    userErrors { field message }
  }
}' '{"input":{"reason":"correction","name":"available","ignoreCompareQuantity":true,"quantities":[{"inventoryItemId":"gid://shopify/InventoryItem/...","locationId":"gid://shopify/Location/...","quantity":100}]}}'
```
<a id="metafields-metaobjects"></a>
## 元字段 & 元对象

元字段可以将自定义数据附加到资源（产品、客户、订单、店铺）上。

```bash
# 读取
shop_gql '
query($id: ID!) {
  product(id: $id) {
    metafields(first: 10, namespace: "custom") {
      edges { node { key type value } }
    }
  }
}' '{"id":"gid://shopify/Product/..."}'

# 写入（适用于任何所有者类型）
shop_gql '
mutation($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id key namespace }
    userErrors { field message code }
  }
}' '{"metafields":[{"ownerId":"gid://shopify/Product/...","namespace":"custom","key":"care_instructions","type":"multi_line_text_field","value":"Wash cold. Tumble dry low."}]}'
```

<a id="storefront-api-public-read-only"></a>
## Storefront API（公开只读）

使用不同的端点、不同的令牌，面向客户端的应用或 Hydrogen 风格的无头架构。请求头有区别：

- **端点：** `https://$SHOPIFY_STORE_DOMAIN/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头（公开）：** `X-Shopify-Storefront-Access-Token: &lt;public token&gt;` — 可嵌入浏览器
- **认证头（私有）：** `Shopify-Storefront-Private-Token: &lt;private token&gt;` — 仅服务端

```bash
curl -sS -X POST \
  "https://${SHOPIFY_STORE_DOMAIN}/api/${SHOPIFY_API_VERSION:-2026-01}/graphql.json" \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Storefront-Access-Token: ${SHOPIFY_STOREFRONT_TOKEN}" \
  -d '{"query":"{ shop { name } products(first: 5) { edges { node { id title handle } } } }"}' | jq
```

<a id="bulk-operations"></a>
## 批量操作

用于数据量超过速率限制允许的范围（例如完整的产品目录、一年的所有订单）：

```bash
# 1. 启动批量查询
shop_gql '
mutation {
  bulkOperationRunQuery(query: """
    { products { edges { node { id title handle variants { edges { node { sku price } } } } } } }
  """) {
    bulkOperation { id status }
    userErrors { field message }
  }
}'

# 2. 轮询状态
shop_gql '{ currentBulkOperation { id status errorCode objectCount fileSize url partialDataUrl } }'

# 3. 当 status=COMPLETED 时，下载 JSONL 文件
curl -sS "$URL" > products.jsonl
```

JSONL 文件中每行是一个节点，嵌套的连接会以独立的行输出并附带 `__parentId`。如需还原，可在客户端自行组装。

<a id="webhooks"></a>
## Webhook

订阅事件，避免轮询：

```bash
shop_gql '
mutation($topic: WebhookSubscriptionTopic!, $sub: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $sub) {
    webhookSubscription { id topic endpoint { __typename ... on WebhookHttpEndpoint { callbackUrl } } }
    userErrors { field message }
  }
}' '{"topic":"ORDERS_CREATE","sub":{"callbackUrl":"https://example.com/webhook","format":"JSON"}}'
```

使用应用的 client secret（而非访问令牌）验证传入 webhook 的 HMAC：

```bash
echo -n "$REQUEST_BODY" | openssl dgst -sha256 -hmac "$APP_SECRET" -binary | base64
# 与 X-Shopify-Hmac-Sha256 请求头进行比较
```

<a id="pitfalls"></a>
## 注意事项

- **REST 端点依然存在，但已冻结。** 不要对 `/admin/api/.../products.json` 编写新的集成代码。请使用 GraphQL。
- **检查令牌格式。** Admin 令牌以 `shpat_` 开头，Storefront 公共令牌以 `shpua_` 开头。如果拿到令牌却用了错误的请求头，每次请求只会返回 401 而没有有用的错误信息。
- **拥有有效令牌但返回 403 = 缺少权限。** Shopify 会返回 `{"errors":[{"message":"Access denied for ..."}]}`。需要在应用中重新配置 Admin API 权限范围，然后重新安装以重新生成令牌。
- **`userErrors` 为空并不等于成功。** 同时检查 `data.&lt;mutation&gt;.&lt;resource&gt;` 是否为非 null。有些失败场景不会填充这两个字段，请检查完整响应。
- **GID 与数字 ID。** 旧版 REST 使用数字 ID；GraphQL 需要完整的 GID 字符串。转换方式：`gid://shopify/Product/<数字>`。
- **速率限制的意外情况。** 一个 `products(first: 250)` 加上深层嵌套的查询可能消耗超过 1000 点，在标准套餐的店铺中会立即触发限流。建议从较小的范围开始，读取 `extensions.cost`，再调整。
- **分页排序。** `products(first: N, reverse: true)` 是按 `id DESC` 排序，而不是 `created_at`。如需“最新优先”，请使用 `sortKey: CREATED_AT, reverse: true`。
- **`read_all_orders` 用于获取历史数据。** 如果没有该权限，`orders(...)` 会默认只返回最近 60 天的数据。你不会得到错误，只是结果比预期的少。对于订单量大的 Shopify Plus 商户，需通过应用的受保护数据设置申请此权限。
- **货币是字符串。** 金额以 `"49.00"` 形式返回，而不是 `49.0`。如果你在意零填充，不要盲目使用 `jq tonumber`。
- **多币种 Money 字段** 包含 `shopMoney`（店铺货币）和 `presentmentMoney`（客户货币）。请一致地选择其中一个。
<a id="safety"></a>
## 安全性

Shopify 中的变更操作是真实生效的——它们会创建商品、处理退款、取消订单、执行发货。在运行 `productDelete`、`orderCancel`、`refundCreate` 或任何批量变更之前：请明确说明变更内容、针对哪个店铺，并与用户确认。除非用户有独立的开发商店，否则不存在生产数据的预演克隆。
