from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionAskYesNoConfirmUserInput(Action):
    def name(self) -> Text:
        return "action_ask_yes_no_confirm__user_input"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = tracker.get_slot("yes_no_confirm__message")
        if not text:
            text = "Is this correct ?"

        reply_markup = {
            "keyboard": [["Yes", "No"]],
            "resize_keyboard": True,
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
