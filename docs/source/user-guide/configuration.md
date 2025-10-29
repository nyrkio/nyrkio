# Configuration

## User Configuration

Access via Settings → User Config

### Change Detection Settings

```json
{
  "core": {
    "min_magnitude": 0.05,  // 5% minimum change
    "max_pvalue": 0.001     // 0.1% significance level
  }
}
```

### Notification Window

```json
{
  "since_days": 14  // Only notify for changes in last 14 days
}
```

## Test Configuration

Configure per-test settings:

```json
{
  "public": true,   // Make test results publicly visible
  "attributes": {
    "git_repo": "https://github.com/org/repo",
    "branch": "main"
  }
}
```

## Thresholds

### min_magnitude

- Lower values = more sensitive
- Higher values = fewer false positives
- Recommended: 0.01 to 0.10 (1% to 10%)

### max_pvalue

- Lower values = more confident
- Higher values = detect smaller changes
- Recommended: 0.001 to 0.05
