from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.json import get_json_key
from actions.utils.order import get_order


class ActionAskDoctorSendMessageMessageId(Action):
    def name(self) -> Text:
        return "action_ask_doctor_send_message__message_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        order_id: Text = tracker.get_slot("doctor_send_message__order_id")
        order: Dict = get_order(order_id)
        patient: Dict = get_json_key(order, "metadata.patient")
        text = f"Please enter the message you want to send to {patient.get('name')} for order #{order_id}."
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
