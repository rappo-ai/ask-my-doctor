from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.entity import get_entity


class ActionResetDoctorSendMessageForm(Action):
    def name(self) -> Text:
        return "action_reset_doctor_send_message_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])
        order_id = get_entity(entities, "o_id", "")
        return [
            SlotSet("doctor_send_message__order_id", order_id),
            SlotSet("doctor_send_message__message_id", None),
        ]
