import logging
import os
from typing_extensions import Annotated

from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, models
from pydantic import BaseModel
import stripe

from backend.auth import auth
from backend.db.db import User, UserUpdate

billing_router = APIRouter(prefix="/billing")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "foo")


class BillingInfo(BaseModel):
    lookup_key: str
    quantity: int


@billing_router.post("/create-checkout-session")
async def create_checkout_session(
    mode: str, lookup_key: Annotated[str, Form()], quantity: Annotated[int, Form()]
):
    if mode != "subscription" and mode != "payment":
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'subscription' or 'payment'",
        )

    if mode == "payment":
        quantity = 1

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": quantity,
                }
            ],
            mode=mode,
            success_url=stripe_success_url(),
            cancel_url=stripe_cancel_url(),
        )
        return RedirectResponse(checkout_session.url, status_code=303)
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=500, detail="Error creating checkout session {e}"
        )


class SubscriptionData(BaseModel):
    session_id: str


@billing_router.post("/subscribe")
async def subscribe_success(
    data: SubscriptionData,
    user: User = Depends(auth.current_active_user),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(
        auth.get_user_manager
    ),
):
    session_id = data.session_id
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription = stripe.Subscription.retrieve(session.subscription)
        print(session)
        print(subscription)
        items = subscription["items"]
        plan = items["data"][0]["price"]["lookup_key"]
        customer_id = session["customer"]
        billing = {"plan": plan, "session_id": session_id, "customer_id": customer_id}
        update = UserUpdate(billing=billing)
        user.billing = billing
        user = await user_manager.update(update, user, safe=True)
    except Exception as e:
        logging.error(f"Error subscribing user: {e}")
        raise HTTPException(status_code=500, detail="Error subscribing user: {e}")
    return {}


def stripe_success_url():
    server = os.environ["SERVER_NAME"]
    return server + "/billing?subscribe_success=true&session_id={CHECKOUT_SESSION_ID}"


def stripe_cancel_url():
    server = os.environ["SERVER_NAME"]
    return server + "/billing?subscribe_cancel=true"


def stripe_return_url():
    server = os.environ["SERVER_NAME"]
    return server + "/billing"


@billing_router.get("/create-portal-session")
async def create_portal_session(user: User = Depends(auth.current_active_user)):
    if not user.billing:
        logging.error(f"User {user.email} has no billing information")
        raise HTTPException(status_code=400, detail="User has no billing information")

    session_id = user.billing["session_id"]
    # customer_id = user.billing["customer_id"]
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        session = stripe.billing_portal.Session.create(
            customer=checkout_session.customer, return_url=stripe_return_url()
        )
        return RedirectResponse(session.url, status_code=303)
    except Exception as e:
        logging.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Error creating portal session")
