---
title: "地图 — 通过 OpenStreetMap/OSRM 进行地理编码、兴趣点、路线、时区"
sidebar_label: "地图"
description: "通过 OpenStreetMap/OSRM 进行地理编码、兴趣点、路线、时区"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 地图 {#maps}

通过 OpenStreetMap/OSRM 进行地理编码、兴趣点、路线、时区。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/maps` |
| 版本 | `1.2.0` |
| 作者 | Mibayy |
| 许可证 | MIT |
| 标签 | `maps`, `geocoding`, `places`, `routing`, `distance`, `directions`, `nearby`, `location`, `openstreetmap`, `nominatim`, `overpass`, `osrm` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 地图技能 {#maps-skill}

使用免费、开放的数据源实现位置智能。8 个命令，44 个 POI 类别，零依赖（仅 Python 标准库），无需 API 密钥。

数据源：OpenStreetMap/Nominatim、Overpass API、OSRM、TimeAPI.io。

此技能取代了旧的 `find-nearby` 技能——find-nearby 的所有功能都由下面的 `nearby` 命令覆盖，支持相同的 `--near "&lt;place&gt;"` 快捷方式和多类别查询。

## 何时使用 {#when-to-use}

- 用户发送包含经纬度的 Telegram 位置引脚 → `nearby`
- 用户想要地名的坐标 → `search`
- 用户有坐标并想要地址 → `reverse`
- 用户询问附近的餐馆、医院、药店、酒店等 → `nearby`
- 用户想要驾车/步行/骑行距离或行程时间 → `distance`
- 用户想要两个地点之间的逐向导航 → `directions`
- 用户想要某个位置的时区信息 → `timezone`
- 用户想要在某个地理区域内搜索 POI → `area` + `bbox`

## 先决条件 {#prerequisites}

Python 3.8+（仅标准库——无需 pip 安装）。

脚本路径：`~/.hermes/skills/maps/scripts/maps_client.py`

## 命令 {#commands}

```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
```

### search — 地理编码一个地名 {#search-geocode-a-place-name}

```bash
python3 $MAPS search "埃菲尔铁塔"
python3 $MAPS search "1600 Pennsylvania Ave, Washington DC"
```

返回：纬度、经度、显示名称、类型、边界框、重要性分数。

### reverse — 坐标转地址 {#reverse-coordinates-to-address}

```bash
python3 $MAPS reverse 48.8584 2.2945
```

返回：完整地址分解（街道、城市、州、国家、邮政编码）。

### nearby — 按类别查找地点 {#nearby-find-places-by-category}

```bash
# 按坐标（例如从 Telegram 位置引脚）
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10
python3 $MAPS nearby 40.7128 -74.0060 hospital --radius 2000

# 按地址/城市/邮编/地标 — --near 自动地理编码
python3 $MAPS nearby --near "纽约时报广场" --category cafe
python3 $MAPS nearby --near "90210" --category pharmacy

# 多个类别合并到一个查询中
python3 $MAPS nearby --near "downtown austin" --category restaurant --category bar --limit 10
```

46 个类别：restaurant, cafe, bar, hospital, pharmacy, hotel, guest_house,
camp_site, supermarket, atm, gas_station, parking, museum, park, school,
university, bank, police, fire_station, library, airport, train_station,
bus_stop, church, mosque, synagogue, dentist, doctor, cinema, theatre, gym,
swimming_pool, post_office, convenience_store, bakery, bookshop, laundry,
car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground,
stadium, nightclub.
每个结果包含：`name`、`address`、`lat`/`lon`、`distance_m`、`maps_url`（可点击的 Google 地图链接）、`directions_url`（从搜索点出发的 Google 地图导航链接），以及可用的推广标签——`cuisine`（菜系）、`hours`（营业时间）、`phone`（电话）、`website`（网站）。

### distance — 出行距离与时间 {#distance-travel-distance-and-time}

```bash
python3 $MAPS distance "Paris" --to "Lyon"
python3 $MAPS distance "New York" --to "Boston" --mode driving
python3 $MAPS distance "Big Ben" --to "Tower Bridge" --mode walking
```

模式：driving（驾车，默认）、walking（步行）、cycling（骑行）。返回道路距离、耗时以及直线距离，方便对比。

### directions — 逐向导航 {#directions-turn-by-turn-navigation}

```bash
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking
python3 $MAPS directions "JFK Airport" --to "Times Square" --mode driving
```

返回带编号的步骤，包含指令、距离、耗时、道路名称和操作类型（转弯、出发、到达等）。

### timezone — 坐标时区 {#timezone-timezone-for-coordinates}

```bash
python3 $MAPS timezone 48.8584 2.2945
python3 $MAPS timezone 35.6762 139.6503
```

返回时区名称、UTC 偏移量和当前当地时间。

### area — 地点的边界框与面积 {#area-bounding-box-and-area-for-a-place}

```bash
python3 $MAPS area "Manhattan, New York"
python3 $MAPS area "London"
```

返回边界框坐标、宽/高（公里）和近似面积。可作为 bbox 命令的输入使用。

### bbox — 在边界框内搜索 {#bbox-search-within-a-bounding-box}

```bash
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

在地理矩形区域内查找兴趣点。先用 `area` 获取命名地点的边界框坐标。

## 使用 Telegram 位置标记 {#working-with-telegram-location-pins}

当用户发送位置标记时，消息中包含 `latitude:` 和 `longitude:` 字段。提取这些值并直接传给 `nearby`：

```bash
# 用户发送了位置标记 (36.17, -115.14) 并询问“附近有咖啡馆吗”
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

将结果以编号列表形式呈现，包含名称、距离和 `maps_url` 字段，方便用户在聊天中点击链接打开。对于“现在营业吗？”这类问题，检查 `hours` 字段；如果缺失或不明确，用 `web_search` 核实，因为 OSM 的营业时间由社区维护，不一定是最新的。

## 工作流示例 {#workflow-examples}

**“找找罗马斗兽场附近的意大利餐厅”：**
1. `nearby --near "Colosseum Rome" --category restaurant --radius 500`
   — 一条命令，自动地理编码

**“他们发的这个位置标记附近有什么？”：**
1. 从 Telegram 消息中提取经纬度
2. `nearby LAT LON cafe --radius 1500`

**“从酒店步行到会议中心怎么走？”：**
1. `directions "Hotel Name" --to "Conference Center" --mode walking`

**“西雅图市中心有哪些餐厅？”：**
1. `area "Downtown Seattle"` → 获取边界框
2. `bbox S W N E restaurant --limit 30`

## 注意事项 {#pitfalls}

- Nominatim 服务条款：最多每秒 1 次请求（脚本会自动处理）
- `nearby` 需要经纬度或 `--near "<地址>"` — 两者必选其一
- OSRM 路线规划在欧洲和北美覆盖最好
- Overpass API 在高峰时段可能较慢；脚本会自动在镜像之间回退（overpass-api.de → overpass.kumi.systems）
- `distance` 和 `directions` 使用 `--to` 标志指定目的地（不是位置参数）
- 如果仅凭邮政编码在全球范围内结果不明确，请包含国家/州信息
## 验证 {#verification}

```bash
python3 ~/.hermes/skills/maps/scripts/maps_client.py search "Statue of Liberty"
# 应返回纬度约 40.689，经度约 -74.044

python3 ~/.hermes/skills/maps/scripts/maps_client.py nearby --near "Times Square" --category restaurant --limit 3
# 应返回时代广场周边约 500 米范围内的餐厅列表
```
