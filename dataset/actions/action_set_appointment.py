from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import set_appointment_details


class ActionSetAppointment(Action):
    def name(self) -> Text:
        return "action_set_appointment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        doctor_name = tracker.get_slot("appointment__doctor")
        speciality = tracker.get_slot("appointment__speciality")
        date = tracker.get_slot("appointment__date")
        time = tracker.get_slot("appointment__time")
        set_appointment_details(
            doctor_name=doctor_name, speciality=speciality, date=date, time=time
        )
        return []
