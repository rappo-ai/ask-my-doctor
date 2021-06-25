from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionOnAppointmentSet(Action):
    def name(self) -> Text:
        return "action_on_appointment_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/EXTERNAL_confirm_patient",
                parse_data={"intent": {"name": "EXTERNAL_confirm_patient"}},
                input_channel="telegram",
            ),
        ]
