from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.command import extract_command
from actions.utils.doctor import ONBOARDING_STATUS_REJECTED, get_doctor, update_doctor


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
        command = extract_command(message_text, True)
        if command:
            doctor_id = command["doctor_id"]
            reject_reason = command["args"]
            doctor = get_doctor(doctor_id)
            doctor["onboarding_status"] = ONBOARDING_STATUS_REJECTED
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
                        f'Your application has been rejected with reason "{reject_reason}". Please use /signup to submit a fresh application.\n'
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
