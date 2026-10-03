"""
GitHub から process_config.json を取得するモジュール。
ETag を利用して変更がない場合は None を返す（API レート節約）。
"""

import base64
import json
import os
import urllib.request
import urllib.error

_OWNER = "MiyamotoEiji1011"
_REPO  = "iris_pipeline_v1"
_PATH  = "raspi/config/process_config.json"
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.json")

_etag: str | None = None


def _load_token() -> str | None:
    try:
        with open(_CONFIG_PATH) as f:
            return json.load(f).get("github_token")
    except Exception:
        return None


def fetch_process_config() -> dict | None:
    """
    GitHub から process_config.json を取得する。
    変更なし（304）またはエラー時は None を返す。

    Returns:
        変更があった場合は config dict、それ以外は None
    """
    global _etag
    token = _load_token()
    if not token:
        print("[fetch_config] トークンなし")
        return None

    url = f"https://api.github.com/repos/{_OWNER}/{_REPO}/contents/{_PATH}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if _etag:
        req.add_header("If-None-Match", _etag)

    try:
        with urllib.request.urlopen(req) as res:
            _etag = res.headers.get("ETag")
            data  = json.loads(res.read())
            return json.loads(base64.b64decode(data["content"].replace("\n", "")))
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None
        print(f"[fetch_config] HTTPエラー: {e.code}")
        return None
    except Exception as e:
        print(f"[fetch_config] エラー: {e}")
        return None
