import json
from typing import Text
import razorpay
import requests
from requests.structures import CaseInsensitiveDict

from actions.utils.host import get_host_url


def create_payment_link(
    amount_rupees: int,
    name: Text,
    email: Text,
    phone: Text,
    description: Text,
    order_id: Text,
):
    # #tbdnikhil - create Razorpay payment link here; add / remove fields as needed

    client = razorpay.Client(
        auth=("rzp_test_rD6PXVUtWKrB8q", "xzeXnI5qAtOWSX96cwSeCw8n")
    )
    url = "https://api.razorpay.com/v1/payment_links"

    headers = CaseInsensitiveDict()
    headers["Content-type"] = "application/json"
    headers[
        "Authorization"
    ] = "Basic cnpwX3Rlc3RfckQ2UFhWVXRXS3JCOHE6eHplWG5JNXFBdE9XU1g5NmN3U2VDdzhu"

    amount_paise = amount_rupees * 100
    # "reference_id": str(order_id),
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
                        "account": "acc_HLeMvH2h0YvRvT",
                        "amount": 500,
                        "currency": "INR",
                        "notes": {
                            "branch": "Acme Corp Bangalore North",
                            "name": "Nikhil Hulle",
                        },
                        "linked_account_notes": ["branch"],
                    }
                ]
            }
        },
    }

    r = json.dumps(data1)

    resp = requests.post(url, headers=headers, data=r)
    l = True
    info = json.loads(resp.text)

    payment_link_info = {"link": info["short_url"]}
    return payment_link_info
