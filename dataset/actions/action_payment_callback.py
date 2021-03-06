from bson import ObjectId
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
from actions.utils.markdown import escape_markdown
from actions.utils.meet import create_meeting
from actions.utils.order import (
    get_latest_open_order_for_user_id,
    get_order,
    update_order,
)
from actions.utils.patient import print_patient
from actions.utils.payment_status import (
    fetch_payment_details,
    get_order_id_for_payment_status,
    print_payment_status,
)
from actions.utils.timeslot_lock import create_lock_for_doctor_slot, get_lock_for_slot
from actions.utils.user import get_user_for_user_id

logger = logging.getLogger(__name__)


def create_booking_confirmation_message(
    order_id,
    cart,
    patient,
    payment_status,
    keyboard,
    is_demo_mode,
    show_user_links=False,
):
    text = (
        escape_markdown("Booking Confirmation\n", enabled=show_user_links)
        + "\n"
        + escape_markdown(f"Order #{order_id}\n", enabled=show_user_links)
        + "\n"
        + escape_markdown("Appoinment Details\n", enabled=show_user_links)
        + "\n"
        + print_cart(cart, show_user_links)
        + "\n"
        + escape_markdown(f"Patient details\n", enabled=show_user_links)
        + "\n"
        + print_patient(patient, show_user_links)
        + "\n"
        + escape_markdown(f"Payment Details\n", enabled=show_user_links)
        + "\n"
        + print_payment_status(payment_status, show_user_links)
        + "\n"
        + escape_markdown(
            f"Your appointment has been scheduled. Concerned doctor will connect with you soon.\n",
            enabled=show_user_links,
        )
    )

    if is_demo_mode:
        text = (
            escape_markdown("DEMO BOOKING\n\n", enabled=show_user_links)
            + text
            + escape_markdown("\nDEMO BOOKING", enabled=show_user_links)
        )

    return {
        "text": text,
        "reply_markup": {
            "keyboard": keyboard,
            "type": "inline",
        },
        "parse_mode": "MarkdownV2" if show_user_links else None,
    }


def create_contact_doctor_button(order):
    return {
        "title": "Contact Doctor",
        "payload": f"/EXT_patient_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
    }


def create_contact_patient_button(order):
    return {
        "title": "Contact Patient",
        "payload": f"/EXT_doctor_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
    }


def create_contact_support_button():
    return {
        "title": "Contact Support",
        "payload": "/help",
    }


def create_join_meeting_button(meeting):
    return {
        "title": "Join Meeting",
        "url": f"{meeting.get('hangoutLink')}",
    }


class ActionPaymentCallback(Action):
    def name(self) -> Text:
        return "action_payment_callback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        telegram_user_id = tracker.get_slot("telegram_user_id") or ""
        user = get_user_for_user_id(telegram_user_id)
        if not user:
            logger.warn("action_create_order: user not found")
        is_demo_mode = (user or False) and (user.get("is_demo_mode") or False)
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
            order = get_latest_open_order_for_user_id(tracker.sender_id)
            if not order:
                dispatcher.utter_message(text="DEBUG: No open order found for /pay")
                return []
            else:
                dispatcher.utter_message(
                    text=f"DEBUG: Found order #{order.get('_id')} for /pay"
                )
            order_id = order.get("_id")

        assert isinstance(order_id, ObjectId)

        # ignore event if order is already marked paid
        if get_json_key(order, "payment_status.razorpay_payment_link_status") == "paid":
            return []

        payment_details = fetch_payment_details(payment_status, is_demo_mode)

        payment_status["payment_details"] = payment_details

        update_order(order_id, payment_status=payment_status)

        if get_json_key(payment_status, "razorpay_payment_link_status") == "paid":
            cart: Dict = order.get("cart")
            cart_item = next(iter(cart.get("items") or []), {})
            doctor_id = cart_item.get("doctor_id")
            appointment_datetime = cart_item.get("appointment_datetime")
            timeslot_lock = get_lock_for_slot(doctor_id, appointment_datetime)
            if timeslot_lock and str(timeslot_lock.get("order_id")) != str(order_id):
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
            if (not is_demo_mode) and (
                (not timeslot_lock)
                or str(timeslot_lock.get("order_id")) != str(order_id)
            ):
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
                requestId=str(order_id),
                is_demo_mode=is_demo_mode,
            )

            if meeting:
                update_order(order_id, meeting=meeting)

            patient_keyboard = [
                [
                    create_contact_doctor_button(order),
                    create_contact_support_button(),
                ]
            ]
            doctor_keyboard = [
                [
                    create_contact_patient_button(order),
                    create_contact_support_button(),
                ]
            ]
            admin_keyboard = [
                [
                    create_contact_doctor_button(order),
                    create_contact_patient_button(order),
                ]
            ]

            if meeting:
                for k in [patient_keyboard, doctor_keyboard, admin_keyboard]:
                    k.insert(0, [create_join_meeting_button(meeting)])

            patient_json_message = create_booking_confirmation_message(
                order_id, cart, patient, payment_status, patient_keyboard, is_demo_mode
            )
            dispatcher.utter_message(json_message=patient_json_message)
            dispatcher.utter_message(text="Click /menu to view the main menu.")

            if admin_group_id:
                admin_json_message = create_booking_confirmation_message(
                    order_id,
                    cart,
                    patient,
                    payment_status,
                    admin_keyboard,
                    is_demo_mode,
                    show_user_links=True,
                )
                admin_json_message["chat_id"] = admin_group_id
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")

            if (not is_demo_mode) and doctor_chat_id:
                doctor_json_message = create_booking_confirmation_message(
                    order_id,
                    cart,
                    patient,
                    payment_status,
                    doctor_keyboard,
                    is_demo_mode,
                )
                doctor_json_message["chat_id"] = doctor_chat_id
                dispatcher.utter_message(json_message=doctor_json_message)
            else:
                logger.warn("Doctor chat id not set.")

            if False and not meeting:
                target_chats = (
                    [tracker.sender_id, admin_group_id]
                    if is_demo_mode
                    else [tracker.sender_id, admin_group_id, doctor_chat_id]
                )
                [
                    dispatcher.utter_message(
                        json_message={
                            "chat_id": chat_id,
                            "text": f"Something went wrong when generating the meeting link for order #{order_id}. Please use /help to contact support.",
                        }
                    )
                    for chat_id in target_chats
                ]
        else:
            json_message = {"text": "Payment error"}
            dispatcher.utter_message(json_message=json_message)

        return []
