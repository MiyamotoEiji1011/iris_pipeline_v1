"""
温度・リレーデータの CSV 記録モジュール
・月ごとに1ファイル (例: 2026_10.csv)
・ファイルが存在しない場合はヘッダー付きで新規作成
・ファイルが存在する場合は末尾に追記（再起動後も継続可能）
・日ごとの区切りは timestamp 列で管理する
"""

import csv
import os
from datetime import datetime


def _get_headers(units: dict) -> list[str]:
    headers = ["timestamp"]
    for name in units:
        headers += [
            f"({name})銅管部温度[℃]",
            f"({name})吸気部温度[℃]",
            f"({name})制御センサ",
            f"({name})ON設定温度[℃]",
            f"({name})OFF設定温度[℃]",
            f"({name})電磁弁状態(ON/OFF)",
        ]
    return headers


def _get_row(units: dict, now: datetime) -> list:
    row = [now.strftime("%Y-%m-%d %H:%M:%S")]
    for unit in units.values():
        sensor = unit.get("control_sensor", "銅管部温度")
        row += [
            unit["銅管部温度"],
            unit["吸気部温度"],
            sensor,
            unit["temp_on"],
            unit["temp_off"],
            "ON" if unit["relay_state"] else "OFF",
        ]
    return row


def append_csv(units: dict, data_dir: str):
    """
    UNITS の現在状態を月次 CSV ファイルに1行追記する。

    Args:
        units:    UNITS dict
        data_dir: CSVを保存するディレクトリのパス
    """
    now      = datetime.now()
    filename = now.strftime("%Y_%m") + ".csv"
    filepath = os.path.join(data_dir, filename)

    os.makedirs(data_dir, exist_ok=True)

    write_header = not os.path.exists(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(_get_headers(units))
        writer.writerow(_get_row(units, now))
