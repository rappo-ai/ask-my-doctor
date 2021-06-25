from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionResetDoctorSignupForm(Action):
    def name(self) -> Text:
        return "action_reset_doctor_signup_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            SlotSet("doctor_signup__name", None),
            SlotSet("doctor_signup__number", None),
            SlotSet("doctor_signup__google_id", None),
            SlotSet("doctor_signup__speciality", None),
            SlotSet("doctor_signup__availability", None),
            SlotSet("doctor_signup__consultation_fee", None),
            SlotSet("doctor_signup__bank_account_number", None),
            SlotSet("doctor_signup__bank_account_name", None),
            SlotSet("doctor_signup__bank_account_ifsc", None),
        ]
