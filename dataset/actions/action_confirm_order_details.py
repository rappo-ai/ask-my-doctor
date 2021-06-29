from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.cart import get_cart, print_cart
from actions.utils.patient import get_patient_for_user_id, print_patient


class ActionConfirmOrderDetails(Action):
    def name(self) -> Text:
        return "action_confirm_order_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        cart = get_cart(user_id)
        patient = get_patient_for_user_id(user_id)
        text = (
            f"You have requested for an appointment with the following details:\n\n"
            + print_cart(cart)
            + "\n"
            + f"Patient Details\n\n"
            + print_patient(patient)
            + "\n\n"
            + f"Is this correct?"
        )
        reply_markup = {
            "keyboard": [["Yes", "No"]],
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
