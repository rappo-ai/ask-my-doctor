import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict


class ValidateConfirmForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_confirm_form"

    def validate_confirm__slot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        values = ["Yes", "No"]
        if slot_value in values:
            return {"confirm__slot": slot_value}
        else:
            dispatcher.utter_message(json_message={"text": "Invalid input."})
            return {"confirm__slot": None}
