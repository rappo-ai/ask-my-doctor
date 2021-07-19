from copy import deepcopy
from datetime import datetime, timedelta
import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import (
    get_admin_group_id,
    get_meeting_duration_in_minutes,
)
from actions.utils.cart import print_cart
from actions.utils.debug import is_debug_env
from actions.utils.doctor import get_doctor
from actions.utils.entity import get_entity
from actions.utils.json import get_json_key
from actions.utils.meet import create_meeting
from actions.utils.order import get_latest_order_for_user_id, get_order, update_order
from actions.utils.patient import print_patient
from actions.utils.payment_status import (
    fetch_payment_details,
    get_order_id_for_payment_status,
    print_payment_status,
)
from actions.utils.sheets import update_order_in_spreadsheet
from actions.utils.timeslot_lock import create_lock_for_doctor_slot, get_lock_for_slot

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

        admin_group_id = get_admin_group_id()
        entities = tracker.latest_message.get("entities", [])

        payment_status: Dict = get_entity(
            entities,
            "payment_status",
            {},
        )

        if not payment_status:
            if is_debug_env():
                payment_status = {
                    "razorpay_payment_link_reference_id": "000000000000000000000001",
                    "razorpay_payment_link_status": "paid",
                }
            else:
                return []

        order_id = get_order_id_for_payment_status(payment_status)
        order: Dict = get_order(order_id)
        if not order and is_debug_env():
            logger.warn(
                "Unable to find order for this payment. Fetching some order for this user for debugging."
            )
            order = get_latest_order_for_user_id(tracker.sender_id)
            order_id = order.get("_id")

        payment_details = fetch_payment_details(payment_status)

        payment_status["payment_details"] = payment_details

        update_order(order_id, payment_status=payment_status)

        if get_json_key(payment_status, "razorpay_payment_link_status") == "paid":
            cart: Dict = order.get("cart")
            cart_item = next(iter(cart.get("items") or []), {})
            doctor_id = cart_item.get("doctor_id")
            appointment_datetime = cart_item.get("appointment_datetime")
            timeslot_lock = get_lock_for_slot(doctor_id, appointment_datetime)
            if timeslot_lock and str(timeslot_lock.get("order_id")) != order_id:
                conflict_order_id = timeslot_lock.get("order_id")
                dispatcher.utter_message(
                    json_message={
                        "text": f"We're really sorry, but the slot for order #{order_id} is no longer available. Please use /help to contact support for a refund.",
                    }
                )
                dispatcher.utter_message(
                    json_message={
                        "chat_id": admin_group_id,
                        "text": f"Timeslot #{timeslot_lock.get('_id')} has been booked again. Original booking order #{conflict_order_id}, new booking order #{order_id}. Second order needs to be refunded.",
                    }
                )
                return []
            if not timeslot_lock or str(timeslot_lock.get("order_id")) != order_id:
                timeslot_lock_id = create_lock_for_doctor_slot(
                    doctor_id=doctor_id,
                    slot_datetime=appointment_datetime,
                    order_id=order_id,
                    force=True,
                )
                update_order(order_id, timeslot_lock_id=timeslot_lock_id)

            patient: Dict = get_json_key(order, "metadata.patient", {})
            doctor: Dict = get_doctor(doctor_id)
            doctor_chat_id = doctor.get("user_id")

            credentials = doctor.get("credentials")
            guest_emails = [patient.get("email")]
            meet_title = "Appointment with " + patient.get("name")
            start_date = datetime.fromisoformat(appointment_datetime)
            end_date = start_date + timedelta(minutes=get_meeting_duration_in_minutes())
            meeting: Dict = create_meeting(
                credentials=credentials,
                guest_emails=guest_emails,
                title=meet_title,
                start_date=start_date,
                end_date=end_date,
                requestId=order_id,
            )

            if meeting:
                update_order(order_id, meeting=meeting)

            update_order_in_spreadsheet(get_order(order_id))

            text = (
                f"Booking Confirmation\n"
                + "\n"
                + f"Order #{order_id}\n"
                + "\n"
                + "Appoinment Details\n"
                + "\n"
                + print_cart(cart)
                + "\n"
                + f"Patient details\n"
                + "\n"
                + print_patient(patient)
                + "\n"
                + f"Payment Details\n"
                + "\n"
                + print_payment_status(payment_status)
                + "\n"
                + f"Your appointment has been scheduled. Please join the meeting at the date and time of the appointment.\n\nIf you need any help with this booking, please contact support."
            )

            keyboard = [[]]

            if meeting:
                keyboard[0].append(
                    {
                        "title": "Join Meeting",
                        "url": f"{meeting.get('hangoutLink')}",
                    }
                )

            keyboard[0].append(
                {
                    "title": "Contact Support",
                    "payload": "/help",
                }
            )

            json_message = {
                "text": text,
                "reply_markup": {
                    "keyboard": keyboard,
                    "type": "inline",
                },
            }
            patient_json_message = deepcopy(json_message)
            patient_json_message["reply_markup"]["keyboard"][0].insert(
                len(keyboard[0]) - 1,
                {
                    "title": "Contact Doctor",
                    "payload": f"/EXT_patient_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
                },
            )
            dispatcher.utter_message(json_message=patient_json_message)

            if admin_group_id:
                admin_json_message = deepcopy(json_message)
                admin_json_message["chat_id"] = admin_group_id
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")

            if doctor_chat_id:
                doctor_json_message = deepcopy(json_message)
                doctor_json_message["chat_id"] = doctor_chat_id
                doctor_json_message["reply_markup"]["keyboard"][0].insert(
                    len(keyboard[0]) - 1,
                    {
                        "title": "Contact Patient",
                        "payload": f"/EXT_doctor_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
                    },
                )
                dispatcher.utter_message(json_message=doctor_json_message)
            else:
                logger.warn("Doctor chat id not set.")

            if not meeting:
                [
                    dispatcher.utter_message(
                        json_message={
                            "chat_id": chat_id,
                            "text": f"Something went wrong when generating the meeting link for order #{order_id}. Please use /help to contact support.",
                        }
                    )
                    for chat_id in [tracker.sender_id, admin_group_id, doctor_chat_id]
                ]
        else:
            json_message = {"text": "Payment error"}
            dispatcher.utter_message(json_message=json_message)

        return []
