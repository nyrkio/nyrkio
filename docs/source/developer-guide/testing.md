# Testing

Comprehensive testing guide for Nyrkiö.

## Backend Testing

### Test Structure

```
backend/
├── tests/              # Unit tests
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_hunter.py
└── integration_tests/  # Integration tests
    ├── test_flows.py
    └── test_github.py
```

### Running Tests

```bash
cd backend

# All tests
./runtests.sh all

# Unit tests only
./runtests.sh unit

# Integration tests
./runtests.sh int

# Specific test file
poetry run pytest tests/test_api.py

# Specific test
poetry run pytest tests/test_api.py::test_submit_result

# With coverage
poetry run pytest --cov=backend --cov-report=html

# Parallel execution
poetry run pytest -n auto
```

### Writing Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from backend.api.api import app

client = TestClient(app)

def test_submit_result():
    response = client.post("/api/v0/result/test-name", json={
        "timestamp": 1640000000,
        "metrics": [{
            "name": "latency",
            "value": 100,
            "direction": "lower_is_better"
        }]
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert "change_id" in response.json()
```

### Fixtures

```python
import pytest
from backend.db import get_database

@pytest.fixture
async def test_db():
    """Provide a test database"""
    db = await get_database()
    yield db
    # Cleanup
    await db.results.delete_many({})

@pytest.fixture
def test_user():
    """Provide a test user"""
    return {
        "_id": "test_user_123",
        "email": "test@example.com"
    }

def test_with_fixtures(test_db, test_user):
    # Test using fixtures
    pass
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch('backend.notifiers.slack.send_slack_message')
def test_notification(mock_send):
    mock_send.return_value = True

    # Test code that calls send_slack_message
    result = trigger_notification()

    mock_send.assert_called_once()
    assert result is True
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

## Frontend Testing

### Test Structure

```
frontend/
└── src/
    ├── components/
    │   └── MyComponent.test.jsx
    └── __tests__/
        └── integration.test.jsx
```

### Running Frontend Tests

```bash
cd frontend

# All tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### Component Testing

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MyComponent } from './MyComponent';

test('renders component', () => {
  render(<MyComponent title="Test" />);
  expect(screen.getByText('Test')).toBeInTheDocument();
});

test('handles user interaction', async () => {
  const user = userEvent.setup();
  render(<MyComponent />);

  const button = screen.getByRole('button', { name: /click me/i });
  await user.click(button);

  expect(screen.getByText('Clicked!')).toBeInTheDocument();
});
```

### API Mocking

```jsx
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/v0/result/test', (req, res, ctx) => {
    return res(ctx.json({ results: [] }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches data', async () => {
  render(<TestResults testName="test" />);
  await waitFor(() => {
    expect(screen.getByText('No results')).toBeInTheDocument();
  });
});
```

## Integration Testing

### End-to-End Flow

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
async def test_complete_workflow():
    # 1. Register user
    response = client.post("/auth/register", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200

    # 2. Submit result
    token = response.json()["token"]
    response = client.post("/api/v0/result/my-test",
        json=test_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # 3. Get results
    response = client.get("/api/v0/result/my-test",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(response.json()["results"]) == 1
```

## Performance Testing

### Load Testing

```bash
cd backend

# Run performance tests
./runtests.sh perf

# With deployment
./runtests.sh perf --deploy
```

### Benchmarking

```python
import pytest

@pytest.mark.benchmark
def test_change_detection_performance(benchmark):
    result = benchmark(detect_changes, test_data)
    assert result is not None
```

## Test Coverage

### Generate Coverage Report

```bash
cd backend
poetry run pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

### Coverage Goals

- Overall: >80%
- Critical paths: >95%
- New code: 100%

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main
- Scheduled nightly builds

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          ./runtests.sh all
```

## Best Practices

1. **Write tests first** (TDD when appropriate)
2. **Keep tests isolated** (no shared state)
3. **Use descriptive names** (`test_submit_result_creates_change_point`)
4. **Test edge cases** (empty input, null values, etc.)
5. **Mock external services** (GitHub API, Slack, etc.)
6. **Clean up after tests** (fixtures with cleanup)
7. **Run tests before commit** (use pre-commit hooks)

## Common Issues

### Database Connection

```python
@pytest.fixture(autouse=True)
async def setup_db():
    # Ensure test database
    os.environ["DB_NAME"] = "nyrkiodb_test"
    yield
    # Cleanup
    db = await get_database()
    await db.client.drop_database("nyrkiodb_test")
```

### Authentication

```python
@pytest.fixture
def auth_headers():
    token = create_test_token("test_user")
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(auth_headers):
    response = client.get("/api/v0/protected", headers=auth_headers)
    assert response.status_code == 200
```
