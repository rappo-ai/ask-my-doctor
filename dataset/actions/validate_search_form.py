from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.admin_config import get_specialities


class ValidateSearchForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_form"

    def validate_search__speciality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in get_specialities():
            return {"search__speciality": slot_value}
        else:
            dispatcher.utter_message(json_message={"text": "Invalid input."})
            return {"search__speciality": None}
