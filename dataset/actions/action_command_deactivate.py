import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, is_admin_group
from actions.utils.doctor import (
    LISTING_STATUS_DISABLED,
    get_doctor,
    get_doctor_card,
    get_doctor_for_user_id,
    is_approved_doctor,
    update_doctor,
)


class ActionCommandDeactivate(Action):
    def name(self) -> Text:
        return "action_command_deactivate"

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
        regex = r"^(/\w+)(\s+#(\w+))?$"
        if _is_admin_group:
            regex = r"^(/\w+)(\s+#(\w+))$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            doctor = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["listing_status"] = LISTING_STATUS_DISABLED
            update_doctor(doctor)

            doctor_card = get_doctor_card(doctor)

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": get_admin_group_id()}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id} has been deactivated by {command_user}.",
                }
            )

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": doctor["user_id"]}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f"Your listing has been deactivated by {command_user}. You can re-activate your listing with /activate.\n"
                    ),
                }
            )

        else:
            usage = "/deactivate"
            if _is_admin_group:
                usage = "/deactivate <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )

        return []
