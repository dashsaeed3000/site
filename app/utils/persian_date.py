"""
Persian (Jalali) Date Utility

Provides a reliable Gregorian -> Jalali conversion and Jinja filter
`to_persian_date(date)` used across templates.
"""

from datetime import datetime, date


def _gregorian_to_jalali(gy, gm, gd):
    """Convert Gregorian date to Jalali (Persian) date.

    Algorithm adapted from public domain implementations used widely
    (works for years in a normal modern range).
    Returns (jy, jm, jd).
    """
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_days_in_month[i]
    # leap year adjustment
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053  # 12053 = 33 years * 365 + 8 leap days
    j_day_no = j_day_no % 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 366) // 365
        j_day_no = (j_day_no - 366) % 365

    jm = 0
    jd = 0
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        j_day_no -= 186
        jm = 7 + j_day_no // 30
        jd = 1 + j_day_no % 30

    return jy, jm, jd


def format_persian_date(date_obj, format_str='%Y/%m/%d'):
    """Format a date/datetime to Jalali string.

    Supported placeholders: %Y, %y, %m, %d, %B, %A
    """
    if date_obj is None:
        return ''

    if isinstance(date_obj, datetime):
        dt = date_obj
    elif isinstance(date_obj, date):
        dt = datetime(date_obj.year, date_obj.month, date_obj.day)
    else:
        # Not a date-like object
        return ''

    gy, gm, gd = dt.year, dt.month, dt.day
    jy, jm, jd = _gregorian_to_jalali(gy, gm, gd)

    month_names = [
        '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]

    weekday_names = [
        'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه'
    ]

    result = format_str
    result = result.replace('%Y', f'{jy:04d}')
    result = result.replace('%y', f'{jy % 100:02d}')
    result = result.replace('%m', f'{jm:02d}')
    result = result.replace('%d', f'{jd:02d}')
    result = result.replace('%B', month_names[jm] if 1 <= jm <= 12 else '')

    # weekday: Python's weekday() -> Monday=0 .. Sunday=6
    weekday = dt.weekday()
    result = result.replace('%A', weekday_names[weekday] if 0 <= weekday <= 6 else '')

    return result


def to_persian_date(date_obj):
    """Jinja filter entrypoint: returns YYYY/MM/DD by default."""
    return format_persian_date(date_obj, '%Y/%m/%d')

