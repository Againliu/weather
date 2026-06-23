# 多源气象数据统一接口

> 五大数据平台，自动选择最优源，覆盖全场景气象需求。

## 快速开始

### 1. 安装

```bash
# 复制 skill 目录到 Hermes skills 目录
cp -r multi-source-weather ~/.hermes/skills/
cd ~/.hermes/skills/multi-source-weather

# 创建凭据文件（可选，Open-Meteo 和 NASA POWER 无需凭据）
cp credentials.example.yaml credentials.yaml
# 编辑 credentials.yaml 填入你的 API Key
```

### 2. 获取 API Key

| 平台 | 是否需要 | 获取方式 |
|------|---------|---------|
| Open-Meteo | ❌ 不需要 | 直接使用 |
| NASA POWER | ❌ 不需要 | 直接使用 |
| 和风天气 | ✅ 需要 | https://console.qweather.com 注册 |
| 彩云天气 | ✅ 需要 | https://platform.caiyunapp.com 注册 |
| IBM Weather | ✅ 需要 | https://developer.ibm.com/apis/catalog/weather-data 注册 |

### 3. 使用示例

```bash
# 实时天气（中国最优）
curl --compressed "https://{QWEATHER_HOST}/v7/grid-weather/now?location={LON},{LAT}&key={QWEATHER_KEY}"

# ET0 蒸散量（仅 Open-Meteo）
curl "https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=et0_fao_evapotranspiration_sum&timezone=Asia/Shanghai"

# 机场实测（Ground Truth）
curl "https://api.weather.com/v1/location/ZBAA:9:CN/observations/historical.json?apiKey={IBM_KEY}&units=m&startDate=20260615&endDate=20260615"

# NASA POWER 历史遥感
curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR&latitude=41.48&longitude=86.21&start=20260101&end=20260601&community=ag&format=JSON"
```

## 五平台定位

| 平台 | 定位 | 历史深度 | 费用 |
|------|------|---------|------|
| **Open-Meteo** | 全球通用核心源 | 1940年至今 | 免费无限制 |
| **和风天气** | 中国首选 | 7天 | 免费5万次/月 |
| **彩云天气** | 分钟级降水最优 | 无 | 按量付费 |
| **IBM Weather** | 机场实测 Ground Truth | 90天+ | 免费（限速） |
| **NASA POWER** | 农业/能源专用 | 1981年至今 | 完全免费 |

## 核心能力

- **实时天气**：温度、湿度、风速、降水、云量、气压
- **天气预报**：分钟级降水（2小时）、逐小时（384h）、逐日（16天）、40天次季节
- **历史数据**：模型再分析（1940年+）、机场实测（90天+）、卫星遥感（1981年+）
- **农业数据**：ET0蒸散量、土壤温湿度（5层）、降水累计、日照时数
- **能源数据**：太阳辐射、多高度风速、云量、温度
- **空气质量**：PM2.5/PM10/O3/NO2/SO2/CO、AQI指数
- **灾害预警**：气象预警、分钟级降水预警、台风路径、洪水/河流
- **预报验证**：基于机场实测的预报准确率评估

## 文件结构

```
multi-source-weather/
├── SKILL.md                          # 完整使用文档（必须通读）
├── credentials.yaml                  # 凭据配置（不上传Git）
├── credentials.example.yaml          # 凭据模板
├── README.md                         # 本文件
├── references/
│   ├── qweather-api.md               # 和风天气 API 参考
│   ├── caiyun-api.md                 # 彩云天气 API 参考
│   ├── open-meteo-api.md             # Open-Meteo API 参考
│   ├── ibm-weather-api.md            # IBM Weather API 参考
│   ├── nasa-power-api.md             # NASA POWER API 参考
│   ├── caiyun-v3-signing.py          # 彩云天气 v3 签名工具
│   ├── qweather-api-setup.md         # 和风天气接入配置
│   ├── provider-comparison.md        # 五平台详细对比表
│   ├── accuracy-validation.md        # 五源数据准确性验证报告
│   └── cma-data-source.md            # 中国气象局数据源调研
└── scripts/
    ├── daily_collect.py              # 每日数据采集脚本
    └── validate_forecasts.py         # 预报准确率验证脚本
```

## 数据验证方法论

本 skill 使用 **IBM Weather（机场METAR实测数据）** 作为 Ground Truth 基准，验证各平台预报准确率：

1. 每日采集各平台预报数据（day+1, day+3, day+7）
2. 同时采集 IBM Weather 机场实测数据
3. 7天后对比预报值 vs 实测值
4. 计算 MAE、RMSE，按平台、指标、提前天数统计准确率

详见 `references/accuracy-validation.md`

## 注意事项

- **凭据安全**：`credentials.yaml` 已加入 `.gitignore`，不上传 Git
- **坐标顺序**：各平台不同，详见 SKILL.md 的 Common Pitfalls
- **和风天气**：必须加 `--compressed`，必须用专属 API Host
- **彩云天气**：湿度是 0-1 小数，气压是 Pa，需转换
- **NASA POWER**：最新数据有 2-3 天延迟，缺失值返回 -999.0
- **Open-Meteo Archive**：不是实测，是 ERA5 再分析，不能作为 Ground Truth

## 许可证

MIT License
