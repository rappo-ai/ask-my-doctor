import re
from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.validate import (
    validate_bank_account_ifsc,
    validate_bank_account_number,
    validate_consulation_fee,
    validate_description,
    validate_name,
    validate_phone_number,
    validate_photo,
    validate_speciality,
)


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
        doctor_name = validate_name(slot_value)
        if doctor_name:
            return {"doctor_signup__name": doctor_name}
        else:
            dispatcher.utter_message(
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
        phone_number = validate_phone_number(slot_value)
        if phone_number:
            return {"doctor_signup__number": phone_number}
        else:
            dispatcher.utter_message(
                json_message={"text": "Phone number must be a 10-digit mobile number."}
            )
            return {"doctor_signup__number": None}

    def validate_doctor_signup__photo(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        photo = validate_photo(slot_value)
        if photo:
            return {"doctor_signup__photo": photo}
        else:
            dispatcher.utter_message(
                json_message={"text": "The message received is not a photo."}
            )
            return {"doctor_signup__photo": None}

    def validate_doctor_signup__speciality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        speciality = validate_speciality(slot_value)
        if speciality:
            return {"doctor_signup__speciality": speciality}
        else:
            dispatcher.utter_message(json_message={"text": "Invalid input."})
            return {"doctor_signup__speciality": None}

    def validate_doctor_signup__description(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        description = validate_description(slot_value)
        if description:
            return {"doctor_signup__description": description}
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "Description cannot be more than 200 characters long."
                }
            )
            return {"doctor_signup__description": None}

    def validate_doctor_signup__consultation_fee(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        fee = validate_consulation_fee(slot_value)
        if fee:
            return {"doctor_signup__consultation_fee": fee}
        else:
            dispatcher.utter_message(
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
        bank_account_number = validate_bank_account_number(slot_value)
        if bank_account_number:
            return {"doctor_signup__bank_account_number": bank_account_number}
        else:
            dispatcher.utter_message(
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
        account_name = validate_name(slot_value)
        if account_name:
            return {"doctor_signup__bank_account_name": account_name}
        else:
            dispatcher.utter_message(
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
        ifsc_code = validate_bank_account_ifsc(slot_value)
        if ifsc_code:
            return {"doctor_signup__bank_account_ifsc": ifsc_code}
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "Bank account IFSC code must be exactly 11 alpha-numeric characters, and the first four cannot be digits."
                }
            )
            return {"doctor_signup__bank_account_ifsc": None}
