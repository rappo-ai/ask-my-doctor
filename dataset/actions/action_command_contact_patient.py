import re
from typing import Any, AnyStr, Dict, List, Match, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.json import get_json_key
from actions.utils.order import get_order


class ActionCommandListDoctors(Action):
    def name(self) -> Text:
        return "action_command_contact_patient"

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
        regex = r"^(/\w+)\s+#(.+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        order_id = matches and matches.group(2)
        order = order_id and get_order(order_id)

        if order and reply_message_id:
            patient: Dict = get_json_key(order, "metadata.patient")
            dispatcher.utter_message(
                json_message={
                    "chat_id": patient.get("user_id"),
                    "text": f"Incoming message from ADMIN for order #{order_id}.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": patient.get("user_id"),
                    "from_chat_id": tracker.sender_id,
                    "message_id": reply_message_id,
                }
            )
        else:
            usage = "/contactpatient <ORDER_ID>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nYou must reply to an existing message to use this command."
                }
            )
        return []
