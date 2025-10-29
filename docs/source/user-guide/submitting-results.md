# Submitting Test Results

## REST API

Submit results via POST request:

```bash
curl -X POST "https://api.nyrkio.com/api/v0/result/test-name" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d @results.json
```

## GitHub Action

```yaml
- name: Submit Results
  uses: nyrkio/change-detection@v1
  with:
    test_name: my-performance-test
    metrics: |
      - name: latency
        value: ${{ steps.test.outputs.latency }}
        unit: ms
        direction: lower_is_better
```

## Python SDK

```python
import requests
import time

results = {
    "timestamp": int(time.time()),
    "metrics": [
        {
            "name": "throughput",
            "value": 1250.5,
            "unit": "req/s",
            "direction": "higher_is_better"
        }
    ],
    "attributes": {
        "git_repo": repo_url,
        "branch": branch_name,
        "git_commit": commit_sha
    }
}

response = requests.post(
    f"https://api.nyrkio.com/api/v0/result/{test_name}",
    json=results,
    headers={"Authorization": f"Bearer {token}"}
)
```

## Data Format

See [Data Models](../api-reference/data-models.md) for complete schema.
