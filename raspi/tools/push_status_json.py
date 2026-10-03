"""
status.json を GitHub Contents API 経由で更新するモジュール。
git commit を使わず API で直接ファイルを書き換える。
"""

import base64
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

_OWNER = "MiyamotoEiji1011"
_REPO  = "iris_pipeline_v1"
_PATH  = "data/status.json"
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.json")
_JST = timezone(timedelta(hours=9))


def _load_token() -> str | None:
    try:
        with open(_CONFIG_PATH) as f:
            return json.load(f).get("github_token")
    except Exception:
        return None


def _get_sha(url: str, token: str) -> str | None:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read()).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _build_status(units: dict, applied_version: int) -> dict:
    return {
        "updated_at": datetime.now(_JST).isoformat(timespec="seconds"),
        "device": {
            "applied_config_version": applied_version
        },
        "units": {
            name: {
                "temperature":        unit["銅管部温度"],
                "intake_temperature": unit["吸気部温度"],
                "mode":               unit["mode"],
                "relay_actual":       "ON" if unit["relay_state"] else "OFF",
                "sensor_ok":          unit["銅管部温度"] is not None,
            }
            for name, unit in units.items()
        }
    }


def push_status_json(units: dict, applied_version: int) -> bool:
    """
    UNITS の現在状態を status.json として GitHub に書き込む。

    Args:
        units:           UNITS dict
        applied_version: 現在適用済みの config バージョン

    Returns:
        成功時 True、失敗時 False
    """
    token = _load_token()
    if not token:
        print("[push_status] トークンなし")
        return False

    url = f"https://api.github.com/repos/{_OWNER}/{_REPO}/contents/{_PATH}"

    try:
        sha = _get_sha(url, token)
    except Exception as e:
        print(f"[push_status] sha取得エラー: {e}")
        return False

    status  = _build_status(units, applied_version)
    content = base64.b64encode(
        json.dumps(status, ensure_ascii=False, indent=2).encode()
    ).decode()

    body = {"message": "status: auto update", "content": content}
    if sha:
        body["sha"] = sha

    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req):
            print("[push_status] 更新完了")
            return True
    except urllib.error.HTTPError as e:
        print(f"[push_status] HTTPエラー: {e.code} {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[push_status] エラー: {e}")
        return False
