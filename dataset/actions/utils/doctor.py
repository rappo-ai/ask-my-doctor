from bson.objectid import ObjectId
from typing import Dict, Text

from actions.db.store import db
from actions.utils.admin_config import get_advance_appointment_days
from actions.utils.date import (
    format_time_slots_for_date,
    get_upcoming_availability,
    print_time_slots,
)


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


def is_approved_doctor(chat_id: Text):
    return bool(
        db.doctor.find_one({"user_id": chat_id, "onboarding_status": "approved"})
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


def print_doctor_profile(
    doctor: Dict,
    include_time_slots: bool = False,
    include_google_id: bool = False,
    include_bank_details: bool = False,
):
    profile = (
        f"ID: #{doctor.get('_id')}\n"
        + "\n"
        + f"Name: {doctor.get('name')}\n"
        + f"Phone Number: {doctor.get('phone_number')}\n"
        + f"Speciality: {doctor.get('speciality')}\n"
        + f"Description: {doctor.get('description')}\n"
        + f"Consultation Fee: {doctor.get('fee')}\n"
    )
    if include_time_slots:
        profile = profile + (
            f"Time Slots: {print_time_slots(doctor.get('time_slots'))}\n"
        )
    if include_google_id:
        profile = profile + (
            f"Google ID: {'Connected' if doctor.get('credentials') else 'Not connected'}\n"
        )
    if include_bank_details:
        profile = profile + (
            "\n"
            + "Bank Details\n\n"
            + f"Account number: {doctor.get('bank_account_number')}\n"
            + f"Account name: {doctor.get('bank_account_name')}\n"
            + f"Account IFSC: {doctor.get('bank_account_ifsc')}\n"
        )
    return profile


def get_doctor_card(doctor: Dict) -> Dict:
    caption = print_doctor_profile(
        doctor, include_time_slots=True, include_google_id=True
    )
    return {"photo": doctor.get("photo"), "caption": caption}


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


def get_doctor_command_help(is_admin: bool = False):
    doctor_id_arg = (is_admin and "<DOCTOR ID> ") or ""
    command_help = (
        f"/profile {doctor_id_arg}- view profile\n"
        + f"/activate {doctor_id_arg}- activate listing\n"
        + f"/deactivate {doctor_id_arg}- deactivate listing\n"
        + f"/setname {doctor_id_arg}<NAME> - update name\n"
        + f"/setphoto {doctor_id_arg}- update profile photo by replying to image message\n"
        + f"/setphonenumber {doctor_id_arg}<PHONE NUMBER>- update phone number\n"
        + f"/setspeciality {doctor_id_arg}<SPECIALITY> - update speciality\n"
        + f"/setdescription {doctor_id_arg}<DESCRIPTION> - update description\n"
        + f"/settimeslots {doctor_id_arg}<TIME SLOT LIST> - update available time slots for the upcoming week\n"
        + f"/setfee {doctor_id_arg}<CONSULTATION FEE> - update consultation fee\n"
    )
    if not is_admin:
        command_help = command_help + (
            "/setgoogleid - update Google ID for meetings\n"
            + "\n"
            + "To update your bank account details or for any other queries, please contact the admin @askmydoctorsupport.\n"
        )
    return command_help
