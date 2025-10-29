# Deployment

Deploy Nyrkiö to production environments.

## Topics

- [Docker Deployment](docker.md) - Deploy with Docker Compose
- [Production Setup](production.md) - Production configuration and best practices
- [Configuration](configuration.md) - Environment variables and settings
- [Monitoring](monitoring.md) - Logging, metrics, and alerts

## Deployment Options

1. **Docker Compose** - Simplest for small deployments
2. **Kubernetes** - For cloud-native deployments
3. **VM/Bare Metal** - Traditional server deployment

## Prerequisites

- Docker & Docker Compose
- MongoDB (or MongoDB Atlas)
- Domain name with SSL certificate
- SMTP server (for emails)
- GitHub OAuth app (optional)

## Quick Start

```bash
# Clone repository
git clone https://github.com/nyrkio/nyrkio.git
cd nyrkio

# Configure environment
cp .env.backend.example .env.backend
# Edit .env.backend with your settings

# Start with Docker
python3 etc/nyrkio_docker.py start
```
