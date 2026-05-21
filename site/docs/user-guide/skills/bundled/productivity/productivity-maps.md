---
title: "地图 — 通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线与时区"
sidebar_label: "地图"
description: "通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线与时区"
---

{/* 本页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="maps"></a>
# 地图

通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线与时区。

<a id="skill-metadata"></a>
## 技能元数据

|          |                                              |
| -------- | -------------------------------------------- |
| 来源     | 内置（默认安装）                                |
| 路径     | `skills/productivity/maps`                   |
| 版本     | `1.2.0`                                      |
| 作者     | Mibayy                                       |
| 许可证   | MIT                                          |
| 平台     | linux, macos, windows                        |
| 标签     | `maps`, `geocoding`, `places`, `routing`, `distance`, `directions`, `nearby`, `location`, `openstreetmap`, `nominatim`, `overpass`, `osrm` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发该技能时所加载的完整技能定义。这是技能生效时 Agent 看到的指令。
:::

<a id="maps-skill"></a>
# 地图技能

利用免费、开放的数据源实现位置智能。包含 8 条命令、44 个 POI 分类、零依赖（仅使用 Python 标准库），无需 API 密钥。

数据来源：OpenStreetMap/Nominatim、Overpass API、OSRM、TimeAPI.io。

此技能替代了旧的 `find-nearby` 技能——`find-nearby` 的所有功能都已由下面的 `nearby` 命令覆盖，并支持同样的 `--near "<地点>"` 快捷方式和多分类查询。

<a id="when-to-use"></a>
## 使用场景

- 用户发送 Telegram 位置标记（消息中的经纬度）→ `nearby`
- 用户想要某个地名的坐标 → `search`
- 用户已有坐标，想要地址 → `reverse`
- 用户询问附近餐厅、医院、药店、酒店等 → `nearby`
- 用户想要驾车/步行/骑行的距离或行程时间 → `distance`
- 用户想要两个地点之间的逐向导航 → `directions`
- 用户想要某个位置的时区信息 → `timezone`
- 用户想要在某个地理区域内搜索 POI → `area` + `bbox`

<a id="prerequisites"></a>
## 前提条件

Python 3.8+（仅标准库——无需 pip 安装）。

脚本路径：`~/.hermes/skills/maps/scripts/maps_client.py`

<a id="commands"></a>
## 命令

```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
```

<a id="search-geocode-a-place-name"></a>
### search — 对地名进行地理编码

```bash
python3 $MAPS search "Eiffel Tower"
python3 $MAPS search "1600 Pennsylvania Ave, Washington DC"
```

返回：纬度、经度、显示名称、类型、边界框、重要性评分。

<a id="reverse-coordinates-to-address"></a>
### reverse — 坐标转地址

```bash
python3 $MAPS reverse 48.8584 2.2945
```

返回：完整地址分解（街道、城市、州、国家、邮政编码）。

<a id="nearby-find-places-by-category"></a>
### nearby — 按分类查找地点

```bash
# 按坐标（例如来自 Telegram 位置标记）
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10
python3 $MAPS nearby 40.7128 -74.0060 hospital --radius 2000

# 按地址/城市/邮编/地标 — --near 会自动进行地理编码
python3 $MAPS nearby --near "Times Square, New York" --category cafe
python3 $MAPS nearby --near "90210" --category pharmacy

# 多个分类合并到一个查询中
python3 $MAPS nearby --near "downtown austin" --category restaurant --category bar --limit 10
```

46 个分类：restaurant, cafe, bar, hospital, pharmacy, hotel, guest_house,
camp_site, supermarket, atm, gas_station, parking, museum, park, school,
university, bank, police, fire_station, library, airport, train_station,
bus_stop, church, mosque, synagogue, dentist, doctor, cinema, theatre, gym,
swimming_pool, post_office, convenience_store, bakery, bookshop, laundry,
car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground,
stadium, nightclub。
每个结果包含：`name`、`address`、`lat`/`lon`、`distance_m`、`maps_url`（可点击的 Google 地图链接）、`directions_url`（从搜索点出发的 Google 地图导航链接），以及可用的推广标签——`cuisine`（菜系）、`hours`（营业时间）、`phone`（电话）、`website`（网站）。

<a id="distance-travel-distance-and-time"></a>
### distance — 出行距离与时间

```bash
python3 $MAPS distance "Paris" --to "Lyon"
python3 $MAPS distance "New York" --to "Boston" --mode driving
python3 $MAPS distance "Big Ben" --to "Tower Bridge" --mode walking
```

模式：driving（驾车，默认）、walking（步行）、cycling（骑行）。返回道路距离、耗时以及直线距离，方便对比。

<a id="directions-turn-by-turn-navigation"></a>
### directions — 逐向导航

```bash
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking
python3 $MAPS directions "JFK Airport" --to "Times Square" --mode driving
```

返回带编号的步骤，包含指令、距离、耗时、道路名称和操作类型（转弯、出发、到达等）。

<a id="timezone-timezone-for-coordinates"></a>
### timezone — 坐标对应的时区

```bash
python3 $MAPS timezone 48.8584 2.2945
python3 $MAPS timezone 35.6762 139.6503
```

返回时区名称、UTC 偏移量和当前当地时间。

<a id="area-bounding-box-and-area-for-a-place"></a>
### area — 地点的边界框与面积

```bash
python3 $MAPS area "Manhattan, New York"
python3 $MAPS area "London"
```

返回边界框坐标、宽/高（公里）和近似面积。适合作为 bbox 命令的输入。

<a id="bbox-search-within-a-bounding-box"></a>
### bbox — 在边界框内搜索

```bash
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

在地理矩形区域内查找兴趣点。先用 `area` 获取指定地点的边界框坐标。

<a id="working-with-telegram-location-pins"></a>
## 配合 Telegram 位置标记使用

当用户发送位置标记时，消息中包含 `latitude:` 和 `longitude:` 字段。提取这些值后直接传给 `nearby`：

```bash
# 用户发送了位置标记 (36.17, -115.14) 并询问“附近有咖啡馆吗”
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

将结果以编号列表形式呈现，包含名称、距离和 `maps_url` 字段，方便用户在聊天中点击链接打开。对于“现在营业吗？”这类问题，检查 `hours` 字段；如果缺失或不明确，用 `web_search` 核实，因为 OSM 的营业时间由社区维护，不一定是最新的。

<a id="workflow-examples"></a>
## 工作流示例

**“找罗马斗兽场附近的意大利餐厅”：**
1. `nearby --near "Colosseum Rome" --category restaurant --radius 500`
   — 一条命令，自动地理编码

**“他们发的位置标记附近有什么？”：**
1. 从 Telegram 消息中提取经纬度
2. `nearby LAT LON cafe --radius 1500`

**“从酒店步行到会议中心怎么走？”：**
1. `directions "Hotel Name" --to "Conference Center" --mode walking`

**“西雅图市中心有哪些餐厅？”：**
1. `area "Downtown Seattle"` → 获取边界框
2. `bbox S W N E restaurant --limit 30`

<a id="pitfalls"></a>
## 注意事项

- Nominatim 服务条款：最多每秒 1 次请求（脚本会自动处理）
- `nearby` 需要经纬度或 `--near "<地址>"` — 两者必须提供其一
- OSRM 路由覆盖范围在欧美地区最佳
- Overpass API 在高峰时段可能较慢；脚本会自动在镜像之间切换（overpass-api.de → overpass.kumi.systems）
- `distance` 和 `directions` 使用 `--to` 标志指定目的地（不是位置参数）
- 如果仅凭邮政编码在全球范围内结果不明确，请包含国家/州信息
<a id="verification"></a>
## 验证

```bash
python3 ~/.hermes/skills/maps/scripts/maps_client.py search "Statue of Liberty"
# Should return lat ~40.689, lon ~-74.044

python3 ~/.hermes/skills/maps/scripts/maps_client.py nearby --near "Times Square" --category restaurant --limit 3
# Should return a list of restaurants within ~500m of Times Square
```
