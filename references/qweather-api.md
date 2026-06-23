# 和风天气 API 完整参考

## 基本信息

- **官方文档**: https://dev.qweather.com/docs/
- **认证方式**: API Key (query 参数 `key=`)
- **API Host**: 每个账号独立（格式：`xxx.def.qweatherapi.com`），**必须用专属 Host**
- **费用**: 免费 5 万次/月，足够农场日常使用
- **数据更新**: 实时天气 5-10 分钟，逐小时 60 分钟，分钟级降水 5 分钟

## ⚠️ 关键注意事项

1. **必须加 `--compressed`**：和风天气默认返回 gzip 压缩，curl 不加会乱码
2. **必须用专属 API Host**：2026 年起 `devapi.qweather.com` 已停用
3. **坐标顺序**：`location=经度,纬度`（lon,lat），与 Open-Meteo 相反
4. **location 格式**：支持 `经度,纬度` 或 `地点 ID`（通过 Geo API 获取）

## API 端点完整列表

### 1. 天气实况 `/v7/weather/now`
```bash
curl --compressed "https://{HOST}/v7/weather/now?location={LON},{LAT}&key={KEY}"
```
**返回字段**: temp(温度°C), feelsLike(体感), icon(天气图标), text(天气描述), wind360(风向度), windDir(风向文字), windScale(风力等级), windSpeed(风速km/h), humidity(湿度%), precip(降水量mm), pressure(气压hPa), vis(能见度km), cloud(云量%), dew(露点°C), uvIndex(紫外线指数)

### 2. 每日天气预报 `/v7/weather/{3d|7d|10d|15d}`
```bash
curl --compressed "https://{HOST}/v7/weather/7d?location={LON},{LAT}&key={KEY}"
```
**返回字段**: fxDate(预报日期), sunrise(日出), sunset(日落), moonrise(月升), moonset(月落), moonPhase(月相名称), moonPhaseIcon(月相图标), tempMax(最高温), tempMin(最低温), iconDay/iconNight, textDay/textNight, wind360Day/windDirDay/windScaleDay/windSpeedDay, 以及夜间对应字段, humidity, precip, pressure, vis, cloud, uvIndex

### 3. 逐小时预报 `/v7/weather/24h` 或 `/v7/weather/72h` 或 `/v7/weather/168h`
```bash
curl --compressed "https://{HOST}/v7/weather/24h?location={LON},{LAT}&key={KEY}"
```
**返回字段**: fxTime(预报时间), temp, icon, text, wind360, windDir, windScale, windSpeed, humidity, pop(降水概率%), precip, pressure, cloud, dew, wetBulb(湿球温度)

### 4. 分钟级降水预报 `/v7/minutely/5m`（仅中国）
```bash
curl --compressed "https://{HOST}/v7/minutely/5m?location={LON},{LAT}&key={KEY}"
```
**特色**: 未来 2 小时逐 5 分钟降水预报，精度 1km
**返回字段**: summary(降水描述文字), minutely[].fxTime(时间), minutely[].precip(降水量mm), minutely[].type(降水类型: rain/snow)

### 5. 格点实时天气 `/v7/grid-weather/now`
```bash
curl --compressed "https://{HOST}/v7/grid-weather/now?location={LON},{LAT}&key={KEY}"
```
**特色**: 3-5km 精度格点数据，比城市级更精确
**返回字段**: 同 weather/now，但基于格点插值

### 6. 格点每日预报 `/v7/grid-weather/{3d|7d}`
```bash
curl --compressed "https://{HOST}/v7/grid-weather/7d?location={LON},{LAT}&key={KEY}"
```

### 7. 格点逐小时预报 `/v7/grid-weather/24h` 或 `72h`
```bash
curl --compressed "https://{HOST}/v7/grid-weather/24h?location={LON},{LAT}&key={KEY}"
```

### 8. 天气预警 `/v7/warning/now`
```bash
curl --compressed "https://{HOST}/v7/warning/now?location={LON},{LAT}&key={KEY}"
```
**返回字段**: warning[].id(预警ID), sender(发布单位), pubTime(发布时间), title(预警标题), startTime(开始时间), endTime(结束时间), status(状态), level(等级), type(类型), typeName(类型名称), severity(严重程度), urgency(紧迫程度), text(预警详情)

### 9. 天气预警城市列表 `/v7/warning/list`
```bash
curl --compressed "https://{HOST}/v7/warning/list?range=cn&key={KEY}"
```

### 10. 空气质量实时 `/v7/air/now`
```bash
curl --compressed "https://{HOST}/v7/air/now?location={LON},{LAT}&key={KEY}"
```
**返回字段**: aqi(空气质量指数), level(等级), category(类别), primary(主要污染物), pm10, pm2p5(PM2.5), no2, so2, co, o3

### 11. 空气质量预报 `/v7/air/5d`
```bash
curl --compressed "https://{HOST}/v7/air/5d?location={LON},{LAT}&key={KEY}"
```

### 12. 生活指数 `/v7/indices/{1d|3d}`
```bash
curl --compressed "https://{HOST}/v7/indices/1d?type=0&location={LON},{LAT}&key={KEY}"
```
**参数**: type=0 表示全部指数，也可指定类型 ID
**指数类型**:
- 1: 运动指数
- 2: 洗车指数
- 3: 穿衣指数
- 4: 钓鱼指数
- 5: 紫外线指数
- 6: 旅游指数
- 7: 花粉过敏指数
- 8: 舒适度指数
- 9: 感冒指数
- 10: 空气污染扩散条件指数
- 11: 空调开启指数
- 12: 太阳镜指数
- 13: 化妆指数
- 14: 晾晒指数
- 15: 交通指数
- 16: 防晒指数

### 13. 太阳辐射 `/v7/solar/{24h|72h}`
```bash
curl --compressed "https://{HOST}/v7/solar/24h?location={LON},{LAT}&key={KEY}"
```
**返回字段**: fxTime, radiation(GHI太阳辐射W/m²), cloudCover, humidity, precip, temperature

### 14. 天文信息

#### 日出日落 `/v7/astronomy/sun`
```bash
curl --compressed "https://{HOST}/v7/astronomy/sun?location={LON},{LAT}&date=20260622&key={KEY}"
```
**返回字段**: sunrise(日出时间), sunset(日落时间)

#### 月升月落 `/v7/astronomy/moon`
```bash
curl --compressed "https://{HOST}/v7/astronomy/moon?location={LON},{LAT}&date=20260622&key={KEY}"
```
**返回字段**: moonrise, moonset, moonPhase[] (月相名称、图标、照明度、月相角度)

### 15. 海洋信息

#### 潮汐 `/v7/ocean/{tide|currents}`
```bash
curl --compressed "https://{HOST}/v7/ocean/tide?location=P2951&date=20260622&key={KEY}"
```
**注意**: location 需使用海洋站点 ID

### 16. 时间机器 `/v7/historical/weather`
```bash
curl --compressed "https://{HOST}/v7/historical/weather?location={LON},{LAT}&date=20260601&key={KEY}"
```
**限制**: 历史天气需要付费套餐

### 17. 地理信息 `/v7/geo/v2/city/lookup`
```bash
curl --compressed "https://{HOST}/v7/geo/v2/city/lookup?location=北京&key={KEY}"
```
**返回字段**: location[].id(地点ID), name, country, adm1(省), adm2(市), isPoi, type, lat, lon

## 通用参数

- `lang`: 语言（默认 zh，可选 en/ja/ko/fr 等）
- `unit`: 单位（默认 m 公制，可选 i 英制）
- `key`: API Key（必填）

## 错误码

| code | 含义 |
|------|------|
| 200 | 成功 |
| 204 | 无数据（该地区不支持） |
| 400 | 请求参数错误 |
| 401 | 认证失败（key 无效） |
| 402 | 超额/余额不足 |
| 403 | 无权限（Host 不匹配等） |
| 404 | 数据不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

## 与 Open-Meteo 对比

| 特性 | 和风天气 | Open-Meteo |
|------|---------|-----------|
| 中国境内精度 | 3-5km（格点） | 15km（CMA全球） |
| 分钟级降水 | 1km（仅中国） | 15分钟级（2-3天） |
| ET0 蒸散量 | ❌ 无 | ✅ 直接提供 |
| 土壤多层 | ❌ 无 | ✅ 5层 |
| 多模型对比 | ❌ 无 | ✅ 16个模型 |
| 历史数据 | ⚠️ 付费 | ✅ 免费（1940-） |
| 生活指数 | ✅ 16种 | ❌ 无 |
| 太阳辐射 | ✅ 24h/72h | ✅ 含卫星辐射 |
| 天气预警 | ✅ 中央气象台 | ❌ 无 |
| 费用 | 免费5万次/月 | 免费无限制 |

## 推荐使用场景

- **中国境内实时天气**: grid-weather/now（最精确）
- **中国境内降水预报**: weather/7d + minutely/5m
- **天气预警**: warning/now（接入中央气象台）
- **生活指数**: indices/1d?type=0
- **太阳辐射**: solar/24h（农业光伏场景）
