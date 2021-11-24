from bson import ObjectId
from typing import Dict
from datetime import datetime
import logging
import os

from actions.utils.date import SERVER_TZINFO
from actions.utils.markdown import escape_markdown

logger = logging.getLogger(__name__)


def get_mock_payment_creation_ts():
    return datetime.now(tz=SERVER_TZINFO).timestamp()


def get_order_id_for_payment_status(payment_status: Dict):
    razorpay_payment_link_reference_id = payment_status.get(
        "razorpay_payment_link_reference_id"
    )
    return (
        ObjectId(razorpay_payment_link_reference_id)
        if razorpay_payment_link_reference_id
        else None
    )


def fetch_payment_details(payment_status: Dict, is_demo_mode: bool = False):
    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
    razorpay_secret_key = os.getenv("RAZORPAY_SECRET_KEY")
    if is_demo_mode:
        razorpay_key_id = os.getenv("DEMO_RAZORPAY_KEY_ID")
        razorpay_secret_key = os.getenv("DEMO_RAZORPAY_SECRET_KEY")

    if not (razorpay_key_id and razorpay_secret_key):
        logger.warn(
            "RAZORPAY_KEY_ID or RAZORPAY_SECRET_KEY not set, using dummy payment details"
        )
        return {
            "amount": 1000,
            "created_at": get_mock_payment_creation_ts(),
            "method": "Credit Card",
            "status": "paid",
        }

    import razorpay

    client = razorpay.Client(auth=(razorpay_key_id, razorpay_secret_key))
    payment_id = payment_status.get("razorpay_payment_id", "")

    return client.payment.fetch(payment_id)


def print_payment_status(payment_status: Dict, enable_markdown: bool = False):
    payment_details = payment_status.get("payment_details", {})
    amount_rupees = payment_details.get("amount", 0) / 100
    date = datetime.fromtimestamp(
        payment_details.get("created_at", get_mock_payment_creation_ts()), SERVER_TZINFO
    ).strftime("%d-%m-%Y %H:%M:%S")
    mode = payment_details.get("method", "")
    status = payment_status.get("razorpay_payment_link_status")

    return (
        escape_markdown(f"Amount: {amount_rupees}\n", enabled=enable_markdown)
        + escape_markdown(
            f"Payment ID: {payment_status.get('razorpay_payment_id', '')}\n",
            enabled=enable_markdown,
        )
        + escape_markdown(f"Date: {date}\n", enabled=enable_markdown)
        + escape_markdown(f"Mode: {mode}\n", enabled=enable_markdown)
        + escape_markdown(f"Status of Payment: {status}\n", enabled=enable_markdown)
    )
