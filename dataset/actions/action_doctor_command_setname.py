import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import get_doctor, get_doctor_for_user_id, update_doctor
from actions.utils.validate import validate_name


class ActionDoctorCommandSetName(Action):
    def name(self) -> Text:
        return "action_doctor_command_setname"

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
        name = matches and validate_name(matches.group(4))
        if matches and name:
            doctor = {}
            doctor_id = ""
            if is_admin:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])

            doctor["name"] = name
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, name has been updated to \"{name}\".",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f'Your name has been updated to "{name}".\n',
                }
            )
        else:
            usage = "/setname <NAME>"
            if is_admin:
                usage = "/setname <DOCTOR ID> <NAME>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nName cannot contain special characters other than apostrophe or period."
                }
            )

        return []
