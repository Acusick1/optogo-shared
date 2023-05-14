from datetime import timedelta
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
