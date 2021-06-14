# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionNewDoctorSignup(Action):

    def name(self) -> Text:
        return "action_new_doctor_signup"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      
        text = f"We have received your details and will review it and get back to you shortly.\n\n" +\
            f"Name: {tracker.get_slot('new_doctor_signup__name')}\n" + \
            f"Phone Number: {tracker.get_slot('new_doctor_signup__number')}\n" + \
            f"Speciality: {tracker.get_slot('new_doctor_signup__speciality')}\n" + \
            f"Availability: {tracker.get_slot('new_doctor_signup__availability')}\n" + \
            f"Consultation Fee: {tracker.get_slot('new_doctor_signup__consultation_fee')}\n\n" + \
            f"Bank Details\n\n" +\
            f"Account number: {tracker.get_slot('new_doctor_signup__bank_account_number')}\n" + \
            f"Account name: {tracker.get_slot('new_doctor_signup__bank_account_name')}\n" + \
            f"Account IFSC: {tracker.get_slot('new_doctor_signup__bank_account_ifsc')}"

        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []