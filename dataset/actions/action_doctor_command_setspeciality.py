import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, get_specialities
from actions.utils.doctor import get_doctor, get_doctor_for_user_id, update_doctor
from actions.utils.validate import validate_speciality


class ActionDoctorCommandSetSpeciality(Action):
    def name(self) -> Text:
        return "action_doctor_command_setspeciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        is_admin = tracker.sender_id == get_admin_group_id()
        regex = r"^(/\w+)(\s+#(\w+))?(.+)$"
        if is_admin:
            regex = r"^(/\w+)(\s+#(\w+))(.+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        speciality = matches and validate_speciality(matches.group(4))
        if matches and speciality:
            doctor = {}
            doctor_id = ""
            if is_admin:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["speciality"] = speciality
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, speciality has been updated to \"{speciality}\".",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f'Your speciality has been updated to "{speciality}".\n',
                }
            )
        else:
            usage = "/setspeciality <SPECIALITY>"
            if is_admin:
                usage = "/setspeciality <DOCTOR ID> <SPECIALITY>"
            specialities = "\n".join(get_specialities())
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nSpeciality must be from this list:\n\n{specialities}"
                }
            )

        return []
