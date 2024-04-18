from typing import Dict, List, Optional, Any
from pydantic import BaseModel, RootModel


class TestResult(BaseModel):
    timestamp: int
    metrics: List[Dict]
    attributes: Dict
    extra_info: Optional[Dict] = {}


class TestResults(RootModel[Any]):
    root: List[TestResult]
