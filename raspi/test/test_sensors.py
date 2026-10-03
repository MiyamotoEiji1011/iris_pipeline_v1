import json
from tools.read_temp_sensor import read_temp_sensor

with open("config/attach_pin.json") as f:
    GPIO_LIST = [int(k) for k in json.load(f)["gpio_sensors"].keys()]

for gpio in GPIO_LIST:
    for r in read_temp_sensor(gpio):
        temp = f"{r['temp']:.3f} C" if r["temp"] is not None else "失敗"
        print(f"{r['name']}  {r['id']}  {temp}")
