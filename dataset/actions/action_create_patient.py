# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionCreatePatient(Action):
    def name(self) -> Text:
        return "action_create_patient"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = (
            f"You have requested for an appointment with the following details:\n\n"
            + f"Doctor's name: {tracker.get_slot('new_appointment_request__doctor')}\n"
            + f"Speciality: {tracker.get_slot('new_appointment_request__speciality')}\n"
            + f"Date: {tracker.get_slot('new_appointment_request__date')}\n"
            + f"Time: {tracker.get_slot('new_appointment_request__time')}\n\n"
            + f"Patient details\n\n"
            + f"Name: {tracker.get_slot('new_patient__name')}\n"
            + f"Age: {tracker.get_slot('new_patient__age')}\n"
            + f"Phone number: {tracker.get_slot('new_patient__phone_number')}"
        )

        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/EXTERNAL_create_order",
                parse_data={"intent": {"name": "EXTERNAL_create_order"}},
                input_channel="telegram",
            ),
        ]
