from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionMainMenu(Action):
    def name(self) -> Text:
        return "action_main_menu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = "What would you like to do?"
        reply_markup = {
            "keyboard": [["Browse Doctors", "Contact Support"]],
            "resize_keyboard": True,
        }
        json_message = {"text": text, "reply_markup": reply_markup}

        dispatcher.utter_message(json_message=json_message)

        return []
