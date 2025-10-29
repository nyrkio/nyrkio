# CLI Tools

Command-line tools for managing Nyrkiö.

## Management Scripts

Nyrkiö provides Python-based management scripts in the `etc/` directory for controlling services.

### Backend Server

**Script**: `etc/nyrkio_backend.py`

Manages the FastAPI backend server.

#### Start Backend

```bash
python3 etc/nyrkio_backend.py start
```

Starts the backend server on port 8001 (configurable via `.env.backend`).

Features:
- Runs in background
- Auto-reload enabled for development
- Uses Poetry environment if available

#### Stop Backend

```bash
python3 etc/nyrkio_backend.py stop
```

Gracefully stops the backend server.

#### Restart Backend

```bash
python3 etc/nyrkio_backend.py restart
```

Stops and starts the backend server.

#### Check Status

```bash
python3 etc/nyrkio_backend.py status
```

Shows whether the backend is running and its process ID.

### Frontend Server

**Script**: `etc/nyrkio_frontend.py`

Manages the Vite development server with deployment mode support.

#### Start Frontend (Local Mode)

```bash
python3 etc/nyrkio_frontend.py start
```

Starts frontend with local backend (http://localhost:8001).

#### Start Frontend (Production Mode)

```bash
python3 etc/nyrkio_frontend.py start --mode production
```

Starts frontend with production backend (https://nyrk.io).

#### Custom Port

```bash
python3 etc/nyrkio_frontend.py start --port 3000
```

Start on custom port (default: 5173).

#### Stop Frontend

```bash
python3 etc/nyrkio_frontend.py stop
```

#### Restart Frontend

```bash
python3 etc/nyrkio_frontend.py restart
```

#### Check Status

```bash
python3 etc/nyrkio_frontend.py status
```

#### Install Dependencies Only

```bash
python3 etc/nyrkio_frontend.py install
```

Installs npm dependencies without starting the server.

### Docker Stack

**Script**: `etc/nyrkio_docker.py`

Manages the full Docker Compose stack.

#### Start Docker Stack

```bash
python3 etc/nyrkio_docker.py start
```

Starts all services:
- Backend API (port 8000)
- Webhooks service (port 8080)
- Nginx proxy (port 80)
- MongoDB (port 27017)

#### Stop Docker Stack

```bash
python3 etc/nyrkio_docker.py stop
```

#### Restart Docker Stack

```bash
python3 etc/nyrkio_docker.py restart
```

#### Check Status

```bash
python3 etc/nyrkio_docker.py status
```

## Testing Scripts

### Backend Tests

**Script**: `backend/runtests.sh`

Comprehensive test runner for backend code.

#### Run All Tests

```bash
cd backend
./runtests.sh all
```

Runs format checks, linting, and all tests.

#### Unit Tests Only

```bash
./runtests.sh unit
```

#### Integration Tests

```bash
./runtests.sh int
```

#### Check Formatting

```bash
./runtests.sh format
```

#### Fix Formatting

```bash
./runtests.sh format --fix
```

#### Run Linting

```bash
./runtests.sh lint
```

#### Fix Linting Issues

```bash
./runtests.sh lint --fix
```

#### Performance Tests

```bash
./runtests.sh perf
```

Run performance benchmarks.

#### Performance Tests with Deployment

```bash
./runtests.sh perf --deploy
```

Run performance tests against Docker deployment.

### Management Script Tests

**Script**: `etc/test_management_scripts.py`

Tests all management scripts.

```bash
python3 etc/test_management_scripts.py
```

Tests verify:
- Script existence and permissions
- Help command support
- Status commands
- Vite configuration files
- Documentation references

## Direct Poetry Commands

For advanced usage, you can use Poetry directly.

### Run Backend

```bash
cd backend
poetry run uvicorn backend.api.api:app --host 0.0.0.0 --port 8001 --reload
```

### Run Tests

```bash
cd backend
poetry run pytest
```

### Run Tests in Parallel

```bash
poetry run pytest -n auto
```

### Run Specific Test File

```bash
poetry run pytest tests/test_api.py
```

### Run with Coverage

```bash
poetry run pytest --cov=backend --cov-report=html
```

### Run Linting

```bash
poetry run ruff check backend/
```

### Fix Linting

```bash
poetry run ruff check --fix backend/
```

### Format Code

```bash
poetry run ruff format backend/
```

## Configuration Files

### Backend Configuration

**File**: `.env.backend`

```bash
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb
API_PORT=8001
SECRET_KEY=your-secret-key
POSTMARK_API_KEY=email-api-key
GITHUB_CLIENT_SECRET=github-oauth-secret
```

### Frontend Configuration

**Local Development**: `frontend/vite.config.test.js`
- Proxies to `http://localhost:8001`

**Production**: `frontend/vite.config.js`
- Proxies to `https://nyrk.io`

## Common Workflows

### Full Stack Development

Start both backend and frontend:

```bash
# Terminal 1: Start backend
python3 etc/nyrkio_backend.py start

# Terminal 2: Start frontend
python3 etc/nyrkio_frontend.py start

# Check status
python3 etc/nyrkio_backend.py status
python3 etc/nyrkio_frontend.py status
```

### Run Tests Before Commit

```bash
cd backend
./runtests.sh all
```

### Docker Deployment

```bash
# Start full stack
python3 etc/nyrkio_docker.py start

# Check logs
docker compose -f docker-compose.dev.yml logs -f

# Stop stack
python3 etc/nyrkio_docker.py stop
```

## Environment Variables

### Backend Environment

```bash
# Database
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb

# API Configuration
API_PORT=8001
SECRET_KEY=your-jwt-secret

# External Services
POSTMARK_API_KEY=email-service-key
GITHUB_CLIENT_SECRET=github-oauth-secret

# Optional
HUNTER_CONFIG=hunter-config-path
GRAFANA_USER=grafana-username
GRAFANA_PASSWORD=grafana-password
```

### Setting Environment Variables

#### macOS/Linux

```bash
export DB_URL=mongodb://localhost:27017/nyrkiodb
export DB_NAME=nyrkiodb
export API_PORT=8001
```

#### Using .env.backend

Create `.env.backend` file at project root:

```bash
cat > .env.backend << 'EOF'
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb
API_PORT=8001
EOF
```

The management scripts will automatically load this file.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

### Poetry Not Found

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### MongoDB Connection Failed

```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or check MongoDB service status
sudo systemctl status mongodb  # Linux
brew services list             # macOS with Homebrew
```

### Module Import Errors

```bash
# Reinstall dependencies
cd backend
poetry install --no-interaction

# Clear Python cache
find backend -type d -name __pycache__ -exec rm -rf {} +
```

## Getting Help

All scripts support the `--help` flag:

```bash
python3 etc/nyrkio_backend.py --help
python3 etc/nyrkio_frontend.py --help
python3 etc/nyrkio_docker.py --help
```
