from bson.objectid import ObjectId
from typing import Dict, Text

from actions.db.store import db
from actions.utils.admin_config import get_advance_appointment_days
from actions.utils.date import format_time_slots_for_date, get_upcoming_availability


def lazy_init():
    if not db.doctor.find_one({"listing_status": "active"}):
        db.doctor.insert_many(
            [
                {
                    "_id": ObjectId(),
                    "name": "Dr. Murali",
                    "speciality": "General Surgeon",
                    "fee": 600,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/stethoscope.png",
                    "time_slots": {
                        "mon": [{"start": "17:00", "end": "19:00"}],
                        "tue": [{"start": "17:00", "end": "19:00"}],
                        "wed": [{"start": "17:00", "end": "19:00"}],
                        "thu": [{"start": "17:00", "end": "19:00"}],
                        "fri": [{"start": "17:00", "end": "19:00"}],
                        "sat": [],
                        "sun": [],
                    },
                    "credentials": {},
                    "user_id": "1",
                    "onboarding_status": "approved",
                    "listing_status": "active",
                },
                {
                    "_id": ObjectId(),
                    "name": "Dr. Lata",
                    "speciality": "Paediatrician",
                    "fee": 400,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/stethoscope.png",
                    "time_slots": {
                        "mon": [],
                        "tue": [],
                        "wed": [],
                        "thu": [],
                        "fri": [{"start": "17:00", "end": "19:00"}],
                        "sat": [{"start": "17:00", "end": "19:00"}],
                        "sun": [{"start": "17:00", "end": "19:00"}],
                    },
                    "credentials": {},
                    "user_id": "2",
                    "onboarding_status": "approved",
                    "listing_status": "active",
                },
                {
                    "_id": ObjectId(),
                    "name": "Dr. Asha",
                    "speciality": "Gynaecologist",
                    "fee": 700,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/stethoscope.png",
                    "time_slots": {
                        "mon": [{"start": "17:00", "end": "19:00"}],
                        "tue": [],
                        "wed": [{"start": "17:00", "end": "19:00"}],
                        "thu": [],
                        "fri": [{"start": "17:00", "end": "19:00"}],
                        "sat": [],
                        "sun": [{"start": "17:00", "end": "19:00"}],
                    },
                    "credentials": {},
                    "user_id": "3",
                    "onboarding_status": "approved",
                    "listing_status": "active",
                },
            ]
        )


def add_doctor(doctor: Dict):
    lazy_init()
    return db.doctor.insert_one(doctor).inserted_id


def get_available_time_slots(doctor_id, date: Text):
    doctor_time_slots = get_doctor_time_slots(doctor_id)
    return format_time_slots_for_date(doctor_time_slots, date)


def get_doctor(id):
    lazy_init()
    return db.doctor.find_one({"_id": ObjectId(id)})


def get_doctor_for_user_id(user_id: Text):
    lazy_init()
    return db.doctor.find_one({"user_id": user_id})


def get_doctor_time_slots(id):
    lazy_init()
    doctor: Dict = db.doctor.find_one({"_id": ObjectId(id)})
    return doctor.get("time_slots")


def get_doctors_for_speciality(speciality: Text):
    lazy_init()
    return db.doctor.find(
        {
            "speciality": speciality,
            "onboarding_status": "approved",
            "listing_status": "active",
        }
    )


def get_upcoming_appointment_dates(doctor_id):
    doctor_time_slots = get_doctor_time_slots(doctor_id)
    return get_upcoming_availability(doctor_time_slots, get_advance_appointment_days())


def print_doctor_signup_form(doctor: Dict):
    return (
        f"ID: #{doctor.get('_id')}\n"
        + "\n"
        + f"Name: {doctor.get('name')}\n"
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
    lazy_init()
    db.doctor.update_one({"_id": doctor.get("_id")}, {"$set": doctor})
