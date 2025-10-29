# Database

MongoDB schema and design for Nyrkiö.

## Collections

### users

User accounts and authentication.

```json
{
  "_id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "github_id": "12345",
  "created_at": 1640000000,
  "config": {
    "core": {
      "min_magnitude": 0.05,
      "max_pvalue": 0.001
    },
    "since_days": 14,
    "slack": {
      "webhook_url": "https://...",
      "channel": "#perf"
    }
  },
  "tokens": [
    {
      "token_id": "tok_xyz",
      "created": 1640000000,
      "last_used": 1640100000
    }
  ]
}
```

**Indexes:**
- `email` (unique)
- `github_id` (unique, sparse)
- `tokens.token_id` (for authentication)

### tests

Test configurations.

```json
{
  "_id": "test_abc123",
  "name": "my-performance-test",
  "user_id": "user_abc123",
  "org_id": "org_xyz",
  "created_at": 1640000000,
  "public": false,
  "enabled": true,
  "attributes": {
    "git_repo": "https://github.com/org/repo",
    "branch": "main"
  }
}
```

**Indexes:**
- `name` + `user_id` (compound, unique)
- `org_id`
- `public`

### results

Performance test results (time-series data).

```json
{
  "_id": "result_abc123",
  "test_id": "test_abc123",
  "test_name": "my-performance-test",
  "user_id": "user_abc123",
  "timestamp": 1640000000,
  "metrics": [
    {
      "name": "response_time",
      "value": 150.5,
      "unit": "ms",
      "direction": "lower_is_better"
    }
  ],
  "attributes": {
    "git_repo": "https://github.com/org/repo",
    "branch": "main",
    "git_commit": "abc123"
  }
}
```

**Indexes:**
- `test_id` + `timestamp` (compound, for queries)
- `user_id`
- `attributes.git_commit`
- `timestamp` (TTL index for expiration)

### changes

Detected change points.

```json
{
  "_id": "change_abc123",
  "test_id": "test_abc123",
  "test_name": "my-performance-test",
  "user_id": "user_abc123",
  "timestamp": 1640000000,
  "metric": "response_time",
  "direction": "forward",
  "magnitude": 0.15,
  "pvalue": 0.0001,
  "before_mean": 100.0,
  "after_mean": 115.0,
  "before_stddev": 5.0,
  "after_stddev": 6.0,
  "notified": true,
  "attributes": {
    "git_commit": "abc123",
    "git_repo": "https://github.com/org/repo"
  }
}
```

**Indexes:**
- `test_id` + `timestamp` (compound)
- `user_id` + `notified` (for notification queries)
- `timestamp`

### organizations

Team workspaces.

```json
{
  "_id": "org_abc123",
  "name": "My Organization",
  "github_org": "myorg",
  "created_at": 1640000000,
  "members": [
    {
      "user_id": "user_123",
      "role": "admin",
      "joined_at": 1640000000
    }
  ],
  "config": {
    "billing_email": "billing@example.com"
  }
}
```

**Indexes:**
- `github_org` (unique, sparse)
- `members.user_id`

## Indexing Strategy

### Query Patterns

Most common queries:

1. **Get test results** - Range query on timestamp
   ```
   db.results.find({test_id: X, timestamp: {$gte: start, $lte: end}})
   ```
   Index: `{test_id: 1, timestamp: -1}`

2. **Get changes** - Filter by user and notification status
   ```
   db.changes.find({user_id: X, notified: false})
   ```
   Index: `{user_id: 1, notified: 1}`

3. **Find user** - Lookup by email or GitHub ID
   ```
   db.users.findOne({email: X})
   ```
   Index: `{email: 1}` (unique)

### Compound Indexes

Order matters for compound indexes:

```javascript
// Good: Supports both queries
db.results.createIndex({test_id: 1, timestamp: -1})

// Supports:
// - {test_id: X}
// - {test_id: X, timestamp: Y}

// Good: Most selective field first
db.changes.createIndex({user_id: 1, timestamp: -1})
```

### Index Maintenance

```javascript
// View indexes
db.collection.getIndexes()

// Drop unused indexes
db.collection.dropIndex("index_name")

// Rebuild indexes
db.collection.reIndex()

// Analyze index usage
db.collection.aggregate([{$indexStats: {}}])
```

## Data Retention

### TTL Indexes

Automatically delete old data:

```javascript
// Delete results older than 90 days
db.results.createIndex(
  {timestamp: 1},
  {expireAfterSeconds: 7776000}  // 90 days
)
```

### Manual Cleanup

For fine-grained control:

```python
async def cleanup_old_data():
    cutoff = time.time() - (90 * 86400)  # 90 days

    # Delete old results
    await db.results.delete_many({
        "timestamp": {"$lt": cutoff}
    })

    # But keep results with changes
    await db.results.delete_many({
        "timestamp": {"$lt": cutoff},
        "has_change": {"$ne": True}
    })
```

## Queries

### Common Patterns

#### Get Recent Results

```python
async def get_recent_results(test_id: str, days: int = 30):
    cutoff = time.time() - (days * 86400)

    results = await db.results.find({
        "test_id": test_id,
        "timestamp": {"$gte": cutoff}
    }).sort("timestamp", -1).to_list(None)

    return results
```

#### Find Unnotified Changes

```python
async def get_pending_changes(user_id: str):
    changes = await db.changes.find({
        "user_id": user_id,
        "notified": False,
        "timestamp": {"$gte": cutoff}
    }).to_list(None)

    return changes
```

#### Aggregate Statistics

```python
async def get_test_stats(test_id: str):
    stats = await db.results.aggregate([
        {"$match": {"test_id": test_id}},
        {"$unwind": "$metrics"},
        {"$group": {
            "_id": "$metrics.name",
            "avg": {"$avg": "$metrics.value"},
            "min": {"$min": "$metrics.value"},
            "max": {"$max": "$metrics.value"},
            "count": {"$sum": 1}
        }}
    ]).to_list(None)

    return stats
```

## Scaling

### Replica Sets

For high availability:

```yaml
replication:
  replSetName: "nyrkio-rs"

members:
  - host: "mongo1:27017"
    priority: 2
  - host: "mongo2:27017"
    priority: 1
  - host: "mongo3:27017"
    arbiterOnly: true
```

### Sharding

For large datasets:

```javascript
// Shard by user_id for even distribution
sh.shardCollection("nyrkio.results", {user_id: 1, timestamp: 1})

// Or shard by test_id if specific tests are large
sh.shardCollection("nyrkio.results", {test_id: 1, timestamp: 1})
```

### Read Preference

```python
# Prefer secondary reads for analytics
client = AsyncIOMotorClient(
    mongo_url,
    read_preference=ReadPreference.SECONDARY_PREFERRED
)
```

## Backup

### Automated Backups

```bash
# Daily backup
mongodump --uri="$MONGO_URI" --out=/backup/$(date +%Y%m%d)

# Incremental backup (oplog)
mongodump --uri="$MONGO_URI" --oplog --out=/backup/oplog
```

### Point-in-Time Recovery

```bash
# Restore to specific timestamp
mongorestore --oplogReplay --oplogLimit 1640000000:1 /backup/oplog
```
