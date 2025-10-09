import requests
import os
import asyncio

# Must include the protocol prefix and port number if not 80
HOST = os.environ.get("TEST_HOST", "http://localhost")


def test_default_data_results(benchmark):
    """
    Run a HTTP GET on the default data results endpoint.
    """

    def fetch():
        response = requests.get(f"{HOST}/api/v0/default/results")
        response.raise_for_status()
        asyncio.sleep(2)

    benchmark(fetch)


def test_default_data_changes(benchmark):
    """
    Run a HTTP GET on the default data changes endpoint.
    """
    response = requests.get(f"{HOST}/api/v0/default/results")
    response.raise_for_status()
    test_name = response.json()[0]

    def fetch(test_name):
        response = requests.get(f"{HOST}/api/v0/default/result/{test_name}/changes")
        response.raise_for_status()

    benchmark(fetch, test_name)
