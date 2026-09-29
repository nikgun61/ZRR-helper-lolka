from datetime import datetime, timedelta, timezone

# Часовой пояс ZRR
ZRR_TIMEZONE = timezone(timedelta(hours=-2))


def get_zrr_current_time() -> datetime:
    return datetime.now(ZRR_TIMEZONE)


def get_zrr_current_weekday() -> int:
    """День недели по времени ZRR: 0 — понедельник, ..., 6 — воскресенье."""
    return get_zrr_current_time().weekday()


def get_previous_weekday(weekday: int) -> int:
    return (weekday - 1) % 7
