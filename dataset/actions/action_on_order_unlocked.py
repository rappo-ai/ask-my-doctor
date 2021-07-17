from bson.objectid import ObjectId
from datetime import datetime
import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.date import format_appointment_date, format_appointment_time
from actions.utils.doctor import get_doctor
from actions.utils.entity import get_entity
from actions.utils.json import get_json_key
from actions.utils.order import get_order

logger = logging.getLogger(__name__)


class ActionOnOrderUnlocked(Action):
    def name(self) -> Text:
        return "action_on_order_unlocked"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])
        order_id_str = get_entity(entities, "order_id")
        order_id: ObjectId = ObjectId(order_id_str)
        order = get_order(order_id)
        cart_items = get_json_key(order, "cart.items")
        cart_item = next(iter(cart_items))
        doctor_id = cart_item.get("doctor_id")
        appointment_datetime = datetime.fromisoformat(
            cart_item.get("appointment_datetime")
        )
        date = format_appointment_date(appointment_datetime)
        time = format_appointment_time(appointment_datetime)
        doctor = get_doctor(doctor_id)
        doctor_name = doctor.get("name")
        dispatcher.utter_message(
            json_message={
                "text": f"The payment link for order #{order_id} with {doctor_name} on {date} at {time} has expired. Please create a new booking.",
            }
        )

        return []
