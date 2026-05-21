---
title: "概念图"
sidebar_label: "概念图"
description: "生成扁平、极简、支持浅色/深色模式的 SVG 图，以独立 HTML 文件形式输出，使用统一的教育视觉语言，包含 9 种语义颜色渐变、句子式排版和自动深色模式。最适合教育类和非软件类图形——物理实验装置、化学机理、数学曲线、物理实物（飞机、涡轮机、智能手机、机械表）、解剖图、平面图、剖面图、叙事旅程（X 的生命周期、Y 的流程）、Hub-Spoke 系统集成（智慧城市、物联网）以及分解层视图。如果存在更针对该主题的专业技能（专用软件/云架构、手绘草图、动画解说等），则优先使用那些技能；否则此技能也可作为通用 SVG 图的后备方案，提供干净的教育风格。附带 15 个示例图。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="concept-diagrams"></a>
# 概念图

生成扁平、极简、支持浅色/深色模式的 SVG 图，以独立 HTML 文件形式输出，使用统一的教育视觉语言，包含 9 种语义颜色渐变、句子式排版和自动深色模式。最适合教育类和非软件类图形——物理实验装置、化学机理、数学曲线、物理实物（飞机、涡轮机、智能手机、机械表）、解剖图、平面图、剖面图、叙事旅程（X 的生命周期、Y 的流程）、Hub-Spoke 系统集成（智慧城市、物联网）以及分解层视图。如果存在更针对该主题的专业技能（专用软件/云架构、手绘草图、动画解说等），则优先使用那些技能；否则此技能也可作为通用 SVG 图的后备方案，提供干净的教育风格。附带 15 个示例图。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/creative/concept-diagrams` 安装 |
| 路径 | `optional-skills/creative/concept-diagrams` |
| 版本 | `0.1.0` |
| 作者 | v1k22（原始 PR），移植至 hermes-agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `diagrams`, `svg`, `visualization`, `education`, `physics`, `chemistry`, `engineering` |
| 相关技能 | [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw), `generative-widgets` |
<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
下方是该技能被触发时 Hermes 加载的完整技能定义。这就是该技能激活时 Agent 所看到的指令。
:::

<a id="concept-diagrams"></a>
# 概念示意图

采用统一的扁平极简设计系统，生成生产级质量的 SVG 示意图。输出为一个独立的 HTML 文件，在任何现代浏览器中渲染效果一致，并自动支持浅色/深色模式。

<a id="scope"></a>
## 适用范围

**最适合：**
- 物理装置、化学机制、数学曲线、生物学
- 实物对象（飞机、涡轮机、智能手机、机械手表、细胞）
- 解剖图、剖面图、分解图层视图
- 平面图、建筑改造图
- 叙事流程（X 的生命周期、Y 的过程）
- 中心辐射式系统集成（智慧城市、物联网网络、电网）
- 任何领域的教育/教科书风格可视化
- 定量图表（分组柱状图、能量曲线图）

**请优先考虑其他技能的场景：**
- 深色科技美学风格的专用软件/云基础设施架构图（如有可用，请考虑使用 `architecture-diagram`）
- 手绘白板草图（如有可用，请考虑使用 `excalidraw`）
- 动画解说或视频输出（请考虑使用动画类技能）

如果存在更专精于该主题的技能，优先使用它。若没有适合的，此技能可作为通用的 SVG 示意图后备方案——输出将带有下述干净的教育风格美学，这几乎是任何主题的合理默认选择。
<a id="workflow"></a>
## 工作流程

1. 确定图表类型（参见下方“图表类型”）。
2. 使用设计系统规则布局组件。
3. 以 `templates/template.html` 为包装器编写完整的 HTML 页面 — 将你的 SVG 粘贴到模板中 `<!-- PASTE SVG HERE -->` 的位置。
4. 保存为独立的 `.html` 文件（例如 `~/my-diagram.html` 或 `./my-diagram.html`）。
5. 用户直接在浏览器中打开 — 无需服务器，无需依赖。

可选：如果用户想要一个可浏览的多图表画廊，请参见底部的“本地预览服务器”。

加载 HTML 模板：
```
skill_view(name="concept-diagrams", file_path="templates/template.html")
```

该模板嵌入了完整的 CSS 设计系统（`c-*` 颜色类、文本类、亮/暗模式变量、箭头标记样式）。你生成的 SVG 依赖于这些类存在于宿主页面上。

---

<a id="design-system"></a>
## 设计系统

<a id="philosophy"></a>
### 设计理念

- **扁平**：无渐变、无投影、无模糊、无发光或霓虹效果。
- **极简**：只展示核心内容。框内无装饰性图标。
- **一致**：每个图表使用相同的颜色、间距、排版和描边宽度。
- **暗色模式就绪**：所有颜色通过 CSS 类自动适配 — 无需为每种模式单独制作 SVG。

<a id="color-palette"></a>
### 调色板

9 个颜色梯度，每个有 7 个色阶。将类名放在 `&lt;g&gt;` 或形状元素上；模板 CSS 会处理两种模式。

| 类名        | 50（最浅） | 100     | 200     | 400     | 600     | 800     | 900（最深） |
|------------|-----------|---------|---------|---------|---------|---------|-----------|
| `c-purple` | #EEEDFE | #CECBF6 | #AFA9EC | #7F77DD | #534AB7 | #3C3489 | #26215C |
| `c-teal`   | #E1F5EE | #9FE1CB | #5DCAA5 | #1D9E75 | #0F6E56 | #085041 | #04342C |
| `c-coral`  | #FAECE7 | #F5C4B3 | #F0997B | #D85A30 | #993C1D | #712B13 | #4A1B0C |
| `c-pink`   | #FBEAF0 | #F4C0D1 | #ED93B1 | #D4537E | #993556 | #72243E | #4B1528 |
| `c-gray`   | #F1EFE8 | #D3D1C7 | #B4B2A9 | #888780 | #5F5E5A | #444441 | #2C2C2A |
| `c-blue`   | #E6F1FB | #B5D4F4 | #85B7EB | #378ADD | #185FA5 | #0C447C | #042C53 |
| `c-green`  | #EAF3DE | #C0DD97 | #97C459 | #639922 | #3B6D11 | #27500A | #173404 |
| `c-amber`  | #FAEEDA | #FAC775 | #EF9F27 | #BA7517 | #854F0B | #633806 | #412402 |
| `c-red`    | #FCEBEB | #F7C1C1 | #F09595 | #E24B4A | #A32D2D | #791F1F | #501313 |
<a id="color-assignment-rules"></a>
#### 颜色分配规则

颜色编码的是**含义**，而非顺序。不要像彩虹一样循环使用颜色。

- 按**类别**对节点进行分组——同一类型的所有节点共享一种颜色。
- 对中性/结构性节点（开始、结束、通用步骤、用户）使用 `c-gray`。
- 每张图表使用 **2-3 种颜色**，而不是 6 种以上。
- 对于一般类别，优先使用 `c-purple`、`c-teal`、`c-coral`、`c-pink`。
- 将 `c-blue`、`c-green`、`c-amber`、`c-red` 保留给语义含义（信息、成功、警告、错误）。

明暗模式颜色映射（由模板 CSS 处理——只需用到类名即可）：
- 浅色模式：50 填充 + 600 描边 + 800 标题 / 600 副标题
- 深色模式：800 填充 + 200 描边 + 100 标题 / 200 副标题

<a id="typography"></a>
### 排版

只有两种字号。没有例外。

| 类名 | 尺寸  | 字重 | 用途                   |
|------|-------|------|------------------------|
| `th` | 14px  | 500  | 节点标题、区域标签     |
| `ts` | 12px  | 400  | 副标题、描述、箭头标签 |
| `t`  | 14px  | 400  | 通用文本               |

- **始终使用首字母小写。** 从不使用首字母大写，也从不使用全部大写。
- 每个 `&lt;text&gt;` 元素**必须**带有类名（`t`、`ts` 或 `th`）。不允许有无类名的文本。
- 所有盒子内的文本均使用 `dominant-baseline="central"`。
- 盒子内居中文本使用 `text-anchor="middle"`。

**宽度估算（近似值）：**
- 14px 字重 500：约每字符 8px
- 12px 字重 400：约每字符 6.5px
- 始终验证：`框宽 >= (字符数 × 每字符像素) + 48`（每边 24px 内边距）

<a id="spacing-layout"></a>
### 间距与布局

- **视口**：`viewBox="0 0 680 H"`，其中 H = 内容高度 + 40px 缓冲。
- **安全区域**：x=40 到 x=640，y=40 到 y=(H-40)。
- **盒子之间**：最小间距 60px。
- **盒子内部**：水平内边距 24px，垂直内边距 12px。
- **箭头间距**：箭头尖端与盒子边缘之间 10px。
- **单行盒子**：高度 44px。
- **双行盒子**：高度 56px，标题与副标题基线之间 18px。
- **容器内边距**：每个容器内部至少 20px。
- **最大嵌套层级**：2–3 层。嵌套更深会在 680px 宽度下难以阅读。
<a id="stroke-shape"></a>
### 描边与形状

- **描边宽度**：所有节点边框为 0.5px。不要 1px，不要 2px。
- **圆角矩形**：节点使用 `rx="8"`，内部容器使用 `rx="12"`，外部容器使用 `rx="16"` 至 `rx="20"`。
- **连线路径**：必须带有 `fill="none"`。否则 SVG 默认以黑色填充。

<a id="arrow-marker"></a>
### 箭头标记

在每个 SVG 的开头包含以下 `&lt;defs&gt;` 块：

```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

在线上使用 `marker-end="url(#arrow)"`。箭头会通过 `context-stroke` 继承线的颜色。

<a id="css-classes-provided-by-the-template"></a>
### CSS 类（由模板提供）

模板页面提供了以下内容：

- 文本：`.t`, `.ts`, `.th`
- 中性：`.box`, `.arr`, `.leader`, `.node`
- 颜色渐变：`.c-purple`, `.c-teal`, `.c-coral`, `.c-pink`, `.c-gray`, `.c-blue`, `.c-green`, `.c-amber`, `.c-red`（全部支持自动亮/暗模式）

你**无需**重新定义这些类——只需在 SVG 中应用即可。模板文件包含完整的 CSS 定义。

---

<a id="svg-boilerplate"></a>
## SVG 基础模板

模板页面中的每个 SVG 都以此精确结构开头：

```xml
<svg width="100%" viewBox="0 0 680 {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- 在此处放置图表内容 -->

</svg>
```
将 `{HEIGHT}` 替换为实际计算出的高度（最后一个元素的底部 + 40px）。

<a id="node-patterns"></a>
### 节点样式

**单行节点（44px）：**
```xml
<g class="node c-blue">
  <rect x="100" y="20" width="180" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="190" y="42" text-anchor="middle" dominant-baseline="central">Service name</text>
</g>
```

**双行节点（56px）：**
```xml
<g class="node c-teal">
  <rect x="100" y="20" width="200" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="200" y="38" text-anchor="middle" dominant-baseline="central">Service name</text>
  <text class="ts" x="200" y="56" text-anchor="middle" dominant-baseline="central">Short description</text>
</g>
```

**连接线（无标签）：**
```xml
<line x1="200" y1="76" x2="200" y2="120" class="arr" marker-end="url(#arrow)"/>
```

**容器（虚线或实线）：**
```xml
<g class="c-purple">
  <rect x="40" y="92" width="600" height="300" rx="16" stroke-width="0.5"/>
  <text class="th" x="66" y="116">Container label</text>
  <text class="ts" x="66" y="134">Subtitle info</text>
</g>
```

---

<a id="diagram-types"></a>
## 图表类型

根据主题选择合适的布局：

1. **流程图** — CI/CD 流水线、请求生命周期、审批工作流、数据处理。单向流程（自上而下或从左到右）。每行最多 4-5 个节点。
2. **结构/包含图** — 云基础设施嵌套、分层系统架构。大外框容器包含内部区域。使用虚线矩形表示逻辑分组。
3. **API/端点映射** — REST 路由、GraphQL 模式。从根节点展开为树形，分支到资源组，每个资源组包含端点节点。
4. **微服务拓扑** — 服务网格、事件驱动系统。服务作为节点，箭头表示通信模式，中间放置消息队列。
5. **数据流图** — ETL 流水线、流式架构。从左到右从数据源经过处理流向目标。
6. **物理/结构图** — 交通工具、建筑物、硬件、解剖图。使用符合物理形态的形状——`&lt;path&gt;` 用于曲线主体，`&lt;polygon&gt;` 用于锥形，`&lt;ellipse&gt;`/`&lt;circle&gt;` 用于圆柱形部件，嵌套 `&lt;rect&gt;` 表示隔间。参见 `references/physical-shape-cookbook.md`。
7. **基础设施/系统集成图** — 智慧城市、物联网网络、多域系统。以中心平台连接子系统的轮辐布局。语义线条样式（`.data-line`、`.power-line`、`.water-pipe`、`.road`）。参见 `references/infrastructure-patterns.md`。
8. **UI/仪表盘线框图** — 管理面板、监控仪表盘。屏幕框架内嵌图表/仪表/指示器元素。参见 `references/dashboard-patterns.md`。
对于物理、基础设施和仪表盘图表，请在生成前加载对应的参考文件——每个文件都提供了现成的 CSS 类和形状基本元素。

---

<a id="validation-checklist"></a>
## 验证清单

在最终确定任何 SVG 之前，请验证以下所有项：

1. 每个 `&lt;text&gt;` 都有类 `t`、`ts` 或 `th`。
2. 每个位于盒子内部的 `&lt;text&gt;` 都有 `dominant-baseline="central"`。
3. 每个用作箭头的连接线 `&lt;path&gt;` 或 `&lt;line&gt;` 都有 `fill="none"`。
4. 没有箭头线穿过无关的盒子。
5. 对于 14px 字体，`box_width >= (最长标签字符数 × 8) + 48`。
6. 对于 12px 字体，`box_width >= (最长标签字符数 × 6.5) + 48`。
7. ViewBox 高度 = 最底部元素 + 40px。
8. 所有内容保持在 x=40 到 x=640 范围内。
9. 颜色类（`c-*`）应用于 `&lt;g&gt;` 或形状元素，绝不能用于 `&lt;path&gt;` 连接线。
10. 箭头 `&lt;defs&gt;` 块必须存在。
11. 不要使用渐变、阴影、模糊或发光效果。
12. 所有节点边框的描边宽度为 0.5px。

---

<a id="output-preview"></a>
## 输出与预览

<a id="default-standalone-html-file"></a>
### 默认：独立的 HTML 文件

编写一个用户可以直接打开的单个 `.html` 文件。无需服务器，无依赖，可离线工作。模式如下：

```python
# 1. 加载模板
template = skill_view("concept-diagrams", "templates/template.html")

# 2. 填写标题、副标题，并粘贴你的 SVG
html = template.replace(
    "<!-- DIAGRAM TITLE HERE -->", "SN2反应机理"
).replace(
    "<!-- OPTIONAL SUBTITLE HERE -->", "双分子亲核取代"
).replace(
    "<!-- PASTE SVG HERE -->", svg_content
)

# 3. 写入用户选择的路径（默认 ./）
write_file("./sn2-mechanism.html", html)
```
告诉用户如何打开它：

```
# macOS
open ./sn2-mechanism.html
# Linux
xdg-open ./sn2-mechanism.html
```

<a id="optional-local-preview-server-multi-diagram-gallery"></a>
### 可选：本地预览服务器（多图表画廊）

仅当用户明确想要可浏览的多图表画廊时使用。

**规则：**
- 仅绑定到 `127.0.0.1`。永远不要使用 `0.0.0.0`。在所有网络接口上暴露图表在共享网络中是一种安全风险。
- 选择一个空闲端口（不要硬编码），并告知用户所选 URL。
- 服务器是可选的，且选择加入——优先使用独立 HTML 文件。

推荐模式（让操作系统选择一个空闲的临时端口）：

```bash
# 将每个图表放在 .diagrams/ 下的单独文件夹中
mkdir -p .diagrams/sn2-mechanism
# ...写入 .diagrams/sn2-mechanism/index.html...

# 仅在回环地址上提供服务，使用空闲端口
cd .diagrams && python3 -c "
import http.server, socketserver
with socketserver.TCPServer(('127.0.0.1', 0), http.server.SimpleHTTPRequestHandler) as s:
    print(f'Serving at http://127.0.0.1:{s.server_address[1]}/')
    s.serve_forever()
" &
```

如果用户坚持使用固定端口，请使用 `127.0.0.1:&lt;port&gt;`——仍然不要用 `0.0.0.0`。记录如何停止服务器（`kill %1` 或 `pkill -f "http.server"`）。

---

<a id="examples-reference"></a>
## 示例参考

`examples/` 目录提供了 15 个完整且经过测试的图表。在编写类似类型的新图表之前，请先浏览这些示例以了解可行的模式：

| 文件 | 类型 | 演示内容 |
|------|------|----------|
| `hospital-emergency-department-flow.md` | 流程图 | 带语义颜色的优先级路由 |
| `feature-film-production-pipeline.md` | 流程图 | 分阶段工作流，水平子流程 |
| `automated-password-reset-flow.md` | 流程图 | 带错误分支的认证流程 |
| `autonomous-llm-research-agent-flow.md` | 流程图 | 回环箭头，决策分支 |
| `place-order-uml-sequence.md` | 序列图 | UML 序列图风格 |
| `commercial-aircraft-structure.md` | 物理结构 | 路径、多边形、椭圆以呈现逼真形状 |
| `wind-turbine-structure.md` | 物理剖视图 | 地下/地上分离，颜色编码 |
| `smartphone-layer-anatomy.md` | 分解视图 | 左右交替标注，分层组件 |
| `apartment-floor-plan-conversion.md` | 楼层平面图 | 墙壁、门、用红色虚线表示的拟议变更 |
| `banana-journey-tree-to-smoothie.md` | 叙事旅程 | 蜿蜒路径，渐进状态变化 |
| `cpu-ooo-microarchitecture.md` | 硬件流水线 | 扇出，内存层次侧栏 |
| `sn2-reaction-mechanism.md` | 化学 | 分子、弯箭头、能量剖面图 |
| `smart-city-infrastructure.md` | 中心辐射 | 按系统的语义线条样式 |
| `electricity-grid-flow.md` | 多阶段流程 | 电压层次，流向标记 |
| `ml-benchmark-grouped-bar-chart.md` | 图表 | 分组柱状图，双轴 |
```
skill_view(name="concept-diagrams", file_path="examples/<filename>")
```

---

<a id="quick-reference-what-to-use-when"></a>
## 快速参考：何时使用何种图表

| 用户说 | 图表类型 | 建议颜色 |
|-----------|--------------|------------------|
| “显示流水线” | 流程图 | 灰色开始/结束，紫色步骤，红色错误，青色部署 |
| “绘制数据流” | 数据管道（从左到右） | 灰色来源，紫色处理，青色接收端 |
| “可视化系统” | 结构图（包含关系） | 紫色容器，青色服务，珊瑚色数据 |
| “映射端点” | API树 | 紫色根节点，每个资源组一个坡道 |
| “显示服务” | 微服务拓扑 | 灰色入口，青色服务，紫色总线，珊瑚色工作者 |
| “绘制飞行器/车辆” | 物理图 | 路径、多边形、椭圆以实现真实形状 |
| “智慧城市/IoT” | 中心辐射集成 | 每个子系统使用语义线型 |
| “显示仪表盘” | UI线框图 | 深色屏幕，图表颜色：青色、紫色、警报用珊瑚色 |
| “电网/电力” | 多级流程 | 电压层级（高压/中压/低压线宽） |
| “风力涡轮机/涡轮” | 物理截面 | 基础+塔筒剖面+机舱颜色编码 |
| “X的旅程/生命周期” | 叙事旅程 | 弯曲路径，渐进状态变化 |
| “X的层次/分解” | 分解视图 | 垂直堆叠，交替标签 |
| “CPU/流水线” | 硬件管道 | 垂直阶段，扇出到执行端口 |
| “布局图/公寓” | 布局图 | 墙壁、门、虚线红色表示提议更改 |
| “反应机理” | 化学反应 | 原子、键、弯曲箭头、过渡态、能量曲线 |
