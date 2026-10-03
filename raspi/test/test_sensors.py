import os

W1_BASE = "/sys/bus/w1/devices"

devices = [d for d in os.listdir(W1_BASE) if d.startswith("28-")]

if not devices:
    print("センサが見つかりません")
else:
    for device_id in devices:
        path = os.path.join(W1_BASE, device_id, "w1_slave")
        try:
            with open(path) as f:
                lines = f.readlines()
            if lines[0].strip().endswith("YES"):
                temp = float(lines[1].strip().split("t=")[1]) / 1000.0
                print(f"{device_id}  {temp:.3f} C")
            else:
                print(f"{device_id}  CRCエラー")
        except Exception as e:
            print(f"{device_id}  エラー: {e}")
