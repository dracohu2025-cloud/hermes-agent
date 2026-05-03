---
title: "健身营养 — 健身房训练计划与营养追踪器"
sidebar_label: "健身营养"
description: "健身房训练计划与营养追踪器"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 健身营养 {#fitness-nutrition}

健身房训练计划与营养追踪器。通过 wger 按肌肉、器械或类别搜索 690 多种训练动作。通过 USDA FoodData Central 查询 38 万多种食物的宏量和卡路里。计算 BMI、TDEE、单次最大重量、宏量营养素分配和体脂率——纯 Python 实现，无需 pip 安装。专为追求增肌、减脂或只是想改善饮食的人打造。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/health/fitness-nutrition` 安装 |
| 路径 | `optional-skills/health/fitness-nutrition` |
| 版本 | `1.0.0` |
| 许可证 | MIT |
| 标签 | `health`, `fitness`, `nutrition`, `gym`, `workout`, `diet`, `exercise` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::
# 健身与营养 {#fitness-nutrition}

专业的健身教练和运动营养师技能。两个数据源加上离线计算器——健身爱好者所需的一切尽在其中。

**数据源（全部免费，无需 pip 依赖）：**

- **wger** (https://wger.de/api/v2/) — 开放运动数据库，690+ 项运动，包含肌肉、器械、图片信息。公共端点无需任何认证。
- **USDA FoodData Central** (https://api.nal.usda.gov/fdc/v1/) — 美国政府营养数据库，380,000+ 种食品。`DEMO_KEY` 立即可用；免费注册可获得更高限额。

**离线计算器（纯 Python 标准库实现）：**

- BMI、TDEE（Mifflin-St Jeor 公式）、单次最大重量（Epley/Brzycki/Lombardi 公式）、宏量营养素分配、体脂率（美国海军方法）

---

## 何时使用 {#when-to-use}

当用户询问以下内容时触发此技能：
- 运动、训练、健身计划、肌肉群、训练分化
- 食物宏量营养素、卡路里、蛋白质含量、饮食规划、卡路里计算
- 身体成分：BMI、体脂率、TDEE、热量盈余/赤字
- 单次最大重量估算、训练百分比、渐进超负荷
- 减脂、增肌或维持期的宏量营养素比例
---

## 步骤 {#procedure}

### 运动查询（wger API） {#exercise-lookup-wger-api}

所有 wger 公共端点均返回 JSON 且无需认证。查询运动时请始终添加 `format=json` 和 `language=2`（英文）。

**第 1 步 — 确定用户需求：**

- 按肌肉 → 使用 `/api/v2/exercise/?muscles={id}&language=2&status=2&format=json`
- 按类别 → 使用 `/api/v2/exercise/?category={id}&language=2&status=2&format=json`
- 按器材 → 使用 `/api/v2/exercise/?equipment={id}&language=2&status=2&format=json`
- 按名称 → 使用 `/api/v2/exercise/search/?term={query}&language=english&format=json`
- 查看完整详情 → 使用 `/api/v2/exerciseinfo/{exercise_id}/?format=json`

**第 2 步 — 参考 ID（这样你就不需要额外的 API 调用）：**

运动类别：

| ID | 类别      |
|----|-----------|
| 8  | 手臂      |
| 9  | 腿部      |
| 10 | 腹肌      |
| 11 | 胸部      |
| 12 | 背部      |
| 13 | 肩部      |
| 14 | 小腿      |
| 15 | 有氧运动  |

肌肉：

| ID | 肌肉                  | ID | 肌肉                |
|----|-----------------------|----|---------------------|
| 1  | 肱二头肌              | 2  | 三角肌前束          |
| 3  | 前锯肌                | 4  | 胸大肌              |
| 5  | 腹外斜肌              | 6  | 腓肠肌              |
| 7  | 腹直肌                | 8  | 臀大肌              |
| 9  | 斜方肌                | 10 | 股四头肌            |
| 11 | 股二头肌              | 12 | 背阔肌              |
| 13 | 肱肌                  | 14 | 肱三头肌            |
| 15 | 比目鱼肌              |    |                     |
Equipment:

| 编号 | 器材            |
|------|-----------------|
| 1    | 杠铃            |
| 3    | 哑铃            |
| 4    | 健身垫          |
| 5    | 瑞士球          |
| 6    | 引体向上杆      |
| 7    | 无（自重）      |
| 8    | 长凳            |
| 9    | 上斜凳          |
| 10   | 壶铃            |

**步骤 3 — 获取并展示结果：**

```bash
# Search exercises by name
QUERY="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY")
curl -s "https://wger.de/api/v2/exercise/search/?term=${ENCODED}&language=english&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
for s in data.get('suggestions',[])[:10]:
    d=s.get('data',{})
    print(f\"  ID {d.get('id','?'):>4} | {d.get('name','N/A'):<35} | Category: {d.get('category','N/A')}\")
"
```

```bash
# Get full details for a specific exercise
EXERCISE_ID="$1"
curl -s "https://wger.de/api/v2/exerciseinfo/${EXERCISE_ID}/?format=json" \
  | python3 -c "
import json,sys,html,re
data=json.load(sys.stdin)
trans=[t for t in data.get('translations',[]) if t.get('language')==2]
t=trans[0] if trans else data.get('translations',[{}])[0]
desc=re.sub('<[^>]+>','',html.unescape(t.get('description','N/A')))
print(f\"Exercise  : {t.get('name','N/A')}\")
print(f\"Category  : {data.get('category',{}).get('name','N/A')}\")
print(f\"Primary   : {', '.join(m.get('name_en','') for m in data.get('muscles',[])) or 'N/A'}\")
print(f\"Secondary : {', '.join(m.get('name_en','') for m in data.get('muscles_secondary',[])) or 'none'}\")
print(f\"Equipment : {', '.join(e.get('name','') for e in data.get('equipment',[])) or 'bodyweight'}\")
print(f\"How to    : {desc[:500]}\")
imgs=data.get('images',[])
if imgs: print(f\"Image     : {imgs[0].get('image','')}\")
"
```
```bash
# 按肌肉、类别或设备筛选练习
# 根据需要组合筛选条件：?muscles=4&equipment=1&language=2&status=2
FILTER="$1"  # 例如："muscles=4" 或 "category=11" 或 "equipment=3"
curl -s "https://wger.de/api/v2/exercise/?${FILTER}&language=2&status=2&limit=20&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(f'找到 {data.get(\"count\",0)} 个练习。')
for ex in data.get('results',[]):
    print(f\"  ID {ex['id']:>4} | 肌肉: {ex.get('muscles',[])} | 设备: {ex.get('equipment',[])}\")
"
```

### 营养查询（USDA FoodData Central） {#nutrition-lookup-usda-fooddata-central}

如果设置了 `USDA_API_KEY` 环境变量则使用该变量，否则回退到 `DEMO_KEY`。
`DEMO_KEY` = 30 次请求/小时。免费注册的密钥 = 1,000 次请求/小时。

```bash
# 按名称搜索食物
FOOD="$1"
API_KEY="${USDA_API_KEY:-DEMO_KEY}"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$FOOD")
curl -s "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=${API_KEY}&query=${ENCODED}&pageSize=5&dataType=Foundation,SR%20Legacy" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
foods=data.get('foods',[])
if not foods: print('未找到食物。'); sys.exit()
for f in foods:
    n={x['nutrientName']:x.get('value','?') for x in f.get('foodNutrients',[])}
    cal=n.get('能量','?'); prot=n.get('蛋白质','?')
    fat=n.get('总脂肪','?'); carb=n.get('碳水化合物（按差值）','?')
    print(f\"{f.get('description','N/A')}\")
    print(f\"  每100克：{cal} 千卡 | {prot}g 蛋白质 | {fat}g 脂肪 | {carb}g 碳水化合物\")
    print(f\"  FDC ID: {f.get('fdcId','N/A')}\")
    print()
"
```
```bash
# 按 FDC ID 获取详细营养素信息
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

### 离线计算器 {#offline-calculators}

使用 `scripts/` 中的辅助脚本进行批量操作，
或直接内联运行进行单次计算：

- `python3 scripts/body_calc.py bmi &lt;weight_kg&gt; &lt;height_cm&gt;`
- `python3 scripts/body_calc.py tdee &lt;weight_kg&gt; &lt;height_cm&gt; &lt;age&gt; &lt;M|F&gt; &lt;activity 1-5&gt;`
- `python3 scripts/body_calc.py 1rm &lt;weight&gt; &lt;reps&gt;`
- `python3 scripts/body_calc.py macros &lt;tdee_kcal&gt; &lt;cut|maintain|bulk&gt;`
- `python3 scripts/body_calc.py bodyfat &lt;M|F&gt; &lt;neck_cm&gt; &lt;waist_cm&gt; [hip_cm] &lt;height_cm&gt;`
See `references/FORMULAS.md` 了解每个公式背后的科学原理。

---

## 常见陷阱 {#pitfalls}

- wger 运动端点**默认返回所有语言**——始终添加 `language=2` 以获取英文结果
- wger 包含**未经验证的用户提交内容**——添加 `status=2` 仅获取已批准的运动
- USDA `DEMO_KEY` 有**每小时 30 次请求限制**——在批量请求之间添加 `sleep 2`，或申请免费密钥
- USDA 数据是**每 100 克**的——提醒用户按实际份量进行缩放
- BMI 无法区分肌肉和脂肪——肌肉发达的人 BMI 偏高不一定不健康
- 体脂公式是**估算值**（±3-5%）——建议使用 DEXA 扫描以获得精确结果
- 1RM 公式在超过 10 次重复时准确性下降——使用 3-5 次重复组可获得最佳估算
- wger 的 `exercise/search` 端点使用 `term` 而非 `query` 作为参数名

---

## 验证 {#verification}

运行运动搜索后：确认结果包含运动名称、肌肉群和器械。
完成营养查询后：确认返回每 100 克的宏量营养素（千卡、蛋白质、脂肪、碳水化合物）。
使用计算器后：检查输出是否合理（例如，大多数成年人的 TDEE 应在 1500-3500 之间）。
---

## 快速参考 {#quick-reference}

| 任务 | 数据源 | 接口地址 |
|------|--------|----------|
| 按名称搜索运动 | wger | `GET /api/v2/exercise/search/?term=&language=english` |
| 运动详情 | wger | `GET /api/v2/exerciseinfo/{id}/` |
| 按肌肉筛选 | wger | `GET /api/v2/exercise/?muscles={id}&language=2&status=2` |
| 按器材筛选 | wger | `GET /api/v2/exercise/?equipment={id}&language=2&status=2` |
| 列出类别 | wger | `GET /api/v2/exercisecategory/` |
| 列出肌肉 | wger | `GET /api/v2/muscle/` |
| 搜索食物 | USDA | `GET /fdc/v1/foods/search?query=&dataType=Foundation,SR Legacy` |
| 食物详情 | USDA | `GET /fdc/v1/food/{fdcId}` |
| BMI / TDEE / 1RM / 宏量营养素 | 离线 | `python3 scripts/body_calc.py` |
