"""
リレーチェッカー
1. 各リレーを1個ずつ ON → OFF
2. 全リレーを順番に ON → 順番に OFF
"""

import sys
import os
import time
import RPi.GPIO as GPIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.units import UNITS

ON_SEC  = 1.0  # ON 維持時間（秒）
OFF_SEC = 0.5  # OFF 待機時間（秒）

pins = [(u["relay_gpio"], f"relay_{name}") for name, u in UNITS.items()]

GPIO.setmode(GPIO.BCM)
for pin, _ in pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)


def relay_on(pin, name):
    GPIO.output(pin, GPIO.HIGH)
    print(f"  {name} (GPIO{pin:02d}) ON")


def relay_off(pin, name):
    GPIO.output(pin, GPIO.LOW)
    print(f"  {name} (GPIO{pin:02d}) OFF")


try:
    # --- 1. 個別チェック ---
    print("=== 個別チェック ===")
    for pin, name in pins:
        relay_on(pin, name)
        time.sleep(ON_SEC)
        relay_off(pin, name)
        time.sleep(OFF_SEC)

    time.sleep(1)

    # --- 2. 順番に全ON ---
    print("\n=== 順番に全ON ===")
    for pin, name in pins:
        relay_on(pin, name)
        time.sleep(OFF_SEC)

    time.sleep(1)

    # --- 3. 順番に全OFF ---
    print("\n=== 順番に全OFF ===")
    for pin, name in pins:
        relay_off(pin, name)
        time.sleep(OFF_SEC)

    print("\n完了")

finally:
    GPIO.cleanup()
    print("GPIO クリーンアップ完了")
