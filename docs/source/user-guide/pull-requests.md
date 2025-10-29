# Pull Request Integration

## Overview

Nyrkiö can analyze PR-specific performance tests in isolation from main branch.

## GitHub Action

```yaml
name: PR Performance Check

on: pull_request

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Performance Tests
        run: ./run-perf-tests.sh

      - name: Submit to Nyrkiö
        uses: nyrkio/change-detection@v1
        with:
          test_name: pr-${{ github.event.pull_request.number }}
          pull_request: ${{ github.event.pull_request.number }}
```

## REST API

```bash
curl -X POST \
  "https://api.nyrkio.com/api/v0/pulls/owner/repo/$PR_NUMBER/result/test-name" \
  -H "Authorization: Bearer TOKEN" \
  -d @results.json
```

## PR Comments

Nyrkiö automatically comments on PRs with:
- Performance comparison
- Detected regressions/improvements
- Graphs showing changes
- Historical context

## Isolated Analysis

PR results are:
- Analyzed separately from main branch
- Not mixed with production data
- Cleaned up automatically after PR merge
