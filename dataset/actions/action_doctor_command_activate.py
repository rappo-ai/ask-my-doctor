import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import get_doctor, get_doctor_for_user_id, update_doctor


class ActionDoctorCommandActivate(Action):
    def name(self) -> Text:
        return "action_doctor_command_activate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        is_admin = tracker.sender_id == get_admin_group_id()
        regex = r"^(/\w+)(\s+#(\w+))?$"
        if is_admin:
            regex = r"^(/\w+)(\s+#(\w+))$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            doctor = {}
            doctor_id = ""
            if is_admin:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["listing_status"] = "active"
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id} has been activated.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f"Your listing is now active. You can deactivate your listing by using /deactivate at any time.\n"
                    ),
                }
            )
        else:
            usage = "/activate"
            if is_admin:
                usage = "/activate <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )

        return []
