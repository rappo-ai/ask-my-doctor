from typing import Dict


def get_order_id_for_payment_status(payment_status: Dict):
    # #tbdnikhil - return the order id from the incoming payment status
    return payment_status.get("order_id")


def print_payment_status(payment_status: Dict):
    # #tbdnikhil modify the output as per actual payment status object (this print is what's shown to patient)
    return (
        f"Amount: {payment_status.get('amount', '')}\n"
        + f"Transaction ID: {payment_status.get('transaction_id', '')}\n"
        + f"Date: {payment_status.get('date', '')}\n"
        + f"Mode: {payment_status.get('mode', '')}\n"
    )
