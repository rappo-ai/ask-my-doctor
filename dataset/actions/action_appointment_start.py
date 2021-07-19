from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctor


class ActionAppointmentStart(Action):
    def name(self) -> Text:
        return "action_appointment_start"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        doctor_id = tracker.get_slot("appointment__doctor_id")
        doctor: Dict = get_doctor(doctor_id)
        text = f"New appointment request for {doctor.get('name')}."
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
