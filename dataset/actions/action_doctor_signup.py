from copy import deepcopy
import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


from actions.utils.admin import get_admin_group_id
from actions.utils.doctor import (
    get_doctor_for_user_id,
    update_doctor,
    print_doctor_signup_form,
)

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

        metadata = tracker.latest_message.get("metadata", {})

        # tbdemily - get credentials & doctor_id from the incoming webhook
        credentials = metadata.get("credentials", {})
        user_id = metadata.get("user_id", tracker.sender_id)

        doctor = get_doctor_for_user_id(user_id)
        if doctor:
            doctor["onboarding_status"] = "signup"
            doctor["credentials"] = credentials
            update_doctor(doctor)

            text = (
                f"Thank you for your interest in Ask My Doctor. We have received your details and will review it and get back to you within 48 hours.\n"
                + "\n"
                + print_doctor_signup_form(doctor)
            )

            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)

            if get_admin_group_id():
                admin_json_message = deepcopy(json_message)
                admin_json_message["chat_id"] = get_admin_group_id()
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")

        return []
