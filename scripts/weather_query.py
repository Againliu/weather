#!/usr/bin/env python3
"""
多源天气查询 Python 包装脚本

提供统一的 CLI 接口查询多源气象数据，内置错误处理和 GitHub issue 自动反馈。
当 API 调用失败时，自动调用 report_issue.py 创建 GitHub issue。

支持的数据源：
  - open-meteo  : 全球通用，免费无需 Key（实时/预报/历史/ET0/土壤/辐射）
  - qweather    : 中国首选，需 API Key（实时/预报/预警/分钟级降水）
  - nasa-power  : 农业/能源专用，免费无需 Key（历史遥感数据 1981年至今）

用法示例：
  # Open-Meteo 实时天气
  python3 weather_query.py --provider open-meteo --lat 39.90 --lon 116.41 --type current

  # Open-Meteo 7天预报
  python3 weather_query.py --provider open-meteo --lat 39.90 --lon 116.41 --type forecast

  # Open-Meteo 历史数据（ET0 + 土壤温湿度）
  python3 weather_query.py --provider open-meteo --lat 39.90 --lon 116.41 --type historical --start 2026-06-01 --end 2026-06-29

  # QWeather 实时天气（需设置 QWEATHER_API_KEY 环境变量）
  python3 weather_query.py --provider qweather --location "101010100" --type current

  # NASA POWER 历史数据
  python3 weather_query.py --provider nasa-power --lat 39.90 --lon 116.41 --type historical --start 2026-01-01 --end 2026-06-29

环境变量：
  QWEATHER_API_KEY  — 和风天气 API Key（使用 qweather 时必须）
  GITHUB_TOKEN      — GitHub token（自动反馈 issue 时需要，未设置则跳过）
  ISSUE_AUTO        — 是否自动提交 issue，默认 "1"

输出：JSON 格式
"""

import argparse
import json
import os
import sys
import traceback
import urllib.request
import urllib.error
from datetime import datetime

# 自动反馈模块（懒加载，不影响主流程）
_report_issue = None
def _get_reporter():
    global _report_issue
    if _report_issue is None:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from report_issue import auto_report_issue
            _report_issue = auto_report_issue
        except ImportError:
            _report_issue = None
    return _report_issue


def _report_error(title, error_detail, context):
    """调用自动反馈（如果可用）"""
    reporter = _get_reporter()
    if reporter:
        reporter(title, error_detail, context)


def _http_get(url, timeout=30):
    """发起 HTTP GET 请求，返回 (status_code, body_text) 或抛出异常"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "multi-source-weather/4.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
    except urllib.error.URLError as e:
        raise ConnectionError(f"网络请求失败: {e.reason}")
    except Exception as e:
        raise ConnectionError(f"请求异常: {e}")


# ──────────────────────────────────────────────
# Open-Meteo
# ──────────────────────────────────────────────

def query_open_meteo(lat, lon, data_type, start_date=None, end_date=None):
    """查询 Open-Meteo API"""
    base = "https://api.open-meteo.com/v1/forecast"

    if data_type == "current":
        params = (
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
            f"&timezone=auto&forecast_days=1"
        )
    elif data_type == "forecast":
        params = (
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
            f"&timezone=auto&forecast_days=7"
        )
    elif data_type == "historical":
        if not start_date or not end_date:
            raise ValueError("历史查询需要 --start 和 --end 参数")
        base = "https://archive-api.open-meteo.com/v1/archive"
        params = (
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={start_date}&end_date={end_date}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&et0_fao_evapotranspiration"
            f"&soil_temperature_0_to_7cm,soil_moisture_0_to_7cm"
            f"&timezone=auto"
        )
    elif data_type == "et0":
        params = (
            f"?latitude={lat}&longitude={lon}"
            f"&daily=et0_fao_evapotranspiration"
            f"&timezone=auto&forecast_days=7"
        )
    elif data_type == "soil":
        params = (
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=soil_temperature_0_to_7cm,soil_temperature_7_to_28cm,"
            f"soil_moisture_0_to_7cm,soil_moisture_7_to_28cm"
            f"&timezone=auto&forecast_days=1"
        )
    else:
        raise ValueError(f"不支持的查询类型: {data_type}")

    url = base + params
    status, body = _http_get(url)

    if status != 200:
        _report_error(
            title=f"Open-Meteo API 返回 HTTP {status}",
            error_detail=body[:1000],
            context={"provider": "open-meteo", "url": url, "lat": lat, "lon": lon, "type": data_type},
        )
        return {"error": f"HTTP {status}", "detail": body[:500], "url": url}

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        _report_error(
            title="Open-Meteo API 返回非法 JSON",
            error_detail=f"JSON parse error: {e}\nRaw: {body[:500]}",
            context={"provider": "open-meteo", "url": url, "lat": lat, "lon": lon, "type": data_type},
        )
        return {"error": "JSON parse failed", "detail": str(e), "url": url}

    # 验证关键字段
    if data_type == "current" and "current_weather" not in data:
        _report_error(
            title="Open-Meteo 响应缺少 current_weather 字段",
            error_detail=f"Keys: {list(data.keys())}\nRaw: {body[:500]}",
            context={"provider": "open-meteo", "url": url, "lat": lat, "lon": lon, "type": data_type},
        )
        return {"error": "Missing current_weather field", "data": data}

    return data


# ──────────────────────────────────────────────
# QWeather (和风天气)
# ──────────────────────────────────────────────

def query_qweather(location_id, data_type, api_key=None):
    """查询和风天气 API"""
    if not api_key:
        api_key = os.environ.get("QWEATHER_API_KEY", "")
    if not api_key:
        print("[weather_query] QWEATHER_API_KEY 未设置，无法查询和风天气", file=sys.stderr)
        return {"error": "QWEATHER_API_KEY not set"}

    if data_type == "current":
        url = f"https://devapi.qweather.com/v7/weather/now?location={location_id}&key={api_key}"
    elif data_type == "forecast":
        url = f"https://devapi.qweather.com/v7/weather/7d?location={location_id}&key={api_key}"
    elif data_type == "warning":
        url = f"https://devapi.qweather.com/v7/warning/list?location={location_id}&key={api_key}"
    else:
        raise ValueError(f"和风天气不支持查询类型: {data_type}")

    status, body = _http_get(url)

    if status != 200:
        _report_error(
            title=f"QWeather API 返回 HTTP {status}",
            error_detail=body[:1000],
            context={"provider": "qweather", "url": url, "location": location_id, "type": data_type},
        )
        return {"error": f"HTTP {status}", "detail": body[:500]}

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        _report_error(
            title="QWeather API 返回非法 JSON",
            error_detail=f"JSON parse error: {e}\nRaw: {body[:500]}",
            context={"provider": "qweather", "url": url, "location": location_id, "type": data_type},
        )
        return {"error": "JSON parse failed", "detail": str(e)}

    # QWeather 返回 code 字段，200 = 成功
    code = data.get("code", "")
    if code != "200":
        _report_error(
            title=f"QWeather API 返回错误码: {code}",
            error_detail=f"Response: {body[:1000]}",
            context={"provider": "qweather", "url": url, "location": location_id, "type": data_type, "code": code},
        )
        return {"error": f"QWeather code {code}", "data": data}

    return data


# ──────────────────────────────────────────────
# NASA POWER
# ──────────────────────────────────────────────

def query_nasa_power(lat, lon, start_date, end_date, parameters=None):
    """查询 NASA POWER API（历史遥感数据）"""
    if parameters is None:
        parameters = (
            "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,"
            "ALLSKY_SFC_SW_DWN,"
            "GWETROOT"
        )

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={parameters}"
        f"&community=AG"
        f"&longitude={lon}&latitude={lat}"
        f"&start={start_date.replace('-','')}&end={end_date.replace('-','')}"
        f"&format=JSON"
    )

    status, body = _http_get(url, timeout=60)

    if status != 200:
        _report_error(
            title=f"NASA POWER API 返回 HTTP {status}",
            error_detail=body[:1000],
            context={"provider": "nasa-power", "url": url, "lat": lat, "lon": lon},
        )
        return {"error": f"HTTP {status}", "detail": body[:500]}

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        _report_error(
            title="NASA POWER API 返回非法 JSON",
            error_detail=f"JSON parse error: {e}\nRaw: {body[:500]}",
            context={"provider": "nasa-power", "url": url, "lat": lat, "lon": lon},
        )
        return {"error": "JSON parse failed", "detail": str(e)}

    return data


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="多源天气查询 — 内置错误处理和 GitHub issue 自动反馈"
    )
    parser.add_argument("--provider", required=True,
                        choices=["open-meteo", "qweather", "nasa-power"],
                        help="数据源")
    parser.add_argument("--type", default="current",
                        choices=["current", "forecast", "historical", "et0", "soil", "warning"],
                        help="查询类型")
    parser.add_argument("--lat", type=float, help="纬度")
    parser.add_argument("--lon", type=float, help="经度")
    parser.add_argument("--location", help="和风天气 location ID (如 101010100)")
    parser.add_argument("--start", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--end", help="结束日期 YYYY-MM-DD")
    args = parser.parse_args()

    result = None
    try:
        if args.provider == "open-meteo":
            if args.lat is None or args.lon is None:
                parser.error("open-meteo 需要 --lat 和 --lon")
            result = query_open_meteo(args.lat, args.lon, args.type, args.start, args.end)

        elif args.provider == "qweather":
            if not args.location:
                parser.error("qweather 需要 --location")
            result = query_qweather(args.location, args.type)

        elif args.provider == "nasa-power":
            if args.lat is None or args.lon is None:
                parser.error("nasa-power 需要 --lat 和 --lon")
            if not args.start or not args.end:
                parser.error("nasa-power 需要 --start 和 --end")
            result = query_nasa_power(args.lat, args.lon, args.start, args.end)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ConnectionError as e:
        _report_error(
            title=f"{args.provider} 网络连接失败",
            error_detail=traceback.format_exc(),
            context={"provider": args.provider, "type": args.type, "lat": args.lat, "lon": args.lon},
        )
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        _report_error(
            title=f"{args.provider} 查询异常: {type(e).__name__}",
            error_detail=traceback.format_exc(),
            context={"provider": args.provider, "type": args.type, "lat": args.lat, "lon": args.lon},
        )
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
