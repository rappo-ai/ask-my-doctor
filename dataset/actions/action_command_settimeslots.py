import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id, is_admin_group
from actions.utils.date import print_time_slots
from actions.utils.doctor import (
    get_doctor,
    get_doctor_card,
    get_doctor_for_user_id,
    is_approved_doctor,
    update_doctor,
)
from actions.utils.validate import validate_time_slots


class ActionCommandSetTimeSlots(Action):
    def name(self) -> Text:
        return "action_command_settimeslots"

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
        regex = r"^(/\w+)(\s+#(\w+))?(.+)$"
        if _is_admin_group:
            regex = r"^(/\w+)(\s+#(\w+))(.+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        new_time_slots = matches and validate_time_slots(matches.group(4))
        if matches and new_time_slots:
            doctor: Dict = {}
            doctor_id = ""
            if _is_admin_group:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            time_slots = doctor.get("time_slots", {})
            time_slots.update(new_time_slots)
            doctor["time_slots"] = time_slots
            update_doctor(doctor)

            doctor_card = get_doctor_card(doctor)
            time_slots_str = print_time_slots(time_slots)

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": get_admin_group_id()}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, time slots have been updated to \"{time_slots_str}\" by {command_user}.",
                }
            )

            dispatcher.utter_message(
                json_message={**doctor_card, "chat_id": doctor["user_id"]}
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f'Your time slots have been updated to "{time_slots_str}" by {command_user}.',
                }
            )
        else:
            usage = "/settimeslots <TIME SLOTS>"
            clear_slots_example = "/settimeslots Mon"
            if _is_admin_group:
                usage = "/settimeslots <DOCTOR ID> <TIME SLOTS>"
                clear_slots_example = "/settimeslots <DOCTOR ID> Mon"
            dispatcher.utter_message(
                json_message={
                    "text": f'The command format is incorrect. Usage:\n\n{usage}\n\n- Time slots must be in the format "Mon, 09:00-13:00".\n- The minutes must be either 00, 15, 30 or 45.\n- You can specify multiple slots by separating them with a comma, and multiple days by separating them with a semicolon. For example "Mon, 10:00-12:00, 14:00-17:00; Tue, 10:00-12:00, 14:00-17:00".\n- This command updates slots only for the days mentioned, leaving the other days as is. To clear the timeslots for a particular day you need to mention the day without any slots. For example "{clear_slots_example}" to clear the slots for Monday.'
                }
            )

        return []