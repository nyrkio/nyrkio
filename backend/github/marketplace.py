from backend.db.db import DBStore
from fastapi import APIRouter
from typing import Dict

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
    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}
