from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctor
from actions.utils.order import get_order


class ActionAskPatientSendMessageMessageId(Action):
    def name(self) -> Text:
        return "action_ask_patient_send_message__message_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        order_id: Text = tracker.get_slot("patient_send_message__order_id")
        order: Dict = get_order(order_id)
        cart: Dict = order.get("cart")
        cart_item: Dict = next(iter(cart.get("items")))
        doctor_id = cart_item.get("doctor_id")
        doctor: Dict = get_doctor(doctor_id)
        text = f"Please enter the message you want to send to {doctor.get('name')} for order #{order_id}."
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
