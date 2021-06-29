from typing import Dict, Text

from actions.db.store import db


def add_patient(patient: Dict):
    return db.patient.insert_one(patient).inserted_id


def get_patient(id: Text):
    return db.patient.find_one({"_id": id})


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
    db.patient.update_one({"_id": patient.get("id")}, {"$set": patient})
