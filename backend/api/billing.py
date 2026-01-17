import logging
import os
from typing_extensions import Annotated

from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi_users import BaseUserManager, models
from pydantic import BaseModel
import stripe

from backend.auth import auth
from backend.db.db import User, UserUpdate
from backend.api.metered import query_meter_consumption

billing_router = APIRouter(prefix="/billing")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "foo")


class BillingInfo(BaseModel):
    lookup_key: str
    quantity: int


@billing_router.post("/create-checkout-session-postpaid")
async def create_checkout_session_postpaid(
    mode: Annotated[str, Form()],
    lookup_key: Annotated[str, Form()],
    user: User = Depends(auth.current_active_user),
):
    if mode not in ["subscription"]:
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'subscription'",
        )

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    "price": prices.data[0].id,
                }
            ],
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
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


@billing_router.post("/create-checkout-session-prepaid")
async def create_checkout_session_prepaid(
    mode: Annotated[str, Form()],
    lookup_key: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
    user: User = Depends(auth.current_active_user),
):
    if mode not in ["payment"]:
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'payment'",
        )

    try:
        prices = stripe.Price.list(
            lookup_keys=[lookup_key],
            expand=["data.product"],
        )

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": quantity,
                    "adjustable_quantity": {
                        "enabled": True,
                        "maximum": 10000,
                    },
                }
            ],
            automatic_tax={"enabled": True},
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


@billing_router.post("/create-checkout-session-js")
async def create_checkout_session_js(
    mode: str,
    lookup_key: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
    user: User = Depends(auth.current_active_user),
):
    if mode not in ["subscription", "payment", "setup"]:
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'payment', 'setup', or 'subscription'",
        )

    if mode == "payment":
        quantity = quantity if quantity else 1

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": quantity,
                    "adjustable_quantity": {
                        "enabled": True,
                    },
                }
            ],
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
            mode=mode,
            success_url=stripe_success_url(),
            cancel_url=stripe_cancel_url(),
        )
        return JSONResponse(
            {"stripe_checkout_url": checkout_session.url}, status_code=200
        )
    except Exception as e:
        logging.error(f"Error creating 2026 JS friendly checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating 2026 JS friendly checkout session {e}",
        )


@billing_router.get("/create-checkout-session-get")
async def create_checkout_session_get(
    mode: str,
    lookup_key: str,
    quantity: int,
    user: User = Depends(auth.current_active_user),
):
    if mode not in ["subscription", "payment", "setup"]:
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'payment', 'setup', or 'subscription'",
        )

    if mode == "payment":
        quantity = quantity if quantity else 1

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": quantity,
                    "adjustable_quantity": {
                        "enabled": True,
                    },
                }
            ],
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
            mode=mode,
            success_url=stripe_success_url(),
            cancel_url=stripe_cancel_url(),
        )
        return RedirectResponse(checkout_session.url, status_code=303)
    except Exception as e:
        logging.error(f"Error creating 2026 JS friendly checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating 2026 JS friendly checkout session {e}",
        )


@billing_router.post("/create-checkout-session")
async def create_checkout_session(
    mode: str,
    lookup_key: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
    user: User = Depends(auth.current_active_user),
):
    if mode not in ["subscription", "payment", "setup"]:
        logging.error(f"Invalid checkout mode: {mode}")
        raise HTTPException(
            status_code=400,
            detail="Invalid checkout mode, expected 'payment', 'setup', or 'subscription'",
        )

    if mode == "payment":
        quantity = quantity if quantity else 1

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
        print(prices)
        print(prices.data)

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": quantity,
                    "adjustable_quantity": {
                        "enabled": True,
                    },
                }
            ],
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
            mode=mode,
            success_url=stripe_success_url(),
            cancel_url=stripe_cancel_url(),
        )
        return RedirectResponse(checkout_session.url, status_code=303)
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error creating checkout session {e}"
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
        if plan in ["runner_postpaid_10"]:
            update = UserUpdate(billing_runners=billing)
            user.billing_runners = billing
            user = await user_manager.update(update, user, safe=True)

        else:
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
    if not user.billing and not user.billing_runners:
        logging.error(f"User {user.email} has no billing information")
        raise HTTPException(status_code=400, detail="User has no billing information")

    logging.info("Starting billing/create-portal-session")
    logging.info(user)
    logging.info(user.billing)
    logging.info(user.billing_runners)
    # session_id = user.billing["session_id"]
    customer_id = None
    if user.billing:
        customer_id = user.billing.get("customer_id")
    if customer_id is None and user.billing_runners:
        customer_id = user.billing_runners["customer_id"]
    try:
        # checkout_session = stripe.checkout.Session.retrieve(session_id)
        session = stripe.billing_portal.Session.create(
            customer=customer_id, return_url=stripe_return_url()
        )
        return {"customer_id": customer_id, "session": session}
    # return RedirectResponse(session.url, status_code=303)
    except Exception as e:
        logging.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Error creating portal session")


@billing_router.get("/meter")
async def get_meter(user: User = Depends(auth.current_active_user)):
    if not user.billing and not user.billing_runners:
        logging.error(f"User {user.email} has no billing information")
        raise HTTPException(status_code=400, detail="User has no billing information")

    stripe_customer_id = user.billing_runners.get(
        "customer_id", user.billing.get("customer_id", user.email)
    )
    return query_meter_consumption(stripe_customer_id)
