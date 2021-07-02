from copy import deepcopy
import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import (
    get_doctor_for_user_id,
    update_doctor,
    print_doctor_signup_form,
)
from actions.utils.sheets import update_doctor_in_spreadsheet

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

        entities = tracker.latest_message.get("entities", [])
        # #tbdemily - add webhook to trigger intent /EXTERNAL_doctor_signup_google_authenticated
        # with "credentials" entity in dataset/connectors/telegram.py; The syntax will be
        # /EXTERNAL_doctor_signup_google_authenticated{"credentials": "value"}; Not sure if value
        # can be a JSON object, can convert JSON to string if not supported
        credentials: Dict = next(
            iter(
                [e.get("value") for e in entities if e.get("entity") == "credentials"]
            ),
            {},
        )
        user_id = tracker.sender_id

        doctor = get_doctor_for_user_id(user_id)
        if doctor:
            doctor["onboarding_status"] = "signup"
            doctor["credentials"] = credentials
            update_doctor(doctor)

            update_doctor_in_spreadsheet(doctor)

            caption = (
                f"Thank you for your interest in Ask My Doctor. We have received your details and will review it and get back to you within 48 hours.\n"
                + "\n"
                + print_doctor_signup_form(doctor)
            )

            json_message = {"photo": doctor.get("photo"), "caption": caption}
            dispatcher.utter_message(json_message=json_message)

            if get_admin_group_id():
                admin_json_message = deepcopy(json_message)
                admin_json_message["chat_id"] = get_admin_group_id()
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")

        return []
