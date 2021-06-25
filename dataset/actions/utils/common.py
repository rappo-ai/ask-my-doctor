from typing import Text

from actions.utils.db import (
    get_doctors as get_doctors_from_db,
    get_specialities as get_specialities_from_db,
)

_appointment_details = {}
_patient_details = {}
_payment_details = {}


def get_specialities():
    return get_specialities_from_db()


def get_doctors():
    return get_doctors_from_db()


def get_upcoming_appointment_dates():
    return [
        "Thursday, 1st July 2021",
        "Friday, 2nd July 2021",
        "Saturday, 3rd July 2021",
    ]


def get_appointment_time_slots():
    return ["5:00 PM", "6:30 PM", "7:00 PM"]


def get_appointment_details():
    return _appointment_details


def set_appointment_details(
    doctor_name: Text, speciality: Text, date: Text, time: Text
):
    _appointment_details["doctor_name"] = doctor_name
    _appointment_details["speciality"] = speciality
    _appointment_details["date"] = date
    _appointment_details["time"] = time
    return _appointment_details


def print_appointment_details():
    return (
        f"Doctor's name: {_appointment_details.get('doctor_name', '')}\n"
        + f"Speciality: {_appointment_details.get('speciality', '')}\n"
        + f"Date: {_appointment_details.get('date', '')}\n"
        + f"Time: {_appointment_details.get('time', '')}\n"
    )


def get_patient_details():
    return _patient_details


def set_patient_details(name: Text, age: Text, phone: Text, email: Text):
    _patient_details["name"] = name
    _patient_details["age"] = age
    _patient_details["phone"] = phone
    _patient_details["email"] = email
    return _patient_details


def print_patient_details():
    return (
        f"Name: {_patient_details.get('name', '')}\n"
        + f"Age: {_patient_details.get('age', '')}\n"
        + f"Phone: {_patient_details.get('phone', '')}\n"
        + f"Email: {_patient_details.get('email', '')}\n"
    )


def get_payment_details():
    return _payment_details


def set_payment_details(amount: Text, transaction_id: Text, date: Text, mode: Text):
    _payment_details["amount"] = amount
    _payment_details["transaction_id"] = transaction_id
    _payment_details["date"] = date
    _payment_details["mode"] = mode
    return _payment_details


def print_payment_details():
    return (
        f"Amount: {_payment_details.get('amount', '')}\n"
        + f"Transaction ID: {_payment_details.get('transaction_id', '')}\n"
        + f"Date: {_payment_details.get('date', '')}\n"
        + f"Mode: {_payment_details.get('mode', '')}\n"
    )


def create_order():
    # tbdnikhil
    return {"id": 1, "amount": 300, "payment_link": "https://rzp.io/i/4E2QCoUO"}


def create_meeting_link():
    # tbdemily
    return "https://meet.google.com/vix-uaxv-hcx"
