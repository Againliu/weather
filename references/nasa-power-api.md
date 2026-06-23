# NASA POWER API 参考

> 数据来源：NASA Langley Research Center
> 数据类型：卫星遥感 + 地面站校正的气象数据
> API 版本：v1
> 认证：无需 API Key，完全免费
> 历史深度：1981年至今（40+年）

## 一、API 概述

NASA POWER（Prediction Of Worldwide Energy Resources）是 NASA 官方提供的免费气象数据服务，专为农业和能源行业设计。数据来自卫星遥感，结合全球地面气象站观测数据进行校正。

**核心优势**：
- 完全免费，无需 API Key
- 历史深度 1981年至今（40+年）
- 专为农业和能源行业优化
- 全球覆盖
- 无速率限制（但建议合理调用）

**局限性**：
- 空间分辨率 ~0.5°（约 50km）
- 最新数据有 2-3 天延迟（不适合实时查询）
- 太阳辐射等部分参数有缺失（返回 -999.0）
- 不提供分钟级/小时级数据（仅日级）

## 二、端点列表

### 2.1 日级时间序列（最常用）

```
GET https://power.larc.nasa.gov/api/temporal/daily/point
```

**参数**：
| 参数 | 必填 | 说明 |
|------|------|------|
| parameters | ✅ | 逗号分隔的参数列表 |
| latitude | ✅ | 纬度 |
| longitude | ✅ | 经度 |
| start | ✅ | 开始日期 YYYYMMDD |
| end | ✅ | 结束日期 YYYYMMDD |
| community | ✅ | 社区：`ag`（农业）、`re`（能源）、`sb`（建筑） |
| format | ✅ | 格式：`JSON`、`CSV`、`NETCDF` |

**示例请求**：
```bash
# 农业社区 - 尉犁县
curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,T2M,PRECTOTCORR,WS2M,WS10M,RH2M,ALLSKY_SFC_SW_DWN&latitude=41.48&longitude=86.21&start=20260615&end=20260619&community=ag&format=JSON"
```

### 2.2 小时级时间序列

```
GET https://power.larc.nasa.gov/api/temporal/hourly/point
```

### 2.3 月级时间序列

```
GET https://power.larc.nasa.gov/api/temporal/monthly/point
```

### 2.4 气候学（30年平均）

```
GET https://power.larc.nasa.gov/api/temporal/climatology/point
```

## 三、参数列表

### 3.1 温度参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| T2M | °C | 2米气温（日均） | ag, re, sb |
| T2M_MAX | °C | 2米最高气温 | ag, re, sb |
| T2M_MIN | °C | 2米最低气温 | ag, re, sb |
| T2M_RANGE | °C | 日较差（最高-最低） | ag |
| T2MDEW | °C | 2米露点温度 | ag, re, sb |
| TS | °C | 地表温度 | ag, re |

### 3.2 降水参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| PRECTOTCORR | mm/day | 校正降水量（推荐） | ag, re, sb |
| PRECTOT | mm/day | 原始降水量 | ag, re |

### 3.3 风速参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| WS2M | m/s | 2米风速 | ag, re, sb |
| WS10M | m/s | 10米风速（推荐） | ag, re, sb |
| WS50M | m/s | 50米风速（风电） | re |
| WD2M | ° | 2米风向 | ag, re |
| WD10M | ° | 10米风向 | ag, re |

### 3.4 湿度参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| RH2M | % | 2米相对湿度 | ag, sb |
| QV2M | g/kg | 2米比湿 | ag, re |

### 3.5 辐射参数（能源/光伏核心）

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| ALLSKY_SFC_SW_DWN | kWh/m²/day | 全天短波辐射（地表向下）| ag, re |
| ALLSKY_SFC_LW_DWN | W/m² | 全天长波辐射（地表向下）| ag, re |
| CLRSKY_SFC_SW_DWN | kWh/m²/day | 晴空短波辐射 | re |
| ALLSKY_SFC_SW_DIFF | kWh/m²/day | 漫射短波辐射 | re |
| ALLSKY_SFC_PAR_TOT | mol/m²/day | 光合有效辐射（农业） | ag |

### 3.6 气压参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| PS | kPa | 地表气压 | ag, re, sb |

### 3.7 土壤参数（农业专用）

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| GWETTOP | 0-1 | 表层土壤湿度（0-10cm）| ag |
| GWETROOT | 0-1 | 根区土壤湿度（10-100cm）| ag |
| GWETPROFILE | 0-1 | 剖面土壤湿度 | ag |

### 3.8 其他参数

| 参数 | 单位 | 说明 | 适用社区 |
|------|------|------|---------|
| CLOUD_AMT | % | 总云量 | ag, re |
| SNODP | cm | 雪深 | ag, re |
| FROST_DAYS | 天 | 霜冻日数 | ag |

## 四、社区说明

| 社区 | 代码 | 适用场景 | 特色参数 |
|------|------|---------|---------|
| **农业** | ag | 农业种植、水文研究 | GWETTOP（土壤湿度）、T2MDEW（露点）、FROST_DAYS（霜冻）|
| **能源** | re | 光伏/风电、能源规划 | WS50M（50m风速）、ALLSKY_SFC_SW_DIFF（漫射辐射）|
| **建筑** | sb | 建筑能耗、HVAC设计 | 较少的参数，侧重温度 |

## 五、Python 调用示例

```python
import json, urllib.request

def fetch_nasa_power(lat, lon, start, end, parameters, community="ag"):
    """
    获取 NASA POWER 数据
    
    Args:
        lat: 纬度
        lon: 经度
        start: 开始日期 YYYYMMDD
        end: 结束日期 YYYYMMDD
        parameters: 参数列表 ["T2M_MAX", "T2M_MIN", ...]
        community: 社区 "ag" 或 "re"
    """
    base = "https://power.larc.nasa.gov/api/temporal/daily/point"
    url = (f"{base}?parameters={','.join(parameters)}"
           f"&latitude={lat}&longitude={lon}"
           f"&start={start}&end={end}"
           f"&community={community}&format=JSON")
    
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    # 提取参数数据
    props = data.get("properties", {}).get("parameter", {})
    
    result = {}
    for param, values in props.items():
        # 过滤缺失值 -999.0
        filtered = {k: v for k, v in values.items() if v != -999.0}
        result[param] = filtered
    
    return result

# 示例：获取尉犁县农业气象数据
data = fetch_nasa_power(
    lat=41.48, lon=86.21,
    start="20260615", end="20260619",
    parameters=[
        "T2M_MAX", "T2M_MIN", "T2M",  # 温度
        "PRECTOTCORR",  # 降水
        "WS2M", "WS10M",  # 风速
        "RH2M",  # 湿度
        "ALLSKY_SFC_SW_DWN",  # 太阳辐射
        "GWETTOP",  # 表层土壤湿度
    ],
    community="ag"
)

for param, values in data.items():
    print(f"\n{param}:")
    for date, val in values.items():
        print(f"  {date}: {val}")
```

## 六、与 Open-Meteo 的对比

| 维度 | NASA POWER | Open-Meteo |
|------|-----------|-----------|
| **费用** | 完全免费 | 免费 |
| **认证** | 无需 Key | 无需 Key |
| **历史深度** | 1981年至今（40+年）| 1940年至今（80+年）|
| **数据延迟** | 2-3天 | 实时 |
| **空间分辨率** | ~50km | ~15km（CMA全球）|
| **时间分辨率** | 日级 | 小时级/日级 |
| **土壤湿度** | 3层（表层/根区/剖面）| 5层（1/3/9/27/81cm）|
| **ET0** | ❌ 不直接提供 | ✅ 直接提供 |
| **太阳辐射** | ✅ 全天短波/长波 | ✅ 短波/长波/直接/散射/紫外线 |
| **适用场景** | 长期气候研究、农业规划 | 日常预报、实时查询 |

**结论**：
- NASA POWER 适合长期历史趋势分析（40+年）
- Open-Meteo 适合日常实时查询和短期预报
- 两者可互补使用

## 七、数据质量说明

NASA POWER 数据来自：
1. **卫星遥感**：NASA CERES、GEOS 等卫星产品
2. **地面站校正**：结合全球气象站观测数据
3. **模型同化**：GEOS-5 数据同化系统

**数据质量**：
- 温度：精度 ±1°C（与地面站对比）
- 降水：精度 ±20%（卫星估算，有不确定性）
- 辐射：精度 ±10%（卫星反演）
- 风速：精度 ±15%（模型估算）

**注意**：NASA POWER 是卫星遥感+地面站校正，不是纯地面站实测。如需 Ground Truth，应使用 IBM Weather（机场METAR）。

## 八、常见问题

**Q: 为什么太阳辐射返回 -999.0？**
A: -999.0 表示数据缺失，可能是云层遮挡或卫星观测失败。需过滤此值。

**Q: 为什么最新数据查不到？**
A: NASA POWER 有 2-3 天延迟，最新可用数据通常是 3 天前。

**Q: 可以查询多长的时间跨度？**
A: 理论上可以查询任意时间跨度，但建议单次请求不超过 1 年，避免超时。

**Q: 有速率限制吗？**
A: 无严格速率限制，但建议合理调用（间隔 1-2 秒），避免给服务器造成压力。

**Q: 数据是实测还是模型？**
A: 是卫星遥感+地面站校正+模型同化的混合产品，不是纯地面站实测。
