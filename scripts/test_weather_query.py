#!/usr/bin/env python3
"""
multi-source-weather 完备测试套件

覆盖场景：
1. _http_get 函数各分支（正常 / HTTPError 4xx / HTTPError 429+5xx 重试 / URLError / 其他异常）
2. 参数验证（缺 lat/lon/start/end 报错、不支持的数据类型）
3. Open-Meteo provider（正常响应 / HTTP 错误 / JSON 解析错误 / 缺字段）
4. QWeather provider（无 API Key / 正常响应 / HTTP 错误 / JSON 错误 / code!=200）
5. NASA POWER provider（正常响应 / HTTP 错误 / JSON 错误）
6. URL 构造验证

所有测试均 mock _http_get 和 _report_error，不依赖真实 API、不创建 GitHub issue。

用法：
    python3 test_weather_query.py
    python3 -m unittest test_weather_query -v
"""

import json
import os
import sys
import unittest
from unittest import mock
from pathlib import Path
from urllib.error import HTTPError, URLError
from io import BytesIO

# 添加脚本目录到 path，确保能 import weather_query
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import weather_query
from weather_query import (
    _http_get,
    query_open_meteo,
    query_qweather,
    query_nasa_power,
)


# ──────────────────────────────────────────────
# 辅助：构造 mock 响应
# ──────────────────────────────────────────────

class FakeHTTPResponse:
    """模拟 urllib 的 HTTP 响应对象"""

    def __init__(self, status, body_bytes):
        self.status = status
        self._body = body_bytes

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# ──────────────────────────────────────────────
# 1. _http_get 单元测试
# ──────────────────────────────────────────────

class TestHttpGet(unittest.TestCase):
    """测试 _http_get 函数的各异常分支"""

    @mock.patch("weather_query.urllib.request.urlopen")
    def test_normal_response(self, mock_urlopen):
        """正常 HTTP 200 响应"""
        resp = FakeHTTPResponse(200, b'{"ok": true}')
        mock_urlopen.return_value = resp
        status, body = _http_get("https://example.com/api")
        self.assertEqual(status, 200)
        self.assertEqual(body, '{"ok": true}')

    @mock.patch("weather_query.time.sleep")  # 防止重试时真实 sleep
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_http_error_4xx_no_retry(self, mock_urlopen, mock_sleep):
        """HTTPError 4xx (非 429) → 不重试，直接返回 (code, body)"""
        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/api",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=BytesIO(b'{"error": "not found"}'),
        )
        status, body = _http_get("https://example.com/api")
        self.assertEqual(status, 404)
        self.assertIn("not found", body)
        # 4xx 不应触发重试
        mock_sleep.assert_not_called()
        self.assertEqual(mock_urlopen.call_count, 1)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_http_error_429_retry(self, mock_urlopen, mock_sleep):
        """HTTPError 429 → 重试，最终返回最后一次结果"""
        # 前两次 429，第三次成功
        mock_urlopen.side_effect = [
            HTTPError("https://example.com/api", 429, "Too Many",
                      None, BytesIO(b'{"error":"rate limit"}')),
            HTTPError("https://example.com/api", 429, "Too Many",
                      None, BytesIO(b'{"error":"rate limit"}')),
            FakeHTTPResponse(200, b'{"ok": true}'),
        ]
        status, body = _http_get("https://example.com/api")
        self.assertEqual(status, 200)
        self.assertEqual(body, '{"ok": true}')
        # 应该重试了 2 次
        self.assertEqual(mock_urlopen.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_http_error_500_retry_exhausted(self, mock_urlopen, mock_sleep):
        """HTTPError 5xx → 重试耗尽后返回最后一次的 (code, body)"""

        # 每次调用都创建并 raise 新的 HTTPError（BytesIO 流读一次后为空）
        def raise_503(*args, **kwargs):
            raise HTTPError(
                url="https://example.com/api",
                code=503,
                msg="Service Unavailable",
                hdrs=None,
                fp=BytesIO(b'{"error": "unavailable"}'),
            )

        mock_urlopen.side_effect = raise_503
        status, body = _http_get("https://example.com/api")
        self.assertEqual(status, 503)
        self.assertIn("unavailable", body)
        # 初始 1 次 + 重试 3 次 = 4 次
        self.assertEqual(mock_urlopen.call_count, 4)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_url_error_retry_exhausted(self, mock_urlopen, mock_sleep):
        """URLError → 重试耗尽后抛出 ConnectionError"""
        mock_urlopen.side_effect = URLError("Name or service not known")
        with self.assertRaises(ConnectionError) as ctx:
            _http_get("https://example.com/api")
        self.assertIn("网络请求失败", str(ctx.exception))
        self.assertIn("重试", str(ctx.exception))
        self.assertEqual(mock_urlopen.call_count, 4)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_os_error_retry_exhausted(self, mock_urlopen, mock_sleep):
        """OSError (timeout) → 重试耗尽后抛出 ConnectionError"""
        mock_urlopen.side_effect = OSError("timeout")
        with self.assertRaises(ConnectionError) as ctx:
            _http_get("https://example.com/api")
        self.assertIn("网络请求失败", str(ctx.exception))
        self.assertIn("timeout", str(ctx.exception))

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_other_exception_no_retry(self, mock_urlopen, mock_sleep):
        """非网络类异常 (如 ValueError) → 不重试，直接抛 ConnectionError"""
        mock_urlopen.side_effect = ValueError("unexpected error")
        with self.assertRaises(ConnectionError) as ctx:
            _http_get("https://example.com/api")
        self.assertIn("请求异常", str(ctx.exception))
        self.assertIn("unexpected error", str(ctx.exception))
        # 不应重试
        mock_sleep.assert_not_called()
        self.assertEqual(mock_urlopen.call_count, 1)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_timeout_passed(self, mock_urlopen, mock_sleep):
        """timeout 参数正确传递给 urlopen"""
        resp = FakeHTTPResponse(200, b"{}")
        mock_urlopen.return_value = resp
        _http_get("https://example.com/api", timeout=60)
        call_kwargs = mock_urlopen.call_args
        self.assertEqual(call_kwargs.kwargs.get("timeout"), 60)

    @mock.patch("weather_query.time.sleep")
    @mock.patch("weather_query.urllib.request.urlopen")
    def test_url_error_then_success(self, mock_urlopen, mock_sleep):
        """URLError 第一次失败，重试后成功"""
        mock_urlopen.side_effect = [
            URLError("connection reset"),
            FakeHTTPResponse(200, b'{"ok": true}'),
        ]
        status, body = _http_get("https://example.com/api")
        self.assertEqual(status, 200)
        self.assertEqual(body, '{"ok": true}')
        self.assertEqual(mock_urlopen.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)


# ──────────────────────────────────────────────
# 2. 参数验证测试
# ──────────────────────────────────────────────

class TestParameterValidation(unittest.TestCase):
    """测试各 provider 的参数验证逻辑"""

    def test_open_meteo_historical_missing_start(self):
        """open-meteo historical 缺少 start_date → ValueError"""
        with self.assertRaises(ValueError) as ctx:
            query_open_meteo(39.9, 116.4, "historical", start_date=None, end_date="2026-06-29")
        self.assertIn("start", str(ctx.exception))

    def test_open_meteo_historical_missing_end(self):
        """open-meteo historical 缺少 end_date → ValueError"""
        with self.assertRaises(ValueError) as ctx:
            query_open_meteo(39.9, 116.4, "historical", start_date="2026-06-01", end_date=None)
        self.assertIn("end", str(ctx.exception))

    def test_open_meteo_historical_missing_both(self):
        """open-meteo historical 缺少 start 和 end → ValueError"""
        with self.assertRaises(ValueError) as ctx:
            query_open_meteo(39.9, 116.4, "historical")
        self.assertIn("start", str(ctx.exception))

    def test_open_meteo_unsupported_type(self):
        """open-meteo 不支持的数据类型 → ValueError"""
        with self.assertRaises(ValueError) as ctx:
            query_open_meteo(39.9, 116.4, "invalid_type")
        self.assertIn("不支持", str(ctx.exception))

    def test_qweather_unsupported_type(self):
        """qweather 不支持的数据类型 → ValueError"""
        with self.assertRaises(ValueError) as ctx:
            query_qweather("101010100", "invalid_type", api_key="fake_key")
        self.assertIn("不支持", str(ctx.exception))

    @mock.patch.dict(os.environ, {}, clear=False)
    def test_qweather_no_api_key(self):
        """qweather 无 API Key → 返回 error dict"""
        # 确保 QWEATHER_API_KEY 未设置
        os.environ.pop("QWEATHER_API_KEY", None)
        result = query_qweather("101010100", "current")
        self.assertIn("error", result)
        self.assertIn("QWEATHER_API_KEY", result["error"])


# ──────────────────────────────────────────────
# 3. Open-Meteo provider 测试
# ──────────────────────────────────────────────

class TestQueryOpenMeteo(unittest.TestCase):
    """测试 query_open_meteo 函数"""

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_current_success(self, mock_get, mock_report):
        """current 查询正常响应"""
        mock_get.return_value = (200, json.dumps({
            "current_weather": {
                "temperature": 25.3,
                "windspeed": 10.5,
                "winddirection": 180,
                "weathercode": 3,
                "time": "2026-06-29T14:00",
            },
            "hourly": {
                "time": ["2026-06-29T14:00"],
                "temperature_2m": [25.3],
            },
        }))
        result = query_open_meteo(39.9, 116.4, "current")
        self.assertIn("current_weather", result)
        self.assertEqual(result["current_weather"]["temperature"], 25.3)
        mock_report.assert_not_called()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_forecast_success(self, mock_get, mock_report):
        """forecast 查询正常响应"""
        mock_get.return_value = (200, json.dumps({
            "daily": {
                "time": ["2026-06-29", "2026-06-30"],
                "temperature_2m_max": [30.0, 31.0],
                "temperature_2m_min": [20.0, 21.0],
            },
        }))
        result = query_open_meteo(39.9, 116.4, "forecast")
        self.assertIn("daily", result)
        self.assertEqual(len(result["daily"]["time"]), 2)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_historical_success(self, mock_get, mock_report):
        """historical 查询正常响应"""
        mock_get.return_value = (200, json.dumps({
            "daily": {
                "time": ["2026-06-01", "2026-06-02"],
                "temperature_2m_max": [28.0, 29.0],
                "et0_fao_evapotranspiration": [3.5, 4.0],
            },
        }))
        result = query_open_meteo(39.9, 116.4, "historical",
                                  start_date="2026-06-01", end_date="2026-06-02")
        self.assertIn("daily", result)
        self.assertIn("et0_fao_evapotranspiration", result["daily"])

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_et0_success(self, mock_get, mock_report):
        """et0 查询正常响应"""
        mock_get.return_value = (200, json.dumps({
            "daily": {
                "time": ["2026-06-29"],
                "et0_fao_evapotranspiration": [3.2],
            },
        }))
        result = query_open_meteo(39.9, 116.4, "et0")
        self.assertIn("daily", result)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_soil_success(self, mock_get, mock_report):
        """soil 查询正常响应"""
        mock_get.return_value = (200, json.dumps({
            "hourly": {
                "time": ["2026-06-29T00:00", "2026-06-29T01:00"],
                "soil_temperature_0_to_7cm": [22.0, 22.1],
            },
        }))
        result = query_open_meteo(39.9, 116.4, "soil")
        self.assertIn("hourly", result)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_http_error_status(self, mock_get, mock_report):
        """HTTP 状态码非 200 → 返回 error dict"""
        mock_get.return_value = (500, "Internal Server Error")
        result = query_open_meteo(39.9, 116.4, "current")
        self.assertIn("error", result)
        self.assertIn("HTTP 500", result["error"])
        self.assertIn("url", result)
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_json_parse_error(self, mock_get, mock_report):
        """JSON 解析失败 → 返回 error dict"""
        mock_get.return_value = (200, "<<not json>>")
        result = query_open_meteo(39.9, 116.4, "current")
        self.assertIn("error", result)
        self.assertIn("JSON parse failed", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_missing_current_weather_field(self, mock_get, mock_report):
        """current 响应缺少 current_weather 字段"""
        mock_get.return_value = (200, json.dumps({"hourly": {"time": []}}))
        result = query_open_meteo(39.9, 116.4, "current")
        self.assertIn("error", result)
        self.assertIn("current_weather", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_connection_error_raised(self, mock_get, mock_report):
        """_http_get 抛出 ConnectionError → 向上传播"""
        mock_get.side_effect = ConnectionError("网络请求失败: timeout")
        with self.assertRaises(ConnectionError):
            query_open_meteo(39.9, 116.4, "current")
        mock_report.assert_not_called()


# ──────────────────────────────────────────────
# 4. QWeather provider 测试
# ──────────────────────────────────────────────

class TestQueryQWeather(unittest.TestCase):
    """测试 query_qweather 函数"""

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_current_success(self, mock_get, mock_report):
        """current 查询正常响应 (code=200)"""
        mock_get.return_value = (200, json.dumps({
            "code": "200",
            "now": {
                "temp": "25",
                "humidity": "60",
                "windSpeed": "10",
            },
        }))
        result = query_qweather("101010100", "current", api_key="fake_key")
        self.assertEqual(result["code"], "200")
        self.assertEqual(result["now"]["temp"], "25")
        mock_report.assert_not_called()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_forecast_success(self, mock_get, mock_report):
        """forecast 查询正常响应 (code=200)"""
        mock_get.return_value = (200, json.dumps({
            "code": "200",
            "daily": [
                {"fxDate": "2026-06-29", "tempMax": "30"},
                {"fxDate": "2026-06-30", "tempMax": "31"},
            ],
        }))
        result = query_qweather("101010100", "forecast", api_key="fake_key")
        self.assertEqual(result["code"], "200")
        self.assertEqual(len(result["daily"]), 2)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_warning_success(self, mock_get, mock_report):
        """warning 查询正常响应 (code=200)"""
        mock_get.return_value = (200, json.dumps({
            "code": "200",
            "warning": [
                {"title": "暴雨预警", "type": "rain"},
            ],
        }))
        result = query_qweather("101010100", "warning", api_key="fake_key")
        self.assertEqual(result["code"], "200")

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_code_not_200(self, mock_get, mock_report):
        """QWeather code != 200 → 返回 error dict"""
        mock_get.return_value = (200, json.dumps({
            "code": "401",
            "message": "API key 无效",
        }))
        result = query_qweather("101010100", "current", api_key="bad_key")
        self.assertIn("error", result)
        self.assertIn("401", result["error"])
        self.assertIn("data", result)
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_code_402_rate_limit(self, mock_get, mock_report):
        """QWeather code=402 (超过限频) → 返回 error dict"""
        mock_get.return_value = (200, json.dumps({
            "code": "402",
            "message": "超过访问频次",
        }))
        result = query_qweather("101010100", "current", api_key="fake_key")
        self.assertIn("error", result)
        self.assertIn("402", result["error"])

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_http_error_status(self, mock_get, mock_report):
        """HTTP 状态码非 200 → 返回 error dict"""
        mock_get.return_value = (503, "Service Unavailable")
        result = query_qweather("101010100", "current", api_key="fake_key")
        self.assertIn("error", result)
        self.assertIn("HTTP 503", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_json_parse_error(self, mock_get, mock_report):
        """JSON 解析失败 → 返回 error dict"""
        mock_get.return_value = (200, "{broken json")
        result = query_qweather("101010100", "current", api_key="fake_key")
        self.assertIn("error", result)
        self.assertIn("JSON parse failed", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_connection_error_raised(self, mock_get, mock_report):
        """_http_get 抛出 ConnectionError → 向上传播"""
        mock_get.side_effect = ConnectionError("网络请求失败: DNS error")
        with self.assertRaises(ConnectionError):
            query_qweather("101010100", "current", api_key="fake_key")
        mock_report.assert_not_called()

    @mock.patch.dict(os.environ, {"QWEATHER_API_KEY": "env_key"}, clear=False)
    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_api_key_from_env(self, mock_get, mock_report):
        """API Key 从环境变量读取"""
        mock_get.return_value = (200, json.dumps({"code": "200", "now": {"temp": "20"}}))
        # 不传 api_key，应从环境变量读取
        result = query_qweather("101010100", "current")
        self.assertEqual(result["code"], "200")
        # 验证 URL 中包含 env_key
        call_args = mock_get.call_args[0][0]
        self.assertIn("env_key", call_args)


# ──────────────────────────────────────────────
# 5. NASA POWER provider 测试
# ──────────────────────────────────────────────

class TestQueryNasaPower(unittest.TestCase):
    """测试 query_nasa_power 函数"""

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_normal_success(self, mock_get, mock_report):
        """正常查询响应"""
        mock_get.return_value = (200, json.dumps({
            "properties": {
                "parameter": {
                    "T2M": {
                        "20260601": 25.3,
                        "20260602": 26.0,
                    },
                    "PRECTOTCORR": {
                        "20260601": 0.5,
                        "20260602": 0.0,
                    },
                },
            },
        }))
        result = query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-02")
        self.assertIn("properties", result)
        self.assertIn("parameter", result["properties"])
        self.assertIn("T2M", result["properties"]["parameter"])
        mock_report.assert_not_called()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_custom_parameters(self, mock_get, mock_report):
        """自定义 parameters 参数"""
        mock_get.return_value = (200, json.dumps({"properties": {"parameter": {}}}))
        query_nasa_power(39.9, 116.4, "2026-01-01", "2026-01-31",
                         parameters="T2M,RH2M")
        call_url = mock_get.call_args[0][0]
        self.assertIn("T2M,RH2M", call_url)
        self.assertNotIn("ALLSKY_SFC_SW_DWN", call_url)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_date_format_stripped(self, mock_get, mock_report):
        """日期中的 '-' 被正确去除"""
        mock_get.return_value = (200, json.dumps({"properties": {"parameter": {}}}))
        query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        call_url = mock_get.call_args[0][0]
        # URL 中 start/end 应为 YYYYMMDD 格式
        self.assertIn("20260601", call_url)
        self.assertIn("20260629", call_url)
        self.assertNotIn("2026-06-01", call_url)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_http_error_status(self, mock_get, mock_report):
        """HTTP 状态码非 200 → 返回 error dict"""
        mock_get.return_value = (400, "Bad Request")
        result = query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        self.assertIn("error", result)
        self.assertIn("HTTP 400", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_json_parse_error(self, mock_get, mock_report):
        """JSON 解析失败 → 返回 error dict"""
        mock_get.return_value = (200, "<<<invalid>>>")
        result = query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        self.assertIn("error", result)
        self.assertIn("JSON parse failed", result["error"])
        mock_report.assert_called_once()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_connection_error_raised(self, mock_get, mock_report):
        """_http_get 抛出 ConnectionError → 向上传播"""
        mock_get.side_effect = ConnectionError("网络请求失败: connection refused")
        with self.assertRaises(ConnectionError):
            query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        mock_report.assert_not_called()

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_timeout_60s(self, mock_get, mock_report):
        """NASA POWER 使用 60s 超时"""
        mock_get.return_value = (200, json.dumps({"properties": {"parameter": {}}}))
        query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        # _http_get 的第二个位置参数是 timeout
        call_args = mock_get.call_args
        timeout_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("timeout")
        self.assertEqual(timeout_arg, 60)


# ──────────────────────────────────────────────
# 6. URL 构造验证
# ──────────────────────────────────────────────

class TestUrlConstruction(unittest.TestCase):
    """验证各 provider 构造的 URL 是否正确"""

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_open_meteo_current_url(self, mock_get, mock_report):
        """open-meteo current URL 包含正确参数"""
        mock_get.return_value = (200, json.dumps({"current_weather": {}}))
        query_open_meteo(39.9, 116.4, "current")
        url = mock_get.call_args[0][0]
        self.assertIn("api.open-meteo.com", url)
        self.assertIn("latitude=39.9", url)
        self.assertIn("longitude=116.4", url)
        self.assertIn("current_weather=true", url)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_open_meteo_historical_url(self, mock_get, mock_report):
        """open-meteo historical URL 使用 archive-api 且包含日期"""
        mock_get.return_value = (200, json.dumps({"daily": {}}))
        query_open_meteo(39.9, 116.4, "historical",
                         start_date="2026-06-01", end_date="2026-06-29")
        url = mock_get.call_args[0][0]
        self.assertIn("archive-api.open-meteo.com", url)
        self.assertIn("start_date=2026-06-01", url)
        self.assertIn("end_date=2026-06-29", url)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_qweather_url(self, mock_get, mock_report):
        """qweather URL 包含 location 和 key"""
        mock_get.return_value = (200, json.dumps({"code": "200"}))
        query_qweather("101010100", "current", api_key="test_key_123")
        url = mock_get.call_args[0][0]
        self.assertIn("devapi.qweather.com", url)
        self.assertIn("location=101010100", url)
        self.assertIn("key=test_key_123", url)

    @mock.patch("weather_query._report_error")
    @mock.patch("weather_query._http_get")
    def test_nasa_power_url(self, mock_get, mock_report):
        """nasa-power URL 包含正确参数"""
        mock_get.return_value = (200, json.dumps({"properties": {"parameter": {}}}))
        query_nasa_power(39.9, 116.4, "2026-06-01", "2026-06-29")
        url = mock_get.call_args[0][0]
        self.assertIn("power.larc.nasa.gov", url)
        self.assertIn("longitude=116.4", url)
        self.assertIn("latitude=39.9", url)
        self.assertIn("format=JSON", url)
        self.assertIn("community=AG", url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
