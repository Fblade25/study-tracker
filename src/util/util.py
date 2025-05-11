def calculate_clock_hand_angles(
    seconds: float, minutes: int, hours: int
) -> tuple[float, float, float]:
    """Returns clock hand angles based on time."""
    angle_second = (seconds / 60) * 360
    angle_minute = (minutes / 60) * 360 + angle_second / 60
    angle_hour = (hours / 12) * 360 + angle_minute / 60

    return angle_second, angle_minute, angle_hour
