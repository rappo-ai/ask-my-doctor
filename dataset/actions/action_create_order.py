from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.common import (
    create_order,
    print_appointment_details,
    print_patient_details,
)


class ActionCreateOrder(Action):
    def name(self) -> Text:
        return "action_create_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        order: Dict = create_order()

        text = (
            f"Order {order.get('id', '')}\n"
            + "\n"
            + "Appointment Details\n"
            + "\n"
            + print_appointment_details()
            + "\n"
            + "Patient Details\n"
            + "\n"
            + print_patient_details()
            + "\n"
            + f"Consultation fee: Rs. {order.get('amount', '')}\n"
            + "\n"
            + f"Click here to pay -> {order.get('payment_link', '')}\n"
        )

        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
