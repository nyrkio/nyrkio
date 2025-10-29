# Production Setup

Best practices for production deployment.

## Infrastructure

### Recommended Setup

- **Application**: 2+ backend instances
- **Database**: MongoDB replica set (3 nodes)
- **Load Balancer**: Nginx or cloud LB
- **Cache**: Redis cluster
- **Storage**: Persistent volumes
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack or cloud logging

### Cloud Providers

#### AWS

- **Compute**: ECS/Fargate or EC2
- **Database**: DocumentDB (MongoDB-compatible)
- **Load Balancer**: ALB/NLB
- **Storage**: EBS or EFS
- **Cache**: ElastiCache (Redis)

#### Google Cloud

- **Compute**: Cloud Run or GKE
- **Database**: MongoDB Atlas
- **Load Balancer**: Cloud Load Balancing
- **Storage**: Persistent Disk
- **Cache**: Memorystore

#### Azure

- **Compute**: Container Instances or AKS
- **Database**: Cosmos DB (MongoDB API)
- **Load Balancer**: Application Gateway
- **Storage**: Azure Disk
- **Cache**: Azure Cache for Redis

## Security

### SSL/TLS

Use Let's Encrypt for free certificates:

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d nyrkio.example.com

# Auto-renewal
certbot renew --dry-run
```

### Secrets Management

Don't commit secrets to git:

```bash
# Use environment variables
export DB_PASSWORD=$(cat /run/secrets/db_password)

# Or cloud secrets manager
export DB_PASSWORD=$(aws secretsmanager get-secret-value   --secret-id nyrkio-db-password   --query SecretString --output text)
```

### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 27017/tcp  # MongoDB only from internal network
ufw enable
```

### Authentication

Configure GitHub OAuth for production:

1. Create OAuth app at https://github.com/settings/developers
2. Set callback URL: `https://nyrkio.example.com/auth/callback`
3. Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`

## Performance

### Database Optimization

```javascript
// Create indexes
db.results.createIndex({test_id: 1, timestamp: -1})
db.results.createIndex({user_id: 1})
db.changes.createIndex({user_id: 1, notified: 1, timestamp: -1})
db.users.createIndex({email: 1}, {unique: true})
db.users.createIndex({github_id: 1}, {unique: true, sparse: true})

// Enable profiling
db.setProfilingLevel(1, 100)  // Log slow queries (>100ms)
```

### Caching

Enable Redis caching:

```python
# settings.py
REDIS_URL = "redis://redis:6379/0"
CACHE_TTL = 300  # 5 minutes
```

### CDN

Use CDN for static assets:

- Cloudflare
- AWS CloudFront
- Google Cloud CDN
- Azure CDN

## Monitoring

### Application Monitoring

```python
# Add Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Log Aggregation

```yaml
# docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Alerts

Configure alerts for:
- High error rate (>1%)
- High response time (>1s p95)
- Database connection issues
- Disk space <20%
- Memory usage >80%

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup MongoDB
mongodump   --uri="$MONGO_URI"   --out="$BACKUP_DIR/mongo_$DATE"

# Compress
tar -czf "$BACKUP_DIR/mongo_$DATE.tar.gz" "$BACKUP_DIR/mongo_$DATE"
rm -rf "$BACKUP_DIR/mongo_$DATE"

# Upload to S3
aws s3 cp "$BACKUP_DIR/mongo_$DATE.tar.gz"   s3://nyrkio-backups/

# Cleanup old local backups
find "$BACKUP_DIR" -name "mongo_*.tar.gz" -mtime +7 -delete
```

### Backup Schedule

```cron
# crontab -e
0 2 * * * /usr/local/bin/backup.sh
```

## Disaster Recovery

### Recovery Plan

1. **Restore from backup**
   ```bash
   mongorestore --uri="$MONGO_URI" /backup/latest
   ```

2. **Redeploy application**
   ```bash
   docker compose up -d
   ```

3. **Verify functionality**
   - Test API endpoints
   - Check database connections
   - Verify authentication

4. **Update DNS** (if needed)

### RTO and RPO

- **RTO** (Recovery Time Objective): <1 hour
- **RPO** (Recovery Point Objective): <24 hours

## Maintenance

### Rolling Updates

```bash
# Update one instance at a time
docker compose up -d --no-deps --scale backend=2 --no-recreate backend

# Update second instance
docker compose up -d --no-deps --scale backend=3 --no-recreate backend
```

### Database Migrations

```python
# migration.py
async def migrate():
    db = await get_database()

    # Add new field to existing documents
    await db.tests.update_many(
        {"new_field": {"$exists": False}},
        {"$set": {"new_field": "default_value"}}
    )
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    # Check database
    try:
        db = await get_database()
        await db.command("ping")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "timestamp": time.time()
    }
```

## Cost Optimization

### Resource Sizing

Start small and scale as needed:

- **Development**: 1 small instance, 1 DB
- **Small Production**: 2 medium instances, 1 DB replica set
- **Large Production**: 3+ large instances, sharded DB

### Auto-Scaling

```yaml
# AWS ECS
"scalingPolicies": [{
  "policyName": "cpu-scaling",
  "targetTrackingScalingPolicyConfiguration": {
    "predefinedMetricSpecification": {
      "predefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "targetValue": 70.0
  }
}]
```

### Cost Monitoring

- Set up billing alerts
- Use reserved instances for stable workloads
- Archive old test results
- Use lifecycle policies for backups
