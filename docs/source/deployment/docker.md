# Docker Deployment

Deploy Nyrkiö using Docker Compose.

## Architecture

```
┌────────────────┐
│  Nginx (443)   │  ← SSL/TLS Termination
└───────┬────────┘
        │
┌───────┼────────────────────┐
│       │                    │
│  ┌────▼──────┐  ┌─────────▼────┐
│  │  Backend  │  │   Webhooks   │
│  │  (8001)   │  │    (8080)    │
│  └───┬───────┘  └──────┬───────┘
│      │                 │
│      └────────┬────────┘
│               │
│      ┌────────▼────────┐
│      │    MongoDB      │
│      │    (27017)      │
│      └─────────────────┘
└──────────────────────────┘
```

## Docker Compose Files

### Development: `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  mongodb:
    image: mongodb/mongodb-community-server:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DB_URL=mongodb://mongodb:27017/nyrkiodb
      - DB_NAME=nyrkiodb
      - API_PORT=8000
    depends_on:
      - mongodb

  webhooks:
    build:
      context: ./webhooks
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - DB_URL=mongodb://mongodb:27017/nyrkiodb
    depends_on:
      - mongodb

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - webhooks

volumes:
  mongo-data:
```

## Building Images

### Backend Dockerfile

```dockerfile
# Multi-stage build for production (from backend/Dockerfile)
FROM python:3.8-slim AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1

WORKDIR /usr/src/backend

FROM base as builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libc-dev
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY . .
RUN poetry export --no-hashes -f requirements.txt | /venv/bin/pip install -r /dev/stdin
RUN poetry build
RUN /venv/bin/pip install dist/*.whl

FROM base as final
RUN addgroup --system app && adduser --system --group app
COPY --from=builder /venv /venv
COPY ./entrypoint.sh ./
COPY ./keys/ /usr/src/backend/keys/
COPY --chown=app:app . ./
USER app
CMD ["/usr/src/backend/entrypoint.sh"]
```

### Build and Push

```bash
# Build image
docker build -t nyrkio/backend:latest backend/

# Tag for registry
docker tag nyrkio/backend:latest registry.example.com/nyrkio/backend:latest

# Push to registry
docker push registry.example.com/nyrkio/backend:latest
```

## Starting Services

### Using Management Script

```bash
python3 etc/nyrkio_docker.py start
```

### Using Docker Compose Directly

```bash
# Set image tag
export IMAGE_TAG=$(git rev-parse HEAD)

# Start services
docker compose -f docker-compose.dev.yml up -d

# Check status
docker compose -f docker-compose.dev.yml ps

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop services
docker compose -f docker-compose.dev.yml down
```

## Configuration

### Environment Variables

Create `.env.backend`:

```bash
# Database
DB_URL=mongodb://mongodb:27017/nyrkiodb
DB_NAME=nyrkiodb

# API
API_PORT=8001
SECRET_KEY=your-secret-key-here

# External Services
POSTMARK_API_KEY=your-postmark-key
GITHUB_CLIENT_SECRET=your-github-secret

# Optional
HUNTER_CONFIG=/app/hunter_config.json
```

### MongoDB Initialization

```bash
# Connect to MongoDB
docker exec -it nyrkio-mongodb mongo

# Create indexes
use nyrkiodb
db.results.createIndex({test_id: 1, timestamp: -1})
db.changes.createIndex({user_id: 1, notified: 1})
db.users.createIndex({email: 1}, {unique: true})
```

## Nginx Configuration

### nginx.conf

```nginx
upstream backend {
    server backend:8001;
}

upstream webhooks {
    server webhooks:8080;
}

server {
    listen 80;
    server_name nyrkio.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nyrkio.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Webhooks
    location /webhooks/ {
        proxy_pass http://webhooks;
        proxy_set_header Host $host;
    }
}
```

## Monitoring

### Health Checks

Add to docker-compose.yml:

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

## Backup

### MongoDB Backup

```bash
# Backup script
docker exec nyrkio-mongodb mongodump   --out=/backup/$(date +%Y%m%d)   --db=nyrkiodb

# Copy backup out
docker cp nyrkio-mongodb:/backup/$(date +%Y%m%d) ./backups/
```

### Automated Backups

```yaml
services:
  mongodb-backup:
    image: mongo:latest
    volumes:
      - ./backups:/backup
      - mongo-data:/data/db
    command: >
      sh -c "while true; do
        mongodump --host mongodb --out /backup/\$$(date +%Y%m%d);
        sleep 86400;
      done"
```

## Scaling

### Multiple Backend Instances

```yaml
services:
  backend:
    deploy:
      replicas: 3
    scale: 3
```

### Load Balancing

```nginx
upstream backend {
    least_conn;
    server backend1:8001;
    server backend2:8001;
    server backend3:8001;
}
```

## Troubleshooting

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Connect to Container

```bash
# Shell access
docker exec -it nyrkio-backend bash

# Python shell
docker exec -it nyrkio-backend python
```

### Restart Service

```bash
docker compose restart backend
```

### Clean Up

```bash
# Stop and remove containers
docker compose down

# Remove volumes too
docker compose down -v

# Remove images
docker compose down --rmi all
```
