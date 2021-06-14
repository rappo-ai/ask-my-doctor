# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher

class ActionCreateAppointment(Action):

    def name(self) -> Text:
        return "action_create_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [ActionExecuted("action_listen"), UserUttered(text="/EXTERNAL_new_patient", parse_data={"intent":{"name": "EXTERNAL_new_patient"}}, input_channel="telegram")]
