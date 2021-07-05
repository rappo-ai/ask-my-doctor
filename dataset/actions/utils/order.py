from bson.objectid import ObjectId
from typing import Dict, Optional, Text

from actions.db.store import db


def create_order(user_id: Text, cart: Dict):
    return db.order.insert_one({"user_id": user_id, "cart": cart}).inserted_id


def get_order(id):
    return db.order.find_one({"_id": ObjectId(id)})


def get_order_for_user_id(user_id):
    return db.order.find_one({"user_id": user_id})


def update_order(
    id,
    cart: Optional[Dict] = None,
    payment_link: Optional[Dict] = None,
    payment_status: Optional[Dict] = None,
    meeting: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
):
    order = {}

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

    db.order.update_one({"_id": ObjectId(id)}, {"$set": order})
