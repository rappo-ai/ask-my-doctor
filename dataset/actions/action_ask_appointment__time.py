from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActiveLoop
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.buttons import add_padding
from actions.utils.date import format_appointment_time
from actions.utils.doctor import (
    get_available_time_slots,
    get_doctor,
    is_approved_and_activated_doctor,
)


class ActionAskAppointmentTime(Action):
    def name(self) -> Text:
        return "action_ask_appointment__time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        doctor_id = tracker.get_slot("appointment__doctor_id")
        doctor: Dict = get_doctor(doctor_id)
        if not is_approved_and_activated_doctor(doctor_id):
            dispatcher.utter_message(
                json_message={
                    "text": f"{doctor.get('name')} is currently unavailable. Please create a new booking with a different doctor."
                }
            )
            return [ActiveLoop(None)]
        appointment_date = tracker.get_slot("appointment__date")
        availaible_time_slots = [
            format_appointment_time(s)
            for s in get_available_time_slots(doctor_id, appointment_date)
        ]
        if not availaible_time_slots:
            dispatcher.utter_message(
                json_message={
                    "text": f"There are no slots available for {doctor.get('name')}. Please check again tomorrow."
                }
            )
            return [ActiveLoop(None)]
        row_width = 4
        add_padding(availaible_time_slots, row_width)
        text = f"Please pick a time slot:"
        reply_markup = {
            "keyboard": [[s for s in availaible_time_slots]],
            "row_width": row_width,
            "resize_keyboard": True,
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
