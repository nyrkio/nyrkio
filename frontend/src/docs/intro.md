# Getting started in 3 easy steps

This guide will show you how to get started with Nyrkiö.

All of the examples in this doc use `curl` but you can use your favourite language and libraries for sending HTTP requests.

## 1.Create a user account

Click on the Login button in the top right corner:

![](/src/static/getting-started-login-button.png)
![](/assets/getting-started-login-button.png)

The easiest and recommended option is to just click on the Github button on the top and you're done.

![](/src/static/getting-started-login.png)
![](/assets/getting-started-login.png)

## 2. Create a JWT token

We use JWT to access the Nyrkiö API. Click again on the red button on your top right. If you are
logged in you can now select _User Settings_.

![](/src/static/getting-started-UserSettings.png)
![](/assets/getting-started-UserSettings.png)

Create a new API key and make sure to copy paste it and save it somewhere.

![](/src/static/getting-started-API-key.png)
![](/assets/getting-started-API-key.png)

## 3. Upload performance test results

Now comes the main bit -- uploading performance test results. The JSON schema for test results has a few required fields which are described in more detail in the [API docs](/openapi).

Briefly, here's a list of the required fields.

| Field      | Description                            |
| ---------- | -------------------------------------- |
| timestamp  | Unix timestamp (secs since Jan 1 1970) |
| metrics    | A list of dictionaries of metrics      |
| attributes | A dictionary of attributes             |

Here's an example payload for a performance test named `benchmark1`.

```bash
export TOKEN=THE_JWT_TOKEN_JUST_CREATED
export TEST_NAME=benchmark1

curl -X POST -H "Content-type: application/json" -H "Authorization: Bearer $TOKEN" https://nyrkio.com/api/v0/result/$TEST_NAME \
           -d '[{"timestamp": 1706220908,
             "metrics": [
               {"name": "p50", "unit": "us", "value": 56 },
               {"name": "p90", "unit": "us", "value": 125 },
               {"name": "p99", "unit": "us", "value": 280 }
             ],
             "attributes": {
               "git_repo": "https://github.com/nyrkio/nyrkio",
               "branch": "main",
               "git_commit": "6995e2de6891c724bfeb2db33d7b87775f913ad1",
             }
       }]'
```

There are a few things to keep in mind when working with test result data:

`timestamp` should be the time of the _git commit_ that was tested, not the timestamp of the test execution. Using the git commit timestamp allows you to accurately pinpoint which commit (or sequence of commits) introduced a change in performance. In other words, you should use the timestamp of when the commits were merged to the branch being monitored. This you can get with the following command:

    commit_date=$(cd $GIT_REPO; git rev-list --format=format:"%ci" --max-count=1 $githash|grep -v commit)

The `git_commit` attribute is special. If you include it and the `git_repo` attribute, then Nyrkiö will link to the url for that commit whenever it's part of a change point.

The units for each metric is arbitrary and can be anything, e.g. "ns", "us", "instructions", "request/s", etc.

## 4. View the charts in the dashboard

Now, if you navigate to https://nyrkio.com/result/BENCHMARK1 you'll see three charts with a single data point each.

## Questions?

You can email us directly at [helloworld@nyrkio.com](mailto:helloworld@nyrkio.com).
