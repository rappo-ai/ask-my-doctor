# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which echoes the user's incoming message as a reply

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.json import get_json_key

class ActionEcho(Action):

    def name(self) -> Text:
        return "action_echo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        reply_to_message_id = get_json_key(tracker.latest_message, "metadata.message.message_id")
        text = "You said " + get_json_key(tracker.latest_message, "metadata.message.text")
        json_message = {"text": text, "reply_to_message_id": reply_to_message_id}
        dispatcher.utter_message(json_message=json_message)

        return []
