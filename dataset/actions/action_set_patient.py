from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import set_patient_details


class ActionSetPatient(Action):
    def name(self) -> Text:
        return "action_set_patient"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("patient__name")
        age = tracker.get_slot("patient__age")
        phone = tracker.get_slot("patient__phone_number")
        email = tracker.get_slot("patient__email")
        set_patient_details(name=name, age=age, phone=phone, email=email)
        return []
