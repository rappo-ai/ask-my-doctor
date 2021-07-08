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


class ActionCommandActivate(Action):
    def name(self) -> Text:
        return "action_command_activate"

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
        regex = r"^(/\w+)(\s+#(\w+))?$"
        if _is_admin_group:
            regex = r"^(/\w+)(\s+#(\w+))$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            doctor: Dict = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            if not doctor.get("credentials"):
                dispatcher.utter_message(
                    json_message={
                        "chat_id": get_admin_group_id(),
                        "text": f"{doctor['name']} with ID #{doctor_id} cannot be activated, missing Google auth. Doctor needs to use /setgoogleid.",
                    }
                )
                dispatcher.utter_message(
                    json_message={
                        "chat_id": doctor["user_id"],
                        "text": f"Your listing cannot be activated as you are yet to connect a Google ID to schedule meetings. Please use /setgoogleid.",
                    }
                )
                return
            if all(value == [] for value in doctor.get("time_slots", {}).values()):
                dispatcher.utter_message(
                    json_message={
                        "chat_id": get_admin_group_id(),
                        "text": f"{doctor['name']} with ID #{doctor_id} cannot be activated, missing time slots. Use \"/settimeslots #{doctor_id} <TIME_SLOTS>\".",
                    }
                )
                dispatcher.utter_message(
                    json_message={
                        "chat_id": doctor["user_id"],
                        "text": f"Your listing cannot be activated as you haven't added your time slots. Please use /settimeslots.",
                    }
                )
                return
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
            if _is_admin_group:
                usage = "/activate <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )

        return []
