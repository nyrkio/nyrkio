from datetime import datetime
import json
import requests
import os
import sys


def calculate_unit(value):
    """
    Calculate the best unit for the value.
    """
    unit = "s"
    if value < 1.0:
        value = value * 1000
        unit = "ms"

    if value < 1.0:
        value = value * 1000
        unit = "us"

    # Round to 3 decimal places
    return round(value, 3), unit


GIT_COMMIT = os.environ.get("GIT_COMMIT")
GIT_TARGET_BRANCH = os.environ.get("GIT_TARGET_BRANCH")


def create_nyrkio_payload(benchmark, extra_info):
    commit = GIT_COMMIT if GIT_COMMIT else os.environ.get("GITHUB_SHA")
    branch = GIT_TARGET_BRANCH if GIT_TARGET_BRANCH else "main"

    # The loops we need to jump through to get the commit time are
    # ridiculous. GitHub actions do a shallow clone so we can't use
    # git show -s --format=%ct HEAD. Instead we have to use the
    # REST API.
    response = requests.get(
        f"https://api.github.com/repos/nyrkio/nyrkio/commits/{commit}"
    )
    response.raise_for_status()
    timestamp = int(
        datetime.strptime(
            response.json()["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%S%z"
        ).timestamp()
    )

    metrics = []
    for m in ("median", "mean", "max", "min", "stddev", "iqr"):
        value, unit = calculate_unit(benchmark["stats"][m])
        metrics.append({"name": m, "value": value, "unit": unit})

    return {
        "timestamp": timestamp,
        "metrics": metrics,
        "attributes": {
            "git_commit": commit,
            "branch": branch,
            "git_repo": "https://github.com/nyrkio/nyrkio",
        },
        "extra_info": extra_info,
    }


def raise_for_status(response, test_name):
    if response.status_code != 200:
        print(
            f"Failed to submit results for {test_name}"
            f" with status {response.status_code}"
        )
        print(response.json())
    response.raise_for_status()


def submit_results(test_name, results, token, pull_number):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
    }

    url = f"https://nyrkio.com/api/v0/result/{test_name}"

    if pull_number:
        repo = "nyrkio/nyrkio"
        url = f"https://nyrkio.com/api/v0/pulls/{repo}/{pull_number}/result/{test_name}"

    response = requests.post(url, json=results, headers=headers)
    raise_for_status(response, test_name)


def main(result_filename, extra_info_filename):
    # ...
    # Load the results from the file
    with open(result_filename, "r") as f:
        results = json.load(f)

    with open(extra_info_filename, "r") as f:
        extra_info = json.load(f)

    username = os.environ.get("NYRKIO_USERNAME")
    password = os.environ.get("NYRKIO_PASSWORD")
    pull_number = os.environ.get("PULL_NUMBER")

    if not username or not password:
        print("NYRKIO_USERNAME and NYRKIO_PASSWORD must be set")
        sys.exit(1)

    # Get JWT token
    response = requests.post(
        "https://nyrkio.com/api/v0/auth/jwt/login",
        data={"username": username, "password": password},
    )
    response.raise_for_status()
    token = response.json()["access_token"]

    post_data = {}
    test_names = []
    for r in results["benchmarks"]:
        test_name = r["fullname"]
        # Convert :: to / to use Nyrkiö's hierarchical navigation and
        # grouping of results.
        test_name = test_name.replace("::", "/")
        test_names.append(test_name)

        payload = create_nyrkio_payload(r, extra_info)
        post_data[test_name] = [payload]

    for test_name in test_names:
        submit_results(test_name, post_data[test_name], token, pull_number)

    if pull_number:
        # Trigger GitHub PR comment notification
        repo = "nyrkio/nyrkio"
        response = requests.get(
            f"https://nyrkio.com/api/v0/pulls/{repo}/{pull_number}/changes/{GIT_COMMIT}?notify=1",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-type": "application/json",
            },
        )
        raise_for_status(response, test_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: process_results.py <result_filename> <extra_info_filename>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
