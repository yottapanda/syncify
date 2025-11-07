from stripe import StripeClient

from common import conf
from common.conf import stripe_secret_key


client = StripeClient(stripe_secret_key)


def create_customer() -> str:
    return client.customers.create().id


def delete_customer(customer_id: str) -> None:
    client.customers.delete(customer_id)


def create_checkout_session(customer_id: str) -> str | None:
    prices = client.prices.list(
        {
            "active": True,
            "product": conf.stripe_product_id,
            "limit": 1,
        }
    )
    if not prices.data:
        raise Exception("No active prices found for product.")

    price_id = prices.data[0].id

    session = client.checkout.sessions.create(
        {
            "payment_method_types": ["card"],
            "customer": customer_id,
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "mode": "subscription",
            "success_url": f"{conf.base_uri}/dashboard",
            "cancel_url": f"{conf.base_uri}/dashboard",
        }
    )

    return session.url


def has_active_subscription(customer_id: str) -> bool:
    subscriptions = client.subscriptions.list(
        {"customer": customer_id, "status": "active"}
    )
    return len(subscriptions.data) > 0


def get_portal_url(customer_id: str) -> str:
    portal_session = client.billing_portal.sessions.create(
        {
            "customer": customer_id,
        }
    )
    return portal_session.url
