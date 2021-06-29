from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_upcoming_appointment_dates


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
        upcoming_dates = get_upcoming_appointment_dates(doctor_id)
        text = f"Please pick a date:"
        reply_markup = {
            "keyboard": [[s] for s in upcoming_dates],
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
