from datetime import datetime
from functools import reduce
from typing import Any, Dict, List, Text

from actions.db.rappo import rappo_db
from actions.utils.date import APPOINTMENT_DATE_FORMAT, APPOINTMENT_TIME_FORMAT
from actions.utils.doctor import get_doctor


def add_cart(user_id, items: List) -> int:
    return rappo_db.cart.insert_one(
        {
            "user_id": user_id,
            "items": items,
        },
    ).inserted_id


def clear_cart(user_id):
    rappo_db.cart.update_one({"user_id": user_id}, {"$set": {"items": []}})


def get_cart(user_id) -> Dict[Text, Any]:
    return rappo_db.cart.find_one({"user_id": user_id})


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
        + f"Date: {appointment_datetime.strftime(APPOINTMENT_DATE_FORMAT)}\n"
        + f"Time: {appointment_datetime.strftime(APPOINTMENT_TIME_FORMAT)}\n"
    )


def update_cart(user_id, items: List) -> int:
    rappo_db.cart.update_one({"user_id": user_id}, {"$set": {"items": items}})
