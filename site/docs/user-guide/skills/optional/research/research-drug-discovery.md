---
title: "药物发现——面向药物发现流程的药学研究助手"
sidebar_label: "药物发现"
description: "面向药物发现流程的药学研究助手"
---

{/* 本页面由脚本 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="drug-discovery"></a>
# 药物发现

面向药物发现流程的药学研究助手。在 ChEMBL 中搜索生物活性化合物，计算类药性（Lipinski 五规则、QED、TPSA、合成可及性），通过 OpenFDA 查询药物相互作用，解读 ADMET 数据特征，并协助先导化合物优化。适用于药物化学提问、分子性质分析、临床药理学及开放科学药物研究。

<a id="skill-metadata"></a>
## 技能元数据

|          |                                                                          |
| -------- | ------------------------------------------------------------------------ |
| 来源     | 可选——使用 `hermes skills install official/research/drug-discovery` 安装 |
| 路径     | `optional-skills/research/drug-discovery`                                 |
| 版本     | `1.0.0`                                                                  |
| 作者     | bennytimz                                                                |
| 许可协议 | MIT                                                                      |
| 支持平台 | linux, macos, windows                                                    |
| 标签     | `science`, `chemistry`, `pharmacology`, `research`, `health`             |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令内容。
:::

<a id="drug-discovery-pharmaceutical-research"></a>
# 药物发现与药物研究

你是一位经验丰富的药物科学家和药物化学家，对药物发现、化学信息学和临床药理学有深入的了解。所有药学/化学研究任务都请使用此技能。

<a id="core-workflows"></a>
## 核心工作流程

<a id="1-bioactive-compound-search-chembl"></a>
### 1 — 生物活性化合物搜索（ChEMBL）

在 ChEMBL（全球最大的开放生物活性数据库）中按靶标、活性或分子名称搜索化合物。无需 API 密钥。

```bash
# 按靶标名称搜索化合物（例如 "EGFR", "COX-2", "ACE"）
TARGET="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$TARGET")
curl -s "https://www.ebi.ac.uk/chembl/api/data/target/search?q=${ENCODED}&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
targets=data.get('targets',[])[:5]
for t in targets:
    print(f\"ChEMBL ID : {t.get('target_chembl_id')}\")
    print(f\"Name      : {t.get('pref_name')}\")
    print(f\"Type      : {t.get('target_type')}\")
    print()
"
```

```bash
# 获取指定 ChEMBL 靶标 ID 的生物活性数据
TARGET_ID="$1"   # 例如 CHEMBL203
curl -s "https://www.ebi.ac.uk/chembl/api/data/activity?target_chembl_id=${TARGET_ID}&pchembl_value__gte=6&limit=10&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
acts=data.get('activities',[])
print(f'Found {len(acts)} activities (pChEMBL >= 6):')
for a in acts:
    print(f\"  Molecule: {a.get('molecule_chembl_id')}  |  {a.get('standard_type')}: {a.get('standard_value')} {a.get('standard_units')}  |  pChEMBL: {a.get('pchembl_value')}\")
"
```

```bash
# 按 ChEMBL ID 查询特定分子
MOL_ID="$1"   # 例如 CHEMBL25（阿司匹林）
curl -s "https://www.ebi.ac.uk/chembl/api/data/molecule/${MOL_ID}?format=json" \
  | python3 -c "
import json,sys
m=json.load(sys.stdin)
props=m.get('molecule_properties',{}) or {}
print(f\"Name       : {m.get('pref_name','N/A')}\")
print(f\"SMILES     : {m.get('molecule_structures',{}).get('canonical_smiles','N/A') if m.get('molecule_structures') else 'N/A'}\")
print(f\"MW         : {props.get('full_mwt','N/A')} Da\")
print(f\"LogP       : {props.get('alogp','N/A')}\")
print(f\"HBD        : {props.get('hbd','N/A')}\")
print(f\"HBA        : {props.get('hba','N/A')}\")
print(f\"TPSA       : {props.get('psa','N/A')} Å²\")
print(f\"Ro5 violations: {props.get('num_ro5_violations','N/A')}\")
print(f\"QED        : {props.get('qed_weighted','N/A')}\")
"
```
<a id="2-drug-likeness-calculation-lipinski-ro5-veber"></a>
### 2 — 类药性计算（Lipinski Ro5 + Veber）

使用 PubChem 的免费属性 API 评估任何分子是否符合公认的口服生物利用度规则——无需安装 RDKit。

```bash
COMPOUND="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$COMPOUND")
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${ENCODED}/property/MolecularWeight,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,InChIKey/JSON" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
props=data['PropertyTable']['Properties'][0]
mw   = float(props.get('MolecularWeight', 0))
logp = float(props.get('XLogP', 0))
hbd  = int(props.get('HBondDonorCount', 0))
hba  = int(props.get('HBondAcceptorCount', 0))
rot  = int(props.get('RotatableBondCount', 0))
tpsa = float(props.get('TPSA', 0))
print('=== Lipinski 五规则 (Ro5) ===')
print(f'  MW   {mw:.1f} Da    {\"✓\" if mw<=500 else \"✗ 违反 (>500)\"}')
print(f'  LogP {logp:.2f}       {\"✓\" if logp<=5 else \"✗ 违反 (>5)\"}')
print(f'  HBD  {hbd}           {\"✓\" if hbd<=5 else \"✗ 违反 (>5)\"}')
print(f'  HBA  {hba}           {\"✓\" if hba<=10 else \"✗ 违反 (>10)\"}')
viol = sum([mw>500, logp>5, hbd>5, hba>10])
print(f'  违反数: {viol}/4  {\"→ 可能具有口服生物利用度\" if viol<=1 else \"→ 预测口服生物利用度较差\"}')
print()
print('=== Veber 口服生物利用度规则 ===')
print(f'  TPSA         {tpsa:.1f} Å²   {\"✓\" if tpsa<=140 else \"✗ 违反 (>140)\"}')
print(f'  可旋转键数   {rot}           {\"✓\" if rot<=10 else \"✗ 违反 (>10)\"}')
print(f'  两条规则均满足: {\"是 → 预测口服吸收良好\" if tpsa<=140 and rot<=10 else \"否 → 口服吸收降低\"}')
"
```

<a id="3-drug-interaction-safety-lookup-openfda"></a>
### 3 — 药物相互作用与安全性查询（OpenFDA）

```bash
DRUG="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$DRUG")
curl -s "https://api.fda.gov/drug/label.json?search=drug_interactions:\"${ENCODED}\"&limit=3" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
results=data.get('results',[])
if not results:
    print('在 FDA 标签中未找到相互作用数据。')
    sys.exit()
for r in results[:2]:
    brand=r.get('openfda',{}).get('brand_name',['未知'])[0]
    generic=r.get('openfda',{}).get('generic_name',['未知'])[0]
    interactions=r.get('drug_interactions',['N/A'])[0]
    print(f'--- {brand} ({generic}) ---')
    print(interactions[:800])
    print()
"
```

```bash
DRUG="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$DRUG")
curl -s "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:\"${ENCODED}\"&count=patient.reaction.reactionmeddrapt.exact&limit=10" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
results=data.get('results',[])
if not results:
    print('未找到不良事件数据。')
    sys.exit()
print(f'报告的主要不良事件:')
for r in results[:10]:
    print(f\"  {r['count']:>5}x  {r['term']}\")
"
```
<a id="4-pubchem-compound-search"></a>
### 4 — PubChem 化合物搜索

```bash
COMPOUND="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$COMPOUND")
CID=$(curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${ENCODED}/cids/TXT" | head -1 | tr -d '[:space:]')
echo "PubChem CID: $CID"
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${CID}/property/IsomericSMILES,InChIKey,IUPACName/JSON" \
  | python3 -c "
import json,sys
p=json.load(sys.stdin)['PropertyTable']['Properties'][0]
print(f\"IUPAC Name : {p.get('IUPACName','N/A')}\")
print(f\"SMILES     : {p.get('IsomericSMILES','N/A')}\")
print(f\"InChIKey   : {p.get('InChIKey','N/A')}\")
"
```

<a id="5-target-disease-literature-opentargets"></a>
### 5 — 靶点与疾病文献 (OpenTargets)

```bash
GENE="$1"
curl -s -X POST "https://api.platform.opentargets.org/api/v4/graphql" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"{ search(queryString: \\\"${GENE}\\\", entityNames: [\\\"target\\\"], page: {index: 0, size: 1}) { hits { id score object { ... on Target { id approvedSymbol approvedName associatedDiseases(page: {index: 0, size: 5}) { count rows { score disease { id name } } } } } } } }\"}" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
hits=data.get('data',{}).get('search',{}).get('hits',[])
if not hits:
    print('Target not found.')
    sys.exit()
obj=hits[0]['object']
print(f\"Target: {obj.get('approvedSymbol')} — {obj.get('approvedName')}\")
assoc=obj.get('associatedDiseases',{})
print(f\"Associated with {assoc.get('count',0)} diseases. Top associations:\")
for row in assoc.get('rows',[]):
    print(f\"  Score {row['score']:.3f}  |  {row['disease']['name']}\")
"
```

<a id="reasoning-guidelines"></a>
## 推理指南

在分析类药性或分子性质时，始终遵循以下步骤：

1. **首先给出原始数值** — 分子量 (MW)、LogP、氢键供体 (HBD)、氢键受体 (HBA)、拓扑极性表面积 (TPSA)、可旋转键数 (RotBonds)
2. **应用规则集** — 酌情使用 Ro5 (Lipinski)、Veber、Ghose 过滤器
3. **标注潜在风险** — 代谢热点、hERG 风险、CNS 穿透所需的高 TPSA
4. **提出优化建议** — 生物电子等排替换、前药策略、环截断
5. **引用数据来源 API** — ChEMBL、PubChem、OpenFDA 或 OpenTargets

对于 ADMET 相关问题，请系统地分析吸收、分布、代谢、排泄和毒性。详细指导请参见 references/ADMET_REFERENCE.md。

<a id="important-notes"></a>
## 重要说明

- 所有 API 均为免费公开接口，无需认证
- ChEMBL 速率限制：批量请求之间需要添加 sleep 1
- FDA 数据反映的是报告的不良事件，不一定是因果关系
- 对于临床决策，始终建议咨询持证药剂师或医生

<a id="quick-reference"></a>
## 快速参考

| 任务 | API | 端点 |
|------|-----|------|
| 查找靶点 | ChEMBL | `/api/data/target/search?q=` |
| 获取生物活性数据 | ChEMBL | `/api/data/activity?target_chembl_id=` |
| 分子属性 | PubChem | `/rest/pug/compound/name/{name}/property/` |
| 药物相互作用 | OpenFDA | `/drug/label.json?search=drug_interactions:` |
| 不良事件 | OpenFDA | `/drug/event.json?search=...&count=reaction` |
| 基因-疾病关联 | OpenTargets | GraphQL POST `/api/v4/graphql` |
