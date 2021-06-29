from typing import Dict


def get_order_id_for_payment_status(payment_status: Dict):
    return payment_status.get("order_id")


def print_payment_status(payment_status: Dict):
    return (
        f"Amount: {payment_status.get('amount', '')}\n"
        + f"Transaction ID: {payment_status.get('transaction_id', '')}\n"
        + f"Date: {payment_status.get('date', '')}\n"
        + f"Mode: {payment_status.get('mode', '')}\n"
    )
