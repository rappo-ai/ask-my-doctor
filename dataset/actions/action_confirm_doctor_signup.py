from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import (
    add_doctor,
    get_doctor_for_user_id,
    print_doctor_signup_form,
    update_doctor,
)
from actions.utils.meet import get_google_auth_url


class ActionConfirmDoctorSignup(Action):
    def name(self) -> Text:
        return "action_confirm_doctor_signup"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id
        google_auth_url = get_google_auth_url(user_id)
        doctor = get_doctor_for_user_id(user_id) or {}
        doctor["user_id"] = user_id
        doctor["onboarding_status"] = "form"
        doctor["name"] = tracker.get_slot("doctor_signup__name")
        doctor["phone_number"] = tracker.get_slot("doctor_signup__number")
        doctor["speciality"] = tracker.get_slot("doctor_signup__speciality")
        doctor["description"] = tracker.get_slot("doctor_signup__description")
        doctor["availability"] = tracker.get_slot("doctor_signup__availability")
        doctor["fee"] = int(tracker.get_slot("doctor_signup__consultation_fee"))
        doctor["bank_account_number"] = tracker.get_slot(
            "doctor_signup__bank_account_number"
        )
        doctor["bank_account_name"] = tracker.get_slot(
            "doctor_signup__bank_account_name"
        )
        doctor["bank_account_ifsc"] = tracker.get_slot(
            "doctor_signup__bank_account_ifsc"
        )
        doctor["google_auth_url"] = google_auth_url
        if doctor.get("_id"):
            update_doctor(doctor)
        else:
            add_doctor(doctor)
        text = (
            f"Doctor Signup Details\n"
            + f"\n"
            + print_doctor_signup_form(doctor)
            + f"\n"
            + f"Ask My Doctor automatically schedules meetings on your behalf using Google Meet. To complete the process, please click {google_auth_url} to connect your Google ID and authorize us to create meetings on your behalf.\n"
            + f"\n"
            + "Please click /signup to make any changes to your details."
        )
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)
        return []
