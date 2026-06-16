# Weather — Free Weather & Forecast Skill

[中文](#中文说明)

A lightweight weather skill using two free, API-key-free services: [wttr.in](https://wttr.in) and [Open-Meteo](https://open-meteo.com). Perfect for AI agents that need quick weather data without managing API credentials.

## Features

- **Zero setup**: No API keys, no accounts, no dependencies beyond `curl`
- **Two data sources**: wttr.in for human-readable output, Open-Meteo for programmatic JSON
- **Flexible output**: One-liners, compact format, full forecasts, PNG images
- **City & airport support**: City names, coordinates, and IATA airport codes
- **Bash script included**: Ready-to-use `references/weather.sh` with Chinese city presets

## Quick Start

### One-liner
```bash
curl -s "wttr.in/Beijing?format=3"
# Output: Beijing: ⛅️ +22°C
```

### Compact format
```bash
curl -s "wttr.in/Tokyo?format=%l:+%c+%t+%h+%w"
# Output: Tokyo: 🌧️ +18°C 85% ↗12km/h
```

### Full forecast
```bash
curl -s "wttr.in/London?T"
```

### As PNG image
```bash
curl -s "wttr.in/Berlin.png" -o /tmp/weather.png
```

## Format Codes

| Code | Meaning | Example |
|------|---------|---------|
| `%c` | Condition icon | ⛅️ |
| `%t` | Temperature | +22°C |
| `%h` | Humidity | 71% |
| `%w` | Wind | ↙5km/h |
| `%l` | Location | London |
| `%m` | Moon phase | 🌒 |

## Query Modifiers

| Modifier | Effect |
|----------|--------|
| `?m` | Metric units (°C, km/h) |
| `?u` | US customary units (°F, mph) |
| `?0` | Current weather only |
| `?1` | Today only |
| `?T` | Plain text (no ANSI colors) |

## Tips

- URL-encode spaces: `wttr.in/New+York`
- Airport IATA codes work: `wttr.in/JFK`, `wttr.in/PEK`
- Chinese city names: `wttr.in/北京`

## Open-Meteo (JSON fallback)

For programmatic use when you need structured data:

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.90&longitude=116.41&current_weather=true"
```

Returns JSON with `temperature`, `windspeed`, `weathercode`, and `time`.

**Weather codes**: 0=Clear, 1-3=Partly cloudy/Overcast, 45-48=Fog, 51-55=Drizzle, 61-65=Rain, 71-75=Snow, 80-82=Showers, 95=Thunderstorm.

Docs: https://open-meteo.com/en/docs

## Included Script

`references/weather.sh` — Bash script with built Chinese city coordinates and weather code descriptions:

```bash
bash references/weather.sh Beijing          # 🌤️ 北京: 晴间多云 25°C 风速 12km/h
bash references/weather.sh Shanghai full    # Full format with details
```

Supported cities: Beijing, Shanghai, Guangzhou, Shenzhen, Hangzhou, Chengdu, Xi'an, Hong Kong, Tokyo.

## Prerequisites

- `curl` (for wttr.in and Open-Meteo)
- `jq` (for the bash script's JSON parsing)
- No API keys required

## Version

1.0.0

---

## 中文说明

# Weather — 免费天气查询 Skill

轻量级天气查询 Skill，基于两个免费、无需 API Key 的服务：[wttr.in](https://wttr.in) 和 [Open-Meteo](https://open-meteo.com)。适合需要快速获取天气数据的 AI Agent，无需管理任何凭据。

## 功能特点

- **零配置**：无需 API Key、无需注册账号、只需 `curl`
- **双数据源**：wttr.in 提供人类可读输出，Open-Meteo 提供结构化 JSON
- **灵活输出**：单行摘要、紧凑格式、完整预报、PNG 图片
- **多种定位方式**：城市名、经纬度坐标、IATA 机场代码
- **附带 Bash 脚本**：`references/weather.sh` 内置中国城市坐标和天气描述

## 快速上手

### 单行天气
```bash
curl -s "wttr.in/北京?format=3"
# 输出: Beijing: ⛅️ +22°C
```

### 紧凑格式
```bash
curl -s "wttr.in/东京?format=%l:+%c+%t+%h+%w"
# 输出: Tokyo: 🌧️ +18°C 85% ↗12km/h
```

### 完整预报
```bash
curl -s "wttr.in/伦敦?T"
```

### 保存为 PNG 图片
```bash
curl -s "wttr.in/柏林.png" -o /tmp/weather.png
```

## 格式化代码

| 代码 | 含义 | 示例 |
|------|------|------|
| `%c` | 天气图标 | ⛅️ |
| `%t` | 温度 | +22°C |
| `%h` | 湿度 | 71% |
| `%w` | 风速风向 | ↙5km/h |
| `%l` | 地点 | London |
| `%m` | 月相 | 🌒 |

## 查询修饰符

| 修饰符 | 效果 |
|--------|------|
| `?m` | 公制单位（°C, km/h） |
| `?u` | 美制单位（°F, mph） |
| `?0` | 仅当前天气 |
| `?1` | 仅今日天气 |
| `?T` | 纯文本（无 ANSI 颜色） |

## 使用技巧

- URL 编码空格：`wttr.in/New+York`
- 支持 IATA 机场代码：`wttr.in/JFK`、`wttr.in/PEK`
- 直接用中文城市名：`wttr.in/北京`

## Open-Meteo（JSON 备用）

需要结构化数据时使用：

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.90&longitude=116.41&current_weather=true"
```

返回 JSON 包含 `temperature`、`windspeed`、`weathercode`、`time`。

**天气代码对照**：0=晴, 1-3=少云/多云/阴, 45-48=雾, 51-55=毛毛雨, 61-65=雨, 71-75=雪, 80-82=阵雨, 95=雷暴。

文档：https://open-meteo.com/en/docs

## 附带脚本

`references/weather.sh` — Bash 脚本，内置中国主要城市坐标和中文天气描述：

```bash
bash references/weather.sh Beijing          # 🌤️ 北京: 晴间多云 25°C 风速 12km/h
bash references/weather.sh Shanghai full    # 完整格式，含温度/天气/风速/更新时间
```

支持城市：北京、上海、广州、深圳、杭州、成都、西安、香港、东京。

## 环境要求

- `curl`（用于 wttr.in 和 Open-Meteo）
- `jq`（Bash 脚本解析 JSON 用）
- 无需任何 API Key

## 版本

1.0.0
