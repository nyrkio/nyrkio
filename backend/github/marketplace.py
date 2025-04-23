from backend.db.db import DBStore
from fastapi import APIRouter
from typing import Dict
from datetime import datetime, timezone

market_router = APIRouter(prefix="/github")


@market_router.post("/marketplace-events")
async def marketplace_events(gh_event: Dict):
    store = DBStore()
    await store.log_json_event(gh_event, "GitHub Marketplace Webhook")
    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}


@market_router.post("/webhook")
async def github_events(gh_event: Dict):
    store = DBStore()
    await store.log_json_event(gh_event, "GitHub App Webhook")

    if gh_event["action"] in ["created"]:
        gh_id = gh_event["installation"]["account"]["id"]
        await store.set_github_installation(gh_id, gh_event)
    if gh_event["action"] in ["deleted"]:
        gh_id = gh_event["installation"]["account"]["id"]
        await store.set_github_installation(
            gh_id,
            {
                "nyrkio_status": "deleted",
                "nyrkio_datetime": datetime.now(tz=timezone.utc),
            },
        )

    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}
