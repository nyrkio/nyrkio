# Data Models

Complete data model schemas for the Nyrkiö API.

## Test Result

A test result submission contains metrics and metadata.

### Schema

```json
{
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
    "git_commit": "abc123",
    "custom_field": "custom_value"
  }
}
```

### Fields

#### timestamp (required)
- **Type**: integer (Unix timestamp)
- **Description**: When the test was run
- **Example**: `1640000000`

#### metrics (required)
- **Type**: array of Metric objects
- **Description**: Performance measurements
- **Min length**: 1

#### attributes (optional)
- **Type**: object
- **Description**: Metadata about the test run
- **Common fields**: `git_repo`, `branch`, `git_commit`, `pull_request`

## Metric

Individual performance measurement.

### Schema

```json
{
  "name": "response_time",
  "value": 150.5,
  "unit": "ms",
  "direction": "lower_is_better"
}
```

### Fields

#### name (required)
- **Type**: string
- **Description**: Metric identifier
- **Example**: `"response_time"`, `"throughput"`, `"memory_usage"`

#### value (required)
- **Type**: number (float or integer)
- **Description**: Measured value
- **Example**: `150.5`, `1200`, `0.95`

#### unit (optional)
- **Type**: string
- **Description**: Unit of measurement
- **Example**: `"ms"`, `"req/s"`, `"MB"`, `"%"`

#### direction (required)
- **Type**: string
- **Values**: `"lower_is_better"` or `"higher_is_better"`
- **Description**: Whether increases are improvements or regressions

## Change Point

Detected performance change.

### Schema

```json
{
  "change_id": "cp_abc123",
  "test_name": "my-test",
  "timestamp": 1640000000,
  "metric": "response_time",
  "direction": "forward",
  "magnitude": 0.15,
  "pvalue": 0.0001,
  "before_mean": 100.0,
  "after_mean": 115.0,
  "before_stddev": 5.0,
  "after_stddev": 6.0,
  "git_commit": "abc123",
  "git_repo": "https://github.com/org/repo",
  "branch": "main"
}
```

### Fields

#### change_id
- **Type**: string
- **Description**: Unique change point identifier

#### test_name
- **Type**: string
- **Description**: Name of the test

#### timestamp
- **Type**: integer (Unix timestamp)
- **Description**: When the change occurred

#### metric
- **Type**: string
- **Description**: Which metric changed

#### direction
- **Type**: string
- **Values**: `"forward"` (regression) or `"backward"` (improvement)

#### magnitude
- **Type**: float
- **Description**: Percentage change (0.15 = 15% change)

#### pvalue
- **Type**: float
- **Description**: Statistical significance (lower = more confident)
- **Range**: 0.0 to 1.0

#### before_mean / after_mean
- **Type**: float
- **Description**: Mean values before and after the change

#### before_stddev / after_stddev
- **Type**: float
- **Description**: Standard deviation before and after

## User Configuration

User-level settings.

### Schema

```json
{
  "core": {
    "min_magnitude": 0.05,
    "max_pvalue": 0.001
  },
  "since_days": 14,
  "slack": {
    "webhook_url": "https://hooks.slack.com/...",
    "channel": "#performance"
  },
  "github": {
    "owner": "myorg",
    "repo": "myrepo",
    "create_issues": true
  }
}
```

### Fields

#### core.min_magnitude
- **Type**: float
- **Default**: 0.05 (5%)
- **Description**: Minimum change % to report

#### core.max_pvalue
- **Type**: float
- **Default**: 0.001 (0.1%)
- **Description**: Maximum p-value for significance

#### since_days
- **Type**: integer
- **Default**: 14
- **Description**: Notification time window in days

## Test Configuration

Per-test settings.

### Schema

```json
{
  "public": true,
  "enabled": true,
  "attributes": {
    "git_repo": "https://github.com/org/repo",
    "branch": "main"
  }
}
```

### Fields

#### public
- **Type**: boolean
- **Default**: false
- **Description**: Make results publicly visible

#### enabled
- **Type**: boolean
- **Default**: true
- **Description**: Enable change detection for this test

## Organization

Team workspace.

### Schema

```json
{
  "org_id": "org_abc123",
  "name": "My Organization",
  "members": [
    {
      "user_id": "user_123",
      "email": "user@example.com",
      "role": "admin"
    }
  ],
  "github_org": "myorg"
}
```

### Fields

#### org_id
- **Type**: string
- **Description**: Unique organization identifier

#### name
- **Type**: string
- **Description**: Organization display name

#### members
- **Type**: array
- **Description**: Organization members with roles

#### github_org
- **Type**: string (optional)
- **Description**: Connected GitHub organization

## Pull Request Result

PR-specific test result.

### Schema

```json
{
  "timestamp": 1640000000,
  "metrics": [...],
  "attributes": {
    "git_repo": "https://github.com/org/repo",
    "pull_request": 123,
    "git_commit": "abc123",
    "branch": "feature-branch"
  }
}
```

### Additional Fields

#### attributes.pull_request (required)
- **Type**: integer
- **Description**: PR number
- **Example**: `123`

## Error Response

Standard error format.

### Schema

```json
{
  "detail": "Error message here"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid data format
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Validation Rules

### Test Names
- Must be alphanumeric with hyphens/underscores
- 1-100 characters
- Pattern: `^[a-zA-Z0-9_-]+$`

### Metric Names
- Must be alphanumeric with hyphens/underscores
- 1-50 characters
- Pattern: `^[a-zA-Z0-9_-]+$`

### Timestamps
- Unix timestamp in seconds
- Must be within reasonable range (not too far in past/future)

### Metric Values
- Must be finite numbers (not NaN or Infinity)
- Can be positive or negative

## Examples

### Minimal Valid Result

```json
{
  "timestamp": 1640000000,
  "metrics": [
    {
      "name": "latency",
      "value": 100,
      "direction": "lower_is_better"
    }
  ]
}
```

### Complete Result

```json
{
  "timestamp": 1640000000,
  "metrics": [
    {
      "name": "response_time",
      "value": 150.5,
      "unit": "ms",
      "direction": "lower_is_better"
    },
    {
      "name": "throughput",
      "value": 1250.0,
      "unit": "req/s",
      "direction": "higher_is_better"
    },
    {
      "name": "error_rate",
      "value": 0.02,
      "unit": "%",
      "direction": "lower_is_better"
    }
  ],
  "attributes": {
    "git_repo": "https://github.com/myorg/myrepo",
    "branch": "main",
    "git_commit": "abc123def456",
    "environment": "staging",
    "test_suite": "load-tests",
    "runner": "github-actions"
  }
}
```
