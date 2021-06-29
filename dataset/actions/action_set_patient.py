from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.patient import add_patient, get_patient_for_user_id, update_patient


class ActionSetPatient(Action):
    def name(self) -> Text:
        return "action_set_patient"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        patient = get_patient_for_user_id(user_id) or {}
        patient["name"] = tracker.get_slot("patient__name")
        patient["age"] = tracker.get_slot("patient__age")
        patient["phone"] = tracker.get_slot("patient__phone_number")
        patient["email"] = tracker.get_slot("patient__email")
        patient["user_id"] = user_id
        if patient.get("_id"):
            update_patient(patient)
        else:
            add_patient(patient)
        return []
