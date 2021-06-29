from copy import deepcopy
from typing import Dict, Text

from actions.utils.admin import get_advance_appointment_days
from actions.utils.date import format_time_slots_for_date, get_upcoming_availability

doctors = [
    {
        "_id": 1,
        "name": "Dr. Murali",
        "speciality": "General Surgeon",
        "fee": 600,
        "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "",
            "",
        ],
        "credentials": {},
        "user_id": "1",
        "onboarding_status": "live",
    },
    {
        "_id": 2,
        "name": "Dr. Lata",
        "speciality": "Paediatrician",
        "fee": 400,
        "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "",
            "",
            "",
            "",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
        ],
        "credentials": {},
        "user_id": "2",
        "onboarding_status": "live",
    },
    {
        "_id": 3,
        "name": "Dr. Asha",
        "speciality": "Gynaecologist",
        "fee": 700,
        "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
            "",
            "17:00,17:15,17:30,17:45,18:00,18:15,18:30,18:45",
        ],
        "credentials": {},
        "user_id": "3",
        "onboarding_status": "live",
    },
]


def add_doctor(doctor: Dict):
    # tbdrenzil - add doctor in db/sheets
    doctor_copy = deepcopy(doctor)
    doctor_copy["_id"] = len(doctors)
    doctors.append(doctor_copy)
    return doctor_copy["_id"]


def get_available_time_slots(doctor_id, date: Text):
    doctor_time_slots = get_doctor_time_slots(doctor_id)
    return format_time_slots_for_date(doctor_time_slots, date)


def get_doctor(id):
    # tbdrenzil - get doctor from db/sheets
    return next(iter([d for d in doctors if d.get("_id") == id]), None)
    # return _get_doctor_from_sheets(doctor_id)


def get_doctor_for_user_id(user_id: Text):
    # tbdrenzil - get doctor from db/sheets
    return next(iter([d for d in doctors if d.get("user_id") == user_id]), None)


def get_doctor_time_slots(doctor_id: Text):
    doctor: Dict = next(iter([d for d in doctors if d.get("_id") == doctor_id]), {})
    return doctor.get("time_slots", [])


def get_doctors_for_speciality(speciality: Text):
    return [
        d
        for d in doctors
        if d.get("speciality") == speciality and d.get("onboarding_status") == "live"
    ]


def get_upcoming_appointment_dates(doctor_id):
    doctor_time_slots = get_doctor_time_slots(doctor_id)
    if len(doctor_time_slots) != 7:
        doctor_time_slots = ["" for i in range(7)]
    return get_upcoming_availability(doctor_time_slots, get_advance_appointment_days())


def print_doctor_signup_form(doctor: Dict):
    return (
        f"Name: {doctor.get('name')}\n"
        + f"Phone Number: {doctor.get('phone_number')}\n"
        + f"Speciality: {doctor.get('speciality')}\n"
        + f"Description: {doctor.get('description')}\n"
        + f"Availability: {doctor.get('availability')}\n"
        + f"Consultation Fee: {doctor.get('fee')}\n\n"
        + f"Bank Details\n\n"
        + f"Account number: {doctor.get('bank_account_number')}\n"
        + f"Account name: {doctor.get('bank_account_name')}\n"
        + f"Account IFSC: {doctor.get('bank_account_ifsc')}\n"
    )


def print_doctor_summary(doctor: Dict):
    return (
        f"Name: {doctor.get('name')}\n"
        + f"Speciality: {doctor.get('speciality')}\n"
        + f"Description: {doctor.get('description')}\n"
        + f"Fee: {doctor.get('fee')}\n"
    )


def update_doctor(doctor: Dict):
    doctor_dbitem: Dict = get_doctor(doctor.get("_id"))
    if doctor_dbitem:
        doctor_dbitem.update(doctor)
        return True
    return False
