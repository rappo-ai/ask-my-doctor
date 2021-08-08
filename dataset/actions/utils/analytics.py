from typing import Dict, Text

from actions.db.store import db


def is_new_user(user_id: Text):
    existing_user = db.user.find_one({"user_id": user_id})
    return not existing_user


def log_new_user(user_id: Text, metadata: Dict):
    return db.user.insert_one({"user_id": user_id, "metadata": metadata}).inserted_id


def total_users():
    return db.user.estimated_document_count()
