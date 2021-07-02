import json
import re
from typing import Any, Text

from actions.utils.admin_config import get_specialities
from actions.utils.date import WEEK_DAYS_SHORT
from actions.utils.json import get_json_key


def validate_age(age: Text):
    test_str = age and age.strip()
    if test_str and re.search(
        r"^1[0-1][0-9]$|^[1-9][0-9]$|^[0-9]$",
        test_str,
    ):
        return test_str
    return None


def validate_bank_account_ifsc(bank_account_ifsc: Text):
    test_str = bank_account_ifsc and bank_account_ifsc.strip()
    if test_str and re.search(
        r"^[A-Za-z]{4}[a-zA-Z0-9]{7}$",
        test_str,
    ):
        return test_str
    return None


def validate_bank_account_number(bank_account_number: Text):
    test_str = bank_account_number and bank_account_number.strip()
    if test_str and re.search(
        r"^\d{9,18}$",
        test_str,
    ):
        return test_str
    return None


def validate_consulation_fee(fee: Text):
    test_str = fee and fee.strip()
    if test_str and re.search(r"^[1-9][0-9]*50$|^[1-9][0-9]*00$", test_str):
        return test_str
    return None


def validate_description(description: Text):
    test_str = description and description.strip()
    if test_str and len(test_str) <= 200:
        return test_str
    return None


def validate_email(email: Text):
    test_str = email and email.strip()
    if test_str and re.search(
        r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$",
        test_str,
    ):
        return test_str
    return None


def validate_name(name: Text):
    test_str = name and name.strip()
    if test_str and re.search(r"^[a-zA-Z.' ]+$", test_str):
        return test_str
    return None


def validate_phone_number(phone_number: Text):
    test_str = phone_number and phone_number.strip()
    if test_str and re.search(r"^[1-9]\d{9}$", test_str):
        return test_str
    return None


def validate_photo(update: Any):
    update_dict = None
    try:
        if isinstance(update, str):
            update_dict = json.loads(update)
        elif isinstance(update, dict):
            update_dict = update
        else:
            return None
        photo = get_json_key(update_dict, "message.photo") or get_json_key(
            update_dict, "message.reply_to_message.photo"
        )
        return photo[0].get("file_id")
    except Exception:
        pass
    return None


def validate_speciality(speciality: Text):
    test_str = speciality and speciality.strip()
    if test_str and test_str in get_specialities():
        return test_str
    return None


def validate_time_slots(time_slots_str: Text):
    test_str = time_slots_str and time_slots_str.strip()
    if test_str:
        time_slots = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thu": [],
            "fri": [],
            "sat": [],
            "sun": [],
        }
        lines = test_str.split(";")
        if not len(lines):
            return None
        for l in lines:
            slots = l.split(",")
            if not len(slots):
                return None
            weekday = str(slots[0]).strip().lower()
            if not weekday in WEEK_DAYS_SHORT:
                return None
            time_slots[weekday] = []
            for s in slots[1:]:
                matches = re.search(
                    r"^(([01]\d|2[0123]):(00|15|30|45))-(([01]\d|2[0123]):(00|15|30|45))$",
                    s.strip(),
                )
                if not matches:
                    return None

                start_hour = int(matches.group(2))
                start_minute = int(matches.group(3))
                end_hour = int(matches.group(5))
                end_minute = int(matches.group(6))
                # supports midnight 00:00 as the last slot of the day
                if (end_hour < start_hour and (end_hour != 0 or end_minute != 0)) or (
                    (end_hour == start_hour) and (end_minute <= start_minute)
                ):
                    return None
                # overlapping slots are okay
                time_slots[weekday].append(
                    {
                        "start": matches.group(1),
                        "end": matches.group(4),
                    }
                )
        return time_slots
    return None
