from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionResetPatientForm(Action):
    def name(self) -> Text:
        return "action_reset_patient_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            SlotSet("patient__name", None),
            SlotSet("patient__age", None),
            SlotSet("patient__phone_number", None),
            SlotSet("patient__email", None),
        ]
