from typing import Text


_appointment_details = {}
_patient_details = {}
_payment_details = {}
_doctor_signup_data = {}
_admin_details = {}


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


def set_doctor_signup_data(
    name,
    phone_number,
    speciality,
    availability,
    consultation_fee,
    bank_account_number,
    bank_account_name,
    bank_account_ifsc,
):
    _doctor_signup_data["name"] = name
    _doctor_signup_data["phone_number"] = phone_number
    _doctor_signup_data["speciality"] = speciality
    _doctor_signup_data["availability"] = availability
    _doctor_signup_data["consultation_fee"] = consultation_fee
    _doctor_signup_data["bank_account_number"] = bank_account_number
    _doctor_signup_data["bank_account_name"] = bank_account_name
    _doctor_signup_data["bank_account_ifsc"] = bank_account_ifsc
    return _doctor_signup_data


def print_doctor_signup_data():
    return (
        f"Name: {_doctor_signup_data.get('name')}\n"
        + f"Phone Number: {_doctor_signup_data.get('phone_number')}\n"
        + f"Speciality: {_doctor_signup_data.get('speciality')}\n"
        + f"Availability: {_doctor_signup_data.get('availability')}\n"
        + f"Consultation Fee: {_doctor_signup_data.get('consultation_fee')}\n\n"
        + f"Bank Details\n\n"
        + f"Account number: {_doctor_signup_data.get('bank_account_number')}\n"
        + f"Account name: {_doctor_signup_data.get('bank_account_name')}\n"
        + f"Account IFSC: {_doctor_signup_data.get('bank_account_ifsc')}\n"
    )


def create_order():
    # tbdnikhil
    return {"id": 1, "amount": 300, "payment_link": "https://rzp.io/i/4E2QCoUO"}


def create_meeting_link():
    # tbdemily
    return "https://meet.google.com/vix-uaxv-hcx"


def get_commission_rate():
    return 20


def set_admin_group_id(group_id):
    _admin_details["group_id"] = group_id


def get_admin_group_id():
    return _admin_details.get("group_id")


def get_google_auth_url():
    # tbdemily
    return "https://accounts.google.com/o/oauth2/v2/auth"
