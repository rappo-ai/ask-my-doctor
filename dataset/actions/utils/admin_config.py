from typing import List, Text
from bson.objectid import ObjectId

from actions.db.rappo import rappo_db
from actions.utils.debug import is_debug_env

ADMIN_CONFID_OBJECT_ID = "000000000000000000000001"


def lazy_init():
    admin_config = rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    )
    specialities = (
        [
            "General Surgeon",
            "Paediatrician",
            "Gynaecologist",
        ]
        if is_debug_env()
        else []
    )
    if not admin_config:
        rappo_db.admin_config.insert_one(
            {
                "_id": ObjectId(ADMIN_CONFID_OBJECT_ID),
                "super_admins": [],
                "admin_group_id": "",
                "advance_appointment_days": 7,
                "booking_advance_time_minutes": 60,
                "payment_link_expiry_time_seconds": 0,
                "max_follow_up_seconds": 2 * 24 * 3600,
                "doctor_commission_rate": 10,
                "meeting_duration_minutes": 15,
                "specialities": specialities,
            },
        )


def is_super_admin(chat_id: Text):
    if is_debug_env():
        return True
    return chat_id in get_super_admins()


def get_payment_route_config():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("payment_route_config")


def is_admin_group(chat_id: Text):
    return get_admin_group_id() == chat_id


def get_super_admins():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("super_admins")


def get_admin_group_id():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("admin_group_id")


def set_admin_group_id(group_id):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"admin_group_id": group_id}},
    )


def get_advance_appointment_days():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("advance_appointment_days")


def set_advance_appointment_days(days: int):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"advance_appointment_days": days}},
    )


def get_booking_advance_time_minutes():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("booking_advance_time_minutes")


def set_booking_advance_time_minutes(minutes: int):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"booking_advance_time_minutes": minutes}},
    )


def get_payment_link_expiry_time_seconds():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("payment_link_expiry_time_seconds")


def get_max_follow_up_seconds():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("max_follow_up_seconds")


def get_doctor_commission_rate():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("doctor_commission_rate")


def set_doctor_commission_rate(rate):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"doctor_commission_rate": rate}},
    )


def get_meeting_duration_in_minutes():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("meeting_duration_minutes")


def set_meeting_duration_in_minutes(minutes: int):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"meeting_duration_minutes": minutes}},
    )


def get_specialities():
    lazy_init()
    return rappo_db.admin_config.find_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}
    ).get("specialities")


def set_specialities(specialities: List):
    lazy_init()
    rappo_db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"specialities": specialities}},
    )


def print_specialities(specialities: List):
    if specialities:
        text = "Current list of specialities:\n" + "\n" + "\n".join(specialities)
    else:
        text = "There are no specialities. Please use /addspeciality.\n"
    return text
