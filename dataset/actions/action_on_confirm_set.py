from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionOnConfirmSet(Action):
    def name(self) -> Text:
        return "action_on_confirm_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot("confirm__slot")
        intent_name = tracker.get_slot("confirm_intent")
        if slot_value == "Yes" and intent_name == "EXTERNAL_confirm_patient":
            events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text="/EXTERNAL_confirm_order_details",
                    parse_data={"intent": {"name": "EXTERNAL_confirm_order_details"}},
                    input_channel="telegram",
                ),
            ]
        elif slot_value == "No" and intent_name == "EXTERNAL_confirm_patient":
            events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text="/EXTERNAL_update_patient",
                    parse_data={"intent": {"name": "EXTERNAL_update_patient"}},
                    input_channel="telegram",
                ),
            ]
        elif slot_value == "Yes" and intent_name == "EXTERNAL_confirm_order_details":
            events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text="/EXTERNAL_create_order",
                    parse_data={"intent": {"name": "EXTERNAL_create_order"}},
                    input_channel="telegram",
                ),
            ]
        else:
            events = [
                ActionExecuted("action_listen"),
                UserUttered(
                    text="/EXTERNAL_change_order",
                    parse_data={"intent": {"name": "EXTERNAL_change_order"}},
                    input_channel="telegram",
                ),
            ]

        return events
