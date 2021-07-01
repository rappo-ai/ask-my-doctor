import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.admin_config import get_specialities


class ValidateDoctorSignupForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_doctor_signup_form"

    def validate_doctor_signup__name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        doctor_name = str(slot_value).strip()
        if re.search(r"^[a-zA-Z.' ]+$", doctor_name):
            return {"doctor_signup__name": doctor_name}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Name cannot contain special characters other than apostrophe or period."
                }
            )
            return {"doctor_signup__name": None}

    def validate_doctor_signup__number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        phone_number = str(slot_value).strip()
        if re.search(r"^[1-9]\d{9}$", phone_number):
            return {"doctor_signup__number": phone_number}
        else:
            dispatcher.utter_custom_json(
                json_message={"text": "Phone number must be a 10-digit mobile number."}
            )
            return {"doctor_signup__number": None}

    def validate_doctor_signup__speciality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in get_specialities():
            return {"doctor_signup__speciality": slot_value}
        else:
            dispatcher.utter_custom_json(json_message={"text": "Invalid input."})
            return {"doctor_signup__speciality": None}

    def validate_doctor_signup__description(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if len(slot_value) <= 200:
            return {"doctor_signup__description": slot_value}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Description cannot be more than 200 characters long."
                }
            )
            return {"doctor_signup__description": None}

    def validate_doctor_signup__availability(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"doctor_signup__availability": slot_value}

    def validate_doctor_signup__consultation_fee(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        fee = str(slot_value).strip()
        if re.search(r"^[1-9][0-9]*50$|^[1-9][0-9]*00$", fee):
            return {"doctor_signup__consultation_fee": fee}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Consultation fee must be a number in multiples of 50. The minimum fee is 100. The amount is automatically converted to Rupees, so no need to add the Rupee prefix / suffix."
                }
            )
            return {"doctor_signup__consultation_fee": None}

    def validate_doctor_signup__bank_account_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        account_number = str(slot_value).strip()
        if re.search(r"^\d{9,18}$", account_number):
            return {"doctor_signup__bank_account_number": account_number}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Bank account number must be between 9-18 digits."
                }
            )
            return {"doctor_signup__bank_account_number": None}

    def validate_doctor_signup__bank_account_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        account_name = str(slot_value).strip()
        if re.search(r"^[a-zA-Z.' ]+$", account_name):
            return {"doctor_signup__bank_account_name": account_name}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Name cannot contain special characters other than apostrophe or period."
                }
            )
            return {"doctor_signup__bank_account_name": None}

    def validate_doctor_signup__bank_account_ifsc(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ifsc_code = str(slot_value).strip()
        if re.search(r"^[A-Za-z]{4}[a-zA-Z0-9]{7}$", ifsc_code):
            return {"doctor_signup__bank_account_ifsc": ifsc_code}
        else:
            dispatcher.utter_custom_json(
                json_message={
                    "text": "Bank account IFSC code must be exactly 11 alpha-numeric characters, and the first four cannot be digits."
                }
            )
            return {"doctor_signup__bank_account_ifsc": None}
