from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionResetAppointmentForm(Action):
    def name(self) -> Text:
        return "action_reset_appointment_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", {})
        doctor_id = next(
            iter([e.get("value") for e in entities if e.get("entity") == "doctor_id"])
        )
        return [
            SlotSet("appointment__doctor_id", doctor_id),
            SlotSet("appointment__date", None),
            SlotSet("appointment__time", None),
        ]
