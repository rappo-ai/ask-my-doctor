# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.bl import   get_specialities

class ActionAskNewAppointmentRequestSpeciality(Action):
    def name(self) -> Text:
        return "action_ask_new_appointment_request__speciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = f"Please select the speciality you are looking for:"
        specialities = get_specialities()
        reply_markup = 
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
