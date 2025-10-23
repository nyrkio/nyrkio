import os
import pytest
from unittest.mock import patch, Mock
from backend.api.billing import stripe_success_url, stripe_cancel_url, stripe_return_url


def test_create_checkout_session(client):
    """Test the create_checkout_session endpoint."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    response = client.post(
        "/api/v0/billing/create-checkout-session?mode=subscription",
        follow_redirects=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"lookup_key": "business_monthly", "quantity": 101},
    )
    assert response.status_code == 303
    assert response.headers["Location"].startswith(
        "https://checkout.stripe.com/c/pay/cs_test"
    )

    response = client.post(
        "/api/v0/billing/create-checkout-session?mode=payment",
        follow_redirects=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"lookup_key": "services_kickstart", "quantity": 1},
    )
    assert response.status_code == 303
    assert response.headers["Location"].startswith(
        "https://checkout.stripe.com/c/pay/cs_test"
    )

    response = client.post(
        "/api/v0/billing/create-checkout-session?mode=invalid",
        follow_redirects=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"lookup_key": "services_kickstart", "quantity": 101},
    )
    assert response.status_code == 400

    response = client.post(
        "/api/v0/billing/create-checkout-session",
        follow_redirects=False,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"lookup_key": "services_kickstart", "quantity": 101},
    )
    assert response.status_code == 422


def test_create_portal_session_without_billing_info(client):
    """Test that create_portal_session fails when user has no billing info."""
    client.login()

    response = client.get("/api/v0/billing/create-portal-session")
    assert response.status_code == 400
    assert "billing information" in response.json()["detail"].lower()


@patch("backend.api.billing.stripe")
def test_subscribe_success(mock_stripe, client):
    """Test successful subscription."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    # Mock Stripe API responses
    mock_session = Mock()
    mock_session.subscription = "sub_123"
    mock_session.__getitem__ = Mock(side_effect=lambda x: {"customer": "cus_123"}[x])

    mock_subscription = Mock()
    mock_subscription.__getitem__ = Mock(
        side_effect=lambda x: {
            "items": {
                "data": [{"price": {"lookup_key": "business_monthly"}}]
            }
        }[x]
    )

    mock_stripe.checkout.Session.retrieve.return_value = mock_session
    mock_stripe.Subscription.retrieve.return_value = mock_subscription

    response = client.post(
        "/api/v0/billing/subscribe",
        json={"session_id": "cs_test_123"},
    )
    assert response.status_code == 200
    assert response.json() == {}


def test_stripe_url_helpers():
    """Test URL helper functions."""
    # Set up environment
    test_server = "https://example.com"
    os.environ["SERVER_NAME"] = test_server

    success_url = stripe_success_url()
    assert success_url.startswith(test_server)
    assert "subscribe_success=true" in success_url
    assert "session_id={CHECKOUT_SESSION_ID}" in success_url

    cancel_url = stripe_cancel_url()
    assert cancel_url.startswith(test_server)
    assert "subscribe_cancel=true" in cancel_url

    return_url = stripe_return_url()
    assert return_url == test_server + "/billing"


@patch("backend.api.billing.stripe")
def test_subscribe_with_stripe_error(mock_stripe, client):
    """Test subscription handling when Stripe API fails."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    # Mock Stripe to raise an exception
    mock_stripe.checkout.Session.retrieve.side_effect = Exception("Stripe API error")

    response = client.post(
        "/api/v0/billing/subscribe",
        json={"session_id": "cs_test_123"},
    )
    assert response.status_code == 500
    assert "Error subscribing user" in response.json()["detail"]


@patch("backend.api.billing.stripe")
def test_create_portal_session_with_billing_info(mock_stripe, client):
    """Test creating portal session for user with billing info."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    # First subscribe the user
    mock_session = Mock()
    mock_session.subscription = "sub_123"
    mock_session.__getitem__ = Mock(side_effect=lambda x: {"customer": "cus_123"}[x])

    mock_subscription = Mock()
    mock_subscription.__getitem__ = Mock(
        side_effect=lambda x: {
            "items": {
                "data": [{"price": {"lookup_key": "business_monthly"}}]
            }
        }[x]
    )

    mock_stripe.checkout.Session.retrieve.return_value = mock_session
    mock_stripe.Subscription.retrieve.return_value = mock_subscription

    # Subscribe first
    response = client.post(
        "/api/v0/billing/subscribe",
        json={"session_id": "cs_test_123"},
    )
    assert response.status_code == 200

    # Mock portal session creation
    mock_portal_session = Mock()
    mock_portal_session.url = "https://billing.stripe.com/session/test"
    mock_stripe.billing_portal.Session.create.return_value = mock_portal_session

    # Now try to create portal session
    response = client.get("/api/v0/billing/create-portal-session")
    assert response.status_code == 200
    json_response = response.json()
    assert "customer_id" in json_response
    assert "session" in json_response


@patch("backend.api.billing.stripe")
def test_create_portal_session_stripe_error(mock_stripe, client):
    """Test portal session creation when Stripe fails."""
    key = os.environ.get("STRIPE_SECRET_KEY", None)
    if not key:
        pytest.skip("STRIPE_SECRET_KEY not set")

    client.login()

    # First subscribe the user
    mock_session = Mock()
    mock_session.subscription = "sub_123"
    mock_session.__getitem__ = Mock(side_effect=lambda x: {"customer": "cus_123"}[x])

    mock_subscription = Mock()
    mock_subscription.__getitem__ = Mock(
        side_effect=lambda x: {
            "items": {
                "data": [{"price": {"lookup_key": "business_monthly"}}]
            }
        }[x]
    )

    mock_stripe.checkout.Session.retrieve.return_value = mock_session
    mock_stripe.Subscription.retrieve.return_value = mock_subscription

    # Subscribe first
    response = client.post(
        "/api/v0/billing/subscribe",
        json={"session_id": "cs_test_123"},
    )
    assert response.status_code == 200

    # Mock portal session creation to fail
    mock_stripe.billing_portal.Session.create.side_effect = Exception("Stripe error")

    response = client.get("/api/v0/billing/create-portal-session")
    assert response.status_code == 500
    assert "Error creating portal session" in response.json()["detail"]
