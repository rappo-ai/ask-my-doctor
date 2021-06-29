from typing import Dict, Optional, Text

from actions.utils.json import get_json_key

orders: Dict = {}


def create_order(user_id: Text, cart: Dict):
    order_id = len(orders) + 1
    orders[order_id] = {"user_id": user_id, "cart": cart}
    return order_id


def get_order(order_id):
    return orders[order_id]


def update_order(
    order_id: int,
    cart: Optional[Dict] = None,
    payment_link: Optional[Dict] = None,
    payment_status: Optional[Dict] = None,
    meeting: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
):
    order = orders[order_id]

    if not order:
        raise KeyError("order_id not found")

    if cart:
        order["cart"] = cart

    if payment_link:
        order["payment_link"] = payment_link

    if payment_status:
        order["payment_status"] = payment_status

    if meeting:
        order["meeting"] = meeting

    if metadata:
        order["metadata"] = metadata


def get_appointment_info(order_id):
    return get_json_key(orders, f"{order_id}.appointment_info", {})


def get_patient_info(order_id):
    return get_json_key(orders, f"{order_id}.patient_info", {})


def get_payment_info(order_id):
    return get_json_key(orders, f"{order_id}.payment_info", {})


def get_meeting_info(order_id):
    return get_json_key(orders, f"{order_id}.meeting_info", {})


def get_metadata(order_id):
    return get_json_key(orders, f"{order_id}.metadata", {})
