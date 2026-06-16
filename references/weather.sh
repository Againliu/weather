#!/bin/bash
# Weather skill - 使用 Open-Meteo API

CITY="${1:-Beijing}"
FORMAT="${2:-simple}"

get_coords() {
    case "$1" in
        beijing|北京) echo "39.90,116.41" ;;
        shanghai|上海) echo "31.23,121.47" ;;
        guangzhou|广州) echo "23.13,113.26" ;;
        shenzhen|深圳) echo "22.54,114.06" ;;
        hangzhou|杭州) echo "30.27,120.15" ;;
        chengdu|成都) echo "30.67,104.07" ;;
        xian|西安) echo "34.34,108.94" ;;
        hongkong|香港) echo "22.32,114.17" ;;
        tokyo|东京) echo "35.68,139.69" ;;
        *) echo "39.90,116.41" ;;
    esac
}

get_city_cn() {
    case "$1" in
        beijing) echo "北京" ;;
        shanghai) echo "上海" ;;
        guangzhou) echo "广州" ;;
        shenzhen) echo "深圳" ;;
        hangzhou) echo "杭州" ;;
        chengdu) echo "成都" ;;
        xian) echo "西安" ;;
        hongkong) echo "香港" ;;
        tokyo) echo "东京" ;;
        *) echo "$1" ;;
    esac
}

get_weather_desc() {
    case "$1" in
        0) echo "晴" ;;
        1) echo "晴间多云" ;;
        2) echo "多云" ;;
        3) echo "阴" ;;
        45|48) echo "雾" ;;
        51|53|55) echo "小雨" ;;
        61|63|65) echo "雨" ;;
        71|73|75) echo "雪" ;;
        80|81|82) echo "阵雨" ;;
        95) echo "雷暴" ;;
        *) echo "多云" ;;
    esac
}

COORDS=$(get_coords "$CITY")
LAT=$(echo "$COORDS" | cut -d',' -f1)
LON=$(echo "$COORDS" | cut -d',' -f2)
CITY_CN=$(get_city_cn "$CITY")

RESULT=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT&longitude=$LON&current_weather=true&timezone=auto" 2>/dev/null)

if [ -z "$RESULT" ]; then
    echo "获取天气失败，请稍后重试"
    exit 1
fi

TEMP=$(echo "$RESULT" | jq -r '.current_weather.temperature')
WIND=$(echo "$RESULT" | jq -r '.current_weather.windspeed')
WCODE=$(echo "$RESULT" | jq -r '.current_weather.weathercode')
TIME=$(echo "$RESULT" | jq -r '.current_weather.time')

WEATHER_DESC=$(get_weather_desc "$WCODE")

case "$FORMAT" in
    simple)
        echo "🌤️ $CITY_CN: $WEATHER_DESC ${TEMP}°C 风速 ${WIND}km/h"
        ;;
    full)
        echo "========== $CITY_CN 天气 =========="
        echo "🌡️ 温度: ${TEMP}°C"
        echo "🌤️ 天气: $WEATHER_DESC"
        echo "💨 风速: ${WIND}km/h"
        echo "🕐 更新时间: $TIME"
        ;;
    *)
        echo "🌤️ $CITY_CN: $WEATHER_DESC ${TEMP}°C"
        ;;
esac
