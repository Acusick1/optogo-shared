from datetime import timedelta, date
import re

PERIOD_MAPPING = {
    "days": "d",
    "hours": "h",
    "minutes": "m",
    "seconds": "s"
}


def time_from_string(v: str):
    """
    Get time data from string: supports period mappings above, including more verbose formats e.g. 1day 6hours 3min
    """
    # TODO: Flip mapping and do one get(startswith) instead of double loop
    out = re.findall(r"((\d+)(\s?[a-z]+))", v)

    args = {}
    for group in out:

        for key, val in PERIOD_MAPPING.items():
            if group[-1].startswith(val):
                args[key] = int(group[1])
                break

    return timedelta(**args)


def minutes_from_string(v: str):

    t = time_from_string(v)
    return t.seconds / 60


def calculate_weekdays(departure_date: date, flexibility: int = 0):
    
    weekdays = []
    for offset in range(-flexibility, flexibility + 1):
        
        day = departure_date + timedelta(days=offset)
        
        #  Adding one to get Sunday as first day (0)
        weekdays.append((day.weekday() + 1) % 7)

    return list(set(weekdays))


from datetime import datetime
def calculate_min_departure_time(arrival_time_str: str, min_stopover_hours: int = 2):
    arrival_time = datetime.strptime(arrival_time_str, '%H:%M')
    min_departure_time = arrival_time + timedelta(hours=min_stopover_hours)
    return min_departure_time.strftime('%H:%M')