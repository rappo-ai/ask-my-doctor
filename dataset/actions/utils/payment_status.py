from typing import Dict
import datetime
import json
import razorpay
import os

from actions.utils.json import (
    get_json_key,
)

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_SECRET_KEY"))
)


def get_order_id_for_payment_status(payment_status: Dict):
    return payment_status.get("razorpay_payment_link_reference_id")


def get_payment_id(payment_status: Dict):
    return payment_status.get("razorpay_payment_id")


def get_payment_details(payment_status: Dict):
    payment_id = get_payment_id(payment_status)
    resp = client.payment.fetch(payment_id)
    amount_rupees = resp["amount"] / 100
    timestamp = datetime.datetime.fromtimestamp(resp["created_at"]).strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    date = timestamp
    mode = resp["method"]
    status = payment_status.get("razorpay_payment_link_status")

    payment_details = {
        "amount_rupees": amount_rupees,
        "dateTime_DD/MM/YYYY": date,
        "Payment_id": payment_id,
        "mode_payment": mode,
        "status": status,
    }
    return payment_details


def print_payment_status(payment_status: Dict):
    payment_id = get_payment_id(payment_status)
    amount_rupees = get_json_key(payment_status, "payment_details.amount_rupees")
    date = get_json_key(payment_status, "payment_details.dateTime_DD/MM/YYYY")
    mode = get_json_key(payment_status, "payment_details.mode_payment")
    status = get_json_key(payment_status, "payment_details.status")

    return (
        f"Amount: {amount_rupees}\n"
        + f"Payment ID: {payment_status.get('razorpay_payment_id', '')}\n"
        + f"Date: {date}\n"
        + f"Mode: {mode}\n"
        + f"Status of Payment: {status}\n"
    )
