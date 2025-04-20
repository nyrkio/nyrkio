## 3. Upload performance test results from GitHub workflows

Now comes the main bit -- uploading performance test results.

By far the easiest way to do this is our `nyrkio/change-detection@v2` GitHub action.

If you use any of the common benchmark frameworks (pytest-benchark, benchmark.js, Google and Catch2 C++ benchmark frameworks...)
then you just pipe their output to the `change-detection` action and it will take care of the rest!

Then add the following YAML after the actual benchmark:

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
              nyrkio-token: ${{ secrets.NYRKIO_JWT_TOKEN }}

```

### Submit NyrkioJson directly

If you are using something else than the supported benchmark frameworks, then you can still use
the `nyrkio/change-detection@v2` GitHub action to upload the results. You can store your results
directly in the JSON format used by Nyrkiö. Just use `tool: NyrkioJson`

Please refer to the official [API docs](https://nyrkio.com/openapi) for the full documentation of
`NyrkioJson`. Below is a simple example:

Main required parts:

| Field      | Description                            |
| ---------- | -------------------------------------- |
| timestamp  | Unix timestamp (secs since Jan 1 1970) |
| metrics    | A list of dictionaries of metrics      |
| attributes | A dictionary of attributes             |

Example payload:

```json
           [{"timestamp": 1706220908,
             "metrics": [
               {"name": "p50", "unit": "us", "value": 56 },
               {"name": "p90", "unit": "us", "value": 125 },
               {"name": "p99", "unit": "us", "value": 280 }
             ],
             "attributes": {
               "git_repo": "https://github.com/nyrkio/nyrkio",
               "branch": "main",
               "git_commit": "6995e2de6891c724bfeb2db33d7b87775f913ad1"
             }
       }]
```

(You can submit multiple results in the same request, that's why the payload is always a list.)

There are a few things to keep in mind when working with test result data:

`timestamp` should be the time of the _git commit_ that was tested, not the timestamp of the test execution. Using the git commit timestamp allows you to accurately pinpoint which commit (or sequence of commits) introduced a change in performance. In other words, you should use the timestamp of when the commits were merged to the branch being monitored. This you can get with the following command:

    commit_date=$(cd $GIT_REPO; git rev-list --format=format:"%ci" --max-count=1 $githash|grep -v commit)

The `git_commit` attribute is special. If you include it and the `git_repo` attribute, then Nyrkiö will link to the url for that commit whenever it's part of a change point.

The units for each metric is arbitrary and can be anything, e.g. "ns", "us", "instructions", "request/s", etc. The `direction` is optional. Nyrkiö will alert for both regressions and improvements.


## 4. View the charts in the dashboard

Once you successfully run the GitHub action, at the end you'll find a link to graphs with your benchmark
results. They will look something like these: https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub

## Questions?

You can email us directly at [helloworld@nyrkio.com](mailto:helloworld@nyrkio.com).
