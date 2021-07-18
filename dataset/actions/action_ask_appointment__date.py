from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActiveLoop
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.buttons import add_padding
from actions.utils.date import format_appointment_date
from actions.utils.doctor import (
    get_available_appointment_dates,
    get_doctor,
    is_approved_and_activated_doctor,
)


class ActionAskAppointmentDate(Action):
    def name(self) -> Text:
        return "action_ask_appointment__date"

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
        upcoming_dates = [
            format_appointment_date(d)
            for d in get_available_appointment_dates(doctor_id)
        ]
        if not upcoming_dates:
            dispatcher.utter_message(
                json_message={
                    "text": f"There are no slots available for {doctor.get('name')}. Please check again tomorrow."
                }
            )
            return [ActiveLoop(None)]
        row_width = 2
        add_padding(upcoming_dates, row_width)
        text = f"Please pick a date:"
        reply_markup = {
            "keyboard": [[s for s in upcoming_dates]],
            "resize_keyboard": True,
            "row_width": row_width,
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
