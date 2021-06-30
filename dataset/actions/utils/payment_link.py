from typing import Text


def create_payment_link(
    amount: int, name: Text, email: Text, phone: Text, description: Text, order_id: Text
):
    # #tbdnikhil - create Razorpay payment link here; add / remove fields as needed
    payment_link_info = {"link": "https://rzp.io/i/4E2QCoUO"}
    return payment_link_info