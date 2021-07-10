from typing import Dict
import datetime
import json
import razorpay
import os

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_SECRET_KEY"))
)


def get_order_id_for_payment_status(payment_status: Dict):
    return payment_status.get("razorpay_payment_link_reference_id")


def get_payment_id(payment_status: Dict):
    return payment_status.get("razorpay_payment_id")


def get_payment_amount(payment_status: Dict):
    return payment_status["amount"]


def get_payment_date(payment_status: Dict):
    timestamp = datetime.datetime.fromtimestamp(payment_status["created_at"]).strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    date = timestamp
    return date


def get_payment_mode(payment_status: Dict):
    return payment_status["method"]


def get_payment_status(payment_status: Dict):
    return payment_status.get("razorpay_payment_link_status")


def get_payment_details(payment_status: Dict):
    payment_id = payment_status.get("razorpay_payment_id")
    resp = client.payment.fetch(payment_id)
    return resp


def print_payment_status(payment_status: Dict):
    payment_id = payment_status.get("razorpay_payment_id")

    amount_rupees = payment_status["payment_details"]["amount_rupees"]
    date = payment_status["payment_details"]["dateTime_DD/MM/YYYY"]
    mode = payment_status["payment_details"]["mode_payment"]
    status = payment_status["payment_details"]["status"]

    return (
        f"Amount: {amount_rupees}\n"
        + f"Payment ID: {payment_status.get('razorpay_payment_id', '')}\n"
        + f"Date: {date}\n"
        + f"Mode: {mode}\n"
        + f"Status of Payment: {status}\n"
    )
