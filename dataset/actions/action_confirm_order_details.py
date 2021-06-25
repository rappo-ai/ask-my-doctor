from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import (
    print_appointment_details,
    print_patient_details,
)


class ActionConfirmOrderDetails(Action):
    def name(self) -> Text:
        return "action_confirm_order_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = (
            f"You have requested for an appointment with the following details:\n\n"
            + print_appointment_details()
            + "\n"
            + f"Patient details\n\n"
            + print_patient_details()
            + "\n\n"
            + f"Is this correct?"
        )
        reply_markup = {
            "keyboard": [["Yes", "No"]],
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
