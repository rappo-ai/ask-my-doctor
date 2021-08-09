from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, is_admin_group
from actions.utils.command import extract_doctor_command
from actions.utils.doctor import (
    get_doctor,
    get_doctor_card,
    get_doctor_for_user_id,
    is_approved_doctor,
    update_doctor,
)
from actions.utils.validate import validate_name


class ActionCommandSetName(Action):
    def name(self) -> Text:
        return "action_command_setname"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        _is_admin_group = is_admin_group(tracker.sender_id)
        if not (_is_admin_group or is_approved_doctor(tracker.sender_id)):
            return []

        command_user = "ADMIN" if _is_admin_group else "DOCTOR"
        message_text = tracker.latest_message.get("text")
        command = extract_doctor_command(message_text, _is_admin_group)
        name = command and validate_name(command["args"])
        if command and name:
            if _is_admin_group:
                doctor_id = command["doctor_id"]
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])

            doctor["name"] = name
            update_doctor(doctor)

            doctor_card = get_doctor_card(doctor)
            admin_doctor_card = get_doctor_card(doctor, True)

            dispatcher.utter_message(
                json_message={
                    **admin_doctor_card,
                    "chat_id": get_admin_group_id(),
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, name has been updated to \"{name}\" by {command_user}.",
                }
            )

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": doctor["user_id"]}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f'Your name has been updated to "{name}" by {command_user}.\n',
                }
            )
        else:
            usage = "/setname <NAME>"
            if _is_admin_group:
                usage = "/setname <DOCTOR ID> <NAME>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nName cannot contain special characters other than apostrophe or period."
                }
            )

        return []
