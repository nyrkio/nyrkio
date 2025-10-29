# Quick Start

This guide will help you submit your first test results and detect performance changes.

## Step 1: Register an Account

Visit http://localhost:5173 and create an account.

## Step 2: Submit Test Results

```bash
curl -X POST "http://localhost:8001/api/v0/result/my-first-test" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "timestamp": '$(date +%s)',
    "metrics": [
      {
        "name": "response_time",
        "value": 150.5,
        "unit": "ms",
        "direction": "lower_is_better"
      }
    ],
    "attributes": {
      "git_repo": "https://github.com/yourorg/yourrepo",
      "branch": "main",
      "git_commit": "'$(git rev-parse HEAD)'"
    }
  }'
```

## Step 3: View Results

Navigate to your dashboard to see the submitted results and any detected changes.

## Step 4: Configure Notifications

Set up Slack or GitHub notifications in your user settings.

## Next Steps

- [Learn about data models](../api-reference/data-models.md)
- [Configure change detection thresholds](../user-guide/configuration.md)
- [Set up GitHub integration](../user-guide/pull-requests.md)
