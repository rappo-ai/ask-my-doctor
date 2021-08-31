from base64 import b64decode
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, SlotSet, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionStart(Action):
    def name(self) -> Text:
        return "action_start"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text: Text = tracker.latest_message.get("text")
        args = message_text.split(" ", 2)
        out_events = []
        if len(args) == 2:
            speciality = b64decode(args[1]).decode("utf-8")
            out_events = [
                SlotSet("search__speciality", speciality),
                ActionExecuted("action_listen"),
                UserUttered(
                    text=f"/searchset",
                    parse_data={"intent": {"name": "searchset"}},
                    input_channel="telegram",
                ),
            ]
        else:
            first_name = tracker.get_slot("first_name")
            dispatcher.utter_message(
                text=f"Hi {first_name}! I am here to assist you in connecting with doctors and scheduling appointments with them."
            )
            out_events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text=f"/menu",
                    parse_data={"intent": {"name": "menu"}},
                    input_channel="telegram",
                ),
            ]
        return out_events
