import os
import pytest


def test_create_checkout_session(client):
    """Test the create_checkout_session endpoint."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    response = client.post(
        "/api/v0/billing/create-checkout-session",
        follow_redirects=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"lookup_key": "business_monthly", "quantity": 101},
    )
    assert response.status_code == 303
    assert response.headers["Location"].startswith(
        "https://checkout.stripe.com/c/pay/cs_test"
    )
