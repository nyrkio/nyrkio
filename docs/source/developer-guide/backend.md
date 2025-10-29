# Backend Development

The Nyrkiö backend is built with FastAPI and follows modern Python async patterns.

## Project Structure

```
backend/
├── api/                 # API endpoints
│   ├── api.py          # Main FastAPI app
│   ├── admin.py        # Admin endpoints
│   ├── changes.py      # Change detection
│   └── ...
├── auth/                # Authentication
│   ├── jwt.py          # JWT handling
│   └── oauth.py        # OAuth providers
├── core/                # Business logic
│   ├── hunter.py       # Change detection
│   └── config.py       # Configuration
├── db/                  # Database layer
│   ├── models.py       # Pydantic models
│   └── operations.py   # CRUD operations
├── github/              # GitHub integration
├── notifiers/           # Notifications
│   ├── slack.py        # Slack notifier
│   └── github.py       # GitHub notifier
├── tests/               # Unit tests
└── hunter/              # Submodule

## Setting Up Development Environment

```bash
cd backend
poetry install
poetry shell
```

## Running the Backend

```bash
# Using management script (recommended)
python3 etc/nyrkio_backend.py start

# Using Poetry directly
poetry run uvicorn backend.api.api:app --reload --port 8001
```

## API Development

### Creating a New Endpoint

1. **Define Pydantic models** in `backend/db/models.py`:

```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    name: str
    value: float
```

2. **Create endpoint** in appropriate file under `backend/api/`:

```python
from fastapi import APIRouter, Depends
from backend.auth.jwt import get_current_user

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(
    request: MyRequest,
    user = Depends(get_current_user)
):
    # Your logic here
    return {"status": "success"}
```

3. **Register router** in `backend/api/api.py`:

```python
from backend.api import my_module

app.include_router(my_module.router, prefix="/api/v0", tags=["my-tag"])
```

## Database Operations

### Using Motor (MongoDB)

```python
from backend.db import get_database

async def get_user_data(user_id: str):
    db = await get_database()
    user = await db.users.find_one({"_id": user_id})
    return user

async def save_result(result_data: dict):
    db = await get_database()
    result = await db.results.insert_one(result_data)
    return str(result.inserted_id)
```

### Indexes

Define indexes in `backend/db/operations.py`:

```python
async def ensure_indexes():
    db = await get_database()
    await db.results.create_index([("timestamp", -1)])
    await db.results.create_index([("test_name", 1), ("timestamp", -1)])
```

## Testing

### Writing Unit Tests

Create test file in `backend/tests/`:

```python
import pytest
from backend.api.api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_my_endpoint():
    response = client.post("/api/v0/my-endpoint", json={
        "name": "test",
        "value": 123.45
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### Running Tests

```bash
cd backend

# All tests
./runtests.sh all

# Specific test
poetry run pytest tests/test_api.py::test_my_endpoint

# With coverage
poetry run pytest --cov=backend
```

## Code Quality

### Formatting with Ruff

```bash
# Check formatting
./runtests.sh format

# Auto-fix
./runtests.sh format --fix
```

### Linting with Ruff

```bash
# Check linting
./runtests.sh lint

# Auto-fix
./runtests.sh lint --fix
```

## Authentication

### Protecting Endpoints

```python
from fastapi import Depends
from backend.auth.jwt import get_current_user

@router.get("/protected")
async def protected_endpoint(user = Depends(get_current_user)):
    return {"user_id": user["_id"]}
```

### Optional Authentication

```python
from backend.auth.jwt import get_current_user_optional

@router.get("/optional")
async def optional_auth(user = Depends(get_current_user_optional)):
    if user:
        return {"user_id": user["_id"]}
    return {"anonymous": True}
```

## Change Detection Integration

### Using Hunter

```python
from backend.core.hunter import detect_changes

async def analyze_test_results(test_name: str):
    # Fetch results from database
    results = await get_test_results(test_name)

    # Run change detection
    changes = await detect_changes(results)

    # Store detected changes
    for change in changes:
        await save_change(change)
```

## Configuration

### Environment Variables

Backend reads from `.env.backend`:

```python
from backend.core.config import settings

# Access configuration
db_url = settings.db_url
api_port = settings.api_port
secret_key = settings.secret_key
```

### Adding New Settings

1. Add to `backend/core/config.py`:

```python
class Settings(BaseSettings):
    my_setting: str = "default_value"
```

2. Add to `.env.backend`:

```
MY_SETTING=production_value
```

## Common Patterns

### Error Handling

```python
from fastapi import HTTPException

@router.get("/item/{item_id}")
async def get_item(item_id: str):
    item = await db.items.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_notification(user_id: str):
    # Long-running task
    pass

@router.post("/trigger")
async def trigger_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_notification, "user_123")
    return {"status": "scheduled"}
```

## Debugging

### Using Print Debugging

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/debug")
async def debug_endpoint():
    logger.info("Entering debug endpoint")
    logger.debug(f"Variable value: {some_var}")
    return {"status": "ok"}
```

### Interactive Debugger

```python
import ipdb

@router.get("/debug")
async def debug_endpoint():
    ipdb.set_trace()  # Breakpoint
    return {"status": "ok"}
```
