#!/usr/bin/env python3
"""
彩云天气 API 签名工具（v2.6 Token + v3 HMAC 签名）

依赖: requests>=2.31, pyyaml>=6.0
安装: uv pip install requests pyyaml

凭据从 credentials.yaml 读取（不上传 Git）

v2.6 API:
  - Host: api.caiyunapp.com
  - Auth: token 参数（简单）
  - 接口: realtime, weather, minutely, hourly, daily, alert

v3 API:
  - Host: singer.caiyunhub.com  ⚠️ 不同 host！
  - Auth: HMAC-SHA256 签名（header）或 token 参数
  - 接口: 生活指数, 空气质量, 台风, 天文, 海洋, 模式预报, 高空, 次季节, 朝晚霞, 高精度温度, 预警, 逆地理
  - ⚠️ 增值服务，需企业套餐

v1 API:
  - Host: api.caiyunapp.com
  - Auth: token 参数
  - 接口: 土壤温湿度, 闪电实况, 生活指数, 次季节, 潮汐, 天文, 卫星, 雷达, 图层
"""

import hashlib
import hmac
import base64
import json
import time
import sys
import os
import urllib.parse

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: uv pip install requests")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: uv pip install pyyaml")
    sys.exit(1)


# ========== 常量 ==========
V26_HOST = "https://api.caiyunapp.com"
V3_HOST = "https://singer.caiyunhub.com"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(SKILL_DIR, "credentials.yaml")


def load_credentials() -> dict:
    """从 credentials.yaml 加载凭据"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found")
        print("请创建 credentials.yaml，格式见 SKILL.md")
        sys.exit(1)
    with open(CREDENTIALS_FILE) as f:
        creds = yaml.safe_load(f)
    caiyun = creds.get("caiyun", {})
    return {
        "app_key": caiyun.get("app_key", ""),
        "app_secret": caiyun.get("app_secret", ""),
        "token": caiyun.get("token", ""),
    }


def generate_v3_signature(method: str, path: str, params: dict, secret: str) -> str:
    """
    生成 v3 HMAC-SHA256 签名
    
    签名原文格式: METHOD\nPATH\nSORTED_QUERY_STRING
    """
    sorted_params = sorted(params.items())
    query_string = "&".join(
        f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params
    )
    signature_string = f"{method.upper()}\n{path}\n{query_string}"
    signature_bytes = hmac.new(
        secret.encode("utf-8"),
        signature_string.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(signature_bytes).decode("utf-8")


def v26_request(endpoint: str, loc: str = "86.213536,41.484522", params: dict = None) -> dict:
    """
    v2.6 Token 请求（简单方式，推荐）
    
    Args:
        endpoint: 接口名 (realtime, weather, minutely, hourly, daily, alert)
        loc: 经度,纬度
        params: 额外参数
    
    Returns:
        API 响应 JSON
    """
    creds = load_credentials()
    url = f"{V26_HOST}/v2.6/{creds['token']}/{loc}/{endpoint}"
    resp = requests.get(url, params=params or {})
    return resp.json()


def v3_request(path: str, params: dict = None, use_token: bool = True) -> dict:
    """
    v3 请求（host: singer.caiyunhub.com）
    
    Args:
        path: API 路径 (如 /v3/lifeindex, /v3/aqi/forecast/station)
        params: 查询参数
        use_token: True=用 token 参数, False=用 HMAC 签名
    
    Returns:
        API 响应 JSON
    """
    creds = load_credentials()
    params = params or {}
    
    if use_token:
        params["token"] = creds["token"]
    else:
        # HMAC 签名方式
        params["app_key"] = creds["app_key"]
        params["timestamp"] = str(int(time.time()))
        signature = generate_v3_signature("GET", path, params, creds["app_secret"])
        params["signature"] = signature
    
    url = f"{V3_HOST}{path}"
    resp = requests.get(url, params=params)
    return resp.json()


def v1_request(endpoint: str, params: dict = None) -> dict:
    """
    v1 请求（如土壤温湿度）
    
    Args:
        endpoint: 接口名 (如 soil)
        params: 查询参数 (需包含 lng, lat)
    
    Returns:
        API 响应 JSON
    """
    creds = load_credentials()
    params = params or {}
    params["token"] = creds["token"]
    url = f"{V26_HOST}/v1/{endpoint}"
    resp = requests.get(url, params=params)
    return resp.json()


# ========== CLI ==========
USAGE = """
彩云天气 API 调用工具

用法:
  v2.6:  python caiyun-v3-signing.py v26 <endpoint> [lon,lat]
         endpoint: realtime | weather | minutely | hourly | daily | alert
         
  v3:    python caiyun-v3-signing.py v3 <path> [lon] [lat]
         path: /v3/lifeindex | /v3/aqi/forecast/station | /v3/typhoon/realtime
               /v3/astro/sun | /v3/astro/moon | /v3/sea/tide | /v3/sea/wave
               /v3/subseasonal | /v3/upper/100m/wind | /v3/glow/location
               /v3/exp/walltapper | /v3/alert/location
               /v3/cartography/reverse-geocoding | /v3/cartography/reverse-admins
               
  v1:    python caiyun-v3-signing.py v1 <endpoint> [lon] [lat]
         endpoint: soil | 12-lightning | ...

示例:
  python caiyun-v3-signing.py v26 weather 86.213536,41.484522
  python caiyun-v3-signing.py v26 realtime
  python caiyun-v3-signing.py v3 /v3/typhoon/realtime
"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit(0)

    version = sys.argv[1]

    if version == "v26":
        endpoint = sys.argv[2]
        loc = sys.argv[3] if len(sys.argv) > 3 else "86.213536,41.484522"
        result = v26_request(endpoint, loc)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif version == "v3":
        path = sys.argv[2]
        lon = sys.argv[3] if len(sys.argv) > 3 else "86.213536"
        lat = sys.argv[4] if len(sys.argv) > 4 else "41.484522"
        result = v3_request(path, {"longitude": lon, "latitude": lat})
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif version == "v1":
        endpoint = sys.argv[2]
        lon = sys.argv[3] if len(sys.argv) > 3 else "86.213536"
        lat = sys.argv[4] if len(sys.argv) > 4 else "41.484522"
        result = v1_request(endpoint, {"lng": lon, "lat": lat})
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"未知版本: {version}，使用 v26、v3 或 v1")
