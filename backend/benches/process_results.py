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


def create_nyrkio_payload(commit_info, benchmark):
    # convert date to epoch
    timestamp = int(
        datetime.strptime(commit_info["time"], "%Y-%m-%dT%H:%M:%S%z").timestamp()
    )

    metrics = []
    for m in ("median", "mean", "max", "min", "stddev", "iqr"):
        value, unit = calculate_unit(benchmark["stats"][m])
        metrics.append({"name": m, "value": value, "unit": unit})

    return {
        "timestamp": timestamp,
        "metrics": metrics,
        "attributes": {
            "git_commit": commit_info["id"],
            "branch": commit_info["branch"],
            "git_repo": "https://github.com/nyrkio/nyrkio",
        },
    }


def submit_results(test_name, results, token):
    # Submit results
    response = requests.post(
        f"https://nyrk.io/api/v0/result/{test_name}",
        json=results,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()


def main(filename):
    # ...
    # Load the results from the file
    with open(filename, "r") as f:
        results = json.load(f)

    username = os.environ.get("NYRKIO_USERNAME")
    password = os.environ.get("NYRKIO_PASSWORD")

    if not username or not password:
        print("NYRKIO_USERNAME and NYRKIO_PASSWORD must be set")
        sys.exit(1)

    # Get JWT token
    response = requests.post(
        "https://nyrk.io/api/v0/auth/jwt/login",
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

        payload = create_nyrkio_payload(results["commit_info"], r)
        post_data[test_name] = [payload]

    for test_name in test_names:
        submit_results(test_name, post_data[test_name], token)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: process_results.py <filename>")
        sys.exit(1)

    main(sys.argv[1])
