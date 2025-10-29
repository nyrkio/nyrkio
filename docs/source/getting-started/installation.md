# Installation

## Prerequisites

- Python 3.8 or higher
- Poetry (Python dependency manager)
- MongoDB (locally or via Docker)
- Node.js & npm (for frontend)

## Quick Install

```bash
# Clone the repository
git clone https://github.com/nyrkio/nyrkio.git
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
API_PORT=8001
SECRET_KEY=your-secret-key-here
EOF
```

## Install MongoDB

### Using Docker

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Start Services

```bash
# Start backend
python3 etc/nyrkio_backend.py start

# Start frontend (in another terminal)
python3 etc/nyrkio_frontend.py start
```

## Verify Installation

Visit http://localhost:5173 to access the Nyrkiö dashboard.

API documentation available at: http://localhost:8001/docs
