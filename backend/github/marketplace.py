from backend.db.db import DBStore
from FastAPI import APIRouter
from typing import Dict

market_router = APIRouter(prefix="/github")


@market_router.post("/marketplace-events")
async def marketplace_events(gh_event: Dict):
    store = DBStore()
    store.log_json_event(gh_event, "GitHub Marketplace Webhook")
    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}
