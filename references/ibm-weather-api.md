# IBM Weather API 参考

> 数据来源：IBM Weather Company（Weather Underground）
> 数据类型：中国民航机场 METAR 气象观测站实测数据（Ground Truth）
> API 版本：v1
> 认证：API Key

## 一、API 概述

IBM Weather Company 提供全球民航机场的地面气象观测数据（METAR报文），这是真正的站点级实测数据，可作为预报准确率验证的 Ground Truth。

**中国覆盖情况**：
- 测试 20 个中国机场，17 个成功返回数据（85%覆盖率）
- 覆盖：北京、上海、广州、深圳、成都、武汉、杭州、西安、兰州、昆明、拉萨、哈尔滨、乌鲁木齐、库尔勒、喀什、阿克苏、克拉玛依
- 不支持：部分新疆小机场（和田、伊宁、吐鲁番等）

**历史深度**：至少 90 天，可能更长

**更新频率**：每小时/半小时

## 二、端点列表

### 2.1 历史逐时观测

```
GET https://api.weather.com/v1/location/{ICAO_CODE}/observations/historical.json
```

**参数**：
| 参数 | 必填 | 说明 |
|------|------|------|
| apiKey | ✅ | API Key |
| units | ✅ | 单位：`m`（公制）、`e`（英制）|
| startDate | ✅ | 开始日期，格式 `YYYYMMDD` |
| endDate | ✅ | 结束日期，格式 `YYYYMMDD` |

**示例请求**：
```bash
curl "https://api.weather.com/v1/location/ZBAA:9:CN/observations/historical.json?apiKey={API_KEY}&units=m&startDate=20260615&endDate=20260621"
```

**返回字段**：
| 字段 | 单位 | 说明 |
|------|------|------|
| temp | °C | 温度 |
| rh | % | 相对湿度 |
| wspd | km/h | 风速 |
| wgst | km/h | 阵风速度 |
| wdir | ° | 风向 |
| pressure | hPa | 气压 |
| precip_hrly | mm | 小时降水量 |
| precip_total | mm | 当日累计降水 |
| dewpt | °C | 露点温度 |
| vis | km | 能见度 |
| clds | 代码 | 云量（FEW/SCT/BKN/OVC/CLR）|
| wx_phrase | 文本 | 天气现象描述 |

**注意事项**：
- `precip_total` 和 `precip_hrly` 可能为 `None`（无降水时）
- 返回数据量可能较大（每天 24 条记录），建议保存为文件再处理
- 免费层有速率限制，建议间隔 1-2 秒

### 2.2 当前观测

```
GET https://api.weather.com/v1/location/{ICAO_CODE}/observations/current.json
```

**参数**：
| 参数 | 必填 | 说明 |
|------|------|------|
| apiKey | ✅ | API Key |
| units | ✅ | 单位：`m`（公制）|

**示例请求**：
```bash
curl "https://api.weather.com/v1/location/ZBAA:9:CN/observations/current.json?apiKey={API_KEY}&units=m"
```

### 2.3 10天预报

```
GET https://api.weather.com/v1/location/{ICAO_CODE}/observations/historical/forecast/daily/10day.json
```

## 三、中国常用机场 ICAO 代码

| 城市 | 机场 | ICAO代码 | API参数 |
|------|------|----------|---------|
| 北京 | 首都机场 | ZBAA | `ZBAA:9:CN` |
| 北京 | 大兴机场 | ZBAD | `ZBAD:9:CN` |
| 上海 | 浦东机场 | ZSSS | `ZSSS:9:CN` |
| 上海 | 虹桥机场 | ZSSS | `ZSSS:9:CN` |
| 广州 | 白云机场 | ZGGG | `ZGGG:9:CN` |
| 深圳 | 宝安机场 | ZGSZ | `ZGSZ:9:CN` |
| 成都 | 双流机场 | ZUUU | `ZUUU:9:CN` |
| 武汉 | 天河机场 | ZHHH | `ZHHH:9:CN` |
| 杭州 | 萧山机场 | ZSHC | `ZSHC:9:CN` |
| 西安 | 咸阳机场 | ZLXY | `ZLXY:9:CN` |
| 兰州 | 中川机场 | ZLLL | `ZLLL:9:CN` |
| 昆明 | 长水机场 | ZPPP | `ZPPP:9:CN` |
| 拉萨 | 贡嘎机场 | ZULS | `ZULS:9:CN` |
| 哈尔滨 | 太平机场 | ZYHB | `ZYHB:9:CN` |
| 乌鲁木齐 | 地窝堡机场 | ZWWW | `ZWWW:9:CN` |
| 库尔勒 | 库尔勒机场 | ZWKL | `ZWKL:9:CN` |
| 喀什 | 喀什机场 | ZWSH | `ZWSH:9:CN` |
| 阿克苏 | 阿克苏机场 | ZWAK | `ZWAK:9:CN` |
| 克拉玛依 | 克拉玛依机场 | ZWKM | `ZWKM:9:CN` |

## 四、与农场的距离

| 站点 | 距超级棉田农场距离 | 适用性 |
|------|-------------------|--------|
| 库尔勒机场 ZWKL | ~50km | ✅ 最近，气温误差<1°C |
| 尉犁县城 | ~53km | 无METAR站 |
| 乌鲁木齐机场 ZWWW | ~400km | ❌ 太远，不具代表性 |

## 五、Python 调用示例

```python
import json, urllib.request

API_KEY="your_api_key_here"
ICAO = "ZWKL:9:CN"  # 库尔勒机场

url = (f"https://api.weather.com/v1/location/{ICAO}"
       f"/observations/historical.json?apiKey={API_KEY}"
       f"&units=m&startDate=20260615&endDate=20260621")

req = urllib.request.Request(url)
req.add_header("User-Agent", "Mozilla/5.0")
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read())

obs = data.get("observations", [])
for o in obs:
    print(f"{o.get('valid_time_gmt')} | "
          f"温度:{o.get('temp')}°C | "
          f"湿度:{o.get('rh')}% | "
          f"风速:{o.get('wspd')}km/h | "
          f"降水:{o.get('precip_hrly')}mm")
```

## 六、局限性

1. **仅在机场附近**：数据来自机场地面站，距农田可能 50km+
2. **气温**：50km 距离误差 <1°C，可接受
3. **降水/风速**：局部差异大，50km 偏差可能显著
4. **不是中国气象局官方数据**：是 IBM 收集整理的 METAR 报文，质量等同但非官方渠道
5. **速率限制**：免费层有严格限制，不适合高频调用
6. **降水字段**：无降水时可能返回 `None` 而非 `0`
