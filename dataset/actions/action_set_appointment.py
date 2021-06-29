from datetime import datetime, timedelta, timezone
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.cart import add_cart, get_cart, update_cart
from actions.utils.date import DATE_FORMAT
from actions.utils.doctor import get_doctor


class ActionSetAppointment(Action):
    def name(self) -> Text:
        return "action_set_appointment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        doctor_id = tracker.get_slot("appointment__doctor_id")
        date: Text = tracker.get_slot("appointment__date")
        time: Text = tracker.get_slot("appointment__time")

        time_iter = iter(time.split(":", 1))
        hour = int(next(time_iter, 0))
        minute = int(next(time_iter, 0))
        tzinfo = timezone(timedelta(hours=5, minutes=30))
        appointment_datetime = datetime.strptime(date, DATE_FORMAT).replace(
            hour=hour, minute=minute, tzinfo=tzinfo
        )

        doctor = get_doctor(doctor_id)
        cart_item = {
            "doctor_id": doctor_id,
            "appointment_datetime": appointment_datetime.isoformat(),
            "amount": doctor.get("fee"),
        }
        cart = get_cart(user_id)
        if cart:
            update_cart(user_id, [cart_item])
        else:
            add_cart(user_id, [cart_item])
        return []
