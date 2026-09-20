from typing import Dict, List, Optional, Any, Union
from typing_extensions import TypedDict, NotRequired
from pydantic import BaseModel, RootModel
from enum import Enum


class DirectionEnum(str, Enum):
    higher_is_better = "higher_is_better"
    lower_is_better = "lower_is_better"


class Metrics(TypedDict):
    name: str
    unit: str
    value: Union[float, int]
    direction: NotRequired[DirectionEnum]


class Attributes(TypedDict):
    git_commit: str
    branch: str
    git_repo: str


class TestResult(BaseModel):
    timestamp: int
    metrics: List[Metrics]
    attributes: Attributes
    extra_info: Optional[Dict] = None


class TestResults(RootModel[Any]):
    root: List[TestResult]


class BulkTestsRequest(BaseModel):
    """
    Body for the bulk results/changes endpoints. POST (not GET+query) because
    a full tree selection can be hundreds of test names — too long for a
    query string / request-line header limit.
    """

    tests: List[str]
    limit: Optional[int] = None
