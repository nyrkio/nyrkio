# Notifications

## Slack Integration

### Setup

1. Create Slack webhook URL
2. Add to user config:

```json
{
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#performance"
  }
}
```

### Notification Format

Slack messages include:
- Test name and metric
- Change magnitude and direction
- Git commit information
- Link to dashboard
- Graph thumbnail

## GitHub Integration

### Issue Creation

Automatically create issues for regressions:

```json
{
  "github": {
    "owner": "yourorg",
    "repo": "yourrepo",
    "create_issues": true
  }
}
```

### PR Comments

Comment on pull requests with performance analysis.

## Email Notifications

Configure email notifications (coming soon).

## Notification Frequency

Control notification timing:
- `since_days`: Only notify for recent changes
- Deduplication: Same change won't notify twice
