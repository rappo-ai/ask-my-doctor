import base64
import json
import http.client
from typing import Text
import razorpay
import requests
from requests.structures import CaseInsensitiveDict

from actions.utils.host import get_host_url
import os

from actions.utils.admin_config import (
    get_account_number,
    set_account_number,
)


def create_payment_link(
    amount_rupees: int,
    name: Text,
    email: Text,
    phone: Text,
    description: Text,
    order_id: Text,
):
    url = "https://api.razorpay.com/v1/payment_links"

    credentials = os.getenv("RAZORPAY_KEY_ID") + ":" + os.getenv("RAZORPAY_SECRET_KEY")
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")

    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"
    headers["Authorization"] = "basic " + credential

    account_number = get_account_number()
    amount_paise = amount_rupees * 100
    amount_transferred = amount_rupees * 0.95 * 100
    url_pay = get_host_url("/webhooks/telegram/payment_callback")

    data1 = {
        "amount": amount_paise,
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
                        "account": account_number,
                        "amount": amount_transferred,
                        "currency": "INR",
                        "currency": "INR",
                        "notes": {
                            "branch": "Acme Corp Bangalore North",
                            "name": "Nikhil Hulle",
                        },
                        "linked_account_notes": ["branch"],
                    }
                ]
            },
            "checkout": {"name": "AskMyDoctor"},
        },
    }

    r = json.dumps(data1)
    resp = requests.post(url, headers=headers, data=r)
    info = json.loads(resp.text)

    payment_link_info = {"link": info["short_url"]}
    return payment_link_info
