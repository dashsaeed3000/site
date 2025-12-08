"""
Persian (Shamsi) Date Utility
Converts Gregorian dates to Persian dates without external libraries
"""


def gregorian_to_julian_day(year, month, day):
    """Convert Gregorian date to Julian Day Number"""
    if month <= 2:
        year -= 1
        month += 12
    
    a = year // 100
    b = 2 - a + (a // 4)
    
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    
    return int(jd)


def julian_day_to_gregorian(jd):
    """Convert Julian Day Number to Gregorian date"""
    jd = jd + 0.5
    z = int(jd)
    f = jd - z
    
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    
    return year, month, int(day)


def gregorian_to_persian(year, month, day):
    """
    Convert Gregorian date to Persian (Shamsi) date
    
    Args:
        year: Gregorian year
        month: Gregorian month (1-12)
        day: Gregorian day
    
    Returns:
        tuple: (persian_year, persian_month, persian_day)
    """
    jd = gregorian_to_julian_day(year, month, day)
    
    # Calculate Persian date
    # Persian epoch: 226899 (Julian Day Number for 622-03-22)
    persian_epoch = 226899
    
    # Days since Persian epoch
    days_since_epoch = jd - persian_epoch
    
    # Persian year (approximate)
    persian_year = int((days_since_epoch - 0.5) / 365.2422) + 1
    
    # Find exact year by checking
    while True:
        # Calculate days from epoch to start of this Persian year
        years_since_epoch = persian_year - 1
        leap_years = int((years_since_epoch + 2346) / 2820) * 683 + \
                     int(((years_since_epoch + 2346) % 2820) / 128)
        days_to_year_start = 365 * years_since_epoch + leap_years
        
        # Days into current year
        day_of_year = days_since_epoch - days_to_year_start
        
        if day_of_year < 0:
            persian_year -= 1
            continue
        
        # Check if it's a leap year
        is_leap = (persian_year + 2346) % 128 == 0 or \
                  ((persian_year + 2346) % 2820 < 128 and (persian_year + 2346) % 128 < 29)
        
        # Days in Persian year
        days_in_year = 366 if is_leap else 365
        
        if day_of_year < days_in_year:
            break
        persian_year += 1
    
    # Calculate month and day
    if day_of_year < 186:
        persian_month = (day_of_year // 31) + 1
        persian_day = (day_of_year % 31) + 1
    else:
        day_of_year -= 186
        persian_month = (day_of_year // 30) + 7
        persian_day = (day_of_year % 30) + 1
    
    return persian_year, persian_month, persian_day


def format_persian_date(date_obj, format_str='%Y/%m/%d'):
    """
    Format a datetime/date object to Persian date string
    
    Args:
        date_obj: datetime or date object
        format_str: Format string with Persian placeholders
                    %Y: Persian year (4 digits)
                    %y: Persian year (2 digits)
                    %m: Persian month (01-12)
                    %d: Persian day (01-31)
                    %B: Persian month name
                    %A: Persian weekday name
    
    Returns:
        str: Formatted Persian date string
    """
    if date_obj is None:
        return ''
    
    # Get year, month, day from date object
    year = date_obj.year if hasattr(date_obj, 'year') else date_obj.year
    month = date_obj.month if hasattr(date_obj, 'month') else date_obj.month
    day = date_obj.day if hasattr(date_obj, 'day') else date_obj.day
    
    # Convert to Persian
    p_year, p_month, p_day = gregorian_to_persian(year, month, day)
    
    # Persian month names
    month_names = [
        '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    
    # Persian weekday names
    weekday_names = [
        'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه'
    ]
    
    # Replace format placeholders
    result = format_str
    result = result.replace('%Y', f'{p_year:04d}')
    result = result.replace('%y', f'{p_year % 100:02d}')
    result = result.replace('%m', f'{p_month:02d}')
    result = result.replace('%d', f'{p_day:02d}')
    result = result.replace('%B', month_names[p_month] if 1 <= p_month <= 12 else '')
    
    # Calculate weekday (0=Monday, 6=Sunday)
    if hasattr(date_obj, 'weekday'):
        weekday = date_obj.weekday()
    else:
        # Calculate weekday from date
        import datetime
        if isinstance(date_obj, datetime.datetime):
            weekday = date_obj.weekday()
        else:
            weekday = datetime.date(year, month, day).weekday()
    
    result = result.replace('%A', weekday_names[weekday] if 0 <= weekday <= 6 else '')
    
    return result


def to_persian_date(date_obj):
    """
    Convert datetime/date object to Persian date string (default format: YYYY/MM/DD)
    
    Args:
        date_obj: datetime or date object
    
    Returns:
        str: Persian date in format YYYY/MM/DD
    """
    return format_persian_date(date_obj, '%Y/%m/%d')
