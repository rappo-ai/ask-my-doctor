from copy import deepcopy
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_slot_blocking_time_seconds
from actions.utils.cart import get_cart, get_cart_total, print_cart
from actions.utils.doctor import get_doctor, is_approved_and_activated_doctor
from actions.utils.order import create_order, get_order, update_order
from actions.utils.patient import get_patient_for_user_id, print_patient
from actions.utils.payment_link import create_payment_link
from actions.utils.sheets import update_order_in_spreadsheet
from actions.utils.timeslot_lock import create_lock_for_doctor_slot, update_lock_for_id


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
        appointment_datetime = cart_item.get("appointment_datetime")
        if not is_approved_and_activated_doctor(doctor_id):
            dispatcher.utter_message(
                json_message={
                    "text": f"{doctor.get('name')} is currently unavailable. Please create a new booking with a different doctor."
                }
            )
            return []
        timeslot_lock: Dict = create_lock_for_doctor_slot(
            doctor_id, appointment_datetime
        )
        if not timeslot_lock:
            dispatcher.utter_message(
                json_message={
                    "text": "This slot is no longer available. Please create a new booking with a different slot."
                }
            )
            return []

        order_id: Text = create_order(user_id, cart=cart, timeslot_lock=timeslot_lock)

        payment_description = f"Consultation fee for {doctor.get('name', '')}"

        patient: Dict = get_patient_for_user_id(user_id)
        patient.pop("_id", None)

        payment_link: Dict = create_payment_link(
            amount_rupees=cart_amount,
            name=patient["name"],
            email=patient["email"],
            phone=patient["phone"],
            description=payment_description,
            expire_by_seconds=get_slot_blocking_time_seconds(),
            order_id=order_id,
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
        )
        reply_markup = {
            "keyboard": [
                [
                    {
                        "title": f"Pay ₹{cart_amount}",
                        "url": payment_link.get("short_url"),
                    }
                ]
            ],
            "type": "inline",
        }

        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
