from bson.objectid import ObjectId
from hashlib import md5
from typing import Dict, Text

from actions.db.store import db


def compute_hased_id(doctor: Dict, slot: Dict):
    text = doctor.get("_id", "") + slot.get("start")
    return md5(text).hexdigest()[:24]


def create_lock(doctor: Dict, slot: Dict):
    lock_id = compute_hased_id(doctor, slot)
    lock = {
        "_id": ObjectID(lock_id),
        "ts": "",
        "status": "blocked",
    }
    try:
        return db.timeslot_lock.insert_one(lock).inserted_id
    except DuplicateKeyError as duplicate_error:
        return None

    return None


def get_lock(lock_id: Text):
    hashed_id = compute_hased_id(doctor, slot)
    return db.timeslot_lock.find_one({"_id": ObjectID(lock_id)})


def update_lock(lock_id: Text, status: Text):
    return db.timeslot_lock.update_one(
        {"_id": ObjectID(lock_id)}, {"$set": {"status": status}}
    )


def delete_lock(lock_id: Text):
    return db.timeslot_lock.delete_one({"_id": ObjectID(lock_id)})
