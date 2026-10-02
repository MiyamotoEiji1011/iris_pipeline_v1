"""
API LED トグルテスト
GitHub の api/command.json をポーリングし、api_led の値に応じて GPIO27 を切り替える。
"""

import json
import time
import base64
import urllib.request
import urllib.error
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    SIMULATION = False
except ImportError:
    # PC上でのテスト実行用（GPIO未使用）
    SIMULATION = True
    print("[INFO] RPi.GPIO が見つかりません。シミュレーションモードで実行します。")

OWNER        = "MiyamotoEiji1011"
REPO         = "iris_pipeline_v1"
FILE_PATH    = "api/command.json"
RAW_URL      = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/{FILE_PATH}"

LED_PIN      = 27   # GPIO27 = API_LED
POLL_INTERVAL = 3   # 秒


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def fetch_command():
    """GitHub raw URLから command.json を取得して api_led の値を返す。取得失敗時は None。"""
    url = f"{RAW_URL}?t={int(time.time())}"  # キャッシュ回避
    try:
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return bool(data.get("api_led", False))
    except urllib.error.HTTPError as e:
        log(f"HTTPエラー: {e.code}")
    except urllib.error.URLError as e:
        log(f"接続エラー: {e.reason}")
    except (json.JSONDecodeError, KeyError) as e:
        log(f"JSONパースエラー: {e}")
    return None


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

    try:
        while True:
            state = fetch_command()

            if state is None:
                log("コマンド取得失敗。リトライします。")
            elif state != current_state:
                set_led(state)
                current_state = state
                log(f"LED 変更 -> {'ON' if state else 'OFF'}")
            else:
                log(f"変化なし (LED={'ON' if state else 'OFF'})")

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
