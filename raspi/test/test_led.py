"""
API LED トグルテスト
GitHub Contents API + ETag で3秒ポーリングし、api_led の値に応じて GPIO27 を切り替える。
変化がない場合は 304 が返るためレート制限を消費しない。
"""

import json
import os
import time
import base64
import urllib.request
import urllib.error
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    SIMULATION = False
except ImportError:
    SIMULATION = True
    print("[INFO] RPi.GPIO が見つかりません。シミュレーションモードで実行します。")

OWNER         = "MiyamotoEiji1011"
REPO          = "iris_pipeline_v1"
FILE_PATH     = "api/command.json"
API_URL       = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

LED_PIN       = 25  # GPIO27 = API_LED
POLL_INTERVAL = 3   # 秒

_config_path = os.path.join(os.path.dirname(__file__), "config/config.json")
with open(_config_path) as f:
    _config = json.load(f)
GITHUB_TOKEN = _config.get("github_token", "")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def fetch_command(etag: str | None) -> tuple[bool | None, str | None]:
    """
    GitHub Contents API から command.json を取得する。
    Returns: (api_led の値 or None, 新しい ETag or None)
      - 変化なし (304): (None, None)
      - 変化あり (200): (bool, etag)
      - エラー      : (None, None)
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    if etag:
        headers["If-None-Match"] = etag

    try:
        req = urllib.request.Request(API_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            new_etag = res.headers.get("ETag")
            data = json.loads(res.read().decode("utf-8"))
            content = json.loads(base64.b64decode(data["content"]).decode("utf-8"))
            return bool(content.get("api_led", False)), new_etag

    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None, None  # 変化なし
        log(f"HTTPエラー: {e.code}")
    except urllib.error.URLError as e:
        log(f"接続エラー: {e.reason}")
    except (json.JSONDecodeError, KeyError) as e:
        log(f"JSONパースエラー: {e}")

    return None, None


def set_led(state: bool):
    if SIMULATION:
        log(f"[SIMULATION] LED -> {'ON' if state else 'OFF'}")
        return
    GPIO.output(LED_PIN, GPIO.HIGH if state else GPIO.LOW)


def main():
    if not SIMULATION:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

    log("API LED テスト開始。Ctrl+C で停止。")

    current_state = None
    etag = None

    try:
        while True:
            state, new_etag = fetch_command(etag)

            if new_etag is None and state is None:
                # 304 または エラー
                if etag:
                    log("変化なし (304)")
                else:
                    log("コマンド取得失敗。リトライします。")
            else:
                etag = new_etag
                if state != current_state:
                    set_led(state)
                    current_state = state
                    log(f"LED 変更 -> {'ON' if state else 'OFF'}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        log("停止しました。")
    finally:
        if not SIMULATION:
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.cleanup()
            log("GPIO クリーンアップ完了。")


if __name__ == "__main__":
    main()
