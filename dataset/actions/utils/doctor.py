from bson.objectid import ObjectId
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from typing import Dict, Text

from actions.db.rappo import rappo_db
from actions.utils.admin_config import get_advance_appointment_days
from actions.utils.branding import get_bot_support_username
from actions.utils.debug import is_debug_env
from actions.utils.date import (
    SERVER_TZINFO,
    generate_time_slots_for_date,
    get_available_dates_for_weekly_slots,
    print_weekly_slots,
)
from actions.utils.json import get_json_key
from actions.utils.markdown import escape_markdown, get_user_link
from actions.utils.timeslot_lock import is_doctor_slot_locked

ONBOARDING_STATUS_APPROVED = "approved"
ONBOARDING_STATUS_REJECTED = "rejected"
ONBOARDING_STATUS_SIGNUP = "signup"
LISTING_STATUS_ENABLED = "enabled"
LISTING_STATUS_DISABLED = "disabled"
MAX_DOCTOR_RANK = 9999999

rappo_db.doctor.create_index(
    [("rank_last_updated_ts", DESCENDING), ("rank", ASCENDING)]
)


def lazy_init():
    if is_debug_env() and not rappo_db.doctor.find_one(
        {"listing_status": LISTING_STATUS_ENABLED}
    ):
        current_date = datetime.now(tz=SERVER_TZINFO)
        rappo_db.doctor.insert_many(
            [
                {
                    "_id": ObjectId(),
                    "creation_ts": current_date.timestamp(),
                    "creation_date": current_date.isoformat(),
                    "last_update_ts": current_date.timestamp(),
                    "last_update_date": current_date.isoformat(),
                    "name": "Dr. Murali",
                    "speciality": "General Surgeon",
                    "fee": 600,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/doctor-profile.png",
                    "weekly_slots": {
                        "mon": [],
                        "tue": [{"start": "17:00", "end": "17:15"}],
                        "wed": [],
                        "thu": [],
                        "fri": [],
                        "sat": [],
                        "sun": [],
                    },
                    "credentials": {},
                    "user_id": "1",
                    "onboarding_status": ONBOARDING_STATUS_APPROVED,
                    "listing_status": LISTING_STATUS_ENABLED,
                    "rank": MAX_DOCTOR_RANK,
                    "rank_last_updated_ts": current_date.timestamp(),
                },
                {
                    "_id": ObjectId(),
                    "creation_ts": current_date.timestamp(),
                    "creation_date": current_date.isoformat(),
                    "last_update_ts": current_date.timestamp(),
                    "last_update_date": current_date.isoformat(),
                    "name": "Dr. Lata",
                    "speciality": "Paediatrician",
                    "fee": 400,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/doctor-profile.png",
                    "weekly_slots": {
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
                    "onboarding_status": ONBOARDING_STATUS_APPROVED,
                    "listing_status": LISTING_STATUS_ENABLED,
                    "rank": MAX_DOCTOR_RANK,
                    "rank_last_updated_ts": current_date.timestamp(),
                },
                {
                    "_id": ObjectId(),
                    "creation_ts": current_date.timestamp(),
                    "creation_date": current_date.isoformat(),
                    "last_update_ts": current_date.timestamp(),
                    "last_update_date": current_date.isoformat(),
                    "name": "Dr. Asha",
                    "speciality": "Gynaecologist",
                    "fee": 700,
                    "description": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "photo": "https://storage.googleapis.com/ask-my-doctor-public/doctor-profile.png",
                    "weekly_slots": {
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
                    "onboarding_status": ONBOARDING_STATUS_APPROVED,
                    "listing_status": LISTING_STATUS_ENABLED,
                    "rank": MAX_DOCTOR_RANK,
                    "rank_last_updated_ts": current_date.timestamp(),
                },
            ]
        )


def is_approved_doctor(chat_id: Text):
    return bool(
        rappo_db.doctor.find_one(
            {"user_id": chat_id, "onboarding_status": ONBOARDING_STATUS_APPROVED}
        )
    )


def is_approved_and_activated_doctor(doctor_id) -> bool:
    return bool(
        rappo_db.doctor.find_one(
            {
                "_id": ObjectId(doctor_id),
                "onboarding_status": ONBOARDING_STATUS_APPROVED,
                "listing_status": LISTING_STATUS_ENABLED,
            }
        )
    )


def add_doctor(doctor: Dict):
    lazy_init()
    current_date = datetime.now(tz=SERVER_TZINFO)
    doctor["creation_ts"] = current_date.timestamp()
    doctor["creation_date"] = current_date.isoformat()
    doctor["last_update_ts"] = current_date.timestamp()
    doctor["last_update_date"] = current_date.isoformat()
    doctor["rank"] = MAX_DOCTOR_RANK
    doctor["rank_last_updated_ts"] = current_date.timestamp()
    return rappo_db.doctor.insert_one(doctor).inserted_id


def get_available_time_slots(doctor_id, date: Text):
    doctor_weekly_slots = get_doctor_weekly_slots(doctor_id)
    return generate_time_slots_for_date(
        doctor_weekly_slots, date, get_time_slot_filter_for_doctor(doctor_id)
    )


def get_doctor(id):
    lazy_init()
    return rappo_db.doctor.find_one({"_id": ObjectId(id)})


def get_doctor_for_user_id(user_id: Text):
    lazy_init()
    return rappo_db.doctor.find_one({"user_id": user_id})


def get_doctor_weekly_slots(id):
    lazy_init()
    doctor: Dict = rappo_db.doctor.find_one({"_id": ObjectId(id)})
    return doctor.get("weekly_slots")


def get_doctors(
    speciality: Text = None,
    onboarding_status: Text = None,
    listing_status: Text = None,
):
    lazy_init()
    query = {}
    if speciality:
        query.update({"speciality": speciality})
    if onboarding_status:
        query.update({"onboarding_status": onboarding_status})
    if listing_status:
        query.update({"listing_status": listing_status})
    return rappo_db.doctor.find(query).sort(
        [("rank_last_updated_ts", DESCENDING), ("rank", ASCENDING)]
    )


def get_time_slot_filter_for_doctor(doctor_id):
    def filter(slot_dt: datetime):
        return not is_doctor_slot_locked(doctor_id, slot_dt.isoformat())

    return filter


def get_available_appointment_dates(doctor_id):
    doctor_weekly_slots = get_doctor_weekly_slots(doctor_id)
    return get_available_dates_for_weekly_slots(
        doctor_weekly_slots,
        get_advance_appointment_days(),
        get_time_slot_filter_for_doctor(doctor_id),
    )


def print_doctor_profile(
    doctor: Dict,
    include_status: bool = False,
    include_time_slots: bool = False,
    include_google_id: bool = False,
    include_bank_details: bool = False,
    include_user_link: bool = False,
    use_markdown: bool = False,
):
    assert include_user_link == False or use_markdown == True

    profile = f"ID: #{doctor.get('_id')}\n"

    if include_status:
        profile = profile + (
            "\n"
            + f"Onboarding Status: {str(doctor.get('onboarding_status')).capitalize()}\n"
            + f"Listing Status: {str(doctor.get('listing_status')).capitalize()}\n"
        )
    profile = profile + (
        "\n"
        + f"Name: {doctor.get('name')}\n"
        + f"Phone Number: {doctor.get('phone_number')}\n"
        + f"Gmail ID: {doctor.get('gmail_id')}\n"
        + f"Speciality: {doctor.get('speciality')}\n"
        + f"Description: {doctor.get('description')}\n"
        + f"Consultation Fee: {doctor.get('fee')}\n"
    )
    if include_time_slots:
        profile = profile + (
            f"Time Slots: {print_weekly_slots(doctor.get('weekly_slots'))}\n"
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

    if use_markdown:
        profile = escape_markdown(profile)

    if include_user_link:
        profile = (
            escape_markdown("User Link: ")
            + get_user_link(
                doctor.get("telegram_user_id"), escape_markdown(doctor.get("name"))
            )
            + "\n"
            + profile
        )

    return profile


def get_doctor_card(doctor: Dict, is_for_admin: bool = False) -> Dict:
    caption = print_doctor_profile(
        doctor,
        include_status=True,
        include_time_slots=True,
        include_google_id=True,
        include_user_link=is_for_admin,
        use_markdown=is_for_admin,
    )
    card = {"photo": doctor.get("photo"), "caption": caption}
    if is_for_admin:
        card.update({"parse_mode": "MarkdownV2"})
    return card


def print_doctor_summary(doctor: Dict):
    return (
        f"Name: {doctor.get('name')}\n"
        + f"Speciality: {doctor.get('speciality')}\n"
        + f"Description: {doctor.get('description')}\n"
        + f"Fee: {doctor.get('fee')}\n"
    )


def update_doctor(doctor: Dict):
    lazy_init()
    current_date = datetime.now(tz=SERVER_TZINFO)
    doctor["last_update_ts"] = current_date.timestamp()
    doctor["last_update_date"] = current_date.isoformat()
    rappo_db.doctor.update_one({"_id": doctor.get("_id")}, {"$set": doctor})


def get_doctor_command_help(is_admin: bool = False):
    doctor_id_arg = (is_admin and " <DOCTOR ID>") or ""
    command_help = (
        f"/profile{doctor_id_arg} - view profile\n"
        + f"/activate{doctor_id_arg} - activate listing\n"
        + f"/deactivate{doctor_id_arg} - deactivate listing\n"
        + f"/listorders{(doctor_id_arg + '[OPTIONAL]') if doctor_id_arg else ''} - list all orders as csv file\n"
        + f"/setname{doctor_id_arg} <NAME> - update name\n"
        + f"/setphoto{doctor_id_arg} - update profile photo by replying to image message\n"
        + f"/setphonenumber{doctor_id_arg} <PHONE NUMBER> - update phone number\n"
        + f"/setspeciality{doctor_id_arg} <SPECIALITY> - update speciality\n"
        + f"/setdescription{doctor_id_arg} <DESCRIPTION> - update description\n"
        + f"/settimeslots{doctor_id_arg} <TIME SLOT LIST> - update available time slots for the upcoming week\n"
        + f"/setfee{doctor_id_arg} <CONSULTATION FEE> - update consultation fee\n"
    )
    if not is_admin:
        command_help = command_help + (
            "/setgoogleid - update Google ID for meetings\n"
            + "\n"
            + f"To update your bank account details or Gmail id, or for any other queries, please contact the admin {get_bot_support_username()}.\n"
        )
    return command_help


def format_doctor_header_for_csv() -> Text:
    header_cols = [
        "Doctor ID",
        "Creation Timestamp",
        "Creation Date",
        "Last Update Timestamp",
        "Last Update Date",
        "Onboarding Status",
        "Listing Status",
        "Name",
        "Phone Number",
        "Gmail ID",
        "Speciality",
        "Description",
        "Consultation Fee",
        "Time Slots",
        "Google ID",
        "Bank Account Number",
        "Bank Account Name",
        "Bank Account IFSC",
    ]
    return ",".join(header_cols)


def format_doctor_for_csv(doctor: Dict) -> Text:
    doctor_cols = [
        f"{get_json_key(doctor, '_id')}",
        f"{get_json_key(doctor, 'creation_ts')}",
        f"{get_json_key(doctor, 'creation_date')}",
        f"{get_json_key(doctor, 'last_update_ts')}",
        f"{get_json_key(doctor, 'last_update_date')}",
        f"{get_json_key(doctor, 'onboarding_status')}",
        f"{get_json_key(doctor, 'listing_status')}",
        f"{get_json_key(doctor, 'name')}",
        f"{get_json_key(doctor, 'phone_number')}",
        f"{get_json_key(doctor, 'gmail_id')}",
        str(get_json_key(doctor, "speciality") or "")
        .replace(",", " ")
        .replace("\n", " ")
        .replace("\t", " "),
        str(get_json_key(doctor, "description") or "")
        .replace(",", " ")
        .replace("\n", " ")
        .replace("\t", " "),
        f"{get_json_key(doctor, 'fee')}",
        f"{print_weekly_slots(get_json_key(doctor, 'weekly_slots'), ' ')}",
        f"{'Connected' if get_json_key(doctor, 'credentials') else 'Not connected'}",
        f"{get_json_key(doctor, 'bank_account_number')}",
        f"{get_json_key(doctor, 'bank_account_name')}",
        f"{get_json_key(doctor, 'bank_account_ifsc')}",
    ]
    return ",".join(doctor_cols)
