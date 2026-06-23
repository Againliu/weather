# Open-Meteo API 完整参考文档（中文）

## 概述
Open-Meteo 提供免费的天气API服务，无需API密钥。支持多种天气预报、历史数据、空气质量、海洋、洪水、气候变迁等多种数据源。

---

## 1. 天气预报 API (Weather Forecast API)

### URL 模式
```
https://api.open-meteo.com/v1/forecast
```

### 基本参数
- `latitude`: 纬度（必填，-90 到 90）
- `longitude`: 经度（必填，-180 到 180）
- `timezone`: 时区（可选，默认 GMT+0）
- `forecast_days`: 预报天数（1-16天，默认7天）
- `past_days`: 过去天数（0-92天，默认0）

### 可用天气模型（16个来源）
- **ECMWF**: IFS HRES 9km, IFS 0.25°, AIFS 0.25°
- **CMA**: GRAPES Global（中国气象局）
- **BOM**: ACCESS Global（澳大利亚气象局）
- **NCEP**: GFS Seamless, GFS 0.11°/0.25°, HRRR Conus, NBM Conus, NAM Conus, GFS GraphCast, AIGFS, HGEFS Ensemble
- **JMA**: Seamless, MSM, GSM（日本气象厅）
- **KMA**: Seamless, LDPS, GDPS（韩国气象厅）
- **DWD**: ICON Seamless, ICON Global, ICON EU, ICON D2（德国气象局）
- **GEM**: Seamless, Global, Regional, HRDPS Continental, HRDPS West（加拿大）
- **Météo-France**: Seamless, ARPEGE World/Europe, AROME France/HD
- **ItaliaMeteo**: ARPAE ICON 2I
- **MET Norway**: Nordic Seamless, Nordic
- **KNMI**: Seamless, Harmonie AROME Europe/Netherlands
- **DMI**: Seamless, Harmonie AROME Europe
- **UK Met Office**: Seamless, Global 10km, UK 2km
- **MeteoSwiss**: ICON Seamless, CH1, CH2
- **GeoSphere Austria**: Seamless, AROME Austria

### 小时变量（Hourly Variables）
**温度与湿度**
- temperature_2m: 2米温度
- relative_humidity_2m: 2米相对湿度
- dewpoint_2m: 2米露点温度
- apparent_temperature: 体感温度
- wet_bulb_temperature_2m: 2米湿球温度

**降水**
- precipitation_probability: 降水概率
- precipitation: 总降水量（雨+阵雨+雪）
- rain: 降雨量
- showers: 阵雨量
- snowfall: 降雪量
- snow_depth: 积雪深度

**天气与能见度**
- weather_code: 天气代码
- visibility: 能见度
- is_day: 白天/夜晚标识

**气压与云量**
- pressure_msl: 海平面气压
- surface_pressure: 地面气压
- cloud_cover: 总云量
- cloud_cover_low: 低云量
- cloud_cover_mid: 中云量
- cloud_cover_high: 高云量

**辐射与蒸发**
- evapotranspiration: 蒸散量
- et0_fao_evapotranspiration: 参考蒸散量（ET₀）
- vapour_pressure_deficit: 饱和水汽压差
- uv_index: 紫外线指数
- uv_index_clear_sky: 晴空紫外线指数
- sunshine_duration: 日照时长
- total_column_integrated_water_vapour: 总柱积分水汽

**辐射变量**
- shortwave_radiation: 短波太阳辐射 GHI
- direct_radiation: 直接太阳辐射
- diffuse_radiation: 漫射太阳辐射 DHI
- direct_normal_irradiance: 法向直接辐照度 DNI
- global_tilted_irradiance: 全局倾斜辐照度 GTI
- terrestrial_radiation: 地面太阳辐射
- 以及所有上述变量的瞬时值版本（_instant）

**风速与风向（多层）**
- wind_speed_10m, wind_speed_80m, wind_speed_120m, wind_speed_180m
- wind_direction_10m, wind_direction_80m, wind_direction_120m, wind_direction_180m
- wind_gusts_10m: 10米阵风
- temperature_80m, temperature_120m, temperature_180m

**土壤变量**
- soil_temperature_0cm, soil_temperature_6cm, soil_temperature_18cm, soil_temperature_54cm
- soil_moisture_0_to_1cm, soil_moisture_1_to_3cm, soil_moisture_3_to_9cm, soil_moisture_9_to_27cm, soil_moisture_27_to_81cm

**大气稳定性**
- cape: 对流有效位能
- lifted_index: 抬升指数
- convective_inhibition: 对流抑制
- freezing_level_height: 冻结高度
- boundary_layer_height: 边界层高度

**等压面变量**（1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30 hPa）

### 日变量（Daily Variables）
- temperature_2m_max, temperature_2m_min
- apparent_temperature_max, apparent_temperature_min
- sunrise, sunset, daylight_duration, sunshine_duration
- precipitation_sum, precipitation_hours, precipitation_probability_max
- rain_sum, showers_sum, snowfall_sum
- wind_speed_10m_max, wind_gusts_10m_max, wind_direction_10m_dominant
- shortwave_radiation_sum
- et0_fao_evapotranspiration
- uv_index_max, uv_index_clear_sky_max
- weather_code
- 以及大量平均值、最大值、最小值统计变量

### 当前变量（Current Variables）
- temperature_2m, relative_humidity_2m, apparent_temperature
- is_day, precipitation, rain, showers, snowfall, weather_code
- cloud_cover, pressure_msl, surface_pressure
- wind_speed_10m, wind_direction_10m, wind_gusts_10m

### 15分钟变量（Minutely 15）
- temperature_2m, relative_humidity_2m, dewpoint_2m, apparent_temperature
- precipitation, rain, showers, snowfall, weather_code
- cloud_cover, pressure_msl, surface_pressure
- wind_speed_10m, wind_direction_10m, wind_gusts_10m
- visibility, cape, lightning_potential_index
- is_day, 以及所有辐射变量

---

## 2. 历史天气 API (Historical Weather API)

### URL 模式
```
https://archive-api.open-meteo.com/v1/archive
```

### 特点
- 数据从1940年至今
- 使用ERA5 (0.25°), ERA5-Land (0.1°), ECMWF IFS (9km, 2017年起)
- 分辨率：0.25°或0.1°

### 可用模型
- ECMWF IFS, ECMWF IFS Analysis Long-Window
- ERA5-Seamless, ERA5, ERA5-Land, ERA5-Ensemble
- CERRA（区域再分析）

### 小时变量
与预报API类似，但包括：
- soil_temperature_0_to_7cm, 7_to_28cm, 28_to_100cm, 100_to_255cm
- soil_moisture_0_to_7cm, 7_to_28cm, 28_to_100cm, 100_to_255cm
- wind_speed_100m, wind_direction_100m
- albedo（仅CERRA）, snow_depth_water_equivalent（仅CERRA）

---

## 3. 空气质量 API (Air Quality API)

### URL 模式
```
https://air-quality-api.open-meteo.com/v1/air-quality
```

### 小时变量
**主要污染物**
- pm10: 颗粒物 PM10
- pm2_5: 颗粒物 PM2.5
- carbon_monoxide: 一氧化碳 CO
- carbon_dioxide: 二氧化碳 CO2
- nitrogen_dioxide: 二氧化氮 NO2
- sulphur_dioxide: 二氧化硫 SO2
- ozone: 臭氧 O3
- aerosol_optical_depth: 气溶胶光学厚度
- dust: 沙尘
- ammonia: 氨气 NH3
- methane: 甲烷 CH4
- nitrogen_monoxide: 一氧化氮 NO

**空气质量指数**
- european_aqi: 欧洲AQI
- european_aqi_pm2_5, european_aqi_pm10, european_aqi_no2, european_aqi_o3, european_aqi_so2
- us_aqi: 美国AQI
- us_aqi_pm2_5, us_aqi_pm10, us_aqi_no2, us_aqi_co, us_aqi_o3, us_aqi_so2

**花粉**（仅欧洲）
- alder_pollen: 桤木花粉
- birch_pollen: 桦木花粉
- grass_pollen: 草花粉
- mugwort_pollen: 艾草花粉
- olive_pollen: 橄榄花粉
- ragweed_pollen: 豚草花粉

**其他**
- uv_index, uv_index_clear_sky
- formaldehyde: 甲醛 CH₂O
- glyoxal: 乙二醛 C₂H₂O₂
- non_methane_volatile_organic_compounds: 非甲烷挥发性有机物
- pm10_wildfires: 野火PM10
- peroxyacyl_nitrates: 过氧乙酰硝酸酯 PAN
- secondary_inorganic_aerosol: 次生无机气溶胶
- residential_elementary_carbon: 居住基本碳
- total_elementary_carbon: 总基本碳
- pm2_5_total_organic_matter: PM2.5总有机物
- sea_salt_aerosol: 海盐气溶胶

### 当前变量
- european_aqi, us_aqi
- pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone
- aerosol_optical_depth, dust, uv_index, uv_index_clear_sky
- 所有花粉类型
- ammonia

---

## 4. 海洋天气 API (Marine Weather API)

### URL 模式
```
https://marine-api.open-meteo.com/v1/marine
```

### 可用模型
- MeteoFrance Wave, MeteoFrance Ocean Currents
- DWD EWAM, DWD GWAM
- ECMWF WAM, ECMWF WAM 0.25
- GFS Wave 0.25°, GFS Wave 0.16°
- ERA5-Ocean

### 小时变量
**波浪**
- wave_height, wave_direction, wave_period, wave_peak_period
- wind_wave_height, wind_wave_direction, wind_wave_period, wind_wave_peak_period
- swell_wave_height, swell_wave_direction, swell_wave_period, swell_wave_peak_period
- secondary_swell_wave_height, secondary_swell_wave_period, secondary_swell_wave_direction
- tertiary_swell_wave_height, tertiary_swell_wave_period, tertiary_swell_wave_direction

**海洋**
- sea_level_height: 海平面高度（含潮汐）
- sea_surface_temperature: 海表温度 SST
- ocean_current_velocity: 海流速度
- ocean_current_direction: 海流方向
- inverted_barometer_height: 反气压计高度

### 日变量
- wave_height_max, wave_direction_dominant, wave_period_max
- wind_wave_height_max, wind_wave_direction_dominant, wind_wave_period_max, wind_wave_peak_period_max
- swell_wave_height_max, swell_wave_direction_dominant, swell_wave_period_max, swell_wave_peak_period_max
- sea_level_height_max
- 以及所有小时变量的日统计

### 15分钟变量
- wave_height, wave_direction, wave_period, wave_peak_period
- wind_wave_height, wind_wave_direction, wind_wave_period, wind_wave_peak_period
- swell_wave_height, swell_wave_direction, swell_wave_period, swell_wave_peak_period
- secondary/tertiary swell 变量
- sea_level_height, sea_surface_temperature
- ocean_current_velocity, ocean_current_direction

---

## 5. 气候变迁 API (Climate Change API)

### URL 模式
```
https://climate-api.open-meteo.com/v1/climate
```

### 特点
- 时间范围：1950年至2100年
- 分辨率：10km（降尺度）
- 使用CMIP6气候模型

### 可用模型（7个）
- CMCC_CM2_VHR4
- FGOALS_f3_H
- HiRAM_SIT_HR
- MRI_AGCM3_2_S
- EC_Earth3P_HR
- MPI_ESM1_2_XR
- NICAM16_8S

### 日变量
- temperature_2m_mean, temperature_2m_max, temperature_2m_min
- wind_speed_10m_mean, wind_speed_10m_max
- cloud_cover_mean
- shortwave_radiation_sum
- relative_humidity_2m_mean, relative_humidity_2m_max, relative_humidity_2m_min
- dewpoint_2m_mean, dewpoint_2m_min, dewpoint_2m_max
- precipitation_sum, rain_sum, snowfall_sum
- sea_level_pressure_mean
- soil_moisture_0_to_10cm_mean
- et0_fao_evapotranspiration

---

## 6. 季节性预报 API (Seasonal Forecast API)

### URL 模式
```
https://seasonal-api.open-meteo.com/v1/seasonal
```

### 特点
- ECMWF SEAS5 和 EC46 集合预报
- 分辨率：36km
- 51个集合成员
- 预报时长：最长7个月

### 可用模型
- ECMWF Seasonal Seamless (EC46 + SEAS5), All 51 members
- ECMWF SEAS5, All 51 members
- ECMWF EC46, All 51 members
- ECMWF Seasonal Seamless (EC46 + SEAS5), Ensemble Mean
- ECMWF SEAS5, Ensemble Mean
- ECMWF EC46, Ensemble Mean

### 6小时变量
**基本气象**
- temperature_2m, temperature_2m_6h_max, temperature_2m_6h_min
- dewpoint_2m, relative_humidity_2m, apparent_temperature
- et0_fao_evapotranspiration, vapour_pressure_deficit
- pressure_msl, weather_code

**降水与云**
- precipitation, showers, snowfall, rain
- cloud_cover, sunshine_duration

**波浪**
- wave_height, wave_direction, wave_period, wave_peak_period

**风**
- wind_speed_10m, wind_speed_100m, wind_speed_200m
- wind_direction_10m, wind_direction_100m, wind_direction_200m
- wind_gusts_10m

**海洋与土壤**
- sea_surface_temperature
- soil_temperature_0_to_7cm, 7_to_28cm, 28_to_100cm, 100_to_255cm
- soil_moisture_0_to_7cm, 7_to_28cm, 28_to_100cm, 100_to_255cm

**辐射**
- 所有辐射变量（shortwave, direct, diffuse, DNI, GTI, terrestrial）
- 以及所有瞬时辐射变量

### 日变量
- 温度：min, mean, max
- 露点：min, mean, max
- 相对湿度：min, mean, max
- 表观温度：min, mean, max
- 降水：sum
- 风速：min, mean, max
- 风向：dominant
- 云量：min, mean, max
- 土壤温度和湿度：mean
- 海表温度：mean
- 异常值（anomaly）统计

### 异常预报指数
- temperature_2m_extreme_forecast_index
- temperature_2m_shift_of_tails_10, temperature_2m_shift_of_tails_90
- temperature_2m_anomaly_greater_than_0k, 1k, 2k, lower_than_-1k, -2k
- precipitation_extreme_forecast_index
- precipitation_shift_of_tails_90
- precipitation_anomaly_greater_than_0mm, 10mm, 20mm
- pressure_mean_sea_level_greater_than_0pa
- surface_temperature_anomaly_greater_than_0k

---

## 7. 集合模型 API (Ensemble Models API)

### URL 模式
```
https://ensemble-api.open-meteo.com/v1/ensemble
```

### 特点
- 提供集合平均和集合成员数据
- 支持多个模型的集合预报

---

## 8. 地理编码 API (Geocoding API)

### URL 模式
```
https://geocoding-api.open-meteo.com/v1/search
```

### 参数
- `name`: 搜索词（必填，地点名或邮编）
- `count`: 返回结果数量（可选，默认10，最多100）
- `format`: 输出格式（可选，json或protobuf）
- `language`: 语言（可选，默认en）
- `apikey`: API密钥（仅商业使用需要）
- `countryCode`: ISO-3166-1 alpha2国家代码（可选）

### 响应字段
- id, name, latitude, longitude
- country, country_code
- admin1, admin2, admin3, admin4
- population, elevation
- timezone
- feature_code

---

## 9. 海拔 API (Elevation API)

### URL 模式
```
https://api.open-meteo.com/v1/elevation
```

### 参数
- `latitude`: 纬度数组（必填）
- `longitude`: 经度数组（必填）
- `apikey`: API密钥（仅商业使用需要）

### 特点
- 90米分辨率数字高程模型
- 基于Copernicus DEM 2021 GLO-90
- 一次最多100个坐标

### 响应
```json
{
  "elevation": [38.0]
}
```

---

## 10. 洪水 API (Flood API)

### URL 模式
```
https://flood-api.open-meteo.com/v1/flood
```

### 特点
- 全球河流流量预报
- 分辨率：5km
- 历史数据从1984年起
- 预报最长7个月（默认3个月）

### 日变量
- river_discharge: 河流流量
- river_discharge_mean: 平均河流流量
- river_discharge_median: 中位数河流流量
- river_discharge_max: 最大河流流量
- river_discharge_min: 最小河流流量
- river_discharge_p25: 25百分位河流流量
- river_discharge_p75: 75百分位河流流量
- river_discharge_member_01 到 river_discharge_member_50: 50个集合成员

---

## 11. 卫星辐射 API (Satellite Radiation API)

### URL 模式
```
https://satellite-api.open-meteo.com/v1/satellite-radiation
```

### 特点
- 实时太阳辐照度数据
- 来自多个卫星（不包括北美GOES）
- 高分辨率卫星数据

### 小时变量
- shortwave_radiation: 短波太阳辐射 GHI
- direct_radiation: 直接太阳辐射
- diffuse_radiation: 漫射太阳辐射 DHI
- direct_normal_irradiance: 法向直接辐照度 DNI
- clear_sky_radiation: 晴空辐射（仅DWD MTG）
- global_tilted_irradiance: 全局倾斜辐照度 GTI
- terrestrial_radiation: 地面太阳辐射
- 以及所有上述变量的瞬时值版本

---

## 通用设置参数

### 单位设置
- `temperature_unit`: celsius（默认）, fahrenheit
- `wind_speed_unit`: kmh（默认）, ms, mph, knots
- `precipitation_unit`: mm（默认）, inch
- `timeformat`: iso8601（默认）, unixtime
- `length_unit`: metric（默认）, imperial

### 其他参数
- `past_hours`: 过去小时数
- `forecast_hours`: 预报小时数
- `temporal_resolution_for_hourly_data`: 小时数据的时间分辨率
- `grid_cell_selection`: 网格单元选择

---

## API 响应结构

### 标准响应格式
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "generationtime_ms": 2.5,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 38.0,
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "wind_speed_10m": "km/h"
  },
  "hourly": {
    "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
    "temperature_2m": [5.2, 5.0],
    "wind_speed_10m": [12.5, 13.0]
  },
  "daily_units": {
    "time": "iso8601",
    "temperature_2m_max": "°C"
  },
  "daily": {
    "time": ["2024-01-01"],
    "temperature_2m_max": [8.5]
  },
  "current": {
    "time": "2024-01-01T12:00",
    "temperature_2m": 6.5,
    "wind_speed_10m": 15.2
  }
}
```

---

## 速率限制与使用政策

### 免费使用
- **非商业用途**：完全免费，无需API密钥
- **请求限制**：无严格限制，但建议合理使用
- **数据更新**：每小时更新一次

### 商业使用
- 需要购买商业许可
- 使用专用服务器URL（customer-前缀）
- 需要API密钥（apikey参数）
- 详见定价页面

### 自托管
- 可下载数据自行托管
- 适合高流量应用
- 数据开源可获取

### 数据许可
- 大部分数据基于开放许可
- 部分数据源有特定许可要求
- 详见各API页面的许可说明

### 使用建议
- 合理缓存数据减少请求
- 使用适当的预报天数（不需要16天就用7天）
- 批量请求使用逗号分隔坐标
- 错误处理：检查HTTP状态码和error字段

---

## 错误处理

### 错误响应格式
```json
{
  "error": true,
  "reason": "Latitude must be in range of -90 to 90°. Given: 522.52."
}
```

### 常见HTTP状态码
- 200: 成功
- 400: 参数错误
- 404: 资源不存在
- 500: 服务器错误

---

## 最佳实践

1. **缓存策略**：天气数据每小时更新，建议缓存1小时
2. **错误重试**：遇到5xx错误时指数退避重试
3. **批量请求**：使用坐标列表一次请求多个位置
4. **选择性变量**：只请求需要的变量减少传输
5. **时区处理**：使用timezone参数获取本地时间
6. **单位一致**：在请求中指定单位避免转换

---

## 与现有技能的对比

### 已覆盖
- ✅ 基本天气预报API
- ✅ 历史天气API
- ✅ 空气质量API
- ✅ 主要天气变量
- ✅ 基本参数说明

### 需要补充/扩展
- ❌ 海洋天气API完整参数
- ❌ 气候变迁API（CMIP6模型）
- ❌ 季节性预报API（ECMWF SEAS5/EC46）
- ❌ 集合模型API详细信息
- ❌ 卫星辐射API
- ❌ 洪水API
- ❌ 地理编码API详细参数
- ❌ 海拔API
- ❌ 15分钟预报变量
- ❌ 当前天气变量
- ❌ 完整的模型列表（16个来源）
- ❌ 日变量统计（平均值、最大值、最小值等）
- ❌ 异常预报指数
- ❌ 等压面变量
- ❌ 土壤多层变量
- ❌ 多层风速风向
- ❌ 响应结构详细说明
- ❌ 速率限制和使用政策
- ❌ 错误处理
- ❌ 最佳实践

---

## 总结

Open-Meteo API提供了极其丰富的天气数据服务，包括：
- **11个主要API端点**
- **数百个天气变量**
- **16个天气模型来源**
- **从1940年至2100年的时间范围**
- **从90米到36公里的多种分辨率**
- **完整的集合预报和异常检测**

这是一个功能完整、覆盖广泛的天气数据平台，适合各种应用场景。
