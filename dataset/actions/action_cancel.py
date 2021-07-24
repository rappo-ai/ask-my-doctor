from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionCancel(Action):
    def name(self) -> Text:
        return "action_cancel"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = (
            "Do you want to continue to answer the previous questions in the form ?\n"
        )
        reply_markup = {
            "keyboard": [["Yes", "No"]],
            "resize_keyboard": True,
        }
        json_message = {"text": text, "reply_markup": reply_markup}

        dispatcher.utter_message(json_message=json_message)

        return []
