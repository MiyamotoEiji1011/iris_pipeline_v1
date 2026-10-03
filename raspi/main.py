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


def control_units():
    """各ユニットの温度に基づいて電磁弁を制御する。手動操作のユニットはスキップ。"""
    log("----電磁弁 制御----")
    for unit_name, unit in UNITS.items():
        if unit["mode"] != "自動操作":
            log(f"  ユニット{unit_name} 手動操作のためスキップ")
            continue

        temp    = unit["銅管部温度"]
        temp_on  = unit["temp_on"]
        temp_off = unit["temp_off"]

        if temp is None or temp_on is None or temp_off is None:
            log(f"  ユニット{unit_name} データ不足のためスキップ")
            continue

        if temp >= temp_on and not unit["relay_state"]:
            result = write_relay_module(unit["relay_gpio"], True)
            if result:
                unit["relay_state"] = True
            log(f"  ユニット{unit_name} ON  ({temp:.3f}C >= {temp_on}C)")

        elif temp <= temp_off and unit["relay_state"]:
            result = write_relay_module(unit["relay_gpio"], False)
            if result:
                unit["relay_state"] = False
            log(f"  ユニット{unit_name} OFF ({temp:.3f}C <= {temp_off}C)")

        else:
            log(f"  ユニット{unit_name} 保持 ({temp:.3f}C, relay={'ON' if unit['relay_state'] else 'OFF'})")


def main():
    setup()

    try:
        temp_sensor()
        control_units()

    finally:
        print(UNITS)
        cleanup()


if __name__ == "__main__":
    main()
