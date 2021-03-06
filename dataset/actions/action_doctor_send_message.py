import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctor
from actions.utils.json import get_json_key
from actions.utils.order import get_order


logger = logging.getLogger(__name__)


class ActionDoctorSendMessage(Action):
    def name(self) -> Text:
        return "action_doctor_send_message"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        events: List[Dict[Text, Any]] = []

        message_id = tracker.get_slot("doctor_send_message__message_id")
        order_id = tracker.get_slot("doctor_send_message__order_id")

        try:
            order = get_order(order_id)
            cart_items = get_json_key(order, "cart.items")
            cart_item = next(iter(cart_items))
            doctor_id = cart_item.get("doctor_id")
            doctor: Dict = get_doctor(doctor_id)
            patient: Dict = get_json_key(order, "metadata.patient")
            dispatcher.utter_message(
                json_message={
                    "chat_id": patient.get("user_id"),
                    "text": f"Incoming message from {doctor.get('name')} for order #{order_id}.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": patient.get("user_id"),
                    "from_chat_id": doctor.get("user_id"),
                    "message_id": message_id,
                }
            )
            dispatcher.utter_message(
                json_message={
                    "text": f"Your message was sent successfully to {patient.get('name')}.",
                }
            )
        except Exception as e:
            logger.error(
                f"Error sending doctor message to patient for order #{order_id}"
            )
            logger.error(str(e))
            dispatcher.utter_message(
                json_message={
                    "text": "Error sending your message. Please use /help to contact support.",
                }
            )

        return events
