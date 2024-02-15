# Getting started

This guide will show you how to get started with Nyrkiö. All of the examples in this doc use `curl` but you can use your favourite language and libraries for sending HTTP requests.

For all of these steps, be sure to change the example email address and password.

## Use your current JWT token

We use JWT to access the Nyrkiö API. If you are already logged in to nyrk.io, then you'll see a
small envelope on your top right. You can click on it, and copy paste your current JWT token
and skip right to *Upload performance test results* below.


**OR...**

If you rather want to do everything via the API, continue reading for how to sign up and get a JWT
token programatically:



## Sign up for an account

You can either do this via the front page of the website or programatically by calling the REST API.

```bash
curl -s -H "Content-type: application/json" https://nyrk.io/api/v0/auth/register \
    -d '{"email": "foo@bar.com", "password": "mypassword"}'
```

After signing up you'll need to verify your email address.

## Verify your account

If you signed up via the website, you'll recieve a verification in your inbox automatically. Click on the link to verify your account and go to the next step.

If instead you used the REST API to sign up, you'll need to execute the following command which will send the verification email to your inbox.

```bash
curl -s -X POST -H "Content-type: application/json" https://nyrk.io/api/v0/auth/request-verify-token -d '{"email": "foo@bar.com"}'
```

Now go to your inbox and click on the link in the verification email.

## Generate an API token

In order to send performance test results to nyrk.io using `HTTP POST` you'll need to generate an API token. To do that, use the following code snippet.

```bash
curl -s -X POST https://nyrk.io/api/v0/auth/jwt/login -d username="foo@bar.com" -d password="mypassword"
```

Your newly generated API token will be returned in the `access_code` field of the JSON response. This API token should be used with the [bearer authenication](https://swagger.io/docs/specification/authentication/bearer-authentication/) scheme.

## Upload performance test results

Now comes the main bit -- uploading performance test results. The JSON schema for test results has a few required fields which are described in more detail in the API docs.

Briefly, here's a list of the required fields.

| Field      | Description                            |
| ---------- | -------------------------------------- |
| timestamp  | Unix timestamp (secs since Jan 1 1970) |
| metrics    | A list of dictionaries of metrics      |
| attributes | A dictionary of attributes             |

Here's an example payload for a performance test named `benchmark1`.

```bash
curl -s -X POST -H "Content-type: application/json" -H "Authorization: Bearer $TOKEN" -X POST https://nyrk.io/api/v0/result/benchmark1 \
           -d '[{"timestamp": 1706220908,
             "metrics": [
               {"name": "p50", "unit": "us", "value": 56 },
               {"name": "p90", "unit": "us", "value": 125 },
               {"name": "p99", "unit": "us", "value": 280 }
             ],
             "attributes": {
               "git_repo": ["https://github.com/nyrkio/nyrkio"],
               "branch": ["main"],
               "git_commit": ["6995e2de6891c724bfeb2db33d7b87775f913ad1"],
             }
       }]'
```

There are a few things to keep in mind when working with test result data:

`timestamp` should be the time of the _git commit_ that was tested, not the timestamp of the test execution. Using the git commit timestamp allows you to accurately pinpoint which commit (or sequence of commits) introduced a change in performance. In other words, you should use the timestamp of when the commits were merged to the branch being monitored. This you can get with the following command:

    commit_date=$(cd $GIT_REPO; git rev-list --format=format:"%ci" --max-count=1 $githash|grep -v commit)

The `git_commit` attribute is special. If you include it in your performance test results and the `git_repo` attribute points to a git repository on GitHub then Nyrkiö will link to the url for that commit whenever it's part of a change point.

The units for each metric is arbitrary and can be anything, e.g. "ns", "us", "instructions", "request/s", etc.

## View the charts in the dashboard

Now, if you navigate to https://nyrk.io/result/benchmark1 you'll see three charts with a single data point each.

## Questions?

You can email us directly at [helloworld@nyrk.io](mailto:helloworld@nyrk.io).
