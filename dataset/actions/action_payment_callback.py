from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import (
    create_meeting_link,
    get_appointment_details,
    print_appointment_details,
    print_patient_details,
    print_payment_details,
    set_payment_details,
)


class ActionPaymentCallback(Action):
    def name(self) -> Text:
        return "action_payment_callback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        metadata = tracker.latest_message.get("metadata", {})
        is_payment_success = metadata.get("is_payment_success", True)
        if is_payment_success:
            amount = metadata.get("amount", 300)
            transaction_id = metadata.get("transaction_id", 1234567890)
            date = metadata.get("date", "July 1st, 2021 5:15 PM IST")
            mode = metadata.get("mode", "Credit Card")
            set_payment_details(amount, transaction_id, date, mode)
            meeting_link: Text = create_meeting_link()
            appointment_details: Dict = get_appointment_details()
            text = (
                f"Booking Confirmation\n"
                + "\n"
                + "Appoinment Details\n"
                + "\n"
                + print_appointment_details()
                + "\n"
                + f"Patient details\n"
                + "\n"
                + print_patient_details()
                + "\n"
                + f"Payment Details\n"
                + "\n"
                + print_payment_details()
                + "\n"
                + f"Your appointment has been scheduled with {appointment_details.get('doctor_name', '')}. Please join this meeting link at the date and time of the appointment:\n{meeting_link}\n\nIf you need any help with this booking, please click /help."
            )

            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)
        else:
            json_message = {"text": "Payment error"}
            dispatcher.utter_message(json_message=json_message)

        return []
