---
name: multi-source-weather
description: 多源气象数据统一接口。根据查询地点和需求自动选择最优数据源（Open-Meteo / 和风天气 / 彩云天气 / IBM Weather / NASA POWER）。覆盖实时天气、预报、历史实测、分钟级降水、ET0蒸散量、土壤湿度、空气质量、太阳辐射、预报准确率验证等全场景需求。适用于农业、能源、物流、科研、应急管理等各行各业。
version: 4.0.0
author: Jian
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [weather, multi-provider, auto-select, api, et0, soil, forecast, validation, agriculture, energy]
    related_skills: [maps, irrigation-control, solar-energy]
---

# 多源气象数据统一接口

## 设计原则

**业务解耦**：本 skill 是通用的全场景气象数据查询工具，不包含任何具体业务逻辑（如晨报生成、灌溉决策等）。业务特定策略应在应用层实现，skill 只提供数据获取能力。

**场景抽象**：选择策略基于抽象维度（地理区域、数据类型、精度需求、成本策略等），而非具体业务场景。这确保 skill 可复用于多种业务上下文。

**凭据安全**：凭据存储在 `credentials.yaml`（.gitignore 排除），上传 Git 时不含任何 token/key。本地日常使用自动读取 credentials.yaml。

**文档深度**：使用前必须通读各平台官方文档（references/ 中有完整摘要），理解每个端点的参数、返回值、限制条件，不要凭印象猜测接口行为。

## 核心能力

### 五大平台定位

| 平台 | 定位 | 数据类型 | 认证 | 费用 | 历史深度 |
|------|------|---------|------|------|---------|
| **Open-Meteo** | 全球通用核心源 | 预报/历史/ET0/土壤/辐射 | 无需 Key | 免费无限制 | 1940年至今 |
| **和风天气** | 中国首选 | 实时/预报/预警/分钟级降水 | API Key + Host | 免费 5万次/月 | 最近7天（时光机） |
| **彩云天气** | 分钟级降水最优 | 实时/分钟级降水/预警 | Token/HMAC签名 | 按量付费 | 无历史API |
| **IBM Weather** | 机场实测 Ground Truth | 机场METAR实测 | API Key | 免费（限速） | 90天+ |
| **NASA POWER** | 农业/能源专用 | 卫星遥感历史数据 | 无需 Key | 完全免费 | 1981年至今 |

### 数据能力总览

#### 1. 实时天气（当前时刻）
- **中国境内**：和风天气（3-5km格点）> 彩云天气（1km）> Open-Meteo
- **国外地区**：Open-Meteo（15km全球覆盖）
- **机场实测**：IBM Weather（地面站实测，Ground Truth）

#### 2. 天气预报
- **分钟级降水（未来2小时）**：彩云天气（1km/1分钟更新）> 和风天气（1km/5分钟）
- **逐小时预报**：三平台均支持，Open-Meteo 最多384小时
- **逐日预报**：和风天气支持15天，Open-Meteo 支持16天
- **40天次季节**：彩云天气 v3（企业专属）

#### 3. 历史数据
- **历史天气（模型再分析）**：Open-Meteo Archive（1940年至今，ERA5+气象站）
- **历史实测（机场METAR）**：IBM Weather（90天+，地面站实测，Ground Truth）
- **历史遥感（卫星+地面）**：NASA POWER（1981年至今，农业/能源专用）
- **气候预测（至2100年）**：Open-Meteo（CMIP6模型）

#### 4. 农业/水文数据
- **ET0 蒸散量**：Open-Meteo（唯一直接提供，FAO-56标准）
- **土壤温湿度**：Open-Meteo（5层：1/3/9/27/81cm）> NASA POWER（表层）> 彩云天气（2层）
- **降水累计**：Open-Meteo daily 或和风天气累计
- **日照时数**：Open-Meteo（sunshine_duration）或 NASA POWER（ALLSKY_SFC_SW_DWN）

#### 5. 能源/光伏数据
- **太阳辐射**：Open-Meteo（短波/长波/直接/散射/紫外线）> NASA POWER（全天短波/长波）
- **云量**：Open-Meteo（总云量/低/中/高云）
- **风速风向**：Open-Meteo（10m/80m/120m/180m多高度）> NASA POWER（2m/10m/50m）
- **温度**：Open-Meteo（地表温度 skin_temperature）

#### 6. 大气环境/空气质量
- **PM2.5/PM10/O3/NO2/SO2/CO**：彩云天气 v2.6 realtime（免费）或 Open-Meteo Air Quality API
- **AQI 指数**：彩云天气（中国标准+美国标准双出）
- **花粉浓度**：Open-Meteo（欧洲地区）

#### 7. 灾害/预警数据
- **🚨 中国官方气象灾害预警（首选）**：中国气象局国家气象中心 NMC REST API（`nmc.cn/rest/findAlarm`），免费公开接口，无需认证，覆盖全国所有省/市/县，按行政区划代码过滤，预警类型完整（暴雨/大风/高温/寒潮/雷电/冰雹/沙尘暴/大雾/霜冻/干旱/地质灾害等），四级等级（蓝/黄/橙/红），由专业气象专家研判发布
- **商业API预警**：和风天气（中央气象台数据）或彩云天气（需付费套餐，基础套餐常返回 403）
- **分钟级降水预警**：彩云天气（1km/1分钟更新）
- **台风路径**：彩云天气 v3（企业）或和风天气
- **洪水/河流**：Open-Meteo（全球河流流量集合预报）
- **森林火险**：Open-Meteo（FWI火险指数）

#### 8. 生活/出行数据
- **生活指数**：和风天气（16种：穿衣/洗车/紫外线/感冒/运动/钓鱼等）或彩云天气 v2.6
- **天文信息**：Open-Meteo（日出日落/日照时长）或和风天气（日出日落/月相）
- **能见度**：和风天气或彩云天气

#### 9. 海洋数据
- **海浪/潮汐**：Open-Meteo Marine API 或彩云天气 v3（企业）
- **海表温度/海流**：Open-Meteo

#### 10. 高空数据
- **高空变量（100m风等）**：彩云天气 v3（企业）
- **等压面变量（1000-30hPa，18层）**：Open-Meteo

## 场景化选择策略

> **原则**：策略基于通用维度抽象，不绑定具体业务。任何行业、任何场景，按以下维度组合即可找到最优数据源。

### 一、按地理区域

**中国境内**：
- 实时天气 → 和风天气（3-5km格点精度最高）
- 分钟级降水 → 彩云天气（1km精度）> 和风天气
- 天气预警 → 和风天气（接入中央气象台）
- 空气质量 → 彩云天气 v2.6 realtime（免费含AQI）或 Open-Meteo（变量更全）
- 机场实测 → IBM Weather（最近机场的METAR数据，Ground Truth）

**国外地区**：
- 通用查询 → Open-Meteo（全球覆盖，免费无限制）
- 多模型对比 → Open-Meteo（16个模型来源）
- 历史遥感 → NASA POWER（1981年至今，农业/能源专用）

### 二、按数据类型

**基础气象（温度/湿度/风/降水/云量/气压）**：
- 中国实时 → 和风天气优先，彩云天气交叉验证
- 国外实时 → Open-Meteo 优先
- 机场实测（Ground Truth）→ IBM Weather
- 全球通用 → Open-Meteo

**农业/水文数据**：
- ET0 蒸散量 → Open-Meteo（唯一直接提供，FAO-56 标准）
- 土壤温湿度 → Open-Meteo（5层：1/3/9/27/81cm）> NASA POWER（表层）> 彩云天气（2层，需企业）
- 降水累计 → Open-Meteo daily 或和风天气累计
- 日照时数 → Open-Meteo（sunshine_duration）或 NASA POWER（ALLSKY_SFC_SW_DWN）

**能源/光伏数据**：
- 太阳辐射 → Open-Meteo（短波/长波/直接/散射/紫外线）> NASA POWER（全天短波/长波）
- 云量 → Open-Meteo（总云量/低/中/高云）
- 温度 → Open-Meteo（地表温度 skin_temperature）
- 风速风向 → Open-Meteo（10m/80m/120m/180m 多高度）> NASA POWER（2m/10m/50m）

**大气环境/空气质量**：
- PM2.5/PM10/O3/NO2/SO2/CO → 彩云天气 v2.6 realtime（免费）或 Open-Meteo Air Quality API
- AQI 指数 → 彩云天气（中国标准+美国标准）
- 花粉浓度 → Open-Meteo（欧洲地区）

**灾害/预警数据**：
- 🚨 中国官方气象灾害预警（首选）→ NMC REST API（`nmc.cn/rest/findAlarm`），免费公开，无需认证，按行政区划代码过滤
- 商业API预警 → 和风天气（中央气象台数据）或彩云天气（需付费套餐）
- 分钟级降水预警 → 彩云天气（1km/1分钟更新）
- 台风路径 → 彩云天气 v3（企业）或和风天气
- 洪水/河流 → Open-Meteo（全球河流流量集合预报）
- 森林火险 → Open-Meteo（FWI 火险指数）

**生活/出行数据**：
- 生活指数 → 和风天气（16种：穿衣/洗车/紫外线/感冒/运动/钓鱼等）或彩云天气 v2.6
- 天文信息 → Open-Meteo（日出日落/日照时长）或和风天气（日出日落/月相）
- 能见度 → 和风天气或彩云天气

**历史/趋势数据**：
- 历史天气（1940年至今，模型再分析）→ Open-Meteo Archive API（独有）
- 历史实测（90天+，机场METAR）→ IBM Weather（Ground Truth）
- 历史遥感（1981年至今）→ NASA POWER（卫星+地面站校正）
- 气候预测（至2100年）→ Open-Meteo（CMIP6 模型）
- 40天次季节预报 → 彩云天气 v3（企业）或 Open-Meteo 季节性预报
- 集合预报（不确定性评估）→ Open-Meteo Ensemble API

**海洋数据**：
- 海浪/潮汐 → Open-Meteo Marine API 或彩云天气 v3（企业）
- 海表温度/海流 → Open-Meteo

**高空数据**：
- 高空变量（100m风等）→ 彩云天气 v3（企业）
- 等压面变量（1000-30hPa，18层）→ Open-Meteo

**时效性数据**：
- 实时（1分钟更新）→ 彩云天气
- 近实时（5-10分钟）→ 和风天气
- 标准（15分钟）→ Open-Meteo
- 分钟级降水（未来2小时）→ 彩云天气 > 和风天气
- 闪电实况 → 彩云天气（独有）

### 三、按精度需求

**高精度（1km）**：
- 分钟级降水 → 彩云天气
- 实时天气 → 彩云天气

**标准精度（3-5km）**：
- 实时天气（中国）→ 和风天气格点
- 小时预报 → 和风天气或彩云天气

**广覆盖（9-15km）**：
- 全球查询 → Open-Meteo
- 多模型对比 → Open-Meteo

**地面站实测（最高可信度）**：
- 机场METAR → IBM Weather（Ground Truth）

### 四、按成本策略

**免费优先（零成本）**：
1. Open-Meteo（免费无限制，无需Key）
2. NASA POWER（完全免费，无需Key，1981年至今）
3. 和风天气（免费5万次/月，需注册）
4. 彩云天气 v2.6（免费额度，需注册）

**质量优先（不考虑成本）**：
- 中国境内 → 和风天气 + 彩云天气 + Open-Meteo + IBM Weather 四源交叉验证
- 多源交叉验证 → 四平台同时查询
- Ground Truth 验证 → IBM Weather 机场实测

**成本敏感（高频大量调用）**：
- 优先 Open-Meteo（无限量）
- 历史数据优先 NASA POWER（无限量，1981年至今）
- 和风天气控制在免费额度内（5万次/月 ≈ 每30分钟1次）
- 彩云天气控制调用频率，避免超出免费额度

### 五、按数据完整性

**单次请求获取全部**：
- 彩云天气综合接口 `/weather`（一次获取 realtime+hourly+daily+alert+forecast_keypoint）

**按需组合**：
- Open-Meteo（灵活选择变量和模型，按需请求）
- 和风天气（按接口分别调用）
- NASA POWER（按参数列表请求）

### 六、按行业场景

| 行业 | 核心数据 | 首选源 | 补充源 |
|------|---------|--------|--------|
| **农业种植** | ET0、土壤湿度、降水、温度、风速、太阳辐射 | Open-Meteo | NASA POWER + 和风天气 + 彩云天气 |
| **能源/光伏** | 太阳辐射、云量、温度、风速(多高度) | Open-Meteo | NASA POWER + 和风天气 |
| **物流/运输** | 降水、风速、能见度、路面温度 | 和风天气 | Open-Meteo |
| **建筑施工** | 风速(多高度)、降水、温度、雷电 | 和风天气 | 彩云天气(分钟级降水) |
| **户外赛事** | 降水、风速、温度、紫外线、空气质量 | 和风天气 | 彩云天气(AQI) |
| **航空/无人机** | 风速(多高度)、能见度、云量、气压、雷电、机场METAR | Open-Meteo | IBM Weather + 和风天气 |
| **旅游/景区** | 天气概况、紫外线、舒适度、日出日落 | 和风天气(生活指数) | Open-Meteo |
| **应急管理** | 预警、台风、暴雨、高温、极端天气 | 和风天气(中央气象台) | 彩云天气 |
| **海洋/渔业** | 海浪、潮汐、海温、风速 | Open-Meteo Marine | 彩云天气 v3 |
| **保险/金融** | 历史极端天气、气候趋势、集合预报 | Open-Meteo Archive | NASA POWER + IBM Weather |
| **城市管理** | 空气质量、高温、暴雨、道路结冰 | Open-Meteo AQI | 和风天气 + 彩云天气 |
| **教育/科普** | 天文、多模型对比、历史天气 | Open-Meteo | NASA POWER + 和风天气 |
| **气候研究** | 历史遥感（1981年至今）、长期趋势 | NASA POWER | Open-Meteo Archive |
| **预报验证** | 机场实测（Ground Truth） | IBM Weather | Open-Meteo Archive |

### 七、按调用频率

**高频（≤5分钟/次）**：
- 只用 Open-Meteo（免费无限量）
- 彩云天气仅用于独家数据（分钟级降水、空气质量）

**中频（15-30分钟/次）**：
- 四源均可（和风天气5万次/月 ≈ 1次/分钟，够用）
- 推荐四源交叉验证

**低频（1次/天或更少）**：
- 四源全量采集，做全面对比
- 适合日报/晨报/数据分析

**事件触发（预警/告警）**：
- 可靠性优先，多源同时查询
- 宁可多调一次也不漏报

### 八、数据融合策略

当多个平台返回相同类型数据时，按以下规则融合：

**独家数据直接取**：
- ET0 → 只取 Open-Meteo
- 空气质量实时 → 优先取彩云天气（免费）
- 天气预警文本 → 优先取和风天气（中央气象台）
- 历史天气（模型再分析）→ 只取 Open-Meteo
- 历史实测数据（机场METAR）→ 只取 IBM Weather（Ground Truth）
- 历史遥感数据（1981年至今）→ 只取 NASA POWER
- 生活指数 → 优先取和风天气（16种）
- 预报准确率验证 → IBM Weather 实测值作为基准

**多源共有数据融合规则**（基于实测验证，非简单取均值）：
- 温度 → 中国境内优先取和风天气（站点实测），国外取 Open-Meteo。差异>3°C时标注不确定性，不取均值
- 湿度 → 优先取和风天气或彩云天气（×100转百分比）。Open-Meteo 系统性偏低（实测偏低5-15%），不作主源
- 风速 → 优先取彩云天气（雷达实测）。Open-Meteo 系统性偏低（实测差2倍），仅作趋势参考
- 降水 → 取彩云天气（分钟级精度最高）。差异大时标注各源数据，不取均值
- 气压 → 三源均可，差异小，取均值即可（彩云需÷100转hPa）
- 太阳辐射 → Open-Meteo > NASA POWER（两者数据接近，Open-Meteo更新更快）
- 土壤湿度 → Open-Meteo（5层）> NASA POWER（表层）

**重要验证结论**：实测对比显示各家平台同时刻数据差异显著（温度0.6-5.4°C，湿度9-15%，风速最高差2倍）。简单取均值会掩盖系统偏差，不推荐作为默认策略。应根据具体指标选择已验证最优的数据源，详见 `references/provider-comparison.md`。

**冲突处理**：
- 差异 ≤10% → 取均值，不标注
- 差异 10-30% → 取均值，标注"多源差异较大"
- 差异 >30% → 不取均值，列出所有源数据，标注"数据冲突，建议人工核实"

**数据验证方法论**：
- 使用 **IBM Weather（机场METAR实测数据）** 作为 Ground Truth 基准，验证预报准确率
- IBM Weather 提供中国民航机场地面站实测数据，每小时更新，质量高
- Open-Meteo Archive 可作为补充（ERA5再分析+气象站观测），但不是实测
- NASA POWER 可作为长期历史趋势验证（1981年至今，卫星+地面站校正）
- 验证应在多个地理坐标上进行（至少5个不同城市/区域），不能只用单一地点
- 验证维度：温度偏差（°C）、降水准确性（mm）、风速偏差（km/h）、湿度偏差（%）
- 验证周期：提前1天/3天/7天的预报值 vs 实测值
- 示例验证脚本见 `references/accuracy-validation.md`

**数据源标注**：
- 每条数据必须标注来源（Open-Meteo / 和风天气 / 彩云天气 / IBM Weather / NASA POWER）
- 融合数据标注所有参与融合的来源
- 降级数据标注"降级自 XXX 平台"

### 九、可靠性与降级策略

**各平台可用性**：
- Open-Meteo：开源项目，全球 CDN，稳定性最高
- 和风天气：中国商业服务，国内访问稳定
- 彩云天气：中国商业服务，v2.6 基础接口稳定
- IBM Weather：IBM 企业级服务，稳定性高
- NASA POWER：NASA 官方服务，稳定性高

**降级链**：
```
实时天气(中国)：  和风天气 → 彩云天气 → Open-Meteo
实时天气(国外)：  Open-Meteo → (无备选)
ET0/土壤：       Open-Meteo → NASA POWER → (无备选)
分钟级降水：     彩云天气 → 和风天气 → Open-Meteo
天气预警：       NMC(中国气象局) → 和风天气 → 彩云天气 → Open-Meteo
空气质量：       彩云天气 → Open-Meteo AQI → (无备选)
历史天气：       Open-Meteo → (无备选)
历史实测：       IBM Weather → (无备选，机场METAR独家)
历史遥感：       NASA POWER → (无备选，1981年至今独家)
太阳辐射：       Open-Meteo → NASA POWER → (无备选)
预报验证基准：   IBM Weather实测值 → Open-Meteo Archive → (无备选)
```

**降级标记**：
- 降级成功 → 数据正常返回，附加字段 `"source_degraded": true, "original_source": "xxx"`
- 全部失败 → 返回 `"error": "所有数据源均不可用"`，不做降级到编造数据

## 凭据配置

凭据存储在 `credentials.yaml`（已加入 .gitignore），不上传 Git。

### 读取凭据

```bash
# 和风天气
QWEATHER_HOST=$(yq '.qweather.api_host' credentials.yaml)
QWEATHER_KEY=$(yq '.qweather.api_key' credentials.yaml)

# 彩云天气
CAIYUN_TOKEN=$(yq '.caiyun.token' credentials.yaml)
CAIYUN_APP_KEY=$(yq '.caiyun.app_key' credentials.yaml)
CAIYUN_APP_SECRET=$(yq '.caiyun.app_secret' credentials.yaml)

# IBM Weather
IBM_WEATHER_KEY=$(yq '.ibm_weather.api_key' credentials.yaml)

# Open-Meteo 和 NASA POWER 无需凭据
```

### 新用户获取指引

**和风天气**：
1. 注册 https://console.qweather.com
2. 创建项目 → 获取 API Key
3. 设置页面 → 获取专属 API Host（格式：`xxx.def.qweatherapi.com`）
4. API Host 安全设置可设为"不限制"
5. ⚠️ 2026年起旧地址（devapi.qweather.com）已停用，必须用专属 Host

**彩云天气**：
1. 注册 https://platform.caiyunapp.com
2. 创建应用 → 获取 AppKey 和 AppSecret
3. 控制台 → Token 管理 → 获取 v2.6 Token（简单方式）
4. v3 API 需要 HMAC-SHA256 签名（见 `references/caiyun-v3-signing.py`）

**IBM Weather**：
1. 注册 https://developer.ibm.com/apis/catalog/weather-data
2. 创建应用 → 获取 API Key
3. 免费层有速率限制，适合低频查询

**Open-Meteo**：无需注册，直接调用。

**NASA POWER**：无需注册，直接调用。

## 快速调用示例

### 1. 实时天气（中国最优）
```bash
# 和风天气格点（3-5km，推荐中国境内）
curl --compressed "https://{QWEATHER_HOST}/v7/grid-weather/now?location={LON},{LAT}&key={QWEATHER_KEY}"

# Open-Meteo（全球通用，备选）
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone={TIMEZONE}"
```

### 2. 分钟级降水（彩云天气最优）
```bash
# 彩云天气（1km精度，v2.6 token方式）
curl "https://api.caiyunapp.com/v2.6/{CAIYUN_TOKEN}/{LON},{LAT}/minutely"

# 和风天气（备选，1km中国境内）
curl --compressed "https://{QWEATHER_HOST}/v7/minutely/5m?location={LON},{LAT}&key={QWEATHER_KEY}"
```

### 3. ET0 蒸散量（仅 Open-Meteo）
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=et0_fao_evapotranspiration_sum,precipitation_sum&hourly=et0_fao_evapotranspiration&timezone={TIMEZONE}&forecast_days=7"
```

### 4. 土壤温湿度（Open-Meteo 5层）
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=soil_temperature_0cm,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm&timezone={TIMEZONE}&forecast_days=7"
```

### 5. 7天天气预报（和风天气，中国最优）
```bash
curl --compressed "https://{QWEATHER_HOST}/v7/weather/7d?location={LON},{LAT}&key={QWEATHER_KEY}"
```

### 6. 中国气象局官方气象灾害预警（首选）
```bash
# 查询全国预警（按省份过滤）
# province=65 为新疆，6528 为巴州，652828 为尉犁县
curl "http://www.nmc.cn/rest/findAlarm?pageNo=1&pageSize=50&signaltype=&signallevel=&province=65"

# 返回格式：
# {
#   "data": {
#     "page": {
#       "list": [
#         {
#           "alertid": "65282841600000_20260623001215",
#           "issuetime": "2026/06/23 00:12",
#           "title": "新疆维吾尔自治区巴音郭楞蒙古自治州尉犁县气象台发布大风黄色预警信号",
#           "url": "/publish/alarm/65282841600000_20260623001215.html",
#           "pic": "https://image.nmc.cn/assets/img/alarm/p0001002.png"
#         }
#       ]
#     },
#     "stat": {
#       "province": {"r": 0, "b": 0, "y": 0, "o": 0},
#       "city": {"r": 0, "b": 0, "y": 0, "o": 0},
#       "county": {"r": 0, "b": 0, "y": 0, "o": 0}
#     }
#   }
# }

# 行政区划代码查询：
# 新疆维吾尔自治区：65
# 巴音郭楞蒙古自治州：6528
# 尉犁县：652828
# 完整列表：http://www.nmc.cn/publish/alarm.html（页面下拉选择省份）
```

### 7. 天气预警（和风天气，备选）
```bash
curl --compressed "https://{QWEATHER_HOST}/v7/warning/now?location={LON},{LAT}&key={QWEATHER_KEY}"
```

### 8. 空气质量（Open-Meteo）
```bash
curl "https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&hourly=pm2_5,pm10,us_aqi,european_aqi,ozone,nitrogen_dioxide&timezone={TIMEZONE}&forecast_days=3"
```

### 9. 多模型对比（Open-Meteo）
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,precipitation_sum&models=ecmwf_ifs025,cma_grapes_global,icon_seamless,gfs_seamless&timezone={TIMEZONE}&forecast_days=7"
```

### 10. 历史天气（Open-Meteo，1940年至今，模型再分析）
```bash
curl "https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={START}&end_date={END}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone={TIMEZONE}"
```

### 11. 历史实测（IBM Weather，机场METAR，90天+，Ground Truth）
```bash
# 北京首都机场 ZBAA
curl "https://api.weather.com/v1/location/ZBAA:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"

# 上海浦东机场 ZSSS
curl "https://api.weather.com/v1/location/ZSSS:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"

# 广州白云机场 ZGGG
curl "https://api.weather.com/v1/location/ZGGG:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"

# 成都双流机场 ZUUU
curl "https://api.weather.com/v1/location/ZUUU:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"

# 乌鲁木齐机场 ZWWW
curl "https://api.weather.com/v1/location/ZWWW:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"

# 库尔勒机场 ZWKL（新疆尉犁附近）
curl "https://api.weather.com/v1/location/ZWKL:9:CN/observations/historical.json?apiKey={IBM_WEATHER_KEY}&units=m&startDate={YYYYMMDD}&endDate={YYYYMMDD}"
```

### 12. 历史遥感（NASA POWER，1981年至今，农业/能源专用）
```bash
# 获取农业气象数据（温度、降水、风速、湿度、辐射）
curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,T2M,PRECTOTCORR,WS2M,WS10M,RH2M,ALLSKY_SFC_SW_DWN,PS&latitude={LAT}&longitude={LON}&start={YYYYMMDD}&end={YYYYMMDD}&community=ag&format=JSON"

# 获取能源数据（辐射、风速、温度）
curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,ALLSKY_SFC_LW_DWN,WS10M,WS50M,T2M&latitude={LAT}&longitude={LON}&start={YYYYMMDD}&end={YYYYMMDD}&community=re&format=JSON"
```

### 13. 日出日落+天文信息
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=sunrise,sunset,daylight_duration,uv_index_max&timezone={TIMEZONE}&forecast_days=7"
```

### 14. 生活指数（和风天气）
```bash
curl --compressed "https://{QWEATHER_HOST}/v7/indices/1d?type=0&location={LON},{LAT}&key={QWEATHER_KEY}"
```

### 15. 彩云天气综合接口（一次获取全部）
```bash
curl "https://api.caiyunapp.com/v2.6/{CAIYUN_TOKEN}/{LON},{LAT}/weather?alert=true&dailysteps=7&hourlysteps=24"
```

### 16. 彩云天气土壤温湿度
```bash
curl "https://api.caiyunapp.com/v1/soil?token={CAIYUN_TOKEN}&lng={LON}&lat={LAT}"
```

## Common Pitfalls

1. **和风天气必须用 --compressed**：默认返回 gzip，不加会乱码
2. **和风天气必须用专属 API Host**：2026年起旧地址已停用，每个账号有独立 Host
3. **和风天气坐标顺序**：`location=经度,纬度`（lon,lat），与 Open-Meteo 相反
4. **Open-Meteo 坐标顺序**：`latitude=X&longitude=Y`（lat,lon 分开传）
5. **彩云天气坐标顺序**：URL 路径中是 `经度,纬度`（lon,lat）
6. **彩云天气 v3 用不同 Host**：`singer.caiyunhub.com`，不是 `api.caiyunapp.com`
7. **彩云天气 v3/v1 是企业增值服务**：免费 token 只有 v2.6 基础接口权限，v3/v1 调用返回 `"no perm"`
8. **时区参数**：Open-Meteo 需要显式指定 timezone（如 `Asia/Urumqi`），不要假设系统时区
9. **彩云天气湿度单位**：humidity 是 0-1 的小数，不是百分比，需乘以 100
10. **彩云天气气压单位**：pressure 是 Pa（帕斯卡），需除 100 转 hPa
11. **彩云天气 v2.6 综合接口最高效**：`/weather` 一次获取 realtime+hourly+daily+alert，减少调用次数
12. **彩云天气更新频率和分辨率**：实时 1min/1km，分钟级降水 1min/1km，小时级 15min/5km，天级 2h/12km
13. **ET0 是参考蒸散量**：实际作物需水量 = ET0 × Kc（作物系数），不同作物不同生长阶段 Kc 不同
14. **土壤湿度单位**：Open-Meteo 是 m³/m³，彩云天气也是 0-1 小数
15. **和风天气免费额度计算**：每 30 分钟取一次 = 1440 次/月，远低于 5 万次免费上限。太阳辐射单独收费（0.003 元/次）
16. **彩云天气免费额度需登录控制台确认**：文档未公开具体数字，三种套餐（按量/包月/企业）QPS 不同
17. **凭据读取不要依赖 pyyaml**：系统 Python 通常没有 pyyaml 模块。Shell 脚本中读 credentials.yaml 应使用 `grep + awk` 而非 `python3 -c "import yaml; ..."`，否则会 ModuleNotFoundError
18. **不要混淆上游数据源和下游商业服务**：和风天气/彩云天气是数据加工服务商（下游），它们的数据来源包含中国气象局（CMA）等上游站点观测数据。但经过插值、模式修正、格点化处理后，已不是站点级原始观测。CMA 的实测蒸发量、站点级逐小时观测（1951年至今）、高空探空廓线等原始数据，商业 API 不覆盖。详见 `references/cma-data-source.md`
19. **调研新数据源时，必须实际测试对比而非凭印象下结论**：不能说"商业API已经覆盖了官方数据"就草草了事，要逐项对比颗粒度、实时性、历史深度，给出有据可查的结论
20. **IBM Weather 机场代码格式**：使用 ICAO 代码 + `:9:CN`，如 `ZBAA:9:CN`（北京首都机场）
21. **NASA POWER 缺失值处理**：返回 `-999.0` 表示数据缺失，需过滤
22. **NASA POWER 时间延迟**：最新数据可能有 2-3 天延迟，不适合实时查询
23. **IBM Weather 速率限制**：免费层有严格速率限制，不适合高频调用
24. **Open-Meteo Archive 不是实测**：基于 ERA5 再分析模型，不能作为 Ground Truth，仅作为参考
25. **Python SDK gzip 处理**：和风天气返回 gzip 压缩数据，使用 `urllib` 时必须自动检测并解压（检查 `raw[:2] == b'\x1f\x8b'`），否则会 UTF-8 解码错误
26. **🚨 绝不能根据数值预报自行判断气象灾害**：这是原则性错误，不是技术细节。用户明确要求："中国的这个气象局没有这种灾害预警吗？我希望有这种专业的这种预警出来，而不是我们根据这个预测的数值来去自己去做这个预警的判断，因为这是个很专业的事情，特别是你的数据源是否很可靠，数据源有偏差的话，可能就会导致你自己判断的这个灾害是不准的"。正确做法：使用中国气象局国家气象中心 (NMC) 官方预警 API（`nmc.cn/rest/findAlarm`），由专业气象专家研判发布，具有法律效力。详见 `references/nmc-warning-api.md`
27. **和风天气预警 API 需要付费套餐**：基础免费套餐调用 `/v7/warning/now` 返回 403 Forbidden，需要联系客服升级权限。NMC API 完全免费且更权威，应作为首选

## 通用工作流模式

### 数据采集流程
1. 根据场景选择策略确定数据源
2. 调用对应平台的 API 接口
3. 解析返回的 JSON 数据
4. 进行单位转换和格式化处理
5. 如需多源验证，调用备选平台对比

### 多源交叉验证
1. 同时查询多个平台获取相同类型数据
2. 对比各平台返回的数值差异
3. 差异过大时标注不确定性，建议人工核实

### 降级策略
1. 首选平台调用失败时，自动切换到备选平台
2. 记录失败原因和降级日志
3. 返回结果中标注实际使用的数据源

### 预报准确率验证
1. 每日采集各平台预报数据（day+1, day+3, day+7）
2. 同时采集 IBM Weather 机场实测数据（Ground Truth）
3. 7天后对比预报值 vs 实测值，计算 MAE、RMSE
4. 按平台、按指标、按提前天数统计准确率
5. 输出验证报告，指导数据源选择优化

## 参考文档

- `references/qweather-api.md` — 和风天气完整 API 参考
- `references/caiyun-api.md` — 彩云天气完整 API 参考（v2.6 免费 + v3/v1 企业增值）
- `references/open-meteo-api.md` — Open-Meteo 完整 API 参考
- `references/ibm-weather-api.md` — IBM Weather API 参考（机场METAR实测，Ground Truth）
- `references/nasa-power-api.md` — NASA POWER API 参考（1981年至今，农业/能源专用）
- `references/nmc-warning-api.md` — 中国气象局国家气象中心预警 API 参考（官方权威，免费公开）
- `references/caiyun-v3-signing.py` — 彩云天气统一 CLI 工具（v2.6/v3/v1）
- `references/qweather-api-setup.md` — 和风天气接入配置指南
- `references/provider-comparison.md` — 五平台详细对比表
- `references/cma-data-source.md` — 中国气象局（CMA）数据源调研：上游原始数据 vs 下游商业服务的差异与价值
- `references/accuracy-validation.md` — 五源数据准确性验证报告（基于 IBM Weather 机场实测基准，5城市对比）

## 相关工具脚本

以下脚本位于 `/opt/data/weather-accuracy/`（不属于 skill 本身，是业务应用层的实现）：

- `daily_collect.py` — 每日数据采集脚本（采集五平台实况+预报+NASA POWER历史）
- `validate_forecasts.py` — 预报准确率验证脚本（对比7天前预报 vs 今天实测）
- `weather_sdk.py` — Python SDK，封装五大平台 API 调用，自动处理 gzip 压缩

**设计原则**：Skill 只包含文档和 API 参考，不包含业务逻辑脚本。数据采集、验证、SDK 等属于应用层实现，放在业务项目中。

## 依赖

### 系统依赖
- `curl`（和风天气必须加 `--compressed`）
- `python3`（>=3.8）

### Python 依赖（仅脚本需要）
- `requests` >= 2.31
- `pyyaml` >= 6.0

```bash
# 安装方式（使用 uv）
uv venv .venv
uv pip install requests pyyaml --python .venv/bin/python
```

## Verification Checklist

- [ ] 坐标顺序正确（各平台不同）
- [ ] 时区参数正确（新疆用 Asia/Urumqi）
- [ ] curl 加 --compressed（和风天气）
- [ ] 使用正确的 API Host（和风天气）
- [ ] 彩云天气 Token 有效（先在控制台确认）
- [ ] 湿度单位已转换（彩云 0-1 → 百分比）
- [ ] ET0 已乘作物系数
- [ ] 调研内容不发群
- [ ] IBM Weather 机场代码格式正确（ICAO:9:CN）
- [ ] NASA POWER 缺失值已过滤（-999.0）

## Changelog

- **5.0.0** (2026-06-23): 新增中国气象局国家气象中心 (NMC) 官方预警 API，支持全国气象灾害预警查询（暴雨/大风/高温/寒潮/雷电/冰雹等），四级等级体系（蓝/黄/橙/红），按行政区划精准过滤。**重要原则**：气象灾害预警必须使用官方权威渠道，不能根据数值预报自行判断
- **4.0.0** (2026-06-22): 新增 IBM Weather（机场METAR实测，Ground Truth）和 NASA POWER（1981年至今历史遥感），完善预报准确率验证体系，新增 Python SDK 和验证脚本，重命名为 multi-source-weather
- **3.0.0** (2026-06-22): 重写为多源统一接口，新增自动选择策略、凭据管理、完整 API 覆盖
- **2.0.0** (2026-06-22): 扩展为多数据源（Open-Meteo + 和风天气 + 彩云天气）
- **1.0.0** (2026-06-15): 初始版本，仅 Open-Meteo
