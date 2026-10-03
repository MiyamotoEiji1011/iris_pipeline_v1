# 空調機ごとの運転設定
# temp_on:  この温度を超えたら電磁弁を開く（ミスト噴射開始）
# temp_off: この温度を下回ったら電磁弁を閉じる（ミスト停止）
# mode:     制御に使用するセンサ "銅管部温度" または "吸気部温度"

PROCESS = {
    "A": {"temp_on": None, "temp_off": None, "mode": None},
    "B": {"temp_on": None, "temp_off": None, "mode": None},
    "C": {"temp_on": None, "temp_off": None, "mode": None},
    "D": {"temp_on": None, "temp_off": None, "mode": None},
    "E": {"temp_on": None, "temp_off": None, "mode": None},
    "F": {"temp_on": None, "temp_off": None, "mode": None},
    "G": {"temp_on": None, "temp_off": None, "mode": None},
    "H": {"temp_on": None, "temp_off": None, "mode": None},
}
