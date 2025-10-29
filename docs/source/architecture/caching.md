# Caching

Performance optimization through caching strategies.

## Caching Layers

```
┌────────────┐
│  Browser   │  ← Local Storage, IndexedDB
└─────┬──────┘
      │
┌─────▼──────┐
│  Frontend  │  ← TanStack Query Cache
└─────┬──────┘
      │
┌─────▼──────┐
│  Backend   │  ← In-Memory Cache, Redis
└─────┬──────┘
      │
┌─────▼──────┐
│  Database  │  ← MongoDB
└────────────┘
```

## Frontend Caching

### TanStack Query

Automatic caching for API requests:

```jsx
import { useQuery } from '@tanstack/react-query';

function TestResults({ testName }) {
  const { data } = useQuery({
    queryKey: ['test', testName],
    queryFn: () => fetchTestResults(testName),
    staleTime: 60000,      // Consider fresh for 1 minute
    cacheTime: 300000,     // Keep in cache for 5 minutes
    refetchOnWindowFocus: true
  });

  return <div>{/* Render results */}</div>;
}
```

### Local Storage

Persist user preferences:

```javascript
// Save settings
localStorage.setItem('userSettings', JSON.stringify(settings));

// Load settings
const settings = JSON.parse(localStorage.getItem('userSettings'));
```

### IndexedDB

For larger data:

```javascript
// Store large datasets locally
const db = await openDB('nyrkio-cache', 1, {
  upgrade(db) {
    db.createObjectStore('results', { keyPath: 'test_name' });
  }
});

await db.put('results', { test_name: 'my-test', data: results });
```

## Backend Caching

### In-Memory Cache

Python dictionary cache with TTL:

```python
from typing import Any, Optional
import time

class Cache:
    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, expires = self.cache[key]
            if time.time() < expires:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        expires = time.time() + ttl
        self.cache[key] = (value, expires)

cache = Cache()
```

### Usage in Endpoints

```python
from backend.core.cache import cache

@app.get("/api/v0/result/{test_name}")
async def get_results(test_name: str):
    # Check cache
    cached = cache.get(f"results:{test_name}")
    if cached:
        return cached

    # Fetch from database
    results = await db.results.find({"test_name": test_name}).to_list(None)

    # Store in cache
    cache.set(f"results:{test_name}", results, ttl=300)

    return results
```

### Redis Cache

For production, use Redis:

```python
import aioredis
import json

redis = await aioredis.create_redis_pool('redis://localhost')

async def get_cached_results(test_name: str):
    # Try cache
    cached = await redis.get(f"results:{test_name}")
    if cached:
        return json.loads(cached)

    # Fetch from DB
    results = await fetch_results(test_name)

    # Store in cache
    await redis.setex(
        f"results:{test_name}",
        300,  # 5 minute TTL
        json.dumps(results)
    )

    return results
```

## Change Detection Caching

Cache change detection results:

```python
async def get_changes(test_name: str, force: bool = False):
    cache_key = f"changes:{test_name}"

    # Check cache unless forced
    if not force:
        cached = cache.get(cache_key)
        if cached:
            return cached

    # Compute changes (expensive)
    changes = await detect_changes(test_name)

    # Cache for 1 hour
    cache.set(cache_key, changes, ttl=3600)

    return changes
```

## Cache Invalidation

### Time-Based

Automatic expiration with TTL:

```python
# Expire after 5 minutes
cache.set("key", value, ttl=300)
```

### Event-Based

Invalidate when data changes:

```python
@app.post("/api/v0/result/{test_name}")
async def submit_result(test_name: str, result: dict):
    # Store result
    await db.results.insert_one(result)

    # Invalidate caches
    cache.delete(f"results:{test_name}")
    cache.delete(f"changes:{test_name}")

    return {"status": "ok"}
```

### Pattern-Based

Invalidate multiple keys:

```python
def invalidate_pattern(pattern: str):
    keys_to_delete = [k for k in cache.cache.keys() if pattern in k]
    for key in keys_to_delete:
        cache.delete(key)

# Invalidate all caches for a test
invalidate_pattern(f"test:{test_name}")
```

## Database Query Caching

### MongoDB Query Cache

```python
async def get_user_by_email(email: str):
    cache_key = f"user:email:{email}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    user = await db.users.find_one({"email": email})
    cache.set(cache_key, user, ttl=600)  # 10 minutes

    return user
```

### Aggregation Caching

Cache expensive aggregations:

```python
async def get_test_stats(test_id: str):
    cache_key = f"stats:{test_id}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    # Expensive aggregation
    stats = await db.results.aggregate([...]).to_list(None)

    cache.set(cache_key, stats, ttl=1800)  # 30 minutes

    return stats
```

## CDN Caching

For static assets and public data:

### Headers

```python
from fastapi.responses import Response

@app.get("/public/results/{test_name}")
async def public_results(test_name: str):
    results = await fetch_results(test_name)

    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=300",
            "ETag": generate_etag(results)
        }
    )
```

### ETags

```python
import hashlib

def generate_etag(data: Any) -> str:
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

@app.get("/api/v0/result/{test_name}")
async def get_results(
    test_name: str,
    request: Request
):
    results = await fetch_results(test_name)
    etag = generate_etag(results)

    # Check If-None-Match
    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304)

    return Response(
        content=json.dumps(results),
        headers={"ETag": etag}
    )
```

## Cache Monitoring

### Metrics

Track cache performance:

```python
class CacheMetrics:
    def __init__(self):
        self.hits = 0
        self.misses = 0

    def hit(self):
        self.hits += 1

    def miss(self):
        self.misses += 1

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

metrics = CacheMetrics()

# In cache.get()
if key in cache:
    metrics.hit()
    return value
else:
    metrics.miss()
    return None
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def get_with_logging(key: str):
    value = cache.get(key)
    if value:
        logger.debug(f"Cache hit: {key}")
    else:
        logger.debug(f"Cache miss: {key}")
    return value
```

## Best Practices

1. **Cache Hot Data** - Most frequently accessed data
2. **Short TTLs** - Avoid stale data
3. **Invalidate on Write** - Keep cache fresh
4. **Monitor Hit Rates** - Optimize cache strategy
5. **Graceful Degradation** - Work if cache unavailable
6. **Cache Keys** - Use consistent naming convention
7. **Size Limits** - Prevent memory exhaustion
