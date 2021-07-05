from datetime import datetime as dt, timedelta, timezone
from typing import Dict, List, Text

from actions.utils.admin_config import get_meeting_duration_in_minutes

WEEK_DAYS_INDEX = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
WEEK_DAYS_SHORT = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

DATE_FORMAT = "%A, %b %d, %Y"
TIME_FORMAT = "%H:%M"

IST_TZINFO = timezone(timedelta(hours=5, minutes=30))

# def suffix(d):
#    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


# def strftime(format, t: dt):
#    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


def get_upcoming_availability(time_slots: Dict, num_days: int):
    today = dt.now(tz=IST_TZINFO)
    weekday = today.weekday()
    upcoming_week_availability = [
        time_slots[WEEK_DAYS_SHORT[(weekday + i) % 7]] for i in range(num_days)
    ]
    return [
        (today + timedelta(days=i)).strftime(DATE_FORMAT)
        for i in range(num_days)
        if upcoming_week_availability[i]
    ]


def format_time_slots_for_date(time_slots: Dict, date: Text):
    day = next(iter(date.split(",", 1)), "")
    week_day = WEEK_DAYS_INDEX.get(day)
    return generate_time_slots_for_range(time_slots[WEEK_DAYS_SHORT[week_day]])


def generate_time_slots_for_range(time_slot_ranges: List):
    time_slots = []
    for range in time_slot_ranges:
        start_dt = dt.strptime(range["start"], TIME_FORMAT)
        end_dt = dt.strptime(range["end"], TIME_FORMAT)
        if end_dt.hour == 0 and end_dt.minute == 0:
            end_dt += timedelta(days=1)
        while start_dt != end_dt:
            slot = start_dt.strftime(TIME_FORMAT)
            if slot not in time_slots:
                time_slots.append(slot)
            start_dt += timedelta(minutes=get_meeting_duration_in_minutes())
    return time_slots


def print_time_slots(time_slots: Dict):
    time_slots_str = ""
    for key, value in time_slots.items():
        if value:
            time_slots_str += f"{str(key).capitalize()}, {', '.join([v['start']+'-'+v['end'] for v in value])}; "
    return time_slots_str
