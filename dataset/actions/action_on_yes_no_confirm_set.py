from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionOnYesNoConfirmSet(Action):
    def name(self) -> Text:
        return "action_on_yes_no_confirm_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_input = tracker.get_slot("yes_no_confirm__user_input")
        if user_input == "Yes":
            intent = tracker.get_slot("yes_no_confirm__yes_intent")
        else:
            intent = tracker.get_slot("yes_no_confirm__no_intent")

        events = [
            ActionExecuted("action_listen"),
            UserUttered(
                text=f"/{intent}",
                parse_data={"intent": {"name": intent}},
                input_channel="telegram",
            ),
        ]
        return events
