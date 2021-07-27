import base64
import calendar
from datetime import datetime, timedelta
import json
import logging
import os
import requests
from requests.structures import CaseInsensitiveDict
from typing import Text

from actions.utils.admin_config import get_payment_route_config
from actions.utils.branding import get_bot_display_name
from actions.utils.date import SERVER_TZINFO
from actions.utils.host import get_host_url

logger = logging.getLogger(__name__)


def create_payment_link(
    amount_rupees: int,
    name: Text,
    email: Text,
    phone: Text,
    description: Text,
    expire_by_seconds: None,
    order_id: Text,
):
    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
    razorpay_secret_key = os.getenv("RAZORPAY_SECRET_KEY")

    if not (razorpay_key_id and razorpay_secret_key):
        logger.warn(
            "RAZORPAY_KEY_ID or RAZORPAY_SECRET_KEY not set, using dummy payment link"
        )
        return {"short_url": "https://rzp.io/i/8sxP5EFYC"}

    url = "https://api.razorpay.com/v1/payment_links"

    credentials = razorpay_key_id + ":" + razorpay_secret_key
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")

    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"
    headers["Authorization"] = "basic " + credential

    payment_route_config = get_payment_route_config()
    transfer_account_number = payment_route_config.get("account_number")
    commission = payment_route_config.get("commission")
    transfer_rate = (100 - commission) / 100
    amount_to_bill = amount_rupees * 100
    amount_to_transfer = amount_rupees * transfer_rate * 100
    url_pay = get_host_url("/webhooks/telegram/payment_callback")

    request_data = {
        "amount": amount_to_bill,
        "currency": "INR",
        "accept_partial": False,
        "reference_id": str(order_id),
        "callback_method": "get",
        "callback_url": url_pay,
        "description": description,
        "customer": {
            "name": name,
            "contact": phone,
            "email": email,
        },
        "options": {
            "order": {
                "transfers": [
                    {
                        "account": transfer_account_number,
                        "amount": amount_to_transfer,
                        "currency": "INR",
                    }
                ]
            },
            "checkout": {"name": get_bot_display_name()},
        },
    }

    if expire_by_seconds:
        EXTRA_SECONDS_FOR_REQUEST = 10
        MIN_RAZORPAY_EXPIRE_BY_MINUTES = 15
        MIN_RAZORPAY_EXPIRE_BY_SECONDS = (
            MIN_RAZORPAY_EXPIRE_BY_MINUTES * 60
        ) + EXTRA_SECONDS_FOR_REQUEST
        if expire_by_seconds < MIN_RAZORPAY_EXPIRE_BY_SECONDS:
            expire_by_seconds = MIN_RAZORPAY_EXPIRE_BY_SECONDS
        expiry_dt = datetime.now(tz=SERVER_TZINFO) + timedelta(
            seconds=expire_by_seconds
        )
        request_data["expire_by"] = calendar.timegm(datetime.utctimetuple(expiry_dt))

    request_data_str = json.dumps(request_data)
    resp = requests.post(url, headers=headers, data=request_data_str)
    payment_link_info = json.loads(resp.text)

    payment_link_internal = get_host_url(
        f"/webhooks/telegram/payment_link?order_id={order_id}"
    )
    return {"url": payment_link_internal, "metadata": payment_link_info}
