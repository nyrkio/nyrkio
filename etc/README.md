# Nyrkiö Management Scripts

This directory contains Python scripts for managing Nyrkiö services during development and deployment.

## Overview

These scripts provide a consistent interface for starting, stopping, and managing different parts of the Nyrkiö stack:

- **`nyrkio_backend.py`** - Backend API server management
- **`nyrkio_frontend.py`** - Frontend development server management
- **`nyrkio_docker.py`** - Full Docker stack management
- **`test_management_scripts.py`** - Test suite for the management scripts

All scripts use a common command interface: `start`, `stop`, `restart`, `status`

## nyrkio_backend.py

Manages the FastAPI backend server using Poetry and Uvicorn.

### Usage

```bash
python3 etc/nyrkio_backend.py {start|stop|restart|status}
```

### Commands

- **`start`** - Start the backend server in background
- **`stop`** - Stop the backend server gracefully
- **`restart`** - Restart the backend server
- **`status`** - Check if backend is running

### Features

- Runs server in background with PID tracking (`.backend.pid`)
- Auto-detects Poetry or system Python environment
- Loads environment variables from `.env.backend`
- Graceful shutdown with fallback to force kill
- Auto-reload enabled for development

### Configuration

The backend reads configuration from `.env.backend` in the repository root. Key variables:

- `API_PORT` - Port to run on (default: 8001)
- `DB_URL` - MongoDB connection string
- `DB_NAME` - Database name
- See `.env.backend.example` for full list

### Examples

```bash
# Start backend
python3 etc/nyrkio_backend.py start
# Backend server started on http://localhost:8001

# Check status
python3 etc/nyrkio_backend.py status
# Backend is running (PID: 12345)

# Stop backend
python3 etc/nyrkio_backend.py stop
# Backend server stopped

# Restart after config changes
python3 etc/nyrkio_backend.py restart
```

### Process Management

- PID file: `etc/.backend.pid`
- Logs: Output to stdout/stderr (check console where started)
- Auto-reload: Changes to Python files automatically restart the server

## nyrkio_frontend.py

Manages the React/Vite frontend development server with support for different deployment modes.

### Usage

```bash
python3 etc/nyrkio_frontend.py [--mode {local|production}] [--port PORT] {start|stop|restart|status|install}
```

### Commands

- **`start`** - Start the frontend server in background
- **`stop`** - Stop the frontend server
- **`restart`** - Restart the frontend server
- **`status`** - Check if frontend is running
- **`install`** - Install npm dependencies only (no server start)

### Options

- **`--mode {local|production}`** - Deployment mode (default: `local`)
  - `local` - Uses `vite.config.test.js`, proxies API to `http://localhost:8001`
  - `production` - Uses `vite.config.js`, proxies API to `https://nyrk.io`
- **`--port PORT`** - Port to run frontend on (default: 5173)

### Features

- Auto-detects and installs npm dependencies if needed
- Runs server in background with PID tracking (`.frontend.pid`)
- Configurable deployment mode (local vs production backend)
- Graceful shutdown support

### Examples

```bash
# Start with local backend (default)
python3 etc/nyrkio_frontend.py start
# Frontend running at http://localhost:5173 (proxying to http://localhost:8001)

# Start with production backend
python3 etc/nyrkio_frontend.py start --mode production
# Frontend running at http://localhost:5173 (proxying to https://nyrk.io)

# Start on custom port
python3 etc/nyrkio_frontend.py start --port 3000
# Frontend running at http://localhost:3000

# Install dependencies without starting
python3 etc/nyrkio_frontend.py install

# Check status
python3 etc/nyrkio_frontend.py status

# Stop frontend
python3 etc/nyrkio_frontend.py stop
```

### Deployment Modes Explained

**Local Mode** (default):
- Best for full-stack local development
- Requires backend running on `localhost:8001`
- Fast iteration, hot reload enabled
- Uses `frontend/vite.config.test.js`

**Production Mode**:
- For frontend-only development against production API
- Connects to live `https://nyrk.io` backend
- Useful for testing frontend changes without running backend locally
- Uses `frontend/vite.config.js`

### Process Management

- PID file: `etc/.frontend.pid`
- Vite config: `frontend/vite.config.test.js` (local) or `frontend/vite.config.js` (production)

## nyrkio_docker.py

Manages the complete Nyrkiö stack using Docker Compose.

### Usage

```bash
python3 etc/nyrkio_docker.py {start|stop|restart|status}
```

### Commands

- **`start`** - Start the full Docker stack
- **`stop`** - Stop the Docker stack
- **`restart`** - Restart the Docker stack
- **`status`** - Show Docker stack status

### Services

When started, the Docker stack runs:

- **Backend API** - `http://localhost:8000`
- **Webhooks** - `http://localhost:8080` (GitHub webhook handler)
- **Nginx** - `http://localhost:80` (reverse proxy)
- **MongoDB** - `localhost:27017`

### Features

- Uses `docker-compose.dev.yml`
- Checks for Docker and Docker Compose availability
- Verifies `.env.backend` exists before starting
- Shows status of all running containers

### Prerequisites

- Docker and Docker Compose installed
- `.env.backend` file configured

### Examples

```bash
# Start full stack
python3 etc/nyrkio_docker.py start
# Docker stack started

# Check status
python3 etc/nyrkio_docker.py status
# Container status output...

# Stop stack
python3 etc/nyrkio_docker.py stop
# Docker stack stopped

# Restart stack
python3 etc/nyrkio_docker.py restart
```

### Docker Compose File

Uses `docker-compose.dev.yml` in the repository root. This includes:
- Backend service
- Webhooks service (same image as backend, different entrypoint)
- MongoDB service
- Nginx reverse proxy

## test_management_scripts.py

Test suite that verifies all management scripts work correctly.

### Usage

```bash
python3 etc/test_management_scripts.py
```

### What It Tests

- All scripts exist and are executable
- Scripts respond to `--help` flag
- Scripts accept correct command-line arguments
- Status commands work when services are stopped
- Vite configuration files exist and have correct targets
- Documentation references correct script paths
- No references to old script names remain

### Example Output

```bash
$ python3 etc/test_management_scripts.py
Testing management scripts...
✓ nyrkio_backend.py exists and is executable
✓ nyrkio_frontend.py exists and is executable
✓ nyrkio_docker.py exists and is executable
✓ All scripts respond to --help
✓ Status commands work correctly
All tests passed!
```

## Common Workflows

### Full Stack Local Development

```bash
# Terminal 1: Start backend
python3 etc/nyrkio_backend.py start

# Terminal 2: Start frontend in local mode
python3 etc/nyrkio_frontend.py start

# Check everything is running
python3 etc/nyrkio_backend.py status
python3 etc/nyrkio_frontend.py status
```

Then access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Frontend Development Only

```bash
# Use production backend, develop frontend only
python3 etc/nyrkio_frontend.py start --mode production
```

### Full Docker Stack

```bash
# Start everything in Docker
python3 etc/nyrkio_docker.py start

# Check status
python3 etc/nyrkio_docker.py status
```

### Stopping Everything

```bash
# Stop individual services
python3 etc/nyrkio_backend.py stop
python3 etc/nyrkio_frontend.py stop

# Or stop Docker stack
python3 etc/nyrkio_docker.py stop
```

## Troubleshooting

### Backend won't start

1. Check if already running:
   ```bash
   python3 etc/nyrkio_backend.py status
   ```

2. Check for port conflicts:
   ```bash
   lsof -i :8001
   ```

3. Verify `.env.backend` exists and is configured

4. Check MongoDB is running (if not using Docker)

### Frontend won't start

1. Check if npm is installed:
   ```bash
   npm --version
   ```

2. Install dependencies manually:
   ```bash
   python3 etc/nyrkio_frontend.py install
   ```

3. Check for port conflicts:
   ```bash
   lsof -i :5173
   ```

### Docker won't start

1. Check Docker is running:
   ```bash
   docker --version
   docker compose version
   ```

2. Verify `.env.backend` exists

3. Check for port conflicts (80, 8000, 8080, 27017)

### Stale PID files

If a script reports a service is running but it's not:

```bash
# Remove stale PID files
rm -f etc/.backend.pid etc/.frontend.pid

# Try starting again
python3 etc/nyrkio_backend.py start
```

## Development Notes

### Script Design Principles

- **Consistent interface**: All scripts use the same command pattern
- **Background execution**: Services run as background processes with PID tracking
- **Graceful shutdown**: Scripts attempt graceful shutdown before force kill
- **Error checking**: Verify prerequisites (Docker, npm, config files) before starting
- **Self-documenting**: All scripts have `--help` output and docstrings

### Adding New Scripts

When adding new management scripts:

1. Follow the naming pattern: `nyrkio_<component>.py`
2. Implement standard commands: `start`, `stop`, `restart`, `status`
3. Use PID file for process tracking (`.component.pid`)
4. Add `--help` output with argparse
5. Include in `test_management_scripts.py`

### Testing Changes

Always run the test suite after modifying scripts:

```bash
python3 etc/test_management_scripts.py
```

## Related Documentation

- Main README: `../README.md`
- Environment variables: `../.env.backend.example`
- Docker setup: `../docker-compose.dev.yml`
