import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import get_doctor, get_doctor_for_user_id, update_doctor
from actions.utils.validate import validate_description


class ActionDoctorCommandSetDescription(Action):
    def name(self) -> Text:
        return "action_doctor_command_setdescription"

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
        description = matches and validate_description(matches.group(4))
        if matches and description:
            doctor = {}
            doctor_id = ""
            if is_admin:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["description"] = description
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, description has been updated to \"{description}\".",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f'Your description has been updated to "{description}".\n'
                    ),
                }
            )
        else:
            usage = "/setdescription <DESCRIPTION>"
            if is_admin:
                usage = "/setdescription <DOCTOR ID> <DESCRIPTION>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nDescription cannot be more than 200 characters long."
                }
            )

        return []
