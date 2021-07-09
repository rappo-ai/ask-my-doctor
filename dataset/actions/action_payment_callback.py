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
from actions.utils.doctor import get_doctor
from actions.utils.entity import get_entity
from actions.utils.json import get_json_key
from actions.utils.meet import create_meeting
from actions.utils.order import (
    get_order,
    get_order_for_user_id,
    update_order,
)
from actions.utils.patient import print_patient
from actions.utils.payment_status import (
    get_order_id_for_payment_status,
    get_payment_id,
    get_payment_amount,
    get_payment_date,
    get_payment_mode,
    get_payment_status,
    get_payment_details,
    print_payment_status,
)
from actions.utils.sheets import update_order_in_spreadsheet

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

        entities = tracker.latest_message.get("entities", [])

        payment_status: Dict = get_entity(
            entities,
            "payment_status",
            {},
        )

        order_id = get_order_id_for_payment_status(payment_status)
        order: Dict = get_order(order_id)
        if not order:
            logger.error("Unable to find order for this payment.")

        payment_id = get_payment_id(payment_status)
        resp = get_payment_details(payment_status)
        amount_rupees = get_payment_amount(resp) / 100
        date = get_payment_date(resp)
        mode = get_payment_mode(resp)
        status = get_payment_status(payment_status)

        payment_details = {
            "amount_rupees": amount_rupees,
            "dateTime_DD/MM/YYYY": date,
            "Payment_id": payment_id,
            "mode_payment": mode,
            "status": status,
        }

        payment_status["payment_details"] = payment_details

        update_order(order_id, payment_status=payment_status)

        if payment_status.get("razorpay_payment_link_status") == "paid":
            cart: Dict = order.get("cart")
            patient: Dict = get_json_key(order, "metadata.patient", {})
            cart_item = next(iter(cart.get("items") or []), {})
            doctor: Dict = get_doctor(cart_item.get("doctor_id"))

            doctor_chat_id = doctor.get("user_id")

            credentials = doctor.get("credentials")
            guest_emails = [patient.get("email")]
            start_date = datetime.fromisoformat(cart_item.get("appointment_datetime"))
            end_date = start_date + timedelta(minutes=get_meeting_duration_in_minutes())
            meeting: Dict = create_meeting(
                credentials=credentials,
                guest_emails=guest_emails,
                start_date=start_date,
                end_date=end_date,
            )

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
                + f"Your appointment has been scheduled. Please join this meeting link at the date and time of the appointment:\n{meeting.get('link')}\n\nIf you need any help with this booking, please click /help."
            )

            json_message = {"text": text, "disable_web_page_preview": True}
            patient_json_message = deepcopy(json_message)
            patient_json_message["reply_markup"] = {
                "keyboard": [
                    [
                        {
                            "title": "Contact Doctor",
                            "payload": f"/EXT_patient_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
                        }
                    ]
                ],
                "type": "inline",
            }
            dispatcher.utter_message(json_message=patient_json_message)

            if get_admin_group_id():
                admin_json_message = deepcopy(json_message)
                admin_json_message["chat_id"] = get_admin_group_id()
                dispatcher.utter_message(json_message=admin_json_message)
            else:
                logger.warn("Admin group id not set. Use /admin or /groupid.")

            if doctor_chat_id:
                doctor_json_message = deepcopy(json_message)
                doctor_json_message["chat_id"] = doctor_chat_id
                doctor_json_message["reply_markup"] = {
                    "keyboard": [
                        [
                            {
                                "title": "Contact Patient",
                                "payload": f"/EXT_doctor_send_message{{\"o_id\":\"{str(order['_id'])}\"}}",
                            }
                        ]
                    ],
                    "type": "inline",
                }
                dispatcher.utter_message(json_message=doctor_json_message)
            else:
                logger.warn("Doctor chat id not set.")
        else:
            json_message = {"text": "Payment error"}
            dispatcher.utter_message(json_message=json_message)

        return []
