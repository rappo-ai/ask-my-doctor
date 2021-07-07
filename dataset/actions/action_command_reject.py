import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import get_doctor, update_doctor


class ActionCommandReject(Action):
    def name(self) -> Text:
        return "action_command_reject"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+#(\w+)\s+(.+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            doctor_id = matches.group(2)
            reject_reason = matches.group(3)
            doctor = get_doctor(doctor_id)
            doctor["onboarding_status"] = "rejected"
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "text": f"{doctor['name']} with ID {doctor_id} has been rejected with reason \"{reject_reason}\"."
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f"Your application has been rejected with reason {reject_reason}. Please use /signup to submit a fresh application.\n"
                    ),
                }
            )
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "The command format is incorrect. Usage:\n\n/reject <DOCTOR ID> <REASON>"
                }
            )

        return []
