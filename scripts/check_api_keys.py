#!/usr/bin/env python3
"""API Key validation script for the multi-source weather skill.

Checks:
  1. QWEATHER_API_KEY environment variable is set and valid
  2. GITHUB_TOKEN environment variable is set (used by report_issue.py)

Exit codes:
  0 — all checks passed (suitable for cron: silent when everything is OK)
  1 — one or more checks failed

Usage:
  python3 check_api_keys.py           # normal output
  python3 check_api_keys.py --quiet   # suppress output when all OK (cron mode)

Only standard-library modules are used (urllib.request, os, sys, json).
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# Collect output lines here. In --quiet mode lines are only flushed when a
# failure is detected, so cron sees no noise when everything is healthy.
_pending_lines = []
_quiet_mode = False

# --- Config ------------------------------------------------------------------

QWEATHER_API_URL = "https://devapi.qweather.com/v7/weather/now"
QWEATHER_TEST_LOCATION = "101010100"  # Beijing — a stable, always-available location
QWEATHER_API_TIMEOUT = 10  # seconds

# --- Helpers -----------------------------------------------------------------


def _print(emoji, message, quiet=False):
    """Buffer a check-result line.

    In non-quiet mode the line is printed immediately.
    In quiet mode the line is buffered; it is only flushed if at least one
    failure exists when the script finishes. This means cron sees no output
    at all when every check passes (exit 0), but failures are still reported.
    """
    line = f"{emoji} {message}"
    if quiet:
        _pending_lines.append(line)
    else:
        print(line)


def _flush_pending():
    """Print all buffered lines (used in quiet mode when failures exist)."""
    for line in _pending_lines:
        print(line)


def check_qweather_key(quiet=False):
    """Verify QWEATHER_API_KEY is set and the key is accepted by the API.

    Returns True on success, False on failure.
    """
    key = os.environ.get("QWEATHER_API_KEY", "").strip()

    if not key:
        _print("❌", "QWEATHER_API_KEY 未设置", quiet)
        return False

    # Key is set — now verify it actually works against the live API.
    params = urllib.parse.urlencode(
        {"location": QWEATHER_TEST_LOCATION, "key": key}
    )
    url = f"{QWEATHER_API_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "check_api_keys/1.0"})
        with urllib.request.urlopen(req, timeout=QWEATHER_API_TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
    except urllib.error.HTTPError as exc:
        _print(
            "❌",
            f"QWEATHER_API_KEY 请求失败: HTTP {exc.code} — {exc.reason}",
            quiet,
        )
        return False
    except urllib.error.URLError as exc:
        _print("❌", f"QWEATHER_API_KEY 请求失败: 网络错误 — {exc.reason}", quiet)
        return False
    except (ValueError, json.JSONDecodeError):
        _print("❌", "QWEATHER_API_KEY 响应解析失败: 返回非 JSON 数据", quiet)
        return False

    code = str(data.get("code", ""))
    if code == "200":
        _print("✅", "QWEATHER_API_KEY 已设置且验证通过", quiet)
        return True

    # Map common QWeather error codes to human-readable hints.
    error_hints = {
        "400": "请求参数错误",
        "401": "认证失败 (key 无效或被禁用)",
        "402": "超过访问配额",
        "403": "无访问权限",
        "404": "查询的数据不存在",
        "429": "请求过于频繁 (限流)",
    }
    hint = error_hints.get(code, f"返回 code={code}")
    _print("❌", f"QWEATHER_API_KEY 验证失败: {hint}", quiet)
    return False


def check_github_token(quiet=False):
    """Verify GITHUB_TOKEN is set (required by report_issue.py).

    Returns True on success, False on failure.
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()

    if not token:
        _print("❌", "GITHUB_TOKEN 未设置 (report_issue.py 需要此变量)", quiet)
        return False

    # We don't make an API call here because:
    #   - GitHub token validation requires an authenticated request
    #   - We want to avoid extra rate-limit consumption
    #   - The mere presence of a non-empty token is sufficient for cron
    #     monitoring purposes. report_issue.py will surface auth errors
    #     at runtime if the token is actually invalid.
    _print("✅", "GITHUB_TOKEN 已设置", quiet)
    return True


# --- Main --------------------------------------------------------------------


def main():
    quiet = "--quiet" in sys.argv or "-q" in sys.argv
    global _quiet_mode
    _quiet_mode = quiet

    results = [
        check_qweather_key(quiet=quiet),
        check_github_token(quiet=quiet),
    ]

    if all(results):
        # Everything OK — in quiet mode stay completely silent (cron-friendly).
        sys.exit(0)
    else:
        # There were failures — flush any buffered lines so the user/cron
        # can see what went wrong, then exit non-zero.
        if quiet:
            _flush_pending()
        sys.exit(1)


if __name__ == "__main__":
    main()
