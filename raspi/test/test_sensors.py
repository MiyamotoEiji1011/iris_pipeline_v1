import os
import re

W1_BASE = "/sys/bus/w1/devices"


def get_gpio(device_id: str) -> str:
    """シンボリックリンクのパスから GPIO 番号を取得する"""
    try:
        link = os.readlink(os.path.join(W1_BASE, device_id))
        match = re.search(r'w1-gpio@(\d+)', link)
        return match.group(1) if match else "?"
    except OSError:
        return "?"


devices = [d for d in os.listdir(W1_BASE) if d.startswith("28-")]

if not devices:
    print("センサが見つかりません")
else:
    for device_id in sorted(devices):
        gpio = get_gpio(device_id)
        path = os.path.join(W1_BASE, device_id, "w1_slave")
        try:
            with open(path) as f:
                lines = f.readlines()
            if lines[0].strip().endswith("YES"):
                temp = float(lines[1].strip().split("t=")[1]) / 1000.0
                print(f"GPIO{gpio:>2}  {device_id}  {temp:.3f} C")
            else:
                print(f"GPIO{gpio:>2}  {device_id}  CRCエラー")
        except Exception as e:
            print(f"GPIO{gpio:>2}  {device_id}  エラー: {e}")
