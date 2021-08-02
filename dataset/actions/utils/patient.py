from bson.objectid import ObjectId
from datetime import datetime
from typing import Dict, Text

from actions.db.store import db
from actions.utils.date import SERVER_TZINFO


def add_patient(patient: Dict):
    current_date = datetime.now(tz=SERVER_TZINFO)
    patient["creation_ts"] = current_date.timestamp()
    patient["creation_date"] = current_date.isoformat()
    patient["last_update_ts"] = current_date.timestamp()
    patient["last_update_date"] = current_date.isoformat()
    return db.patient.insert_one(patient).inserted_id


def get_patient(id: Text):
    return db.patient.find_one({"_id": ObjectId(id)})


def get_patient_for_user_id(user_id):
    return db.patient.find_one({"user_id": user_id})


def print_patient(patient: Dict):
    return (
        f"Name: {patient.get('name', '')}\n"
        + f"Age: {patient.get('age', '')}\n"
        + f"Phone: {patient.get('phone', '')}\n"
        + f"Email: {patient.get('email', '')}\n"
    )


def update_patient(patient: Dict):
    current_date = datetime.now(tz=SERVER_TZINFO)
    patient["last_update_ts"] = current_date.timestamp()
    patient["last_update_date"] = current_date.isoformat()
    db.patient.update_one({"_id": patient.get("_id")}, {"$set": patient})
