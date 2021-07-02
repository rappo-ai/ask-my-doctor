import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.validate import (
    validate_age,
    validate_email,
    validate_name,
    validate_phone_number,
)


class ValidatePatientForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_patient_form"

    def validate_patient__name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        patient_name = validate_name(slot_value)
        if patient_name:
            return {"patient__name": patient_name}
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "Name cannot contain special characters other than apostrophe or period."
                }
            )
            return {"patient__name": None}

    def validate_patient__age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        age = validate_age(slot_value)
        if age:
            return {"patient__age": age}
        else:
            dispatcher.utter_message(
                json_message={"text": "Age must be a number between 0 and 120."}
            )
            return {"patient__age": None}

    def validate_patient__phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        phone_number = validate_phone_number(slot_value)
        if phone_number:
            return {"patient__phone_number": phone_number}
        else:
            dispatcher.utter_message(
                json_message={"text": "Phone number must be a 10-digit mobile number."}
            )
            return {"patient__phone_number": None}

    def validate_patient__email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        email = validate_email(slot_value)
        if email:
            return {"patient__email": email}
        else:
            dispatcher.utter_message(
                json_message={"text": "This email id is not a valid format."}
            )
            return {"patient__email": None}
