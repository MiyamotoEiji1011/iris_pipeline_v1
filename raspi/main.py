import RPi.GPIO as GPIO  # type: ignore
import json
import os
import time
from datetime import datetime
from config.units import UNITS
from config.data_config import (
    CONTROL_INTERVAL, CONFIG_POLL_INTERVAL, RECORD_INTERVAL,
    STATUS_PUSH_INTERVAL, DATA_PUSH_INTERVAL,
)
from tools.read_temp_sensor import read_temp_sensor
from tools.write_relay_module import write_relay_module
from tools.write_csv import append_csv
from tools.fetch_process_config import fetch_process_config
from tools.push_status_json import push_status_json
from tools.git_push_data import git_push_data

_PROCESS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/process_config.json")
_DATA_DIR            = os.path.join(os.path.dirname(__file__), "../data")

DAEMON_LED_GPIO = 25

_applied_version: int       = 0
_pending_config:  dict | None = None


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ---------------------------------------------------------------------------
# config 適用
# ---------------------------------------------------------------------------

def _apply_units_config(config: dict, apply_manual: bool = True):
    """
    config dict の内容を UNITS に適用する。
    モード変更時はリレーを安全にOFF（Desired State → Actual State の橋渡し）。

    Args:
        config:       process_config.json の内容
        apply_manual: False の場合、手動モードでも relay を ON しない（起動時用）
    """
    global _applied_version
    for unit_name, unit in UNITS.items():
        if unit_name not in config.get("units", {}):
            continue
        cfg      = config["units"][unit_name]
        new_mode = cfg["mode"]
        old_mode = unit["mode"]

        # モードが変わるときは先にリレーをOFF
        if old_mode is not None and old_mode != new_mode:
            write_relay_module(unit["relay_gpio"], False)
            unit["relay_state"] = False
            log(f"  ユニット{unit_name} モード変更 ({old_mode}→{new_mode}) 強制OFF")

        unit["temp_on"]        = cfg["temp_on"]
        unit["temp_off"]       = cfg["temp_off"]
        unit["mode"]           = cfg["mode"]
        unit["manual_command"] = cfg["manual_command"]

        # 手動モード: manual_command を即時適用（起動時は常にOFF）
        if new_mode == "manual":
            state = (cfg["manual_command"] == "ON") and apply_manual
            write_relay_module(unit["relay_gpio"], state)
            unit["relay_state"] = state
            cmd_str = "ON" if state else "OFF"
            log(f"  ユニット{unit_name} 手動コマンド適用: {cmd_str}")

    _applied_version = config.get("version", _applied_version)
    log(f"config v{_applied_version} 適用完了")


def load_process_config():
    """起動時: ローカルの process_config.json を読み込む（手動コマンドは適用しない）。"""
    with open(_PROCESS_CONFIG_PATH) as f:
        config = json.load(f)
    _apply_units_config(config, apply_manual=False)


def check_and_apply_config():
    """GitHub から設定を取得し、バージョンが新しければ pending_config にセットする。"""
    global _pending_config
    new_config = fetch_process_config()
    if new_config is None:
        return
    if new_config.get("version", 0) > _applied_version:
        _pending_config = new_config
        log(f"新しいconfig検知 v{new_config['version']} → 次の制御サイクルで適用")


# ---------------------------------------------------------------------------
# GPIO
# ---------------------------------------------------------------------------

def cleanup():
    try:
        GPIO.output(DAEMON_LED_GPIO, False)
    except RuntimeError:
        pass
    GPIO.cleanup()
    log("GPIO クリーンアップ完了")


def setup():
    cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DAEMON_LED_GPIO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(DAEMON_LED_GPIO, True)
    log("GPIO セットアップ完了")
    load_process_config()


# ---------------------------------------------------------------------------
# センサ・制御
# ---------------------------------------------------------------------------

def temp_sensor() -> list[dict]:
    log("----温度センサ----")
    results = []
    for unit_name, unit in UNITS.items():
        for r in read_temp_sensor(unit["sensors"]):
            unit[r["role"]] = r["temp"]
            temp_str = f"{r['temp']:.3f} C" if r["temp"] is not None else "読み取り失敗"
            log(f"  ユニット{unit_name}  {r['name']:12s}  {r['role']}  {temp_str}")
            results.append(r)
    return results


def control_units():
    """自動モードは温度閾値で制御。手動モードは pending_config 適用時に処理済みのためスキップ。"""
    log("----電磁弁 制御----")
    for unit_name, unit in UNITS.items():
        if unit["mode"] != "auto":
            log(f"  ユニット{unit_name} 手動操作")
            continue

        temp     = unit["銅管部温度"]
        temp_on  = unit["temp_on"]
        temp_off = unit["temp_off"]

        if temp is None or temp_on is None or temp_off is None:
            log(f"  ユニット{unit_name} データ不足のためスキップ")
            continue

        if temp >= temp_on and not unit["relay_state"]:
            if write_relay_module(unit["relay_gpio"], True):
                unit["relay_state"] = True
            log(f"  ユニット{unit_name} ON  ({temp:.3f}C >= {temp_on}C)")
        elif temp <= temp_off and unit["relay_state"]:
            if write_relay_module(unit["relay_gpio"], False):
                unit["relay_state"] = False
            log(f"  ユニット{unit_name} OFF ({temp:.3f}C <= {temp_off}C)")
        else:
            log(f"  ユニット{unit_name} 保持 ({temp:.3f}C, relay={'ON' if unit['relay_state'] else 'OFF'})")


def record_csv():
    append_csv(UNITS, _DATA_DIR)
    log("CSV 記録完了")


# ---------------------------------------------------------------------------
# メインループ
# ---------------------------------------------------------------------------

def main():
    global _pending_config
    setup()

    last_control     = 0.0
    last_config_poll = 0.0
    last_record      = 0.0
    last_status_push = 0.0
    last_data_push   = 0.0

    try:
        while True:
            now = time.time()

            # ① センサ・制御（CONTROL_INTERVAL）
            if now - last_control >= CONTROL_INTERVAL:
                last_control = now
                temp_sensor()
                control_units()
                # 制御サイクル完了後に pending config を安全に適用
                if _pending_config is not None:
                    _apply_units_config(_pending_config)
                    _pending_config = None

            # ② GitHub 設定確認（CONFIG_POLL_INTERVAL）
            if now - last_config_poll >= CONFIG_POLL_INTERVAL:
                last_config_poll = now
                check_and_apply_config()

            # ③ CSV 記録（RECORD_INTERVAL）
            if now - last_record >= RECORD_INTERVAL:
                last_record = now
                record_csv()

            # ④ status.json 更新（STATUS_PUSH_INTERVAL）
            if now - last_status_push >= STATUS_PUSH_INTERVAL:
                last_status_push = now
                log("----status push----")
                push_status_json(UNITS, _applied_version)

            # ⑤ CSV git push（DATA_PUSH_INTERVAL）
            if now - last_data_push >= DATA_PUSH_INTERVAL:
                last_data_push = now
                log("----git push----")
                git_push_data()

            time.sleep(0.1)

    except KeyboardInterrupt:
        log("停止しました")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
