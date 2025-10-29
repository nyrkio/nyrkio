# Change Detection

Nyrkiö uses the E-Divisive algorithm via Apache Otava (Hunter) for statistical change point detection.

## E-Divisive Algorithm

### Overview

E-Divisive is a non-parametric change point detection algorithm that:
- Makes no assumptions about data distribution
- Handles noisy performance data
- Detects multiple change points
- Provides statistical significance (p-value)

### How It Works

1. **Divide** - Split time series at potential change points
2. **Measure** - Calculate statistical distance between segments
3. **Test** - Permutation testing for significance
4. **Iterate** - Find multiple change points recursively

### Mathematical Foundation

For time series X = {x₁, x₂, ..., xₙ}:

1. Split at point τ: X₁ = {x₁...xτ}, X₂ = {xτ+1...xₙ}
2. Compute divergence: D(X₁, X₂) using Euclidean distance
3. Find τ that maximizes D
4. Test significance via permutation
5. Recursively apply to segments if significant

## Hunter Integration

### Architecture

```
Backend API
    │
    ▼
Hunter Python API
    │
    ▼
E-Divisive Core
    │
    ├─▶ Permutation Testing
    ├─▶ Statistical Analysis
    └─▶ Significance Testing
```

### Usage in Backend

```python
from backend.core.hunter import detect_changes

async def analyze_test_results(test_name: str):
    # Fetch results from database
    results = await db.results.find(
        {"test_name": test_name}
    ).sort("timestamp", 1).to_list(None)

    # Format data for Hunter
    data = [r["value"] for r in results]
    timestamps = [r["timestamp"] for r in results]

    # Run change detection
    changes = await detect_changes(
        data=data,
        timestamps=timestamps,
        min_magnitude=0.01,  # 1% minimum change
        max_pvalue=0.001     # 0.1% significance
    )

    return changes
```

## Configuration

### User-Level Settings

```json
{
  "core": {
    "min_magnitude": 0.05,  // 5% minimum change
    "max_pvalue": 0.001     // 0.1% significance level
  }
}
```

### Parameters

#### min_magnitude

Minimum percentage change to report.

- **Lower values** = More sensitive, more false positives
- **Higher values** = Less sensitive, fewer false positives
- **Recommended**: 0.01 to 0.10 (1% to 10%)

#### max_pvalue

Maximum p-value for statistical significance.

- **Lower values** = More confident, fewer detections
- **Higher values** = Less confident, more detections
- **Recommended**: 0.001 to 0.05

## Change Point Output

### Data Structure

```python
{
    "change_id": "cp_abc123",
    "timestamp": 1640000000,
    "metric": "response_time",
    "direction": "forward",      # forward=regression, backward=improvement
    "magnitude": 0.15,           # 15% change
    "pvalue": 0.0001,            # Very significant
    "before_mean": 100.0,
    "after_mean": 115.0,
    "before_stddev": 5.0,
    "after_stddev": 6.0,
    "git_commit": "abc123"
}
```

### Direction

- **forward**: Performance got worse (regression)
- **backward**: Performance got better (improvement)

Determined by metric direction:
- `lower_is_better`: increase = forward (regression)
- `higher_is_better`: decrease = forward (regression)

### Magnitude

Percentage change calculated as:
```
magnitude = (after_mean - before_mean) / before_mean
```

Example:
- Before: 100ms
- After: 115ms
- Magnitude: 0.15 (15% slower)

### P-Value

Statistical significance from permutation testing:
- **0.001**: Very confident (99.9%)
- **0.01**: Confident (99%)
- **0.05**: Significant (95%)

Lower p-values indicate higher confidence.

## Performance

### Optimization Strategies

1. **Caching**: Cache change detection results
2. **Windowing**: Only analyze recent data
3. **Sampling**: Downsample very large datasets
4. **Parallelization**: Analyze metrics in parallel

### Complexity

- **Time**: O(n² log n) for n data points
- **Space**: O(n) memory usage

For large datasets (>10,000 points), consider:
- Analyzing last N days only
- Incremental analysis
- Sampling strategies

## Accuracy

### False Positives

Controlled by:
- Lower `max_pvalue` (more stringent)
- Higher `min_magnitude` (larger changes only)
- More data points (better statistics)

### False Negatives

Reduced by:
- Higher `max_pvalue` (less stringent)
- Lower `min_magnitude` (detect smaller changes)
- Less noisy data

### Typical Performance

With default settings (5% min magnitude, 0.1% p-value):
- Detects changes ≥5% with >99.9% confidence
- False positive rate: <0.1%
- False negative rate: Depends on noise level

## Testing

### Unit Tests

```python
def test_change_detection():
    # Generate synthetic data with known change
    before = [100] * 50  # 50 samples at 100
    after = [120] * 50   # 50 samples at 120 (20% increase)
    data = before + after

    # Run detection
    changes = detect_changes(data)

    # Verify detection
    assert len(changes) == 1
    assert changes[0]["magnitude"] ≈ 0.20
    assert changes[0]["pvalue"] < 0.001
```

### Integration Tests

Test with real performance data to validate:
- Detection accuracy
- False positive rate
- Performance (execution time)
