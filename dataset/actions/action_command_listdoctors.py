import re
from typing import Any, AnyStr, Dict, List, Match, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group, get_specialities
from actions.utils.doctor import get_doctors, get_doctor_card
from actions.utils.validate import validate_speciality

from actions.utils.command import extract_command


class ActionCommandListDoctors(Action):
    def name(self) -> Text:
        return "action_command_listdoctors"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        message_text = tracker.latest_message.get("text")
        command = extract_command(message_text, False)
        speciality = command and validate_speciality(command["args"])

        if command and speciality:
            doctors = get_doctors(speciality=speciality)
            dispatcher.utter_message(
                json_message={
                    "text": f"Found {doctors.count()} doctors for speciality '{speciality}'"
                }
            )
            for d in doctors:
                dispatcher.utter_message(json_message=get_doctor_card(d))
        else:
            usage = "/listdoctors <SPECIALITY>"
            specialities = "\n".join(get_specialities())
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nSpeciality must be from this list:\n\n{specialities}"
                }
            )
        return []
