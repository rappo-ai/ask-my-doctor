import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, is_admin_group
from actions.utils.doctor import (
    get_doctor,
    get_doctor_card,
    get_doctor_for_user_id,
    is_approved_doctor,
    update_doctor,
)
from actions.utils.command import match_command
from actions.utils.validate import validate_photo


class ActionCommandSetPhoto(Action):
    def name(self) -> Text:
        return "action_command_setphoto"

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
        metadata = tracker.latest_message.get("metadata")
        command = match_command(message_text, _is_admin_group)
        photo = validate_photo(
            metadata,
            min_size=(256, 256),
            target_size=(512, 512),
            target_chat_id=tracker.sender_id,
        )
        if photo:
            doctor = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = command["doctor_id"]
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["photo"] = photo
            update_doctor(doctor)

            doctor_card = get_doctor_card(doctor)

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": get_admin_group_id()}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, photo has been updated by {command_user}.",
                }
            )

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": doctor["user_id"]}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f"Your photo has been updated by {command_user}.\n",
                }
            )
        else:
            usage = "/setphoto"
            if _is_admin_group:
                usage = "/setphoto <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nYou must reply to an image message with this command to set that image as the photo."
                }
            )

        return []
