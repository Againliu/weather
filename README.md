# 🌤️ Weather — Free Weather & Forecast Skill for AI Agents

[中文](#中文说明)

Give your AI agent instant access to real-time weather data worldwide — **zero API keys, zero accounts, zero cost**. Combines two free, production-grade weather services into a single skill with both human-readable output and structured JSON for programmatic use.

## What Data You Get

| Data Type | Source | Coverage | Granularity |
|-----------|--------|----------|-------------|
| **Current conditions** | wttr.in + Open-Meteo | Global (any city/airport/coordinates) | Real-time |
| **Temperature** | Both | Global | Current + hourly + daily |
| **Humidity** | wttr.in | Global | Current |
| **Wind speed & direction** | Both | Global | Current + hourly |
| **Weather condition** | Both | Global | 15+ condition codes (clear/cloudy/rain/snow/thunderstorm…) |
| **Multi-day forecast** | wttr.in | Global | 1-3 day forecasts |
| **Moon phase** | wttr.in | Global | Current |
| **Precipitation** | Open-Meteo | Global | Hourly mm |
| **Visibility** | Open-Meteo | Global | Hourly km |
| **UV Index** | Open-Meteo | Global | Hourly |
| **Sunrise/Sunset** | Open-Meteo | Global | Daily |

## Why This Skill

- **No setup friction**: No API keys, no OAuth, no rate-limit management — just `curl`
- **Dual-source redundancy**: If wttr.in is down, Open-Meteo works (and vice versa)
- **Two output modes**: Human-readable text for quick answers, structured JSON for data pipelines
- **Global coverage**: Any city name, IATA airport code (JFK, PEK, LHR), or lat/lon coordinates
- **Battle-tested**: Used daily by multiple AI agents in production

## Quick Start

```bash
# Current weather — one line
curl -s "wttr.in/Beijing?format=3"
# → Beijing: ⛅️ +22°C

# Compact with details
curl -s "wttr.in/Tokyo?format=%l:+%c+%t+%h+%w"
# → Tokyo: 🌧️ +18°C 85% ↗12km/h

# Full 3-day forecast (plain text)
curl -s "wttr.in/London?T"

# Save as PNG image
curl -s "wttr.in/Berlin.png" -o /tmp/weather.png

# Structured JSON (for programmatic use)
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.90&longitude=116.41&current_weather=true"
```

## Included Tools

| Tool | Description |
|------|-------------|
| `references/weather.sh` | Bash script with 9 Chinese city presets (Beijing, Shanghai, Guangzhou, Shenzhen, Hangzhou, Chengdu, Xi'an, Hong Kong, Tokyo), Chinese weather descriptions, and simple/full output modes |

## Format Codes Reference

| Code | Meaning | Example |
|------|---------|---------|
| `%c` | Weather condition icon | ⛅️ 🌧️ ❄️ |
| `%t` | Temperature | +22°C |
| `%h` | Humidity | 71% |
| `%w` | Wind speed + direction | ↙5km/h |
| `%l` | Location name | London |
| `%m` | Moon phase | 🌒 |

## Query Modifiers

| Modifier | Effect | Example |
|----------|--------|---------|
| `?m` | Metric units (°C, km/h) | `wttr.in/Paris?m` |
| `?u` | US units (°F, mph) | `wttr.in/NYC?u` |
| `?0` | Current weather only | `wttr.in/Seoul?0` |
| `?1` | Today only (no forecast) | `wttr.in/Bangkok?1` |
| `?T` | Plain text, no ANSI colors | `wttr.in/Berlin?T` |

## Open-Meteo Weather Codes

| Code | Condition |
|------|-----------|
| 0 | ☀️ Clear sky |
| 1–3 | ⛅ Partly cloudy / Overcast |
| 45–48 | 🌫️ Fog |
| 51–55 | 🌦️ Drizzle (light/moderate/dense) |
| 61–65 | 🌧️ Rain (slight/moderate/heavy) |
| 71–75 | ❄️ Snow (slight/moderate/heavy) |
| 80–82 | 🌧️ Rain showers |
| 95 | ⛈️ Thunderstorm |

## Prerequisites

- `curl` — for wttr.in and Open-Meteo API calls
- `jq` — for the included bash script's JSON parsing
- **No API keys required**

## Typical Use Cases

- **Agriculture AI**: Check weather before recommending spray/fertilize operations
- **Travel assistants**: Quick weather lookup for trip planning
- **Monitoring agents**: Periodic weather checks for outdoor equipment
- **Daily briefings**: Include weather in morning summaries

## Version

v1.0.0

---

## 中文说明

# 🌤️ Weather — AI Agent 免费天气查询 Skill

让你的 AI Agent 即时获取全球实时天气数据 — **无需 API Key、无需注册账号、零成本**。整合两个免费、生产级天气服务，同时提供人类可读输出和结构化 JSON 数据。

## 数据能力

| 数据类型 | 数据源 | 覆盖范围 | 精度 |
|---------|--------|---------|------|
| **实时天气状况** | wttr.in + Open-Meteo | 全球（任意城市/机场/坐标） | 实时 |
| **温度** | 双源 | 全球 | 实时 + 逐小时 + 逐日 |
| **湿度** | wttr.in | 全球 | 实时 |
| **风速风向** | 双源 | 全球 | 实时 + 逐小时 |
| **天气状况** | 双源 | 全球 | 15+ 种天气代码（晴/多云/雨/雪/雷暴…） |
| **多日预报** | wttr.in | 全球 | 1-3 天预报 |
| **月相** | wttr.in | 全球 | 实时 |
| **降水量** | Open-Meteo | 全球 | 逐小时 mm |
| **能见度** | Open-Meteo | 全球 | 逐小时 km |
| **紫外线指数** | Open-Meteo | 全球 | 逐小时 |
| **日出日落** | Open-Meteo | 全球 | 逐日 |

## 核心价值

- **零配置门槛**：无需 API Key、无需 OAuth、无需管理限流 — 一个 `curl` 命令搞定
- **双源冗余**：wttr.in 挂了 Open-Meteo 照样用（反之亦然）
- **双模式输出**：人类可读文本用于快速查看，结构化 JSON 用于数据管道
- **全球覆盖**：支持城市名、IATA 机场代码（JFK、PEK、LHR）、经纬度坐标
- **生产验证**：多个 AI Agent 每日实际使用中

## 快速上手

```bash
# 一行拿到当前天气
curl -s "wttr.in/北京?format=3"
# → Beijing: ⛅️ +22°C

# 紧凑格式（含湿度风速）
curl -s "wttr.in/东京?format=%l:+%c+%t+%h+%w"
# → Tokyo: 🌧️ +18°C 85% ↗12km/h

# 完整 3 天预报（纯文本）
curl -s "wttr.in/伦敦?T"

# 保存为 PNG 图片
curl -s "wttr.in/柏林.png" -o /tmp/weather.png

# 结构化 JSON（程序调用）
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.90&longitude=116.41&current_weather=true"
```

## 附带工具

| 工具 | 说明 |
|------|------|
| `references/weather.sh` | Bash 脚本，内置 9 个中国城市坐标（北京/上海/广州/深圳/杭州/成都/西安/香港/东京），中文天气描述，简洁/详细两种输出模式 |

## 格式化代码速查

| 代码 | 含义 | 示例 |
|------|------|------|
| `%c` | 天气图标 | ⛅️ 🌧️ ❄️ |
| `%t` | 温度 | +22°C |
| `%h` | 湿度 | 71% |
| `%w` | 风速+风向 | ↙5km/h |
| `%l` | 地点 | London |
| `%m` | 月相 | 🌒 |

## 查询修饰符

| 修饰符 | 效果 | 示例 |
|--------|------|------|
| `?m` | 公制单位（°C, km/h） | `wttr.in/Paris?m` |
| `?u` | 美制单位（°F, mph） | `wttr.in/NYC?u` |
| `?0` | 仅当前天气 | `wttr.in/Seoul?0` |
| `?1` | 仅今日天气 | `wttr.in/Bangkok?1` |
| `?T` | 纯文本，无 ANSI 颜色 | `wttr.in/Berlin?T` |

## Open-Meteo 天气代码对照

| 代码 | 天气状况 |
|------|---------|
| 0 | ☀️ 晴 |
| 1–3 | ⛅ 少云 / 多云 / 阴 |
| 45–48 | 🌫️ 雾 |
| 51–55 | 🌦️ 毛毛雨（轻/中/浓） |
| 61–65 | 🌧️ 雨（小/中/大） |
| 71–75 | ❄️ 雪（小/中/大） |
| 80–82 | 🌧️ 阵雨 |
| 95 | ⛈️ 雷暴 |

## 环境要求

- `curl` — 用于 wttr.in 和 Open-Meteo API 调用
- `jq` — 附带 Bash 脚本解析 JSON 用
- **无需任何 API Key**

## 典型使用场景

- **农业 AI**：喷洒/施肥作业前检查天气条件
- **出行助手**：行程规划时快速查天气
- **监控 Agent**：定时检查户外设备所在区域天气
- **日报生成**：在晨间摘要中加入天气信息

## 版本

v1.0.0
