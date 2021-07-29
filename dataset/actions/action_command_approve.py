import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import (
    ONBOARDING_STATUS_APPROVED,
    get_doctor,
    get_doctor_command_help,
    update_doctor,
)
from actions.utils.regex import match_command


class ActionCommandApprove(Action):
    def name(self) -> Text:
        return "action_command_approve"

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
        if command_breakup["command"]:
            doctor_id = command_breakup["id"]
            doctor = get_doctor(doctor_id)
            doctor["onboarding_status"] = ONBOARDING_STATUS_APPROVED
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "text": f"{doctor['name']} with ID {doctor_id} has been approved. Please use /activate #{doctor_id} to make this doctor's listing live."
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f"Your application has been approved. Please use /setgoogleid to connect your Google ID to create meetings, and /settimeslots to update your timeslots for the upcoming week. Once you have done this, use /activate to make your listing live.\n"
                        + "\n"
                        "Here is the list of commands to view or update your doctor profile:\n"
                        + "\n"
                        + get_doctor_command_help()
                    ),
                }
            )
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "The command format is incorrect. Usage:\n\n/approve <DOCTOR ID>"
                }
            )

        return []
