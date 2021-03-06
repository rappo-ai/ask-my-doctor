import json
import logging
import re
from typing import Any, Dict, List, Text, Tuple

from actions.utils.admin_config import get_specialities
from actions.utils.date import WEEK_DAYS_SHORT
from actions.utils.json import get_json_key
from actions.utils.telegram import get_bot_token

logger = logging.getLogger(__name__)


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


def validate_email(email: Text, domain: Text = None):
    test_str = email and email.strip()
    if test_str and re.search(
        r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$",
        test_str,
    ):
        if domain:
            email_components = test_str.split("@", 2)
            email_domain = len(email_components) == 2 and email_components[1]
            if email_domain != domain:
                return None
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


def resize_photo(photo: Dict, target_size: Tuple[int, int], target_chat_id):
    original_file_id = photo.get("file_id")
    if target_size[0] == photo.get("width") and target_size[1] == photo.get("height"):
        return original_file_id

    from io import BytesIO
    from PIL import Image
    from telebot import TeleBot

    def crop_resize(image: Image, size, ratio):
        # crop to ratio, center
        w, h = image.size
        if w > ratio * h:  # width is larger then necessary
            x, y = (w - ratio * h) // 2, 0
        else:  # ratio*height >= width (height is larger)
            x, y = 0, (h - w / ratio) // 2
        image = image.crop((x, y, w - x, h - y))

        # resize
        if image.size > size:  # don't stretch smaller images
            image.thumbnail(size=size, resample=Image.BICUBIC, reducing_gap=None)
        return image

    bot_token = get_bot_token()
    telebot = TeleBot(bot_token)
    file = telebot.get_file(original_file_id)
    file_content = telebot.download_file(file.file_path)
    file_content_bytesio = BytesIO(file_content)
    image = Image.open(file_content_bytesio)
    resized_image = crop_resize(
        image,
        target_size,
        1.0,
    )
    send_photo_response = telebot.send_photo(
        chat_id=target_chat_id,
        photo=resized_image,
        caption=f"The photo has been cropped and resized to {target_size[0]} px by {target_size[1]} px.",
    )
    resized_photos = send_photo_response.photo
    resized_photo = resized_photos[len(resized_photos) - 1]
    return resized_photo.file_id


def validate_photo(
    update: Any,
    min_size: Tuple[int, int] = None,
    target_size: Tuple[int, int] = None,
    target_chat_id: Text = None,
):
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
        original_photo = photo[len(photo) - 1]
        if min_size and (
            original_photo.get("width") < min_size[0]
            or original_photo.get("height") < min_size[1]
        ):
            return None

        resized_photo_id = resize_photo(original_photo, target_size, target_chat_id)
        return resized_photo_id
    except Exception as e:
        logger.error(e)
    return None


def validate_speciality(speciality: Text):
    test_str = speciality and speciality.strip()
    if test_str and test_str in get_specialities():
        return test_str
    return None


def validate_time_slots(time_slots_str: Text):
    def slot_start_value(slot):
        return slot["start_hour"] * 60 + slot["start_minute"]

    def slot_end_value(slot):
        end_hour = (
            24
            if slot["end_hour"] == 0 and slot["end_minute"] == 0
            else slot["end_hour"]
        )
        return end_hour * 60 + slot["end_minute"]

    def merge_overlapping_slots(slot_to_merge, other_slot):
        if slot_start_value(slot_to_merge) > slot_end_value(
            other_slot
        ) or slot_start_value(other_slot) > slot_end_value(slot_to_merge):
            return True
        if slot_start_value(other_slot) < slot_start_value(slot_to_merge):
            slot_to_merge["start_hour"] = other_slot["start_hour"]
            slot_to_merge["start_minute"] = other_slot["start_minute"]
            slot_to_merge["start"] = other_slot["start"]
        if slot_end_value(other_slot) > slot_end_value(slot_to_merge):
            slot_to_merge["end_hour"] = other_slot["end_hour"]
            slot_to_merge["end_minute"] = other_slot["end_minute"]
            slot_to_merge["end"] = other_slot["end"]
        return False

    def add_or_merge_time_slot(
        start_hour: int,
        start_minute: int,
        start: Text,
        end_hour: int,
        end_minute: int,
        end: Text,
        slots_list: List,
    ):
        slot_to_add = {
            "start_hour": start_hour,
            "start_minute": start_minute,
            "start": start,
            "end_hour": end_hour,
            "end_minute": end_minute,
            "end": end,
        }
        new_slots_list = [
            slot for slot in slots_list if merge_overlapping_slots(slot_to_add, slot)
        ]
        new_slots_list.append(slot_to_add)
        new_slots_list.sort(key=slot_start_value)
        return new_slots_list

    test_str = time_slots_str and time_slots_str.strip()
    if test_str:
        time_slots = {}
        lines = test_str.split(";")
        if not len(lines):
            return None
        for l in lines:
            slots = l.split(",")
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
                if (
                    (end_hour < start_hour)
                    or (end_hour == start_hour and end_minute <= start_minute)
                ) and (end_hour != 0 or end_minute != 0):
                    return None

                time_slots[weekday] = add_or_merge_time_slot(
                    start_hour,
                    start_minute,
                    matches.group(1),
                    end_hour,
                    end_minute,
                    matches.group(4),
                    time_slots[weekday],
                )
        return time_slots
    return None
