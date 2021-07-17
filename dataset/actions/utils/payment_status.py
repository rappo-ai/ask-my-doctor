from typing import Dict
import datetime
import json
import logging
import os

from actions.utils.date import SERVER_TZINFO
from actions.utils.json import get_json_key

logger = logging.getLogger(__name__)

MOCK_PAYMENT_CREATION_TS = 1626002365


def get_order_id_for_payment_status(payment_status: Dict):
    return payment_status.get("razorpay_payment_link_reference_id", "")


def fetch_payment_details(payment_status: Dict):
    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
    razorpay_secret_key = os.getenv("RAZORPAY_SECRET_KEY")

    if not (razorpay_key_id and razorpay_secret_key):
        logger.warn(
            "RAZORPAY_KEY_ID or RAZORPAY_SECRET_KEY not set, using dummy payment details"
        )
        return {
            "amount": 1000,
            "created_at": MOCK_PAYMENT_CREATION_TS,
            "method": "Credit Card",
            "status": "paid",
        }

    import razorpay

    client = razorpay.Client(auth=(razorpay_key_id, razorpay_secret_key))
    payment_id = payment_status.get("razorpay_payment_id", "")

    return client.payment.fetch(payment_id)


def print_payment_status(payment_status: Dict):
    payment_details = payment_status.get("payment_details", {})
    amount_rupees = payment_details.get("amount", 0) / 100
    date = datetime.datetime.fromtimestamp(
        payment_details.get("created_at", MOCK_PAYMENT_CREATION_TS), SERVER_TZINFO
    ).strftime("%d-%m-%Y %H:%M:%S")
    mode = payment_details.get("method", "")
    status = payment_status.get("razorpay_payment_link_status")

    return (
        f"Amount: {amount_rupees}\n"
        + f"Payment ID: {payment_status.get('razorpay_payment_id', '')}\n"
        + f"Date: {date}\n"
        + f"Mode: {mode}\n"
        + f"Status of Payment: {status}\n"
    )
