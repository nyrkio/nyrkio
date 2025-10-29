# Configuration

Environment variables and configuration options.

## Environment Variables

### Required Variables

```bash
# Database
DB_URL=mongodb://localhost:27017/nyrkiodb
DB_NAME=nyrkiodb

# API
API_PORT=8001
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# Authentication
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Optional Variables

```bash
# Email (Postmark)
POSTMARK_API_KEY=your-postmark-key
POSTMARK_FROM_EMAIL=noreply@nyrkio.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO

# Hunter (Change Detection)
HUNTER_CONFIG=/path/to/hunter_config.json
HUNTER_MIN_SAMPLES=30

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Grafana Integration
GRAFANA_URL=https://grafana.example.com
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# GitHub Webhook
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

## Configuration Files

### .env.backend

```bash
# .env.backend
DB_URL=mongodb://mongodb.nyrkio.local:27017/nyrkiodb
DB_NAME=nyrkiodb
API_PORT=8001
SECRET_KEY=$(openssl rand -hex 32)
POSTMARK_API_KEY=your-key-here
GITHUB_CLIENT_SECRET=your-secret-here
LOG_LEVEL=INFO
```

### Hunter Configuration

`hunter_config.json`:

```json
{
  "algorithm": "edivisive",
  "min_magnitude": 0.01,
  "max_pvalue": 0.001,
  "min_samples": 30,
  "permutations": 1000
}
```

## Application Settings

### User Configuration

Default settings for new users:

```python
DEFAULT_USER_CONFIG = {
    "core": {
        "min_magnitude": 0.05,  # 5%
        "max_pvalue": 0.001     # 0.1%
    },
    "since_days": 14,
    "notifications": {
        "email": True,
        "slack": False,
        "github": False
    }
}
```

### Test Configuration

Default test settings:

```python
DEFAULT_TEST_CONFIG = {
    "public": False,
    "enabled": True,
    "retention_days": 90
}
```

## Database Configuration

### Connection String

```python
# Local
DB_URL = "mongodb://localhost:27017/nyrkiodb"

# Replica Set
DB_URL = "mongodb://host1:27017,host2:27017,host3:27017/nyrkiodb?replicaSet=rs0"

# MongoDB Atlas
DB_URL = "mongodb+srv://user:pass@cluster.mongodb.net/nyrkiodb"

# With authentication
DB_URL = "mongodb://user:password@localhost:27017/nyrkiodb?authSource=admin"
```

### Connection Pool

```python
MONGO_CONFIG = {
    "maxPoolSize": 100,
    "minPoolSize": 10,
    "maxIdleTimeMS": 300000,
    "serverSelectionTimeoutMS": 5000
}
```

## Security Configuration

### JWT Settings

```python
JWT_CONFIG = {
    "algorithm": "HS256",
    "expiration": 30 * 86400,  # 30 days
    "issuer": "nyrkio",
    "audience": "nyrkio-api"
}
```

### CORS Settings

```python
CORS_CONFIG = {
    "allow_origins": [
        "http://localhost:5173",
        "https://nyrkio.com"
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}
```

### Rate Limiting

```python
RATE_LIMIT = {
    "default": "1000/hour",
    "authenticated": "5000/hour",
    "anonymous": "100/hour"
}
```

## Logging Configuration

### Log Levels

```python
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}
```

### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]
)
```

## Monitoring Configuration

### Prometheus Metrics

```python
METRICS_CONFIG = {
    "enable": True,
    "endpoint": "/metrics",
    "include_system_metrics": True
}
```

### Sentry

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENV", "production"),
    traces_sample_rate=0.1
)
```

## Feature Flags

```python
FEATURES = {
    "github_integration": True,
    "slack_notifications": True,
    "email_notifications": True,
    "public_dashboards": True,
    "organizations": True,
    "billing": False  # Not yet implemented
}
```

## Performance Configuration

### Cache Settings

```python
CACHE_CONFIG = {
    "backend": "redis",
    "url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "default_ttl": 300,
    "key_prefix": "nyrkio:"
}
```

### Worker Configuration

```python
WORKER_CONFIG = {
    "workers": 4,
    "threads": 2,
    "timeout": 30,
    "keepalive": 5
}
```

## Validation

### Validate Configuration

```python
def validate_config():
    required = ["DB_URL", "SECRET_KEY"]
    missing = [k for k in required if not os.getenv(k)]

    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")

    # Validate SECRET_KEY length
    if len(os.getenv("SECRET_KEY", "")) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters")

validate_config()
```

## Configuration Loading

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    db_url: str
    db_name: str
    api_port: int = 8001
    secret_key: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env.backend"
        case_sensitive = False

settings = Settings()
```
