# Hermes Agent 中文文档站

这个目录是 **Hermes Agent 官方文档站的中文版本**，用于单独部署到 Vercel。

设计原则很简单：

- 英文源站保留在 [website](/Users/dracohu/REPO/hermes-agent/website)
- 中文站单独维护在 [site](/Users/dracohu/REPO/hermes-agent/site)
- Vercel 只部署 `site/`

这样做的好处是结构清晰，维护成本低，也不用处理 Docusaurus 的多语言配置。

## 目录说明

- [docs](/Users/dracohu/REPO/hermes-agent/site/docs)：中文文档正文
- [docusaurus.config.ts](/Users/dracohu/REPO/hermes-agent/site/docusaurus.config.ts)：站点配置
- [sidebars.ts](/Users/dracohu/REPO/hermes-agent/site/sidebars.ts)：侧边栏结构
- [vercel.json](/Users/dracohu/REPO/hermes-agent/site/vercel.json)：Vercel 构建配置
- [scripts/check_docs_parity.py](/Users/dracohu/REPO/hermes-agent/site/scripts/check_docs_parity.py)：检查中文站与英文源站的文档结构是否一致
- [scripts/translate_docs.py](/Users/dracohu/REPO/hermes-agent/site/scripts/translate_docs.py)：批量翻译脚本

## 环境要求

- Node.js `>= 20`
- npm `>= 10`
- Python 3

## 本地安装

在 `site/` 目录下安装依赖：

```bash
npm ci
```

## 本地开发

启动本地开发服务器：

```bash
npm start
```

如果你只是想验证静态构建是否正常：

```bash
npm run build
```

构建产物会输出到 `build/` 目录。

## 本地预览构建结果

```bash
npm run serve
```

## Vercel 部署

Vercel 中请直接选择 `site/` 作为 Root Directory。

当前构建配置已经写在 [vercel.json](/Users/dracohu/REPO/hermes-agent/site/vercel.json)：

- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: `build`

如果你使用 Vercel Web 控制台，通常不需要再手动改这些值。

## 结构一致性检查

每次同步或翻译完文档后，建议先跑一次结构检查：

```bash
npm run check:docs-parity
```

这个脚本会对比：

- 英文源站：`website/docs`
- 中文站：`site/docs`

目标是确保文档数量、路径和层级结构保持一致，避免漏页。

## 批量翻译

批量翻译脚本入口：

```bash
npm run translate:docs -- --help
```

常见用法示例：

```bash
npm run translate:docs -- --skip-translated
```

如果只想重翻某几篇：

```bash
npm run translate:docs -- --files "docs/getting-started/quickstart.md" "docs/reference/faq.md"
```

注意：

- 这个脚本会调用外部模型 API
- 文档内容会发送到你配置的模型服务
- 不要把 API Key 写进仓库

## 日常维护建议

推荐按下面的顺序更新中文站：

1. 先同步英文源站的变更到 `website/`
2. 把对应文件复制或同步到 `site/`
3. 运行结构检查
4. 只翻译新增或变更的文档
5. 跑一次 `npm run build`
6. 确认没有 broken links / broken anchors 再部署

## 当前维护约定

- 保持与官方源站相同的文档结构
- 中文尽量写得自然、清楚，不堆术语
- 产品名、协议名、平台名可保留原文，必要时加中文说明
- 如果翻译后导致标题锚点变化，优先补显式锚点，避免站内链接失效

## 故障排查

### 构建失败，提示 MDX 解析错误

优先检查这些地方：

- 表格里是否出现了 `<1%`、`<100ms` 这类内容
- 是否写了 `**http://...**` 这种带加粗的裸 URL
- 是否使用了 MDX 不兼容的尖括号链接

通常改成下面几种形式就能解决：

- `<1%` 改成 `&lt;1%`
- `**http://example.com**` 改成 `` `http://example.com` ``
- `<https://example.com>` 改成 `[example.com](https://example.com)`

### 构建通过，但有 broken anchors

这通常是因为标题翻译后，Docusaurus 自动生成的锚点变了。

处理方法：

- 给标题补显式锚点，例如 `## 标题 {#stable-anchor}`
- 或把引用方的链接改成新的锚点名

---

如果后面继续扩展这个中文站，建议优先把变更控制在 `site/` 内，不要直接改英文源站目录。
