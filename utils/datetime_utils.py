from datetime import datetime, timezone, timedelta

# Часовой пояс ZRR
ZRR_TIMEZONE = timezone(timedelta(hours=-2))

def get_zrr_current_time() -> datetime:
    return datetime.now(ZRR_TIMEZONE)

def get_zrr_current_weekday() -> int:
    return get_zrr_current_time().weekday()
