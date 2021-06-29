from datetime import datetime
from functools import reduce
from typing import Any, Dict, List, Text

from actions.utils.date import DATE_FORMAT, TIME_FORMAT
from actions.utils.doctor import get_doctor

cart: Dict = {}


def add_cart(user_id, items: List) -> int:
    user_cart = cart[user_id] = {}
    user_cart["items"] = items
    return len(cart)


def add_to_cart(user_id, items: List):
    user_cart: Dict = cart.get(user_id)
    user_cart_items: List = user_cart["items"]
    user_cart_items.extend(items)
    return len(user_cart_items)


def clear_cart(user_id):
    user_cart: Dict = cart.get(user_id)
    user_cart_items: List = user_cart["items"]
    user_cart_items.clear()


def get_cart(user_id) -> Dict[Text, Any]:
    return cart.get(user_id)


def get_cart_total(user_cart):
    user_cart_items: List = user_cart["items"]
    if user_cart_items and type(user_cart_items) == list:
        return reduce(
            lambda a, b: a.get("amount", 0) + b.get("amount", 0),
            user_cart_items,
            {"amount": 0},
        )
    return 0


def print_cart(cart: Dict):
    cart_item = next(iter(cart.get("items", [])), {})
    doctor_id = cart_item.get("doctor_id")
    doctor: Dict = get_doctor(doctor_id)
    appointment_datetime: datetime = datetime.fromisoformat(
        cart_item.get("appointment_datetime")
    )
    return (
        f"Doctor: {doctor.get('name', '')}\n"
        + f"Speciality: {doctor.get('speciality', '')}\n"
        + f"Date: {appointment_datetime.strftime(DATE_FORMAT)}\n"
        + f"Time: {appointment_datetime.strftime(TIME_FORMAT)}\n"
    )


def update_cart(user_id, items: List) -> int:
    user_cart: Dict = cart.get(user_id)
    user_cart["items"] = items
    return len(user_cart["items"])
