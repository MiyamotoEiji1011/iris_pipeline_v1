# 空調機ユニット定義
#
# ハードウェア設定（固定値・変更時はコード編集が必要）
#   relay_gpio     : 電磁弁を制御するリレーの GPIO ピン番号
#   sensor_gpio    : 温度センサが接続されている GPIO ピン番号
#   sensors        : センサのデバイスID・名称・役割リスト
#
# 運転設定（起動時に process_config.json から反映・実行中も再ロード可）
#   temp_on        : この温度を超えたら電磁弁を開く（ミスト噴射開始）
#   temp_off       : この温度を下回ったら電磁弁を閉じる（ミスト停止）
#   mode           : 制御モード
#                      "auto"   … temp_on/temp_off に基づいて電磁弁を自動制御
#                      "manual" … Web から直接 ON/OFF を指示、自動制御は無効
#   manual_command : 手動モード時の指示値 "ON" / "OFF"
#
# 現在値・状態（実行時に更新）
#   銅管部温度  : 銅管センサの最新温度（float or None）
#   吸気部温度  : 吸気センサの最新温度（float or None）
#   relay_state : リレーの現在状態（True=ON / False=OFF）

UNITS = {
    "A": {
        # ハードウェア設定
        "relay_gpio":  7,
        "sensor_gpio": 5,
        "sensors": [
            {"id": "28-000000ca859a", "name": "sensor_A1", "role": "銅管部温度"},
            {"id": "28-000000c98317", "name": "sensor_A2", "role": "吸気部温度"},
        ],
        # 運転設定（process_config.json から反映）
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        # 現在値・状態（実行時に更新）
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "B": {
        "relay_gpio":  8,
        "sensor_gpio": 6,
        "sensors": [
            {"id": "28-000000c8d3db", "name": "sensor_B1", "role": "銅管部温度"},
            {"id": "28-000000cb8154", "name": "sensor_B2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "C": {
        "relay_gpio":  9,
        "sensor_gpio": 12,
        "sensors": [
            {"id": "28-000000cb9b44", "name": "sensor_C1", "role": "銅管部温度"},
            {"id": "28-000000c9ac5f", "name": "sensor_C2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "D": {
        "relay_gpio":  10,
        "sensor_gpio": 13,
        "sensors": [
            {"id": "28-000000c9f0d5", "name": "sensor_D1", "role": "銅管部温度"},
            {"id": "28-000000cb4364", "name": "sensor_D2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "E": {
        "relay_gpio":  11,
        "sensor_gpio": 16,
        "sensors": [
            {"id": "28-000000caafe7", "name": "sensor_E1", "role": "銅管部温度"},
            {"id": "28-000000c8fb2f", "name": "sensor_E2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "F": {
        "relay_gpio":  22,
        "sensor_gpio": 17,
        "sensors": [
            {"id": "", "name": "sensor_F1", "role": "銅管部温度"},
            {"id": "", "name": "sensor_F2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "G": {
        "relay_gpio":  23,
        "sensor_gpio": 18,
        "sensors": [
            {"id": "", "name": "sensor_G1", "role": "銅管部温度"},
            {"id": "", "name": "sensor_G2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
    "H": {
        "relay_gpio":  24,
        "sensor_gpio": 19,
        "sensors": [
            {"id": "", "name": "sensor_H1", "role": "銅管部温度"},
            {"id": "", "name": "sensor_H2", "role": "吸気部温度"},
        ],
        "temp_on":        None,
        "temp_off":       None,
        "mode":           None,
        "manual_command": "OFF",
        "銅管部温度":   None,
        "吸気部温度":   None,
        "relay_state": False,
    },
}
