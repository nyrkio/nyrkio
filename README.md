# [![nyrkio-logo]][product]

Nyrkio provides tools for *Continuous Benchmarking* on GitHub.

## Nyrkio Runners

**New in v2:** GitHub runners configured for stable, repeatable benchmark results.

Standard GitHub runners cause benchmark noise of 20-50%. Nyrkio runners are tuned for stability:
- No hyperthreading (each vCPU is a full physical core)
- Disabled frequency scaling (no turbo boost variance)
- No NUMA (single memory domain)
- Optimized kernel parameters

The common belief that benchmarking requires dedicated or bare-metal instances turns out to be largely false.
With the right configuration, cloud VMs deliver consistent results. Typical outcome: **10x noise reduction**.

| Standard GitHub Runner | Nyrkio Runner |
|------------------------|---------------|
| ![before][runner-before] | ![after][runner-after] |
| Noise range: ~75% | Noise range: ~5% |

*Some pilot customers achieved a min-max range of noise that was less than 1 ns!*

```yaml
# Replace runs-on: ubuntu-latest with:
runs-on: nyrkio_4   # 4-CPU Nyrkio runner
```

Available sizes: `nyrkio_2`, `nyrkio_4`, `nyrkio_8`, `nyrkio_16`, `nyrkio_32`, `nyrkio_64`, `nyrkio_96`

## Change Point Detection

- Submit results using a [REST API][nyrkio-getting-started] or [GitHub Action][github-action]
- State of the art algorithm finds regressions and improvements in noisy data (down to 0.5%)
- Integrates with GitHub to identify the commit that caused a performance change
- Notifications via Slack, email, or GitHub issues

![nyrkio-footer-graph]

## Getting Started

This software runs [nyrkio.com][dotcom].

1. [Install Nyrkio on GitHub](https://github.com/apps/nyrkio/installations/new)
2. [Select a subscription](https://nyrkio.com/pricing)
3. Change `runs-on:` to a Nyrkio runner label

[Full getting started guide][nyrkio-getting-started]

## Developers

### Credits

**Change point detection** is powered by [Apache Otava (incubating)][otava], an 8-year-old battle-tested
algorithm created and open sourced by the performance teams at MongoDB (2017) and DataStax (2020).
Used by Netflix, Dremio, Hazelcast, and others.

**The GitHub Action** ([nyrkio/change-detection][github-action]) is based on
[benchmark-action/github-action-benchmark][benchmark-action], which provides framework parsing
for pytest-benchmark, Google Benchmark, Catch2, Go testing, JMH, and more.

### Running locally

The frontend is React, the backend is FastAPI with MongoDB.

```console
# Frontend development (uses nyrkio.com backend)
cd frontend
npm install
npm run dev
```

Full stack with Docker:

```console
git clone git@github.com:nyrkio/nyrkio.git
cd nyrkio
git submodule init
git submodule update

cat > .env.backend << END
DB_URL=mongodb://mongodb.nyrkio.local:27017/mongodb
DB_NAME=nyrkiodb
POSTMARK_API_KEY=
GITHUB_CLIENT_SECRET=
SECRET_KEY=
END

export IMAGE_TAG=$(git rev-parse HEAD)
docker compose -f docker-compose.dev.yml up --build
```

### Contributing

Open a pull request against `main`. PRs run linters and tests automatically.

## References

- [The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System](https://arxiv.org/pdf/2003.00584)
- [Hunter: Using Change Point Detection to Hunt for Performance](https://arxiv.org/pdf/2301.03034.pdf)


[product]: https://nyrkio.com/product
[dotcom]: https://nyrkio.com
[nyrkio-getting-started]: https://nyrkio.com/docs/getting-started
[nyrkio-logo]: https://nyrkio.com/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png
[nyrkio-footer-graph]: https://nyrkio.com/assets/footer-white-graphic-8R7Ap4-5.png
[runner-before]: https://raw.githubusercontent.com/nyrkio/nyrkio/main/frontend/src/static/runner/turso_select1_ghrunner.png
[runner-after]: https://raw.githubusercontent.com/nyrkio/nyrkio/main/frontend/src/static/runner/turso_select1_nyrkiorunner.png
[github-action]: https://github.com/nyrkio/change-detection
[benchmark-action]: https://github.com/benchmark-action/github-action-benchmark
[otava]: https://otava.apache.org

## License

Licensed under the [Apache License, Version 2.0](https://opensource.org/license/apache-2-0/) ("the license"); you may not use these files except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0


Apache and Apache Otava are trademarks of the Apache Software Foundation
Nyrkiö and Nyrkiö Change Detection are trademarks of Nyrkiö Oy
