import RPi.GPIO as GPIO  # type: ignore


def write_relay_module(gpio: int, state: bool) -> bool:
    """
    指定GPIOのリレーを制御する。

    Args:
        gpio:  GPIO ピン番号
        state: True = ON (HIGH), False = OFF (LOW)

    Returns:
        成功時 True、失敗時 False
    """
    try:
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, GPIO.HIGH if state else GPIO.LOW)
        return True
    except Exception as e:
        print(f"リレー制御エラー GPIO{gpio}: {e}")
        return False
