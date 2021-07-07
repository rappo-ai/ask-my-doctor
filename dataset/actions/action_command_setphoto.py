import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, is_admin_group
from actions.utils.doctor import (
    get_doctor,
    get_doctor_for_user_id,
    is_approved_doctor,
    update_doctor,
)
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

        message_text = tracker.latest_message.get("text")
        metadata = tracker.latest_message.get("metadata")
        regex = r"^(/\w+)(\s+#(\w+))?$"
        if _is_admin_group:
            regex = r"^(/\w+)(\s+#(\w+))$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        photo = validate_photo(metadata)
        if matches and photo:
            doctor = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["photo"] = photo
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, photo has been updated.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f"Your photo has been updated.\n",
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
