from bson.objectid import ObjectId
from datetime import datetime
from hashlib import md5
from pymongo.errors import DuplicateKeyError
from typing import Dict, Optional, Text

from actions.utils.date import SERVER_TZINFO
from actions.db.store import db


def compute_hased_id(doctor_id, slot_datetime: Text):
    text = (str(doctor_id) + slot_datetime).encode("utf-8")
    return md5(text).hexdigest()[:24]


def create_lock_for_doctor_slot(
    doctor_id,
    slot_datetime: Text,
    order_id: Optional[ObjectId] = None,
    force: Optional[bool] = False,
) -> ObjectId:
    lock_id = compute_hased_id(doctor_id, slot_datetime)
    current_date = datetime.now(tz=SERVER_TZINFO)
    lock = {
        "_id": ObjectId(lock_id),
        "doctor_id": doctor_id,
        "slot": slot_datetime,
        "creation_ts": current_date.timestamp(),
        "creation_date": current_date.isoformat(),
        "last_update_ts": current_date.timestamp(),
        "last_update_ts": current_date.isoformat(),
    }
    if order_id:
        lock["order_id"] = order_id
    if force:
        delete_lock_for_id(lock_id)
    try:
        return db.timeslot_lock.insert_one(lock).inserted_id
    except DuplicateKeyError:
        return None


def is_doctor_slot_locked(doctor_id, slot_datetime: Text) -> bool:
    lock_id = compute_hased_id(doctor_id, slot_datetime)
    return bool(db.timeslot_lock.find_one({"_id": ObjectId(lock_id)}))


def get_lock_for_slot(doctor_id, slot_datetime: Text) -> bool:
    lock_id = compute_hased_id(doctor_id, slot_datetime)
    return db.timeslot_lock.find_one({"_id": ObjectId(lock_id)})


def get_lock_for_id(lock_id) -> Dict:
    return db.timeslot_lock.find_one({"_id": ObjectId(lock_id)})


def update_lock_for_id(lock_id, order_id: ObjectId):
    current_date = datetime.now(tz=SERVER_TZINFO)
    return db.timeslot_lock.update_one(
        {"_id": ObjectId(lock_id)},
        {
            "$set": {
                "order_id": order_id,
                "last_update_ts": current_date.timestamp(),
                "last_update_ts": current_date.isoformat(),
            }
        },
    )


def delete_lock_for_id(lock_id: Text):
    return db.timeslot_lock.delete_one({"_id": ObjectId(lock_id)})
