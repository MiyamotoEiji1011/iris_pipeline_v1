from config.attach_pin import GPIO_SENSORS
from tools.read_temp_sensor import read_temp_sensor

for gpio, sensors in GPIO_SENSORS.items():
    for r in read_temp_sensor(sensors):
        temp = f"{r['temp']:.3f} C" if r["temp"] is not None else "失敗"
        print(f"{r['name']}  {r['id']}  {temp}")
