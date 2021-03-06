import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.branding import get_bot_display_name
from actions.utils.doctor import (
    LISTING_STATUS_DISABLED,
    ONBOARDING_STATUS_SIGNUP,
    add_doctor,
    get_doctor_for_user_id,
    update_doctor,
    print_doctor_profile,
)
from actions.utils.markdown import escape_markdown

logger = logging.getLogger(__name__)


class ActionNewDoctorSignup(Action):
    def name(self) -> Text:
        return "action_doctor_signup"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        telegram_user_id = tracker.get_slot("telegram_user_id") or ""

        doctor = get_doctor_for_user_id(user_id) or {}
        doctor["user_id"] = user_id
        doctor["telegram_user_id"] = telegram_user_id
        doctor["onboarding_status"] = ONBOARDING_STATUS_SIGNUP
        doctor["listing_status"] = LISTING_STATUS_DISABLED
        doctor["name"] = tracker.get_slot("doctor_signup__name")
        doctor["phone_number"] = tracker.get_slot("doctor_signup__number")
        doctor["gmail_id"] = tracker.get_slot("doctor_signup__gmail_id")
        doctor["photo"] = tracker.get_slot("doctor_signup__photo")
        doctor["speciality"] = tracker.get_slot("doctor_signup__speciality")
        doctor["description"] = tracker.get_slot("doctor_signup__description")
        doctor["weekly_slots"] = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thu": [],
            "fri": [],
            "sat": [],
            "sun": [],
        }
        doctor["fee"] = int(tracker.get_slot("doctor_signup__consultation_fee"))
        doctor["bank_account_number"] = tracker.get_slot(
            "doctor_signup__bank_account_number"
        )
        doctor["bank_account_name"] = tracker.get_slot(
            "doctor_signup__bank_account_name"
        )
        doctor["bank_account_ifsc"] = tracker.get_slot(
            "doctor_signup__bank_account_ifsc"
        )

        if doctor.get("_id"):
            update_doctor(doctor)
        else:
            add_doctor(doctor)

        caption = (
            f"Thank you for your interest in {get_bot_display_name()}. We have received your details and will review it and get back to you within 48 hours.\n"
            + "\n"
            + print_doctor_profile(doctor, include_bank_details=True)
        )

        json_message = {"photo": doctor.get("photo"), "caption": caption}
        dispatcher.utter_message(json_message=json_message)

        if get_admin_group_id():
            admin_caption = (
                escape_markdown("NEW DOCTOR SIGNUP!\n")
                + "\n"
                + print_doctor_profile(
                    doctor,
                    include_bank_details=True,
                    include_user_link=True,
                    use_markdown=True,
                )
            )
            admin_json_message = {
                "chat_id": get_admin_group_id(),
                "photo": doctor.get("photo"),
                "caption": admin_caption,
                "parse_mode": "MarkdownV2",
            }
            dispatcher.utter_message(json_message=admin_json_message)
        else:
            logger.warn("Admin group id not set. Use /admin or /groupid.")

        return []
