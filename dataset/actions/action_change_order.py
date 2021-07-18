from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionChangeOrder(Action):
    def name(self) -> Text:
        return "action_change_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/menu",
                parse_data={"intent": {"name": "menu"}},
                input_channel="telegram",
            ),
        ]
