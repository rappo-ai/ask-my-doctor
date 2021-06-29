from copy import deepcopy
from typing import Dict

patients = []


def add_patient(patient: Dict):
    id = len(patients)
    patient_copy = deepcopy(patient)
    patient_copy["_id"] = id
    patients.append(patient)
    return patient_copy["_id"]


def get_patient(id: int):
    return next(iter([p for p in patients if p.get("_id") == id]), None)


def get_patient_for_user_id(user_id):
    return next(iter([p for p in patients if p["user_id"] == user_id]), None)


def print_patient(patient: Dict):
    return (
        f"Name: {patient.get('name', '')}\n"
        + f"Age: {patient.get('age', '')}\n"
        + f"Phone: {patient.get('phone', '')}\n"
        + f"Email: {patient.get('email', '')}\n"
    )


def update_patient(patient: Dict):
    patient_dbitem: Dict = get_patient(patient.get("_id"))
    if patient_dbitem:
        patient_dbitem.update(patient)
        return True
    return False
