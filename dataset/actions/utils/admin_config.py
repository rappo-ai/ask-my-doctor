from bson.objectid import ObjectId
from actions.db.store import db

ADMIN_CONFID_OBJECT_ID = "000000000000000000000001"


def lazy_init():
    admin_config = db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)})
    if not admin_config:
        db.admin_config.insert_one(
            {
                "_id": ObjectId(ADMIN_CONFID_OBJECT_ID),
                "advance_appointment_days": 7,
                "commission_rate": 20,
                "meeting_duration_minutes": 15,
                "specialities": [
                    "General Surgeon",
                    "Paediatrician",
                    "Gynaecologist",
                ],
            },
        )


def get_admin_group_id():
    lazy_init()
    return db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}).get(
        "group_id"
    )


def set_admin_group_id(group_id):
    lazy_init()
    db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}, {"$set": {"group_id": group_id}}
    )


def get_advance_appointment_days():
    lazy_init()
    return db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}).get(
        "advance_appointment_days"
    )


def set_advance_appointment_days(days: int):
    lazy_init()
    db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"advance_appointment_days": days}},
    )


def get_commission_rate():
    lazy_init()
    return db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}).get(
        "commission_rate"
    )


def set_commission_rate(rate):
    lazy_init()
    db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}, {"$set": {"commission_rate": rate}}
    )


def get_meeting_duration_in_minutes():
    lazy_init()
    return db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}).get(
        "meeting_duration_minutes"
    )


def set_meeting_duration_in_minutes(minutes: int):
    lazy_init()
    db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"meeting_duration_minutes": minutes}},
    )


def get_specialities():
    lazy_init()
    return db.admin_config.find_one({"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)}).get(
        "specialities"
    )


def set_specialities(specialities: list):
    lazy_init()
    db.admin_config.update_one(
        {"_id": ObjectId(ADMIN_CONFID_OBJECT_ID)},
        {"$set": {"specialities": specialities}},
    )
