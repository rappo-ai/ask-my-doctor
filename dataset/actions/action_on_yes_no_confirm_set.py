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

        next_intent_name = "nlu_fallback"
        latest_message_intent = tracker.latest_message.get("intent", {})
        latest_message_intent_name = latest_message_intent.get("name")
        if latest_message_intent_name == "affirm":
            next_intent_name = tracker.get_slot("yes_no_confirm__yes_intent")
        elif latest_message_intent_name == "deny":
            next_intent_name = tracker.get_slot("yes_no_confirm__no_intent")
        if not next_intent_name:
            next_intent_name = "nlu_fallback"

        events = [
            ActionExecuted("action_listen"),
            UserUttered(
                text=f"/{next_intent_name}",
                parse_data={"intent": {"name": next_intent_name}},
                input_channel="telegram",
            ),
        ]
        return events
