import os

_W1_BASE = "/sys/bus/w1/devices"


def _read_sysfs(device_id: str) -> float | None:
    path = os.path.join(_W1_BASE, device_id, "w1_slave")

    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            lines = f.readlines()
        if not lines[0].strip().endswith("YES"):
            return None
        return float(lines[1].strip().split("t=")[1]) / 1000.0
    except (IndexError, ValueError):
        return None


def read_temp_sensor(sensors: list[dict]) -> list[dict]:
    """
    センサリストの温度を取得する。

    Args:
        sensors: attach_pin.py の GPIO_SENSORS[gpio] の値

    Returns:
        [{"id": "28-xxx", "name": "sensor_A1", "role": "copper", "temp": 38.25}, ...]
        温度取得失敗時は temp が None になる。
    """
    return [
        {
            "id":   s["id"],
            "name": s["name"],
            "role": s["role"],
            "temp": _read_sysfs(s["id"])
        }
        for s in sensors
    ]
