from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import get_patient_details


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

        patient_details: Dict = get_patient_details()
        if patient_details:
            text = (
                f"Patient Details\n\n"
                + f"Name: {patient_details.get('name', '')}\n"
                + f"Age: {patient_details.get('age', '')}\n"
                + f"Phone: {patient_details.get('phone', '')}\n"
                + f"Email: {patient_details.get('email', '')}\n\n"
                + f"Is this correct?"
            )
            reply_markup = {
                "keyboard": [["Yes", "No"]],
            }
            json_message = {"text": text, "reply_markup": reply_markup}
            dispatcher.utter_message(json_message=json_message)
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
