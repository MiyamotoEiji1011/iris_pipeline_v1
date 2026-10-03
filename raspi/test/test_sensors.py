import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.attach_pin import GPIO_SENSORS

W1_BASE = "/sys/bus/w1/devices"

# attach_pin から デバイスID → GPIO の逆引きマップを作成
id_to_gpio = {
    s["id"]: gpio
    for gpio, sensors in GPIO_SENSORS.items()
    for s in sensors
}

devices = sorted(d for d in os.listdir(W1_BASE) if d.startswith("28-"))

if not devices:
    print("センサが見つかりません")
else:
    for device_id in devices:
        gpio = id_to_gpio.get(device_id, "?")
        path = os.path.join(W1_BASE, device_id, "w1_slave")
        try:
            with open(path) as f:
                lines = f.readlines()
            if lines[0].strip().endswith("YES"):
                temp = float(lines[1].strip().split("t=")[1]) / 1000.0
                print(f"GPIO{str(gpio):>2}  {device_id}  {temp:.3f} C")
            else:
                print(f"GPIO{str(gpio):>2}  {device_id}  CRCエラー")
        except Exception as e:
            print(f"GPIO{str(gpio):>2}  {device_id}  エラー: {e}")
