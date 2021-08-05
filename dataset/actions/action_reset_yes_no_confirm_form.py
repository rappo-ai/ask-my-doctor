from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionResetYesNoConfirmForm(Action):
    def name(self) -> Text:
        return "action_reset_yes_no_confirm_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            SlotSet("yes_no_confirm__user_input", None),
            SlotSet("yes_no_confirm__message", None),
        ]
