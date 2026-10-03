import RPi.GPIO as GPIO  # type: ignore
import json
import os
import time
from datetime import datetime
from config.units import UNITS
from tools.read_temp_sensor import read_temp_sensor
from tools.write_relay_module import write_relay_module

_PROCESS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/process_config.json")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def load_process_config():
    """process_config.json を読み込み UNITS の運転設定を更新する。"""
    with open(_PROCESS_CONFIG_PATH) as f:
        config = json.load(f)
    for unit_name, unit in UNITS.items():
        if unit_name in config:
            unit["temp_on"]  = config[unit_name]["temp_on"]
            unit["temp_off"] = config[unit_name]["temp_off"]
            unit["mode"]     = config[unit_name]["mode"]
    log("process_config.json をロードしました")


def cleanup():
    GPIO.cleanup()
    log("GPIO クリーンアップ完了")


def setup():
    cleanup()
    GPIO.setmode(GPIO.BCM)
    log("GPIO セットアップ完了")
    load_process_config()


def temp_sensor() -> list[dict]:
    log("----温度センサ----")
    log("読み取り開始")

    results = []
    for unit_name, unit in UNITS.items():
        for r in read_temp_sensor(unit["sensors"]):
            unit[r["role"]] = r["temp"]
            temp_str = f"{r['temp']:.3f} C" if r["temp"] is not None else "読み取り失敗"
            log(f"ユニット{unit_name}  {r['name']:12s}  {r['role']}  {temp_str}")
            results.append(r)

    log("読み取り終了")
    return results


def relay_all(state: bool):
    label = "ON" if state else "OFF"
    log(f"----電磁弁 全{label}----")
    for unit_name, unit in UNITS.items():
        result = write_relay_module(unit["relay_gpio"], state)
        if result:
            unit["relay_state"] = state
        log(f"  ユニット{unit_name} (GPIO{unit['relay_gpio']:02d}) {label} {'OK' if result else 'FAIL'}")
    time.sleep(1)


def main():
    setup()

    try:
        temp_sensor()
        relay_all(True)

    finally:
        print(UNITS)
        cleanup()


if __name__ == "__main__":
    main()
