import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import ONBOARDING_STATUS_REJECTED, get_doctor, update_doctor
from actions.utils.regex import match_command


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
        command_breakup = match_command(message_text)
        specialities_list = command_breakup["string"]
        if command_breakup:
            doctor_id = command_breakup["id"]
            reject_reason = command_breakup["string"]
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
