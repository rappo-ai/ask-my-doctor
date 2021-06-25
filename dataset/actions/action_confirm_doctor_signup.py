from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import (
    get_google_auth_url,
    print_doctor_signup_data,
    set_doctor_signup_data,
)


class ActionConfirmDoctorSignup(Action):
    def name(self) -> Text:
        return "action_confirm_doctor_signup"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("doctor_signup__name")
        phone_number = tracker.get_slot("doctor_signup__number")
        speciality = tracker.get_slot("doctor_signup__speciality")
        availability = tracker.get_slot("doctor_signup__availability")
        consultation_fee = tracker.get_slot("doctor_signup__consultation_fee")
        bank_account_number = tracker.get_slot("doctor_signup__bank_account_number")
        bank_account_name = tracker.get_slot("doctor_signup__bank_account_name")
        bank_account_ifsc = tracker.get_slot("doctor_signup__bank_account_ifsc")

        set_doctor_signup_data(
            name,
            phone_number,
            speciality,
            availability,
            consultation_fee,
            bank_account_number,
            bank_account_name,
            bank_account_ifsc,
        )
        google_auth_url = get_google_auth_url()
        text = (
            f"Doctor Signup Details\n"
            + f"\n"
            + print_doctor_signup_data()
            + f"\n"
            + f"Ask My Doctor automatically schedules meetings on your behalf using Google Meet. To complete the process, please click {google_auth_url} to connect your Google ID and authorize us to create meetings on your behalf.\n"
            + f"\n"
            + "Please click /signup to make any changes to your details."
        )
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)
        return []
