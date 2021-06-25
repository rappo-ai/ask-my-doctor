from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import get_patient_details


class ActionOnPatientSet(Action):
    def name(self) -> Text:
        return "action_on_patient_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/EXTERNAL_confirm_order_details",
                parse_data={"intent": {"name": "EXTERNAL_confirm_order_details"}},
                input_channel="telegram",
            ),
        ]
