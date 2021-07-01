import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict


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
        patient_name = str(slot_value).strip()
        if re.search(r"^[a-zA-Z.' ]+$", patient_name):
            return {"patient__name": patient_name}
        else:
            dispatcher.utter_custom_json(
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
        age = str(slot_value).strip()
        if re.search(r"^1[0-1][0-9]$|^[1-9][0-9]$|^[0-9]$", age):
            return {"patient__age": age}
        else:
            dispatcher.utter_custom_json(
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
        phone_number = str(slot_value).strip()
        if re.search(r"^[1-9]\d{9}$", phone_number):
            return {"patient__phone_number": phone_number}
        else:
            dispatcher.utter_custom_json(
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
        email = str(slot_value).strip()
        if re.search(
            r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$",
            email,
        ):
            return {"patient__email": email}
        else:
            dispatcher.utter_custom_json(
                json_message={"text": "This email id is not a valid format."}
            )
            return {"patient__email": None}
