"""
システム監視デーモン（main.py とは独立して動作）

・NETWORK_LED (GPIO14): ネットワーク接続中=点灯、切断=消灯
・Reset_SW   (GPIO15): 3秒長押しでラズパイを再起動
"""

import os
import socket
import subprocess
import threading
import time
from datetime import datetime

import RPi.GPIO as GPIO  # type: ignore

NETWORK_LED_GPIO = 14
RESET_SW_GPIO    = 15

NET_CHECK_INTERVAL = 10   # ネットワーク確認間隔（秒）
REBOOT_HOLD_SEC    = 3    # リセットSW の長押し判定時間（秒）


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [system] {msg}", flush=True)


# ---------------------------------------------------------------------------
# ネットワーク確認
# ---------------------------------------------------------------------------

def _is_network_available() -> bool:
    """8.8.8.8:53 への TCP 接続でインターネット疎通を確認する。"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(("8.8.8.8", 53))
        sock.close()
        return True
    except OSError:
        return False


def _network_monitor():
    """バックグラウンドスレッド: 定期的にネットワークを確認して LED を制御する。"""
    prev = None
    while True:
        connected = _is_network_available()
        if connected != prev:
            GPIO.output(NETWORK_LED_GPIO, connected)
            log(f"ネットワーク: {'接続中' if connected else '切断'}")
            prev = connected
        time.sleep(NET_CHECK_INTERVAL)


# ---------------------------------------------------------------------------
# リセットスイッチ監視
# ---------------------------------------------------------------------------

def _watch_reset_sw():
    """
    メインスレッドでリセット SW を監視する。
    プルアップ接続（押下で LOW）を前提とする。
    3秒長押しで sudo reboot を実行。
    """
    while True:
        if GPIO.input(RESET_SW_GPIO) == GPIO.LOW:
            log(f"リセットSW 押下検知 ({REBOOT_HOLD_SEC}秒ホールドで再起動)")
            press_start = time.time()
            while GPIO.input(RESET_SW_GPIO) == GPIO.LOW:
                if time.time() - press_start >= REBOOT_HOLD_SEC:
                    log("再起動実行")
                    _cleanup()
                    subprocess.run(["sudo", "reboot"], check=False)
                    return
                time.sleep(0.05)
            log("リセットSW 短押し（無視）")
        time.sleep(0.05)


# ---------------------------------------------------------------------------
# GPIO セットアップ / クリーンアップ
# ---------------------------------------------------------------------------

def _setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(NETWORK_LED_GPIO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(RESET_SW_GPIO,    GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    log("GPIO セットアップ完了")


def _cleanup():
    try:
        GPIO.output(NETWORK_LED_GPIO, False)
    except RuntimeError:
        pass
    GPIO.cleanup()
    log("GPIO クリーンアップ完了")


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------

def main():
    _setup()

    threading.Thread(target=_network_monitor, daemon=True).start()
    log("システム監視開始")

    try:
        _watch_reset_sw()
    except KeyboardInterrupt:
        log("停止しました")
    finally:
        _cleanup()


if __name__ == "__main__":
    main()
