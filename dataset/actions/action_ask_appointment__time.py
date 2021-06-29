from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_available_time_slots


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
        appointment_date = tracker.get_slot("appointment__date")
        availaible_time_slots = get_available_time_slots(doctor_id, appointment_date)
        text = f"Please pick a time slot:"
        reply_markup = {
            "keyboard": [[s] for s in availaible_time_slots],
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
