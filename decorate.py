def format_dynamic_duration(seconds: int) -> str:
    if seconds <= 0:
        return "inf"

    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    YEAR = 31536000

    if seconds >= YEAR:
        years = seconds // YEAR
        days = (seconds % YEAR) // DAY
        return f"{years}y {days}d"
    elif seconds >= DAY:
        days = seconds // DAY
        hours = (seconds % DAY) // HOUR
        return f"{days}d {hours}h"
    elif seconds >= HOUR:
        hours = seconds // HOUR
        minutes = (seconds % HOUR) // MINUTE
        return f"{hours}h {minutes}m"
    elif seconds >= MINUTE:
        minutes = seconds // MINUTE
        secs = seconds % MINUTE
        return f"{minutes}m {secs}s"
    else:
        return f"{seconds}s"
