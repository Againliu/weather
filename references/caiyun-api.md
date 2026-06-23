# 彩云天气 API 完整参考

## 基本信息

- **官方文档**: https://docs.caiyunapp.com/weather-api/
- **API 版本分布**:
  - **v2.6**: 常规天气（实况/分钟级/小时/天级/预警/综合）→ **免费套餐可用**
  - **v3**: 增值服务（生活指数/空气质量/台风/天文/海洋/模式预报/高空/次季节/朝晚霞/高精度温度/预警/逆地理）→ **企业套餐**
  - **v1**: 历史接口（土壤温湿度/闪电/雷达/天文/潮汐/卫星/图层）→ **企业套餐**
- **认证方式**:
  - v2.6: Token 参数（简单，`token=` query param）
  - v3: Token 参数 或 HMAC-SHA256 签名（header）
  - v1: Token 参数
- **费用**: 按量付费（具体需登录控制台确认）

## ⚠️ 关键发现

1. **v3 用不同 Host**: `singer.caiyunhub.com`（不是 `api.caiyunapp.com`）
2. **v3/v1 接口是企业增值服务**: 免费套餐只有 v2.6 基础接口权限
3. **v2.6 综合接口 `/weather`**: 一次获取 realtime + hourly + daily，最高效
4. **v2.6 realtime 已包含**: 温度、湿度、气压、风速风向、云量、能见度、短波辐射、PM2.5/PM10/O3/SO2/NO2/CO、AQI(中国+美国)、紫外线指数、舒适度指数

## API Host 汇总

| 版本 | Host | 权限要求 |
|------|------|---------|
| v2.6 | `api.caiyunapp.com` | 免费套餐 |
| v3 | `singer.caiyunhub.com` | 企业套餐 |
| v1 | `api.caiyunapp.com` | 企业套餐 |

## v2.6 API 端点（免费可用）

### 1. 综合接口 `/v2.6/{token}/{lon},{lat}/weather`（推荐）
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/weather?alert=true&dailysteps=7&hourlysteps=24"
```
**一次获取**: realtime + hourly + daily + alert + forecast_keypoint

### 2. 实况 `/v2.6/{token}/{lon},{lat}/realtime`
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/realtime"
```
**返回**: temperature(°C), humidity(0-1), cloudrate, skycon, visibility, dswrf(W/m²), wind{speed(km/h),direction(°)}, pressure(Pa), apparent_temperature, precipitation{local,nearest}, air_quality{pm25,pm10,o3,so2,no2,co,aqi}, life_index{ultraviolet,comfort}

### 3. 分钟级降水 `/v2.6/{token}/{lon},{lat}/minutely`
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/minutely"
```
**返回**: 未来2小时逐分钟降水预报

### 4. 逐小时预报 `/v2.6/{token}/{lon},{lat}/hourly`
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/hourly?hourlysteps=24"
```
**返回**: temperature, humidity, precipitation, wind, cloudrate, skycon, precipitation_probability

### 5. 逐日预报 `/v2.6/{token}/{lon},{lat}/daily`
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/daily?dailysteps=7"
```
**返回**: temperature_max/min, precipitation, wind, skycon, sunrise/sunset, moonphase, humidity_max/min, cloudrate_max/min

### 6. 预警 `/v2.6/{token}/{lon},{lat}/alert`
```bash
curl "https://api.caiyunapp.com/v2.6/{token}/{LON},{LAT}/alert"
```

## v3 API 端点（企业套餐）

| 接口 | Host | Path | 参数 |
|------|------|------|------|
| 丰富版生活指数 | singer.caiyunhub.com | `/v3/lifeindex` | longitude, latitude, days[1-15], fields |
| 空气质量站点预报 | singer.caiyunhub.com | `/v3/aqi/forecast/station` | longitude, latitude, hours[1-120] |
| 气象预警 | singer.caiyunhub.com | `/v3/alert/location` | longitude, latitude |
| 台风 | singer.caiyunhub.com | `/v3/typhoon/realtime` | (无坐标参数) |
| 日出日落 | singer.caiyunhub.com | `/v3/astro/sun` | longitude, latitude, days[1-15] |
| 月升月落 | singer.caiyunhub.com | `/v3/astro/moon` | longitude, latitude, days[1-15] |
| 潮汐 | singer.caiyunhub.com | `/v3/sea/tide` | longitude, latitude |
| 海浪 | singer.caiyunhub.com | `/v3/sea/wave` | longitude, latitude |
| 数值模式预报 | singer.caiyunhub.com | `/v3/nwc/china/nc` | (返回NC文件链接) |
| 40天次季节 | singer.caiyunhub.com | `/v3/subseasonal` | longitude, latitude, days |
| 高空100m风 | singer.caiyunhub.com | `/v3/upper/100m/wind` | longitude, latitude, hours |
| 朝晚霞 | singer.caiyunhub.com | `/v3/glow/location` | longitude, latitude |
| 高精度温度(30m) | singer.caiyunhub.com | `/v3/exp/walltapper` | longitude, latitude |
| 逆地理编码 | singer.caiyunhub.com | `/v3/cartography/reverse-geocoding` | longitude, latitude |
| 行政区划 | singer.caiyunhub.com | `/v3/cartography/reverse-admins` | longitude, latitude |

## v1 API 端点（企业套餐）

| 接口 | Path | 参数 |
|------|------|------|
| 土壤温湿度 | `/v1/soil` | lng, lat, token |
| 闪电实况 | `/v1/12-lightning` | lng, lat, token |
| 雷达图 | `/v1/6-radar` | token |
| 天文 | `/v1/5-astro` | lng, lat, token |
| 潮汐 | `/v1/4-tide` | lng, lat, token |
| 卫星 | `/v1/11-satellite` | token |
| 多要素图层 | `/v1/7-layer` | token |

## 生活指数枚举（v3 丰富版，36种）

| 编号 | 名称 | 编号 | 名称 |
|------|------|------|------|
| 1 | 空调 | 19 | 夜生活 |
| 2 | 过敏 | 20 | 雨具 |
| 3 | 钓鱼 | 21 | 路况 |
| 4 | 空气污染扩散 | 22 | 逛街 |
| 5 | 划船 | 23 | 运动 |
| 6 | 洗车 | 24 | 交通 |
| 7 | 感冒 | 25 | 旅游 |
| 8 | 舒适度 | 26 | 紫外线/防晒 |
| 9 | 约会 | 27 | 洗衣 |
| 10 | 穿衣 | 28 | 风寒 |
| 11 | 啤酒 | 30 | 摆摊 |
| 12 | 晾晒 | 31 | 送外卖 |
| 13 | 美发 | 32 | 骑行 |
| 14 | 中暑 | 33 | 火锅 |
| 15 | 放风筝 | 35 | 霉变 |
| 16 | 化妆 | 36 | 观星 |
| 17 | 心情 | | |
| 18 | 晨练 | | |

## Common Pitfalls

1. **v3 用不同 Host**: `singer.caiyunhub.com`，不是 `api.caiyunapp.com`
2. **v3/v1 需要企业套餐**: 免费 token 调用会返回 `"no perm"` 或 `"unauthorized token"`
3. **湿度单位**: humidity 是 0-1 的小数，需乘 100 转百分比
4. **气压单位**: pressure 是 Pa（帕斯卡），需除 100 转 hPa
5. **风速单位**: wind.speed 是 km/h
6. **坐标顺序**: URL 路径中是 `经度,纬度`（lon,lat）
7. **v2.6 综合接口最高效**: `/weather` 一次获取全部数据，减少调用次数

## 工具脚本

- `references/caiyun-v3-signing.py` — 统一 CLI 工具，支持 v2.6/v3/v1 三种版本
- 依赖: `requests>=2.31`, `pyyaml>=6.0`
- 安装: `uv pip install requests pyyaml`
