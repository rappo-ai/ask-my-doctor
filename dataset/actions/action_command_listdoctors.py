import re
from typing import Any, AnyStr, Dict, List, Match, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group, get_specialities
from actions.utils.doctor import get_doctors, get_doctor_card
from actions.utils.text import format_count
from actions.utils.validate import validate_speciality


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
        regex = r"^(/\w+)(\s+(.+))?$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        speciality = matches and matches.group(3)
        is_valid_speciality = speciality and validate_speciality(matches.group(3))

        if matches and (not speciality or is_valid_speciality):
            doctors = get_doctors(speciality=speciality)
            num_doctors = doctors.count()
            dispatcher.utter_message(
                json_message={
                    "text": f"Found {num_doctors} {format_count('doctor', 'doctors', num_doctors)}"
                    + (f" for speciality '{speciality}'" if speciality else "")
                }
            )
            for d in doctors:
                dispatcher.utter_message(json_message=get_doctor_card(d))
        else:
            usage = "/listdoctors <SPECIALITY>[OPTIONAL]"
            specialities = "\n".join(get_specialities())
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nSpeciality is optional. If specified it must be from this list:\n\n{specialities}"
                }
            )
        return []
