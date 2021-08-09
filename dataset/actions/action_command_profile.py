import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.command import extract_doctor_command
from actions.utils.doctor import (
    get_doctor,
    get_doctor_card,
    get_doctor_for_user_id,
    is_approved_doctor,
)

logger = logging.getLogger(__name__)


class ActionCommandProfile(Action):
    def name(self) -> Text:
        return "action_command_profile"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        _is_admin_group = is_admin_group(tracker.sender_id)
        if not (_is_admin_group or is_approved_doctor(tracker.sender_id)):
            return []

        message_text = tracker.latest_message.get("text")
        command = extract_doctor_command(message_text, _is_admin_group)
        if command:
            doctor: Dict = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = command["doctor_id"]
                doctor = get_doctor(doctor_id)
                admin_doctor_card = get_doctor_card(doctor, True)
                dispatcher.utter_message(json_message=admin_doctor_card)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
                doctor_card = get_doctor_card(doctor)
                dispatcher.utter_message(json_message=doctor_card)
        else:
            usage = "/profile"
            if _is_admin_group:
                usage = "/profile <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )
        return []
