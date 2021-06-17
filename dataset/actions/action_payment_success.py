# This files contains a custom action which can be used to run
# custom Python code.
#
# See this guide on how to implement these actions:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionPaymentSuccess(Action):

    def name(self) -> Text:
        return "action_payment_success"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text = f"Booking Confirmation\n\nAppoinment Details\n\n" + \
            f"Doctor's name: {tracker.get_slot('new_appointment_request__doctor')}\n" + \
            f"Speciality: {tracker.get_slot('new_appointment_request__speciality')}\n" + \
            f"Date: {tracker.get_slot('new_appointment_request__date')}\n" + \
            f"Time: {tracker.get_slot('new_appointment_request__time')}\n\n" + \
            f"Patient details\n\n" + \
            f"Name: {tracker.get_slot('new_patient__name')}\n" + \
            f"Age: {tracker.get_slot('new_patient__age')}\n" + \
            f"Phone number: {tracker.get_slot('new_patient__phone_number')}\n\n" + \
            f"Payment Details\n\n" + \
            f"Amount: Rs. 300\n" + \
            f"Transaction id: 214293098037\n" + \
            f"Date: 15th June, 2021 8:15 PM\n" + \
            f"Mode: Credit Card\n\n" + \
            f"Your appointment has been scheduled with Dr. Murali. Please join this meeting link at the date and time of the appointment - https://meet.google.com/vix-uaxv-hcx . If you need any help with this booking, please click /help."

        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
