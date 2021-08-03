from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered, SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.patient import get_patient_for_user_id, print_patient


class ActionConfirmPatient(Action):
    def name(self) -> Text:
        return "action_confirm_patient"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        events: List[Dict[Text, Any]] = []

        user_id = tracker.sender_id
        patient: Dict = get_patient_for_user_id(user_id)
        if patient:
            text = f"Patient Details\n\n" + print_patient(patient) + "\n\n"
            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)
            events = [SlotSet("confirm_intent", "EXTERNAL_confirm_patient")]
        else:
            events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text="/EXTERNAL_update_patient",
                    parse_data={"intent": {"name": "EXTERNAL_update_patient"}},
                    input_channel="telegram",
                ),
            ]

        return events
