from apscheduler.job import Job
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
import logging
import requests
from requests.structures import CaseInsensitiveDict
from typing import Dict, Optional, Text

from actions.db.store import db
from actions.utils.admin_config import get_payment_link_expiry_time_seconds
from actions.utils.date import SERVER_TZINFO
from actions.utils.host import get_host_url
from actions.utils.json import get_json_key
from actions.utils.scheduler import scheduler
from actions.utils.timeslot_lock import delete_lock_for_id, get_lock_for_id

logger = logging.getLogger(__name__)


def create_order(user_id: Text, cart: Dict, timeslot_lock_id: ObjectId = None):
    order = {
        "creation_ts": datetime.now(tz=SERVER_TZINFO).isoformat(),
        "user_id": user_id,
        "cart": cart,
    }
    if timeslot_lock_id:
        order["timeslot_lock_id"] = timeslot_lock_id
    order_id = db.order.insert_one(order).inserted_id
    if timeslot_lock_id:
        unlock_order_job: Job = scheduler().add_job(
            unlock_order,
            "date",
            run_date=(
                datetime.now(tz=SERVER_TZINFO)
                + timedelta(seconds=get_payment_link_expiry_time_seconds())
            ),
            args=[str(order_id)],
            id=str(order_id),
            replace_existing=True,
            name="Unlock Order",
        )
        db.order.update_one(
            {"_id": order_id}, {"$set": {"unlock_order_job_id": unlock_order_job.id}}
        )
    return order_id


def unlock_order(order_id):
    try:
        order: Dict = db.order.find_one({"_id": ObjectId(order_id)})
        payment_status = order.get("payment_status", {})
        if get_json_key(payment_status, "razorpay_payment_link_status") != "paid":
            timeslot_lock_id = order.get("timeslot_lock_id")
            timeslot_lock = get_lock_for_id(timeslot_lock_id)
            if not timeslot_lock:
                logger.warn(f"Missing timeslot_lock for order #{order_id}")
                return
            if timeslot_lock.get("order_id") != order.get("_id"):
                logger.info(
                    f"Skipping unlock of order #{order_id} as the lock is assigned to a different order"
                )
                return
            delete_lock_for_id(timeslot_lock_id)
            notify_url = get_host_url("/webhooks/telegram/order_unlocked")
            headers = CaseInsensitiveDict()
            headers["Content-type"] = "application/json"
            request_data = {
                "order_id": str(order_id),
                "sender_id": str(get_json_key(order, "metadata.patient.user_id")),
            }
            request_data_str = json.dumps(request_data)
            requests.post(notify_url, headers=headers, data=request_data_str)
    except Exception as e:
        logger.error(e)


def get_order(id) -> Dict:
    return db.order.find_one({"_id": ObjectId(id)})


def get_latest_order_for_user_id(user_id):
    cursor = db.order.find({"user_id": user_id}).sort({"_id": 1}).limit(1)
    for doc in cursor:
        return doc
    return None


def update_order(
    id,
    cart: Optional[Dict] = None,
    payment_link: Optional[Dict] = None,
    payment_status: Optional[Dict] = None,
    meeting: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    timeslot_lock_id: Optional[ObjectId] = None,
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

    if timeslot_lock_id:
        order["timeslot_lock_id"] = timeslot_lock_id

    db.order.update_one({"_id": ObjectId(id)}, {"$set": order})
