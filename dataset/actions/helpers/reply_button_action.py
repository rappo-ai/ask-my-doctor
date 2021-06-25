# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ReplyButtonAction(Action):
    def name(self) -> Text:
        return "reply_button_action"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        json_message = {"text": self.text, "reply_markup": self.reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
