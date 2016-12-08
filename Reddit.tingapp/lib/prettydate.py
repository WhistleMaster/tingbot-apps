from datetime import datetime

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int or type(time) is float:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + "s"
        if second_diff < 120:
            return "a minute"
        if second_diff < 3600:
            return str(second_diff / 60) + "m"
        if second_diff < 7200:
            return "an hour"
        if second_diff < 86400:
            return str(second_diff / 3600) + "h"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return str(day_diff) + "d"
    if day_diff < 31:
        return str(day_diff / 7) + "w"
    if day_diff < 365:
        return str(day_diff / 30) + "mo"
    return str(day_diff / 365) + "y"