"""
DS18B20 温度センサ テストコード
接続中の全センサを検出し、3秒ごとに温度を表示する。
"""

from w1thermsensor import W1ThermSensor
import time
from datetime import datetime


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def main():
    log("DS18B20 温度センサ テスト開始。Ctrl+C で停止。")

    # 起動時に接続センサを一覧表示
    sensors = W1ThermSensor.get_available_sensors()
    if not sensors:
        log("センサが見つかりません。配線と /boot/config.txt の dtoverlay=w1-gpio を確認してください。")
        return

    log(f"{len(sensors)} 個のセンサを検出:")
    for sensor in sensors:
        log(f"  ID: {sensor.id}")

    print()

    try:
        while True:
            sensors = W1ThermSensor.get_available_sensors()
            for sensor in sensors:
                try:
                    temp = sensor.get_temperature()
                    log(f"ID: {sensor.id}  {temp:.3f} C")
                except Exception as e:
                    log(f"ID: {sensor.id}  読み取りエラー: {e}")
            print()
            time.sleep(3)

    except KeyboardInterrupt:
        log("停止しました。")


if __name__ == "__main__":
    main()
