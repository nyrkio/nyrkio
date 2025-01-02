from typing import Dict, List, Optional, Any
from pydantic import BaseModel, RootModel
from enum import Enum


class DirectionEnum(str, Enum):
    higher_is_better = "higher_is_better"
    lower_is_better = "lower_is_better"


class TestResultMetrics(BaseModel):
    name: str
    unit: Optional[str]
    value: float
    direction: Optional[str]


class TestResult(BaseModel):
    timestamp: int
    metrics: List[Dict]
    attributes: Dict
    extra_info: Optional[Dict] = {}


class TestResults(RootModel[Any]):
    root: List[TestResult]
