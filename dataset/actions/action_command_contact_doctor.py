import re
from typing import Any, AnyStr, Dict, List, Match, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import get_doctor, get_doctors
from actions.utils.json import get_json_key
from actions.utils.order import get_order
from actions.utils.text import format_count


class ActionCommandContactDoctor(Action):
    def name(self) -> Text:
        return "action_command_contact_doctor"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        reply_message_id = get_json_key(
            tracker.latest_message, "metadata.message.reply_to_message.message_id"
        )
        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+#(.+)?$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        object_id = matches and matches.group(2)
        order = object_id and get_order(object_id)
        doctor = object_id and get_doctor(object_id)

        if reply_message_id:
            if order:
                doctor: Dict = get_json_key(order, "metadata.doctor")

            target_doctors = []
            if doctor:
                target_doctors.append(doctor)
            else:
                target_doctors = [d for d in get_doctors()]

            for d in target_doctors:
                dispatcher.utter_message(
                    json_message={
                        "chat_id": d.get("user_id"),
                        "text": f"Message from ADMIN{(' for order #' + object_id) if order else ''}.",
                    }
                )
                dispatcher.utter_message(
                    json_message={
                        "chat_id": d.get("user_id"),
                        "from_chat_id": tracker.sender_id,
                        "message_id": reply_message_id,
                    }
                )

            dispatcher.utter_message(
                json_message={
                    "text": f"Your message was sent to {len(target_doctors)} {format_count('doctor', 'doctors', len(target_doctors))}."
                }
            )
        else:
            usage = "/contactdoctor <ORDER ID>[OPTIONAL] <DOCTOR ID>[OPTIONAL]"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nYou must reply to an existing message to use this command. Without any arguments, this will broadcast to all doctors. If using an optional argument, please use exactly one - either the ORDER ID or DOCTOR ID."
                }
            )
        return []
