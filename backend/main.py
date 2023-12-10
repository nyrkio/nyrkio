# Copyright (c) 2024, Nyrkiö Oy

from fastapi import FastAPI

from . import api, auth

app = FastAPI()

app.include_router(api.router)
app.include_router(auth.token_router)
app.include_router(auth.user_router)


@app.get("/")
async def root():
    return {}

"""
This is a description of the core logic of Nyrkiö. It is written in such a way
that a performance engineer can understand it without having to read the code.
Though we use specific technologies internally (e.g. change point detection,
databases, etc), we try to avoid mentioning them here to keep the core logic
pure and free from technical details.



Nyrkiö detects performance changes in test results.

Multiple performance test results (frequently referred to as just "test results"
throughout the code) can be added together to form a test result series.

Test results must have a unique timestamp -- you cannot add a test result with
an existing timestamp to a series. However, you can update an existing test
result, for example when a performance engineer discovers that the
infrastructure they ran the test on is noisy, or they fix a bug in the test
code.

Test results can also be deleted.

Test results are made up of metrics and attributes. Metrics record some value
during a test run, e.g. the number of requests per second. Attributes provide
additional information about the test run, e.g. the version of the software or
the git commit hash.

A test result series can be analyzed to find changes in performance by identifying
individual test results where some metric changed in a statistically significant
way from previous test results. A performance change can represent either a
regression or an improvement.

Notifications can be sent when a performance change is detected.

"""

class PerformanceTestResult:
    def __init__(self, timestamp, metrics, attributes):
        self.timestamp = timestamp
        self.metrics = metrics
        self.attributes = attributes


class PerformanceTestResultSeries:
    def __init__(self):
        self.results = []

    def add_result(self, result: PerformanceTestResult):
        if result in self.results:
            raise PerformanceTestResultExistsError()

        self.results.append(result)


class PerformanceTestResultExistsError(Exception):
    pass