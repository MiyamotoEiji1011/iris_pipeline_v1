from datetime import datetime
from config.attach_pin import GPIO_SENSORS
from tools.read_temp_sensor import read_temp_sensor


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def main():
    log("温度センサ読み取り開始")

    for gpio, sensors in GPIO_SENSORS.items():
        for r in read_temp_sensor(sensors):
            temp = f"{r['temp']:.3f} C" if r["temp"] is not None else "読み取り失敗"
            log(f"GPIO{gpio:02d}  {r['name']:12s}  {r['role']}  {temp}")

    log("完了")


if __name__ == "__main__":
    main()
