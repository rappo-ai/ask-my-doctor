from bson.objectid import ObjectId
from typing import Dict, Union

from actions.db.rappo import rappo_db


def add_new_user(user_id: int, metadata: Dict):
    return rappo_db.user.insert_one(
        {"user_id": user_id, "metadata": metadata}
    ).inserted_id


def is_new_user(user_id: int):
    existing_user = rappo_db.user.find_one({"user_id": user_id})
    return not existing_user


def get_user_for_user_id(user_id: Union[int, str]):
    if isinstance(user_id, str):
        user_id = int(user_id)

    return rappo_db.user.find_one({"user_id": user_id})


def update_user(id, demo_mode: Dict = None):
    user = {}

    if demo_mode:
        user["is_demo_mode"] = demo_mode.get("value") or False

    if user:
        rappo_db.user.update_one({"_id": ObjectId(id)}, {"$set": user})


def total_users():
    return rappo_db.user.estimated_document_count()
