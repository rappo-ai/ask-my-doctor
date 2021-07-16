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


class ActionDoctorSetGoogleAuth(Action):
    def name(self) -> Text:
        return "action_on_order_unlocked"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])
        order_id: Dict = get_entity(entities, "order_id")
        order = get_order(order_id)
        doctor_id = get_json_key(order, "cart.doctor_id")
        appointment_datetime = datetime.fromisoformat(
            get_json_key(order, "cart.appointment_datetime")
        )
        date = format_appointment_date(appointment_datetime)
        time = format_appointment_time(appointment_datetime)
        doctor = get_doctor(doctor_id)
        doctor_name = doctor.get("name")
        dispatcher.utter_message(
            json_message={
                "text": f"Your pending order #{order_id} for appointment with {doctor_name} on {date} at {time} has expired. Please create a new booking.",
            }
        )

        return []
