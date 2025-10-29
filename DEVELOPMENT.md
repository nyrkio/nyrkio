# Nyrkiö Development Guide

This guide provides detailed instructions for setting up and working with the Nyrkiö codebase.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation Options](#installation-options)
- [Running the Backend](#running-the-backend)
- [Running Tests](#running-tests)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Quick Start

The fastest way to get started:

```bash
# Clone the repository
git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio

# Initialize submodules
git submodule init
git submodule update

# Install backend dependencies
cd backend
poetry install
cd ..

# Create environment file
cat > .env.backend << 'EOF'
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=
API_PORT=8001
EOF

# Start the backend
python3 etc/nyrkio_backend.py start
```

The backend will be available at http://localhost:8001 with OpenAPI docs at http://localhost:8001/docs.

## Installation Options

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - Python dependency manager
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```
- **MongoDB** - Either installed locally or via Docker
  ```bash
  # Using Docker
  docker run -d -p 27017:27017 --name mongodb mongo:latest

  # Or install MongoDB Community Edition
  # See: https://docs.mongodb.com/manual/installation/
  ```
- **Node.js & npm** (for frontend) - [Download Node.js](https://nodejs.org/)
- **Docker & Docker Compose** (optional, for full stack) - [Download Docker](https://www.docker.com/get-started)

## Running the Frontend

### Using nyrkio_frontend.py (Recommended)

The `etc/nyrkio_frontend.py` script manages the frontend development server with support for different deployment modes:

```bash
# Start frontend with local backend (default)
python3 etc/nyrkio_frontend.py start

# Start frontend with production backend
python3 etc/nyrkio_frontend.py start --mode production

# Start on custom port
python3 etc/nyrkio_frontend.py start --port 3000

# Check frontend status
python3 etc/nyrkio_frontend.py status

# Stop frontend
python3 etc/nyrkio_frontend.py stop

# Restart frontend
python3 etc/nyrkio_frontend.py restart

# Install dependencies only
python3 etc/nyrkio_frontend.py install
```

**Deployment Modes:**

- **local** (default): Uses `vite.config.test.js` - proxies API requests to `http://localhost:8001`
- **production**: Uses `vite.config.js` - proxies API requests to `https://nyrk.io`

**Features:**
- Auto-detects and installs npm dependencies
- Runs server in background with PID tracking
- Configurable port (default: 5173)
- Graceful shutdown support

**Frontend Configuration Files:**

- `frontend/vite.config.js` - Production configuration (proxies to https://nyrk.io)
- `frontend/vite.config.test.js` - Local development configuration (proxies to http://localhost:8001)

### Using npm Directly

For foreground execution with full output:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start with local config
npm run dev -- --config vite.config.test.js --port 5173

# Start with production config
npm run dev -- --config vite.config.js --port 5173
```

**Default URLs:**
- Frontend: http://localhost:5173
- API (local): http://localhost:8001
- API (production): https://nyrk.io

### Full Stack Development

For a complete local development environment:

```bash
# Terminal 1: Start backend
python3 etc/nyrkio_backend.py start

# Terminal 2: Start frontend in local mode
python3 etc/nyrkio_frontend.py start

# Or run both and check status
python3 etc/nyrkio_backend.py status
python3 etc/nyrkio_frontend.py status
```

## Running the Backend

### Using nyrkio_backend.py (Recommended)

The `etc/nyrkio_backend.py` script manages the backend server process:

```bash
# Start the backend server
python3 etc/nyrkio_backend.py start

# Check if backend is running
python3 etc/nyrkio_backend.py status

# Stop the backend server
python3 etc/nyrkio_backend.py stop

# Restart the backend server
python3 etc/nyrkio_backend.py restart
```

**Features:**
- Runs server in background
- Auto-detects Poetry or system Python environment
- Manages PID file for process tracking
- Graceful shutdown with fallback to force kill

**Default Configuration:**
- Port: 8001 (configurable via `.env.backend`)
- Auto-reload: Enabled for development

### Using Poetry Directly

For foreground execution with full output:

```bash
cd backend
poetry run uvicorn backend.api.api:app --host 0.0.0.0 --port 8001 --reload
```

### Using Docker Compose (Full Stack)

To run the complete stack including nginx, webhooks, and MongoDB:

```bash
# Start Docker stack
python3 etc/nyrkio_docker.py start

# Check Docker stack status
python3 etc/nyrkio_docker.py status

# Stop Docker stack
python3 etc/nyrkio_docker.py stop

# Restart Docker stack
python3 etc/nyrkio_docker.py restart

# Or using docker compose directly
export IMAGE_TAG=$(git rev-parse HEAD)
docker compose -f docker-compose.dev.yml up --build
```

**Services:**
- Backend API: http://localhost:8000
- Webhooks: http://localhost:8080
- Nginx proxy: http://localhost:80
- MongoDB: localhost:27017

## Testing Management Scripts

To verify that all management scripts are working correctly:

```bash
# Run the management scripts test suite
python3 etc/test_management_scripts.py
```

This test suite verifies:
- All scripts exist and are executable
- Scripts respond to `--help` flag
- Scripts accept correct command-line arguments
- Status commands work when services are stopped
- Vite configuration files exist and have correct targets
- Documentation references correct script paths
- No references to old script names remain

## Running Tests

### Backend Tests

The `backend/runtests.sh` script provides various testing options:

```bash
cd backend

# Run all checks (format, lint, tests)
./runtests.sh all

# Run unit tests only
./runtests.sh unit

# Run integration tests
./runtests.sh int

# Check code formatting
./runtests.sh format

# Run linting
./runtests.sh lint

# Fix formatting issues automatically
./runtests.sh format --fix

# Fix linting issues automatically
./runtests.sh lint --fix
```

### Using Poetry/Pytest Directly

```bash
cd backend

# Run all tests
poetry run pytest

# Run tests in parallel
poetry run pytest -n auto

# Run specific test file
poetry run pytest tests/test_api.py

# Run with coverage
poetry run pytest --cov=backend --cov-report=html

# Run with verbose output
poetry run pytest -v
```

### Performance Tests

```bash
cd backend

# Run performance benchmarks
./runtests.sh perf

# With Docker deployment
./runtests.sh perf --deploy
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature-name
```

### 2. Make Changes

Edit code in the `backend/` directory. The server will auto-reload when files change (if using `--reload` flag).

### 3. Run Tests and Linting

```bash
cd backend
./runtests.sh all
```

### 4. Format and Lint

```bash
cd backend

# Check formatting
./runtests.sh format

# Fix formatting
./runtests.sh format --fix

# Run linting
./runtests.sh lint

# Fix linting issues
./runtests.sh lint --fix
```

### 5. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

### 6. Push and Create PR

```bash
git push origin feature-name
```

Then open a pull request on GitHub against the `main` branch.

## Project Structure

```
nyrkio/
├── backend/                  # FastAPI backend application
│   ├── api/                 # API endpoints
│   │   ├── api.py          # Main FastAPI app
│   │   ├── admin.py        # Admin endpoints
│   │   ├── billing.py      # Billing endpoints
│   │   ├── changes.py      # Change detection endpoints
│   │   └── ...
│   ├── auth/                # Authentication logic
│   ├── core/                # Core business logic
│   ├── db/                  # Database models and operations
│   ├── github/              # GitHub integration
│   ├── notifiers/           # Notification services (Slack, GitHub)
│   ├── tests/               # Unit tests
│   ├── integration_tests/   # Integration tests
│   ├── hunter/              # Hunter submodule (change detection)
│   ├── pyproject.toml       # Poetry dependencies
│   ├── runtests.sh          # Test runner script
│   └── entrypoint.sh        # Docker entrypoint
├── frontend/                 # React frontend application
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   ├── package.json         # npm dependencies
│   ├── vite.config.js       # Production Vite config (proxies to nyrk.io)
│   └── vite.config.test.js  # Local dev Vite config (proxies to localhost:8001)
├── nginx/                    # Nginx configuration
├── etc/                      # Management scripts
│   ├── nyrkio_backend.py    # Backend server manager (standalone)
│   ├── nyrkio_frontend.py   # Frontend server manager (with deployment modes)
│   ├── nyrkio_docker.py     # Docker stack manager (full stack)
│   └── test_management_scripts.py  # Test suite for management scripts
├── docker-compose.dev.yml    # Docker Compose for development
├── .env.backend              # Environment configuration (create this)
├── .backend.pid              # Backend process ID (auto-generated)
└── README.md                 # Main documentation
```

## Configuration

### Environment Variables

Configuration is managed through the `.env.backend` file:

```bash
# Database Configuration
DB_URL=mongodb://mongodb.nyrkio.local:27017/mongodb
DB_NAME=nyrkiodb

# API Keys
POSTMARK_API_KEY=           # Email service
GITHUB_CLIENT_SECRET=       # GitHub OAuth
SECRET_KEY=                 # JWT signing key

# Optional
HUNTER_CONFIG=              # Hunter configuration
GRAFANA_USER=               # Grafana integration
GRAFANA_PASSWORD=           # Grafana password

# Development Settings
API_PORT=8001               # Backend server port
```

### Port Configuration

To change the backend port, edit `.env.backend`:

```bash
API_PORT=8001  # Change to desired port
```

Then restart the backend:

```bash
python3 etc/nyrkio_backend.py restart
```

## Troubleshooting

### Backend Won't Start

1. **Check if already running:**
   ```bash
   python3 etc/nyrkio_backend.py status
   ```

2. **Check for port conflicts:**
   ```bash
   lsof -i :8001  # Or your configured port
   ```

3. **Check dependencies are installed:**
   ```bash
   cd backend
   poetry install
   ```

4. **Check MongoDB is running (if using Docker):**
   ```bash
   docker ps | grep mongodb
   ```

### Installation Issues

1. **Poetry not found:**
   ```bash
   # Add Poetry to PATH
   export PATH="$HOME/.local/bin:$PATH"

   # Or reinstall
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Python version issues:**
   ```bash
   python3 --version  # Should be >= 3.8
   ```

3. **Permission errors:**
   ```bash
   # Make scripts executable
   chmod +x etc/nyrkio_backend.py etc/nyrkio_frontend.py etc/nyrkio_docker.py
   ```

### Test Failures

1. **Database connection issues:**
   - Ensure MongoDB is running
   - Check `DB_URL` in `.env.backend`

2. **Import errors:**
   ```bash
   cd backend
   poetry install --no-interaction
   ```

3. **Stale cache:**
   ```bash
   find backend -type d -name __pycache__ -exec rm -rf {} +
   ```

### Docker Issues

1. **Docker not running:**
   - macOS: Start Docker Desktop
   - Linux: `sudo systemctl start docker`

2. **Permission denied:**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Port conflicts:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Apache Otava (Hunter)](https://otava.apache.org)

## Getting Help

- Open an issue on [GitHub](https://github.com/nyrkio/nyrkio/issues)
- Check the [main README](README.md)
- Review existing [pull requests](https://github.com/nyrkio/nyrkio/pulls)

## Contributing

Please see the [main README](README.md) for contribution guidelines. All contributions should:
- Pass linting and formatting checks
- Include tests for new features
- Update documentation as needed
- Be submitted via pull request against the `main` branch
