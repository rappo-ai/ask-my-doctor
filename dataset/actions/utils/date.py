from datetime import datetime as dt, timedelta, timezone
from typing import Dict, List, Text

from actions.utils.admin_config import (
    get_advance_time_slot_minutes,
    get_meeting_duration_in_minutes,
)

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


def filter_available_time_slots(time_slots: List):
    now = dt.now(tz=IST_TZINFO)
    now_datetime = dt.strptime(f"{now.hour}:{now.minute}", "%H:%M")
    new_time_slots = []
    for time_slot in time_slots:
        delta = dt.strptime(time_slot, TIME_FORMAT) - now_datetime
        delta_seconds = delta.total_seconds()
        if (delta_seconds / 60) > get_advance_time_slot_minutes():
            new_time_slots.append(time_slot)
    return new_time_slots


def get_upcoming_availability(weekly_slots: Dict, num_days: int):
    now = dt.now(tz=IST_TZINFO)
    weekday = now.weekday()
    upcoming_week_availability = [
        weekly_slots[WEEK_DAYS_SHORT[(weekday + i) % 7]] for i in range(num_days)
    ]
    if len(upcoming_week_availability) and len(upcoming_week_availability[0]):
        slot_ranges_for_today: List = upcoming_week_availability[0]
        time_slots_for_today: List = generate_time_slots_for_range(
            slot_ranges_for_today
        )
        upcoming_week_availability[0] = filter_available_time_slots(
            time_slots_for_today
        )
    return [
        (now + timedelta(days=i)).strftime(DATE_FORMAT)
        for i in range(num_days)
        if upcoming_week_availability[i]
    ]


def generate_time_slots_for_date(weekly_slots: Dict, date: Text):
    day = next(iter(date.split(",", 1)), "")
    week_day = WEEK_DAYS_INDEX.get(day)

    time_slots = generate_time_slots_for_range(weekly_slots[WEEK_DAYS_SHORT[week_day]])

    date_datetime = dt.strptime(date, DATE_FORMAT)
    if date_datetime.day == dt.now(tz=IST_TZINFO).day:
        time_slots = filter_available_time_slots(time_slots)
    return time_slots


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


def print_time_slots(weekly_slots: Dict):
    time_slots_str = ""
    for key, value in weekly_slots.items():
        if value:
            time_slots_str += f"{str(key).capitalize()}, {', '.join([v['start']+'-'+v['end'] for v in value])}; "
    return time_slots_str
