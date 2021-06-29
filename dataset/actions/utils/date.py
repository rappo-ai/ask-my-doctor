from datetime import date, datetime as dt, timedelta
from typing import List, Text

WEEK_DAYS_INDEX = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

DATE_FORMAT = "%A, %b %d, %Y"
TIME_FORMAT = "%H:%M"

# def suffix(d):
#    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


# def strftime(format, t: dt):
#    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


def get_upcoming_availability(time_slots: List, num_days: int):
    weekday = dt.now().weekday()
    upcoming_week_availability = [
        bool(time_slots[(weekday + i) % 7]) for i in range(num_days)
    ]
    return [
        (date.today() + timedelta(days=i)).strftime(DATE_FORMAT)
        for i in range(num_days)
        if upcoming_week_availability[i]
    ]


def format_time_slots_for_date(week_time_slots: List, date: Text):
    day = next(iter(date.split(",", 1)), "")
    week_day = WEEK_DAYS_INDEX.get(day)
    day_time_slots = []
    if week_day:
        day_time_slots = (week_time_slots[week_day] or "").split(",")
    return day_time_slots
