from datetime import datetime, timedelta
from pytz import timezone
from typing import Any, Callable, Dict, List, Optional, Text

from actions.utils.admin_config import (
    get_booking_advance_time_minutes,
    get_meeting_duration_in_minutes,
)

WEEK_DAYS_SHORT = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

APPOINTMENT_DATE_FORMAT = "%a, %b %d, %Y"
APPOINTMENT_TIME_FORMAT = "%H:%M"

SERVER_TZINFO = timezone("Asia/Kolkata")


def get_available_dates_for_weekly_slots(
    weekly_slots: Dict,
    num_days: int,
    filter: Optional[Callable[[datetime], bool]] = None,
):
    now = datetime.now(tz=SERVER_TZINFO)
    dates = [now + timedelta(days=i) for i in range(num_days)]
    return [
        d for d in dates if bool(generate_time_slots_for_date(weekly_slots, d, filter))
    ]


def generate_time_slots_for_date(
    weekly_slots: Dict,
    date: Any,
    filter: Optional[Callable[[datetime], bool]] = None,
):
    date_datetime = date
    if isinstance(date, str):
        date_datetime = SERVER_TZINFO.localize(
            datetime.strptime(date, APPOINTMENT_DATE_FORMAT)
        )

    weekday = date_datetime.weekday()

    time_slots = _generate_time_slots_for_ranges(
        weekly_slots[WEEK_DAYS_SHORT[weekday]], date_datetime
    )
    filtered_time_slots = []
    now = datetime.now(tz=SERVER_TZINFO)
    for slot_dt in time_slots:
        is_booking_advance_time_elapsed = now > (
            date_datetime.replace(hour=slot_dt.hour, minute=slot_dt.minute)
            - timedelta(minutes=get_booking_advance_time_minutes())
        )
        if is_booking_advance_time_elapsed:
            continue
        if filter and not filter(slot_dt):
            continue
        filtered_time_slots.append(slot_dt)

    return filtered_time_slots


def _generate_time_slots_for_ranges(time_slot_ranges: List, date_dt: datetime):
    time_slots = []
    for range in time_slot_ranges:
        start_dt = SERVER_TZINFO.localize(
            datetime.strptime(range["start"], APPOINTMENT_TIME_FORMAT).replace(
                year=date_dt.year,
                month=date_dt.month,
                day=date_dt.day,
                microsecond=0,
            )
        )
        end_dt = SERVER_TZINFO.localize(
            datetime.strptime(range["end"], APPOINTMENT_TIME_FORMAT).replace(
                year=date_dt.year,
                month=date_dt.month,
                day=date_dt.day,
                microsecond=0,
            )
        )
        if end_dt.hour == 0 and end_dt.minute == 0:
            end_dt += timedelta(days=1)
        while start_dt != end_dt:
            if start_dt not in time_slots:
                time_slots.append(start_dt)
            start_dt += timedelta(minutes=get_meeting_duration_in_minutes())
    return time_slots


def print_weekly_slots(weekly_slots: Dict, separator: Text = ", "):
    time_slots_str = ""
    for key, value in weekly_slots.items():
        if value:
            time_slots_str += f"{str(key).capitalize()}{separator}{separator.join([v['start']+'-'+v['end'] for v in value])}; "
    return time_slots_str


def format_appointment_date(time: datetime):
    return time.strftime(APPOINTMENT_DATE_FORMAT)


def format_appointment_time(time: datetime):
    return time.strftime(APPOINTMENT_TIME_FORMAT)


def is_empty_weekly_slots(weekly_slots: Dict):
    return all(value == [] for value in weekly_slots.values())
