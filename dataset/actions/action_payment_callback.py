from copy import deepcopy
import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import (
    create_meeting_link,
    get_admin_group_id,
    print_appointment_details,
    print_patient_details,
    print_payment_details,
)

logger = logging.getLogger(__name__)


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
        payment_info: Dict = metadata.get(
            "payment_info",
            {
                "status": "complete",
                "amount": 300,
                "transaction_id": "1234567890",
                "date": "July 1st, 2021 5:15 PM IST",
                "mode": "Credit Card",
            },
        )
        if payment_info.get("status") == "complete":
            order_id = get_order_id_for_payment(payment_info)
            meeting_link: Text = create_meeting_link()
            update_order(order_id, meeting_link=meeting_link, payment_info=payment_info)
            text = (
                f"Booking Confirmation\n"
                + "\n"
                + "Appoinment Details\n"
                + "\n"
                + print_appointment_details(order_id)
                + "\n"
                + f"Patient details\n"
                + "\n"
                + print_patient_details(order_id)
                + "\n"
                + f"Payment Details\n"
                + "\n"
                + print_payment_details(order_id)
                + "\n"
                + f"Your appointment has been scheduled. Please join this meeting link at the date and time of the appointment:\n{meeting_link}\n\nIf you need any help with this booking, please click /help."
            )

            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)

            if get_admin_group_id():
                admin_json_message = deepcopy(json_message)
                admin_json_message["chat_id"] = get_admin_group_id()
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")
        else:
            json_message = {"text": "Payment error"}
            dispatcher.utter_message(json_message=json_message)

        return []
