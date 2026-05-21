---
title: "健身营养 — 健身房训练计划与营养追踪器"
sidebar_label: "健身营养"
description: "健身房训练计划与营养追踪器"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="fitness-nutrition"></a>
# 健身营养

健身房训练计划与营养追踪器。通过 wger 搜索 690+ 种按肌肉、器械或类别分类的运动。通过 USDA FoodData Central 查找 380,000+ 种食物的宏量和卡路里。计算 BMI、TDEE、最大重复次数、宏量分配和体脂率——纯 Python，无需 pip 安装。专为追求健身增肌、减重或只是想吃得更好的人设计。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/health/fitness-nutrition` 安装 |
| 路径 | `optional-skills/health/fitness-nutrition` |
| 版本 | `1.0.0` |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `health`, `fitness`, `nutrition`, `gym`, `workout`, `diet`, `exercise` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。当技能激活时，代理看到的指令就是以下内容。
:::

# 健身与营养

专业健身教练与运动营养技能。两个数据源加上离线计算器——健身房爱好者所需的一切尽在一处。

**数据源（全部免费，无 pip 依赖）：**

- **wger** (https://wger.de/api/v2/) — 开放式运动数据库，690+ 种运动，包含肌肉、器械、图片。公共端点无需认证。
- **USDA FoodData Central** (https://api.nal.usda.gov/fdc/v1/) — 美国政府营养数据库，380,000+ 种食物。使用 `DEMO_KEY` 即可立即使用；免费注册可获得更高限额。

**离线计算器（纯标准库 Python）：**

- BMI、TDEE（Mifflin-St Jeor 公式）、最大重复次数（Epley/Brzycki/Lombardi）、宏量分配、体脂率（美国海军方法）

---

<a id="when-to-use"></a>
## 何时使用

当用户询问以下内容时触发此技能：
- 运动、训练、健身房套路、肌肉群、训练分化
- 食物宏量、卡路里、蛋白质含量、饮食计划、卡路里计算
- 身体成分：BMI、体脂、TDEE、卡路里盈余/赤字
- 最大重复次数估算、训练百分比、渐进超负荷
- 减脂、增肌或维持的宏量比例

---

<a id="procedure"></a>
## 操作流程

<a id="exercise-lookup-wger-api"></a>
### 运动查询（wger API）

所有 wger 公共端点均返回 JSON，无需认证。始终在运动查询中添加 `format=json` 和 `language=2`（英语）。

**步骤 1 — 识别用户需求：**

- 按肌肉 → 使用 `/api/v2/exercise/?muscles={id}&language=2&status=2&format=json`
- 按类别 → 使用 `/api/v2/exercise/?category={id}&language=2&status=2&format=json`
- 按器械 → 使用 `/api/v2/exercise/?equipment={id}&language=2&status=2&format=json`
- 按名称 → 使用 `/api/v2/exercise/search/?term={query}&language=english&format=json`
- 完整详情 → 使用 `/api/v2/exerciseinfo/{exercise_id}/?format=json`

**步骤 2 — 参考 ID（以便无需额外 API 调用）：**

运动类别：

| ID | 类别    |
|----|---------|
| 8  | 手臂    |
| 9  | 腿部    |
| 10 | 腹部    |
| 11 | 胸部    |
| 12 | 背部    |
| 13 | 肩部    |
| 14 | 小腿    |
| 15 | 有氧    |
肌肉：

| ID | 肌肉名称                | ID | 肌肉名称              |
|----|-------------------------|----|-----------------------|
| 1  | 肱二头肌                | 2  | 三角肌前束            |
| 3  | 前锯肌                  | 4  | 胸大肌                |
| 5  | 腹外斜肌                | 6  | 腓肠肌                |
| 7  | 腹直肌                  | 8  | 臀大肌                |
| 9  | 斜方肌                  | 10 | 股四头肌              |
| 11 | 股二头肌                | 12 | 背阔肌                |
| 13 | 肱肌                    | 14 | 肱三头肌              |
| 15 | 比目鱼肌                |    |                       |

器材：

| ID | 器材名称        |
|----|-----------------|
| 1  | 杠铃            |
| 3  | 哑铃            |
| 4  | 瑜伽垫          |
| 5  | 瑞士球          |
| 6  | 引体向上杆      |
| 7  | 无（自重）      |
| 8  | 长凳            |
| 9  | 上斜凳          |
| 10 | 壶铃            |

**步骤 3 — 获取并展示结果：**

```bash
# 按名称搜索动作
QUERY="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY")
curl -s "https://wger.de/api/v2/exercise/search/?term=${ENCODED}&language=english&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
for s in data.get('suggestions',[])[:10]:
    d=s.get('data',{})
    print(f\"  ID {d.get('id','?'):>4} | {d.get('name','N/A'):<35} | 类别: {d.get('category','N/A')}\")
"
```

```bash
# 获取某个动作的完整详情
EXERCISE_ID="$1"
curl -s "https://wger.de/api/v2/exerciseinfo/${EXERCISE_ID}/?format=json" \
  | python3 -c "
import json,sys,html,re
data=json.load(sys.stdin)
trans=[t for t in data.get('translations',[]) if t.get('language')==2]
t=trans[0] if trans else data.get('translations',[{}])[0]
desc=re.sub('<[^>]+>','',html.unescape(t.get('description','N/A')))
print(f\"动作名称  : {t.get('name','N/A')}\")
print(f\"类别      : {data.get('category',{}).get('name','N/A')}\")
print(f\"主要肌群  : {', '.join(m.get('name_en','') for m in data.get('muscles',[])) or 'N/A'}\")
print(f\"辅助肌群  : {', '.join(m.get('name_en','') for m in data.get('muscles_secondary',[])) or '无'}\")
print(f\"所需器材  : {', '.join(e.get('name','') for e in data.get('equipment',[])) or '自重'}\")
print(f\"动作要领  : {desc[:500]}\")
imgs=data.get('images',[])
if imgs: print(f\"图片链接  : {imgs[0].get('image','')}\")
"
```

```bash
# 按肌肉、类别或器材筛选动作
# 根据需要组合筛选条件：?muscles=4&equipment=1&language=2&status=2
FILTER="$1"  # 例如 "muscles=4" 或 "category=11" 或 "equipment=3"
curl -s "https://wger.de/api/v2/exercise/?${FILTER}&language=2&status=2&limit=20&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(f'共找到 {data.get(\"count\",0)} 个动作。')
for ex in data.get('results',[]):
    print(f\"  ID {ex['id']:>4} | 肌肉: {ex.get('muscles',[])} | 器材: {ex.get('equipment',[])}\")
"
```

<a id="nutrition-lookup-usda-fooddata-central"></a>
### 营养查询（USDA FoodData Central）
如果设置了 `USDA_API_KEY` 环境变量，则使用它，否则回退到 `DEMO_KEY`。
`DEMO_KEY` 限制为 30 次请求/小时。免费注册密钥限制为 1,000 次请求/小时。

```bash
# 按名称搜索食品
FOOD="$1"
API_KEY="${USDA_API_KEY:-DEMO_KEY}"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$FOOD")
curl -s "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=${API_KEY}&query=${ENCODED}&pageSize=5&dataType=Foundation,SR%20Legacy" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
foods=data.get('foods',[])
if not foods: print('No foods found.'); sys.exit()
for f in foods:
    n={x['nutrientName']:x.get('value','?') for x in f.get('foodNutrients',[])}
    cal=n.get('Energy','?'); prot=n.get('Protein','?')
    fat=n.get('Total lipid (fat)','?'); carb=n.get('Carbohydrate, by difference','?')
    print(f\"{f.get('description','N/A')}\")
    print(f\"  Per 100g: {cal} kcal | {prot}g protein | {fat}g fat | {carb}g carbs\")
    print(f\"  FDC ID: {f.get('fdcId','N/A')}\")
    print()
"
```

```bash
# 按FDC ID获取详细营养信息
FDC_ID="$1"
API_KEY="${USDA_API_KEY:-DEMO_KEY}"
curl -s "https://api.nal.usda.gov/fdc/v1/food/${FDC_ID}?api_key=${API_KEY}" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"Food: {d.get('description','N/A')}\")
print(f\"{'Nutrient':<40} {'Amount':>8} {'Unit'}\")
print('-'*56)
for x in sorted(d.get('foodNutrients',[]),key=lambda x:x.get('nutrient',{}).get('rank',9999)):
    nut=x.get('nutrient',{}); amt=x.get('amount',0)
    if amt and float(amt)>0:
        print(f\"  {nut.get('name',''):<38} {amt:>8} {nut.get('unitName','')}\")
"
```

<a id="offline-calculators"></a>
### 离线计算器

使用 `scripts/` 中的辅助脚本进行批量操作，
或者直接内联运行进行单次计算：

- `python3 scripts/body_calc.py bmi <体重_kg> <身高_cm>`
- `python3 scripts/body_calc.py tdee <体重_kg> <身高_cm> <年龄> &lt;M|F&gt; <活动水平 1-5>`
- `python3 scripts/body_calc.py 1rm <重量> <次数>`
- `python3 scripts/body_calc.py macros &lt;tdee_kcal&gt; &lt;cut|maintain|bulk&gt;`
- `python3 scripts/body_calc.py bodyfat &lt;M|F&gt; <颈围_cm> <腰围_cm> [臀围_cm] <身高_cm>`

详见 `references/FORMULAS.md`，了解每个公式背后的科学原理。

---

<a id="pitfalls"></a>
## 常见陷阱

- wger 运动端点**默认返回所有语言**——务必添加 `language=2` 只获取英文结果
- wger 包含**未经审核的用户提交内容**——添加 `status=2` 只获取已批准的运动
- USDA `DEMO_KEY` 限制 **30 次请求/小时**——批量请求之间添加 `sleep 2`，或者获取免费密钥
- USDA 数据是**每 100g 的数值**——提醒用户按实际份量换算
- BMI 无法区分肌肉和脂肪——肌肉发达的人 BMI 偏高不一定不健康
- 体脂公式是**估算值**（±3-5%）——如需精确结果，建议进行 DEXA 扫描
- 1RM 公式在超过 10 次时准确度下降——使用 3-5 次组能获得最佳估算
- wger 的 `exercise/search` 端点参数名是 `term` 而非 `query`

---

<a id="verification"></a>
## 验证

执行运动搜索后：确认结果包含运动名称、肌肉群和器材信息。
执行营养查询后：确认返回每 100g 的宏量营养素（千卡、蛋白质、脂肪、碳水化合物）。
执行计算器后：对输出进行合理性检查（例如，大多数成年人的 TDEE 应在 1500-3500 之间）。
---

<a id="quick-reference"></a>
## 快速参考

| 任务 | 数据源 | 端点 |
|------|--------|----------|
| 按名称搜索练习 | wger | `GET /api/v2/exercise/search/?term=&language=english` |
| 练习详情 | wger | `GET /api/v2/exerciseinfo/{id}/` |
| 按肌肉筛选 | wger | `GET /api/v2/exercise/?muscles={id}&language=2&status=2` |
| 按器材筛选 | wger | `GET /api/v2/exercise/?equipment={id}&language=2&status=2` |
| 列出类别 | wger | `GET /api/v2/exercisecategory/` |
| 列出肌肉 | wger | `GET /api/v2/muscle/` |
| 搜索食物 | USDA | `GET /fdc/v1/foods/search?query=&dataType=Foundation,SR Legacy` |
| 食物详情 | USDA | `GET /fdc/v1/food/{fdcId}` |
| BMI / TDEE / 1RM / 宏量营养素 | 离线 | `python3 scripts/body_calc.py` |
