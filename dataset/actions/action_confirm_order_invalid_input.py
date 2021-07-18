from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUtteranceReverted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionConfirmOrderInvalidInput(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_confirm_order_invalid_input"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = "Invalid Input"
        json_message = {"text": text}

        dispatcher.utter_message(json_message=json_message)

        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/EXTERNAL_confirm_order_details",
                parse_data={"intent": {"name": "EXTERNAL_confirm_order_details"}},
                input_channel="telegram",
            ),
        ]
