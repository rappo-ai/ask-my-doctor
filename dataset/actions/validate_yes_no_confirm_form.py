import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict


class ValidateYesNoConfirmForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_yes_no_confirm_form"

    def validate_yes_no_confirm__user_input(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        values = ["Yes", "No"]
        if slot_value in values:
            return {"yes_no_confirm__user_input": slot_value}
        else:
            dispatcher.utter_message(
                json_message={"text": "Invalid input. Please enter Yes or No."}
            )
            return {"yes_no_confirm__user_input": None}
