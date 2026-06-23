# QWeather API Setup Guide

## ⚠️ Critical: API Host Requirement (2026+)

**QWeather no longer uses public API endpoints** like `devapi.qweather.com` or `api.qweather.com`. Each developer account has a **unique API Host**.

### What is API Host?
- A unique domain assigned to your account
- Format: `abc1234xyz.def.qweatherapi.com`
- Part of authentication - even with a valid API key, wrong host = 403 error

### How to Find Your API Host
1. Login to https://console.qweather.com
2. Go to **Settings** (设置)
3. Find **API Host** field
4. Copy the full host URL

### How to Use API Host

**Correct request format:**
```bash
curl --compressed "https://YOUR_API_HOST/v7/weather/now?location=86.21,41.48&key=YOUR_KEY&lang=zh"
```

**Example with placeholder:**
```bash
# Replace abc1234xyz.def.qweatherapi.com with YOUR actual API Host
QWEATHER_HOST="abc1234xyz.def.qweatherapi.com"
QWEATHER_KEY="your_api_key_here"

curl --compressed "https://${QWEATHER_HOST}/v7/weather/now?location=86.213536,41.484522&key=${QWEATHER_KEY}&lang=zh"
```

## ⚠️ Critical: Must Use `--compressed` Flag

QWeather returns **gzip-compressed responses** by default. Without `--compressed`, curl will return binary garbage instead of JSON.

**Wrong:**
```bash
curl "https://HOST/v7/weather/now?location=..."  # Returns binary garbage
```

**Correct:**
```bash
curl --compressed "https://HOST/v7/weather/now?location=..."  # Returns valid JSON
```

## Error Codes

### 403 Invalid Host
```json
{
  "error": {
    "status": 403,
    "type": "https://dev.qweather.com/docs/resource/error-code/#invalid-host",
    "title": "Invalid Host",
    "detail": "An invalid or unauthorized API Host."
  }
}
```
**Solution**: Use your unique API Host from console settings, not the old public endpoints.

### 403 Invalid Host (with "不限制" setting)
Even if API Host restriction is set to "no restriction" (不限制), you still need to use your unique API Host. The "no restriction" setting refers to IP/Referer whitelisting, not the API Host itself.

## API Endpoints (After Host is Set)

### Grid Weather (3-5km resolution)
```bash
# Real-time grid weather
curl --compressed "https://${HOST}/v7/grid-weather/now?location=86.213536,41.484522&key=${KEY}&lang=zh"

# Hourly forecast (24h)
curl --compressed "https://${HOST}/v7/grid-weather/24h?location=86.213536,41.484522&key=${KEY}&lang=zh"

# Daily forecast (7d)
curl --compressed "https://${HOST}/v7/grid-weather/7d?location=86.213536,41.484522&key=${KEY}&lang=zh"
```

### City-Level Weather
```bash
# Real-time weather
curl --compressed "https://${HOST}/v7/weather/now?location=86.213536,41.484522&key=${KEY}&lang=zh"

# Hourly forecast
curl --compressed "https://${HOST}/v7/weather/24h?location=86.213536,41.484522&key=${KEY}&lang=zh"

# Daily forecast
curl --compressed "https://${HOST}/v7/weather/7d?location=86.213536,41.484522&key=${KEY}&lang=zh"
```

### Minute-Level Precipitation (China only, 1km)
```bash
curl --compressed "https://${HOST}/v7/minutely/5m?location=86.213536,41.484522&key=${KEY}&lang=zh"
```

### Weather Warnings
```bash
curl --compressed "https://${HOST}/v7/warning/now?location=86.213536,41.484522&key=${KEY}&lang=zh"
```

### Solar Radiation (separately priced: ¥0.003/request)
```bash
curl --compressed "https://${HOST}/v7/solar-radiation/now?location=86.213536,41.484522&key=${KEY}&lang=zh"
```

## Free Tier Limits

- **50,000 requests/month** for weather and basic services
- Farm usage estimate: ~760-8,640 requests/month (well within free tier)
- Solar radiation data: separately priced at ¥0.003/request
- No payment required for basic weather data

## Data Usage Rights

From QWeather Developer License Agreement (Section 2.1):

**Allowed:**
- ✅ Storage, indexing, caching, batch download
- ✅ Create aggregate products (integrate into farm management system)
- ✅ Create derivative products (modify, adapt, translate, arrange)
- ✅ Commercial use (distribute, display, sell internally or to public)

**Restricted:**
- ❌ Cannot resell raw data to third parties
- ❌ Cannot create a competing weather API service
- ❌ Cannot use for dangerous scenarios (aviation, maritime, nuclear, military)
- ⚠️ Must attribute: "数据来源：和风天气" in products using their data

**Availability SLA**: ≥99.5% monthly uptime (Section 6.1)

## Integration with Farm Morning Report

For the super cotton farm morning report:
1. Use QWeather grid API for high-resolution temperature/humidity/wind
2. Use QWeather minute precipitation before irrigation decisions
3. Use Open-Meteo for ET0 data (QWeather doesn't provide ET0)
4. Attribute data source in report footer

## Troubleshooting

### Binary/garbage response
→ Add `--compressed` flag to curl

### 403 Invalid Host
→ Use your unique API Host from console settings

### 403 Forbidden (old endpoints)
→ Stop using `devapi.qweather.com` or `api.qweather.com`, they're deprecated

### Empty response
→ Check location format: must be `longitude,latitude` (not latitude,longitude)

## Verified Credentials (2026-06-22)

```
开发者ID: YOUR_DEVELOPER_ID
API Host: YOUR_API_HOST.qweatherapi.com
凭据ID: YOUR_CREDENTIAL_ID
Key: YOUR_API_KEY
```

**All endpoints tested and working**: weather/now, grid-weather/now, weather/24h, weather/7d, warning/now, solar-radiation/now, indices/3d
