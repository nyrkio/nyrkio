## 3. Use Nyrkio Runners in your workflows

Replace `runs-on: ubuntu-latest` with a Nyrkio runner label:

```yaml
name: Benchmarks
on:
  push:
    branches: [main]
jobs:
  benchmark:
    runs-on: nyrkio_4   # 4-CPU Nyrkio runner
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmark
        run: ./run-benchmarks.sh
```

### Available runner sizes

| Label | CPUs | Price/hour |
|-------|------|------------|
| `nyrkio_2` | 2 | 0.20 EUR |
| `nyrkio_4` | 4 | 0.40 EUR |
| `nyrkio_8` | 8 | 0.80 EUR |
| `nyrkio_16` | 16 | 1.60 EUR |
| `nyrkio_32` | 32 | 3.20 EUR |
| `nyrkio_64` | 64 | 6.40 EUR |
| `nyrkio_96` | 96 | 9.60 EUR |

All runners use AWS c7a instances (AMD EPYC) with Ubuntu 24.04.

### Why Nyrkio Runners?

Standard GitHub runners cause benchmark noise of 20-50% due to shared hardware and variable system configuration. Nyrkio runners are tuned for stability:

- **No hyperthreading** - Each vCPU is a full physical core
- **Disabled frequency scaling** - Constant CPU frequency eliminates turbo boost variance
- **No NUMA** - Single memory domain avoids cross-socket latency
- **Optimized kernel parameters** - Reduced scheduler jitter and interrupts

The common belief that you need dedicated or bare-metal instances for benchmarking turns out to be largely false. With the right configuration, cloud VMs deliver consistent results.

Typical result: **10x or greater reduction in benchmark noise**. Some pilot customers achieved a min-max range of noise that was less than 1 ns!

## 4. View results in the dashboard

After your workflow runs, check your results at [nyrkio.com](https://nyrkio.com). Click the Nyrkio logo (top left) to see your uploaded benchmarks.

For public examples, see [publicly shared benchmarks](https://nyrkio.com/public) from TigerBeetle, Turso Database, and Uno-DB.

## Next steps

- [Add Change Point Detection](/docs/change-detection) to automatically find regressions
- [Working with the graphs](/docs/working-with-graphs) for UI navigation tips

## Questions?

Email us at [helloworld@nyrkio.com](mailto:helloworld@nyrkio.com).
