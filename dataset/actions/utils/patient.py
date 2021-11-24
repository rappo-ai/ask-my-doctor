from bson.objectid import ObjectId
from datetime import datetime
from typing import Dict, Text

from actions.db.rappo import rappo_db
from actions.utils.date import SERVER_TZINFO
from actions.utils.markdown import escape_markdown, get_user_link


def add_patient(patient: Dict):
    current_date = datetime.now(tz=SERVER_TZINFO)
    patient["creation_ts"] = current_date.timestamp()
    patient["creation_date"] = current_date.isoformat()
    patient["last_update_ts"] = current_date.timestamp()
    patient["last_update_date"] = current_date.isoformat()
    return rappo_db.patient.insert_one(patient).inserted_id


def get_patient(id: Text):
    return rappo_db.patient.find_one({"_id": ObjectId(id)})


def get_patient_for_user_id(user_id):
    return rappo_db.patient.find_one({"user_id": user_id})


def print_patient(patient: Dict, show_user_links: bool = False):
    patient_name = patient.get("name", "")
    patient_text = (
        f"Doctor: {get_user_link(patient.get('user_id', ''), escape_markdown(patient_name, enabled=show_user_links))}\n"
        if show_user_links
        else escape_markdown(f"Name: {patient_name}\n", enabled=show_user_links)
    )
    return (
        patient_text
        + escape_markdown(f"Age: {patient.get('age', '')}\n", enabled=show_user_links)
        + escape_markdown(
            f"Phone: {patient.get('phone', '')}\n", enabled=show_user_links
        )
        + escape_markdown(
            f"Email: {patient.get('email', '')}\n", enabled=show_user_links
        )
    )


def update_patient(patient: Dict):
    current_date = datetime.now(tz=SERVER_TZINFO)
    patient["last_update_ts"] = current_date.timestamp()
    patient["last_update_date"] = current_date.isoformat()
    rappo_db.patient.update_one({"_id": patient.get("_id")}, {"$set": patient})
