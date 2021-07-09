from typing import Dict
import datetime
import json


def get_order_id_for_payment_status(payment_status: Dict):
    return payment_status.get("razorpay_payment_link_reference_id")


def print_payment_status(payment_status: Dict):
    payment_id = payment_status.get("razorpay_payment_id")

    amount_rupees = payment_status["payment_details"]["amount_rupees"]
    date = payment_status["payment_details"]["dateTime_DD/MM/YYYY"]
    mode = payment_status["payment_details"]["mode_payment"]
    status = payment_status["payment_details"]["status"]

    return (
        f"Amount: {amount_rupees}\n"
        + f"Transaction ID: {payment_status.get('razorpay_payment_id', '')}\n"
        + f"Date: {date}\n"
        + f"Mode: {mode}\n"
        + f"Mode: {status}\n"
    )
