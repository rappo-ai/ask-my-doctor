from copy import deepcopy
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.cart import get_cart, get_cart_total, print_cart
from actions.utils.doctor import get_doctor
from actions.utils.order import create_order, get_order, update_order
from actions.utils.payment_link import create_payment_link
from actions.utils.patient import get_patient_for_user_id, print_patient
from actions.utils.sheets import update_order_in_spreadsheet


class ActionCreateOrder(Action):
    def name(self) -> Text:
        return "action_create_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id

        cart: Dict = get_cart(user_id)
        cart_amount = get_cart_total(cart)
        cart_item: Dict = next(iter(cart.get("items", [])), {})
        doctor_id = cart_item.get("doctor_id")
        doctor: Dict = get_doctor(doctor_id)
        payment_description = f"Consultation fee for {doctor.get('name', '')}"

        order_id: Text = create_order(user_id, cart)

        patient: Dict = get_patient_for_user_id(user_id)
        patient.pop("_id", None)

        payment_link: Dict = create_payment_link(
            cart_amount,
            patient["name"],
            patient["email"],
            patient["phone"],
            payment_description,
            order_id,
        )

        order_metadata = {"patient": patient}

        update_order(order_id, payment_link=payment_link, metadata=order_metadata)
        update_order_in_spreadsheet(get_order(order_id))

        text = (
            f"Order #{order_id}\n"
            + "\n"
            + "Appointment Details\n"
            + "\n"
            + print_cart(cart)
            + "\n"
            + "Patient Details\n"
            + "\n"
            + print_patient(patient)
            + "\n"
            + f"Consultation fee: Rs. {cart_amount}\n"
            + "\n"
            + f"Click here to pay -> {payment_link.get('short_url')}\n"
        )

        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
