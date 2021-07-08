from copy import deepcopy
import logging
import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import (
    get_doctor,
    get_doctor_for_user_id,
    is_approved_doctor,
    print_doctor_profile,
)

logger = logging.getLogger(__name__)


class ActionCommandProfile(Action):
    def name(self) -> Text:
        return "action_command_profile"

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

            caption = print_doctor_profile(
                doctor, include_time_slots=True, include_google_id=True
            )
            json_message = {"photo": doctor.get("photo"), "caption": caption}
            dispatcher.utter_message(json_message=json_message)
        else:
            usage = "/profile"
            if _is_admin_group:
                usage = "/profile <DOCTOR ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )
        return []
