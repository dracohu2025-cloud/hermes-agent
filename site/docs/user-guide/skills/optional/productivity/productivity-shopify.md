---
title: "Shopify — 通过 curl 调用 Shopify Admin 与 Storefront GraphQL API"
sidebar_label: "Shopify"
description: "通过 curl 调用 Shopify Admin 与 Storefront GraphQL API"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Shopify {#shopify}

通过 curl 调用 Shopify Admin 与 Storefront GraphQL API。涵盖产品、订单、客户、库存、元字段等。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/shopify` 安装 |
| 路径 | `optional-skills/productivity/shopify` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `Shopify`、`E-commerce`、`Commerce`、`API`、`GraphQL` |
| 相关技能 | [`airtable`](/user-guide/skills/bundled/productivity/productivity-airtable)、[`xurl`](/user-guide/skills/bundled/social-media/social-media-xurl) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Shopify — Admin 与 Storefront GraphQL API {#shopify-admin-storefront-graphql-apis}

通过 `curl` 直接操作 Shopify 店铺：列出产品、管理库存、拉取订单、更新客户、读取元字段。无需 SDK，无需应用框架——只需 GraphQL 端点和一个自定义应用访问令牌。

REST Admin API 自 2024 年 4 月起已进入遗留状态，仅接收安全修复。**所有管理操作请使用 GraphQL Admin**。面向客户的只读查询（产品、集合、购物车）请使用 **Storefront GraphQL**。

## 前置条件 {#prerequisites}

1. 在 Shopify 管理后台中：**设置 → 应用和销售渠道 → 开发应用 → 创建应用**。
2. 点击 **配置 Admin API 作用域**，选择你需要的范围（示例如下），然后保存。
3. **安装应用** → Admin API 访问令牌会**一次性**显示。请立即复制——Shopify 不会再显示它。令牌以 `shpat_` 开头。
4. 保存到 `~/.hermes/.env`：
   ```
   SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx
   SHOPIFY_STORE_DOMAIN=my-store.myshopify.com
   SHOPIFY_API_VERSION=2026-01
   ```

> **注意：** 自 2026 年 1 月 1 日起，在 Shopify 管理后台中创建的新“遗留自定义应用”已不可用。新设置应使用 **Dev Dashboard**（`shopify.dev/docs/apps/build/dev-dashboard`）。现有管理后台创建的应用仍可继续使用。如果用户的店铺没有现有自定义应用且时间在 2026-01-01 之后，请引导他们使用 Dev Dashboard 而非管理后台流程。

按任务划分的常见作用域：
- 产品 / 集合：`read_products`、`write_products`
- 库存：`read_inventory`、`write_inventory`、`read_locations`
- 订单：`read_orders`、`write_orders`（无 `read_all_orders` 时仅限最近 30 条）
- 客户：`read_customers`、`write_customers`
- 草稿订单：`read_draft_orders`、`write_draft_orders`
- 发货：`read_fulfillments`、`write_fulfillments`
- 元字段 / 元对象：由对应的资源作用域覆盖

## API 基础 {#api-basics}

- **端点：** `https://$SHOPIFY_STORE_DOMAIN/admin/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头：** `X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN`（**不是** `Authorization: Bearer`）
- **方法：** 始终为 `POST`，始终为 `Content-Type: application/json`，请求体为 `{"query": "...", "variables": {...}}`
- **HTTP 200 不代表成功。** GraphQL 会在顶层 `errors` 数组和字段级 `userErrors` 中返回错误。请始终检查两者。
- **ID 是 GID 字符串：** `gid://shopify/Product/10079467700516`、`gid://shopify/Variant/...`、`gid://shopify/Order/...`。请原样传递——不要去掉前缀。
- **速率限制：** 通过查询成本（漏桶算法）计算。每个响应都包含 `extensions.cost`，其中有 `requestedQueryCost`、`actualQueryCost`、`throttleStatus.{currentlyAvailable, maximumAvailable, restoreRate}`。当 `currentlyAvailable` 低于下一次查询的成本时，请退避。标准店铺 = 100 点桶，50/秒恢复；Plus 店铺 = 1000/100。
Base curl 模式（可复用）：

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

通过 `jq` 管道输出可读结果。`-sS` 保持错误可见，但隐藏进度条。

## 发现 {#discovery}

### 店铺信息 + 当前 API 版本 {#shop-info-current-api-version}
```bash
shop_gql '{ shop { name myshopifyDomain primaryDomain { url } currencyCode plan { displayName } } }' | jq
```

### 列出所有支持的 API 版本 {#list-all-supported-api-versions}
```bash
shop_gql '{ publicApiVersions { handle supported } }' | jq '.data.publicApiVersions[] | select(.supported)'
```

## 产品 {#products}

### 搜索产品（前 20 个匹配查询） {#search-products-first-20-matching-query}
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

### 分页产品（游标） {#paginate-products-cursor}
```bash
shop_gql '
query($cursor: String) {
  products(first: 100, after: $cursor) {
    edges { cursor node { id handle } }
    pageInfo { hasNextPage endCursor }
  }
}' '{"cursor":null}'
# 后续调用：传入上一个 endCursor
```

### 获取产品（含变体 + 元字段） {#get-a-product-with-variants-metafields}
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

### 创建一个产品（含一个变体） {#create-a-product-with-one-variant}
```bash
shop_gql '
mutation($input: ProductCreateInput!) {
  productCreate(product: $input) {
    product { id handle }
    userErrors { field message }
  }
}' '{"input":{"title":"Test Hoodie","status":"DRAFT","vendor":"Hermes","productType":"Apparel","tags":["test"]}}'
```

在较新版本中，变体现在有自己的变更操作：

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

### 更新价格 / SKU {#update-price-sku}
```bash
shop_gql '
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}' '{"productId":"gid://shopify/Product/...","variants":[{"id":"gid://shopify/ProductVariant/...","price":"55.00"}]}'
```
## 订单 {#orders}

### 列出最近订单（不带 `read_all_orders` 时默认最近30个） {#list-recent-orders-last-30-by-default-without-readallorders}
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

有用的订单查询筛选条件：`financial_status:paid|pending|refunded`（已支付|待处理|已退款）、`fulfillment_status:unfulfilled|fulfilled`（未发货|已发货）、`created_at:>2025-01-01`、`tag:gift`、`email:foo@example.com`。

### 获取单个订单及收货地址 {#fetch-a-single-order-with-shipping-address}
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

## 客户 {#customers}

```bash
# 搜索
shop_gql '
{
  customers(first: 10, query: "email:*@example.com") {
    edges { node { id email displayName numberOfOrders amountSpent { amount currencyCode } } }
  }
}'

# 创建
shop_gql '
mutation($input: CustomerInput!) {
  customerCreate(input: $input) {
    customer { id email }
    userErrors { field message }
  }
}' '{"input":{"email":"test@example.com","firstName":"Test","lastName":"User","tags":["api-created"]}}'
```

## 库存 {#inventory}

库存由与变体关联的**库存项**管理，数量按**地点**追踪。

```bash
# 获取某个变体在所有地点的库存
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

调整库存（增量）——使用 `inventoryAdjustQuantities`：

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

设置绝对库存（非增量）—— `inventorySetQuantities`：

```bash
shop_gql '
mutation($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { id }
    userErrors { field message }
  }
}' '{"input":{"reason":"correction","name":"available","ignoreCompareQuantity":true,"quantities":[{"inventoryItemId":"gid://shopify/InventoryItem/...","locationId":"gid://shopify/Location/...","quantity":100}]}}'
```
## 元字段与元对象 {#metafields-metaobjects}

元字段可以为资源（产品、客户、订单、商店）附加自定义数据。

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

## Storefront API（公开只读） {#storefront-api-public-read-only}

使用不同的端点、不同的令牌，适用于面向客户的应用程序或类似 Hydrogen 的无头架构。请求头不同：

- **端点：** `https://$SHOPIFY_STORE_DOMAIN/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头（公开）：** `X-Shopify-Storefront-Access-Token: <公共令牌>` — 可嵌入浏览器
- **认证头（私有）：** `Shopify-Storefront-Private-Token: <私有令牌>` — 仅服务端

```bash
curl -sS -X POST \
  "https://${SHOPIFY_STORE_DOMAIN}/api/${SHOPIFY_API_VERSION:-2026-01}/graphql.json" \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Storefront-Access-Token: ${SHOPIFY_STOREFRONT_TOKEN}" \
  -d '{"query":"{ shop { name } products(first: 5) { edges { node { id title handle } } } }"}' | jq
```

## 批量操作 {#bulk-operations}

用于导出超过速率限制的数据（完整产品目录、全年所有订单等）：

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

# 3. 当状态为 COMPLETED 时，下载 JSONL 文件
curl -sS "$URL" > products.jsonl
```

JSONL 文件中的每一行对应一个节点，嵌套的连接会作为单独的行输出，并带有 `__parentId`。如果需要，可在客户端重新组装。

## Webhooks {#webhooks}

订阅事件，无需轮询：

```bash
shop_gql '
mutation($topic: WebhookSubscriptionTopic!, $sub: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $sub) {
    webhookSubscription { id topic endpoint { __typename ... on WebhookHttpEndpoint { callbackUrl } } }
    userErrors { field message }
  }
}' '{"topic":"ORDERS_CREATE","sub":{"callbackUrl":"https://example.com/webhook","format":"JSON"}}'
```

使用应用的客户端密钥（而非访问令牌）验证传入的 Webhook HMAC：

```bash
echo -n "$REQUEST_BODY" | openssl dgst -sha256 -hmac "$APP_SECRET" -binary | base64
# 与 X-Shopify-Hmac-Sha256 请求头比较
```

## 注意事项 {#pitfalls}

- **REST 端点仍然存在但已冻结。** 不要再针对 `/admin/api/.../products.json` 编写新的集成。请使用 GraphQL。
- **检查令牌格式。** 管理员令牌以 `shpat_` 开头。Storefront 公开令牌以 `shpua_` 开头。如果使用了错误的令牌和请求头组合，每次请求都会返回 401，且没有有用的错误消息体。
- **拿到 403 但令牌有效 = 缺少作用域。** Shopify 会返回 `{"errors":[{"message":"Access denied for ..."}]}`。在应用中重新配置 Admin API 作用域，然后重新安装以重新生成令牌。
- **`userErrors` 为空并不代表成功。** 还要检查 `data.&lt;mutation&gt;.&lt;resource&gt;` 是否为非 null。某些失败可能两者都不返回——请检查整个响应。
- **GID 与数字 ID。** 旧的 REST API 返回数字 ID，但 GraphQL 需要完整的 GID 字符串。转换方式：`gid://shopify/Product/<数字ID>`。
- **速率限制陷阱。** 一个深度嵌套的 `products(first: 250)` 查询可能消耗 1000 个点，并在标准计划的商店上立即触发限流。建议从窄范围开始，读取 `extensions.cost`，再相应调整。
- **分页排序。** `products(first: N, reverse: true)` 按 `id DESC` 排序，而不是按 `created_at`。要获取“最新优先”，请使用 `sortKey: CREATED_AT, reverse: true`。
- **历史数据需要 `read_all_orders`**。没有此权限时，`orders(...)` 会静默限制在 60 天窗口内。你不会收到错误提示，只是结果比预期少。对于订单量大的 Shopify Plus 商家，请通过应用的受保护数据设置申请此作用域。
- **货币是字符串。** 金额以 `"49.00"` 而非 `49.0` 的形式返回。如果你在意零填充，不要盲目使用 `jq tonumber`。
- **多币种金额字段** 包含 `shopMoney`（商店货币）和 `presentmentMoney`（客户显示货币）。请统一选择其中一个。
## 安全性 {#safety}

Shopify 中的变更操作是真实生效的——它们会创建商品、处理退款、取消订单、执行发货。在执行 `productDelete`、`orderCancel`、`refundCreate` 或任何批量变更操作之前：请明确说明变更内容、涉及哪个店铺，并与用户确认。除非用户拥有独立的开发商店，否则不存在生产数据的预演克隆。
