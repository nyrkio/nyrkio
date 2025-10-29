# Monitoring

Logging, metrics, and alerting for production.

## Logging

### Application Logs

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str, result: dict):
    logger.info(f"Submitting result for test: {test_name}")

    try:
        change_id = await process_result(result)
        logger.info(f"Result processed: {change_id}")
        return {"change_id": change_id}
    except Exception as e:
        logger.error(f"Error processing result: {e}", exc_info=True)
        raise
```

### Structured Logging

```python
import structlog

log = structlog.get_logger()

@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str, result: dict):
    log.info("result_submitted",
        test_name=test_name,
        user_id=user["_id"],
        metric_count=len(result["metrics"])
    )
```

### Log Aggregation

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/nyrkio/*.log
    json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Metrics

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

# Define metrics
requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Use in endpoints
@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str):
    with request_duration.labels('POST', '/result').time():
        # Process request
        result = await process_result()

    requests_total.labels('POST', '/result', '200').inc()
    return result
```

### Custom Metrics

```python
from prometheus_client import Gauge, Info

# Change detection metrics
changes_detected = Counter(
    'nyrkio_changes_detected_total',
    'Total changes detected',
    ['test_name', 'direction']
)

# Database metrics
db_query_duration = Histogram(
    'nyrkio_db_query_duration_seconds',
    'Database query duration',
    ['collection', 'operation']
)

# System info
app_info = Info('nyrkio_app', 'Application info')
app_info.info({'version': '0.1.0', 'env': 'production'})
```

## Dashboards

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Nyrkiö Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "Changes Detected",
        "targets": [{
          "expr": "rate(nyrkio_changes_detected_total[1h])"
        }]
      }
    ]
  }
}
```

### Key Metrics to Monitor

1. **Request Metrics**
   - Request rate (req/s)
   - Response time (p50, p95, p99)
   - Error rate (%)

2. **Business Metrics**
   - Results submitted per hour
   - Changes detected per hour
   - Active users
   - Active tests

3. **System Metrics**
   - CPU usage (%)
   - Memory usage (%)
   - Disk usage (%)
   - Network I/O

4. **Database Metrics**
   - Query response time
   - Connection pool usage
   - Slow queries
   - Document count

## Alerts

### Alert Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: nyrkio
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        annotations:
          summary: "High response time detected"

      - alert: DatabaseDown
        expr: up{job="mongodb"} == 0
        for: 1m
        annotations:
          summary: "Database is down"

      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.2
        for: 5m
        annotations:
          summary: "Disk space below 20%"
```

### Notification Channels

```yaml
# alertmanager.yml
route:
  receiver: 'slack-critical'
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'

    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#alerts-critical'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
```

## Health Checks

### Application Health

```python
@app.get("/health")
async def health_check():
    health = {
        "status": "ok",
        "checks": {}
    }

    # Check database
    try:
        db = await get_database()
        await db.command("ping")
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {e}"
        health["status"] = "degraded"

    # Check Redis
    try:
        await redis.ping()
        health["checks"]["cache"] = "ok"
    except Exception as e:
        health["checks"]["cache"] = f"error: {e}"
        health["status"] = "degraded"

    return health
```

### Liveness and Readiness

```python
@app.get("/healthz")
async def liveness():
    """Liveness probe - is the service alive?"""
    return {"status": "alive"}

@app.get("/readyz")
async def readiness():
    """Readiness probe - is the service ready to handle requests?"""
    # Check dependencies
    db_ready = await check_database()
    cache_ready = await check_cache()

    if db_ready and cache_ready:
        return {"status": "ready"}
    else:
        return {"status": "not ready"}, 503
```

## Tracing

### OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Custom spans
@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str):
    with tracer.start_as_current_span("process_result"):
        result = await process_result()

        with tracer.start_as_current_span("detect_changes"):
            changes = await detect_changes(result)

    return {"status": "ok"}
```

## Error Tracking

### Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENV", "production")
)

# Automatic error capture
@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str):
    # Any unhandled exception will be sent to Sentry
    result = await process_result()
    return result
```

## Performance Monitoring

### APM (Application Performance Monitoring)

```python
from ddtrace import tracer, patch_all

# Datadog APM
patch_all()

@tracer.wrap()
async def process_result(result: dict):
    # Automatically traced
    pass
```

### Query Performance

```python
import time

async def query_with_timing(collection, query):
    start = time.time()
    result = await collection.find(query).to_list(None)
    duration = time.time() - start

    db_query_duration.labels(
        collection=collection.name,
        operation='find'
    ).observe(duration)

    if duration > 1.0:
        logger.warning(f"Slow query: {duration:.2f}s", extra={
            "collection": collection.name,
            "query": query
        })

    return result
```

## Monitoring Best Practices

1. **Monitor the right metrics** - Focus on user experience
2. **Set meaningful alerts** - Avoid alert fatigue
3. **Dashboard for humans** - Clear, actionable visualizations
4. **Automate responses** - Auto-scaling, auto-healing
5. **Review regularly** - Adjust thresholds and alerts
6. **Document runbooks** - How to respond to alerts
7. **Test monitoring** - Verify alerts work before production
