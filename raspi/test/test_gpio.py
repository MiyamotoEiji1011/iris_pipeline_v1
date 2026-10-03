"""
GPIO チェッカー
入力例: 22 H  → GPIO22 を HIGH に
        22 L  → GPIO22 を LOW に
        q     → 終了
"""

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
print("GPIO チェッカー起動。終了: q")
print("入力形式: <GPIO番号> <H|L>  例: 22 H")

active = set()

try:
    while True:
        line = input("> ").strip()
        if line.lower() == "q":
            break

        parts = line.split()
        if len(parts) != 2 or parts[1].upper() not in ("H", "L"):
            print("形式エラー。例: 22 H")
            continue

        try:
            pin = int(parts[0])
        except ValueError:
            print("GPIO番号が不正です")
            continue

        if pin not in active:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            active.add(pin)

        state = GPIO.HIGH if parts[1].upper() == "H" else GPIO.LOW
        GPIO.output(pin, state)
        print(f"GPIO{pin} -> {'HIGH' if state else 'LOW'}")

finally:
    GPIO.cleanup()
    print("GPIO クリーンアップ完了")
