# Key Concepts

## Test Results

A **test result** is a single data point containing:
- **Metrics**: Measurements (e.g., response time, throughput)
- **Attributes**: Git metadata (repo, branch, commit)
- **Timestamp**: When the test was run

## Change Points

A **change point** is a statistically significant shift in performance detected by the E-Divisive algorithm.

Change points have:
- **Direction**: Forward (regression) or backward (improvement)
- **Magnitude**: Percentage change
- **P-value**: Statistical significance (lower = more confident)
- **Affected Metrics**: Which measurements changed

## Configuration

### User-Level Config

- **min_magnitude**: Minimum change % to report (default: 0.05 = 5%)
- **max_pvalue**: Maximum p-value for significance (default: 0.001)
- **since_days**: Notification time window (default: 14 days)

### Test-Level Config

- **public**: Make results publicly accessible
- **enabled**: Enable/disable change detection

## Organizations

Teams can create **organizations** to:
- Share test results across members
- Manage access control
- Track team-wide performance

## Pull Requests

Nyrkiö can analyze PR-specific test results in isolation without affecting main branch analysis.
