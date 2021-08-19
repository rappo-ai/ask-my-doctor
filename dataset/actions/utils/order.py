from apscheduler.job import Job
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
import logging
from pymongo import DESCENDING
import requests
from requests.structures import CaseInsensitiveDict
from typing import Dict, Optional, Text

from actions.db.rappo import rappo_db
from actions.utils.admin_config import get_payment_link_expiry_time_seconds
from actions.utils.date import SERVER_TZINFO
from actions.utils.host import get_host_url
from actions.utils.json import get_json_key
from actions.utils.scheduler import scheduler
from actions.utils.timeslot_lock import delete_lock_for_id, get_lock_for_id

logger = logging.getLogger(__name__)


def create_order(
    user_id: Text,
    cart: Dict,
    timeslot_lock_id: ObjectId = None,
    is_demo_mode: bool = False,
):
    current_date = datetime.now(tz=SERVER_TZINFO)
    order = {
        "creation_ts": current_date.timestamp(),
        "creation_date": current_date.isoformat(),
        "last_update_ts": current_date.timestamp(),
        "last_update_date": current_date.isoformat(),
        "user_id": user_id,
        "cart": cart,
        "is_demo_mode": is_demo_mode,
    }
    if timeslot_lock_id:
        order["timeslot_lock_id"] = timeslot_lock_id

    order_id = rappo_db.order.insert_one(order).inserted_id
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
        rappo_db.order.update_one(
            {"_id": order_id}, {"$set": {"unlock_order_job_id": unlock_order_job.id}}
        )
    return order_id


def unlock_order(order_id):
    try:
        order: Dict = rappo_db.order.find_one({"_id": ObjectId(order_id)})
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
    return rappo_db.order.find_one({"_id": ObjectId(id)})


def get_orders(doctor_id, include_demo_mode: bool = False) -> Dict:
    query = {}
    if not include_demo_mode:
        query["is_demo_mode"] = {"$ne": True}
    if doctor_id:
        query["metadata.doctor._id"] = ObjectId(doctor_id)
    return rappo_db.order.find(query).sort("_id", DESCENDING)


def get_latest_open_order_for_user_id(user_id):
    cursor = (
        rappo_db.order.find(
            {
                "$and": [
                    {"user_id": user_id},
                    {"payment_status.razorpay_payment_link_status": {"$ne": "paid"}},
                ]
            }
        )
        .sort("_id", DESCENDING)
        .limit(1)
    )
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
    current_date = datetime.now(tz=SERVER_TZINFO)
    order = {
        "last_update_ts": current_date.timestamp(),
        "last_update_date": current_date.isoformat(),
    }

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

    rappo_db.order.update_one({"_id": ObjectId(id)}, {"$set": order})


def format_order_header_for_csv() -> Text:
    header_cols = [
        "Order ID",
        "Creation Timestamp",
        "Creation Date",
        "Last Update Timestamp",
        "Last Update Date",
        "Patient ID",
        "Patient Name",
        "Patient Age",
        "Patient Phone",
        "Patient Email",
        "Patient User ID",
        "Doctor ID",
        "Doctor Name",
        "Doctor Phone Number",
        "Doctor Speciality",
        "Doctor User ID",
        "Appointment Date",
        "Meeting ID",
        "Meeting Link Url",
        "Payment Link ID",
        "Payment Link Url",
        "Payment ID",
        "Payment Link Status",
        "Payment Amount (INR)",
        "Payment Creation Timestamp",
        "Payment Method",
        "Payment Status",
    ]
    return ",".join(header_cols)


def format_order_for_csv(order: Dict) -> Text:
    order_cols = [
        f"{get_json_key(order, '_id')}",
        f"{get_json_key(order, 'creation_ts')}",
        f"{get_json_key(order, 'creation_date')}",
        f"{get_json_key(order, 'last_update_ts')}",
        f"{get_json_key(order, 'last_update_date')}",
        f"{get_json_key(order, 'metadata.patient._id')}",
        f"{get_json_key(order, 'metadata.patient.name')}",
        f"{get_json_key(order, 'metadata.patient.age')}",
        f"{get_json_key(order, 'metadata.patient.phone')}",
        f"{get_json_key(order, 'metadata.patient.email')}",
        f"{get_json_key(order, 'metadata.patient.user_id')}",
        f"{get_json_key(order, 'metadata.doctor._id')}",
        f"{get_json_key(order, 'metadata.doctor.name')}",
        f"{get_json_key(order, 'metadata.doctor.phone_number')}",
        f"{get_json_key(order, 'metadata.doctor.speciality')}",
        f"{get_json_key(order, 'metadata.doctor.user_id')}",
        f"{get_json_key(order, 'metadata.appointment_datetime')}",
        f"{get_json_key(order, 'meeting.id')}",
        f"{get_json_key(order, 'meeting.hangoutLink')}",
        f"{get_json_key(order, 'payment_link.metadata.id')}",
        f"{get_json_key(order, 'payment_link.metadata.short_url')}",
        f"{get_json_key(order, 'payment_status.razorpay_payment_id')}",
        f"{get_json_key(order, 'payment_status.razorpay_payment_link_status')}",
        f"{float(get_json_key(order, 'payment_status.payment_details.amount') or 0) / 100}",
        f"{get_json_key(order, 'payment_status.payment_details.created_at')}",
        f"{get_json_key(order, 'payment_status.payment_details.method')}",
        f"{get_json_key(order, 'payment_status.payment_details.status')}",
    ]
    return ",".join(order_cols)
