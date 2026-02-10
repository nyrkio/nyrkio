### Upload benchmark results to Nyrkio

Add the `nyrkio/change-detection@v2` action after your benchmark step.

If you use common frameworks (pytest-benchmark, benchmark.js, Google Benchmark, Catch2, Go testing, JMH...) the action parses their output automatically.

Example workflow:

```markdown
    name: Minimal Benchmark+Nyrkiö setup
    on:
      push:
        branches:
          - master
      pull_request:
        branches:
          - master
    jobs:
      benchmark:
        name: Performance regression check
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-go@v4
            with:
              go-version: "stable"
            # Run benchmark with `go test -bench` and stores the output to a file
          - name: Run benchmark
            run: go test -bench 'BenchmarkFib' | tee output.txt
          - name: Analyze benchmark results with Nyrkiö
            uses: nyrkio/change-detection@v2
            with:
              tool: 'go'
              output-file-path: output.txt
              # Pick up your token at https://nyrkio.com/docs/getting-started
              # Then head to https://github.com/USER_OR_ORG/PROJECT/settings/secrets/actions
              # Store the token you just created as a Repository secret. We'll use the variable name `NYRKIO_JWT_TOKEN` for it below.
              nyrkio-token: ${{ secrets.NYRKIO_JWT_TOKEN }}

```
Each programming language and framework has its own documentation. Please see:

[benchmarkdotnet](https://github.com/nyrkio/change-detection/blob/master/examples/benchmarkdotnet) |
[benchmarkjs](https://github.com/nyrkio/change-detection/blob/master/examples/benchmarkjs) |
[catch2](https://github.com/nyrkio/change-detection/blob/master/examples/catch2) |
[cpp](https://github.com/nyrkio/change-detection/blob/master/examples/cpp) |
[go](https://github.com/nyrkio/change-detection/blob/master/examples/go) |
[java jmh](https://github.com/nyrkio/change-detection/blob/master/examples/java) |
[julia](https://github.com/nyrkio/change-detection/blob/master/examples/julia) |
[pytest](https://github.com/nyrkio/change-detection/blob/master/examples/pytest) |
[rust](https://github.com/nyrkio/change-detection/blob/master/examples/rust) |
[time](https://github.com/nyrkio/change-detection/blob/master/.github/workflows/time.yml) |


### Submit NyrkioJson directly

If you are using something else than the supported benchmark frameworks, then you can still use
the `nyrkio/change-detection@v2` GitHub action to upload the results. You can store your results
directly in the JSON format used by Nyrkiö. Just use `tool: NyrkioJson`

Please refer to [the generic HTTP / curl tutorial](/docs/getting-started-http) and the official
[API docs](https://nyrkio.com/openapi) for the full documentation of
`NyrkioJson`.


## 4. View the charts in the dashboard

Once you successfully run the GitHub action, at the end you'll find a link to graphs with your benchmark
results. They will look something like these: https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub

## Questions?

You can email us directly at [helloworld@nyrkio.com](mailto:helloworld@nyrkio.com).
