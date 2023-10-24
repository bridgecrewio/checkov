from typing import Dict, Any, Set

from pydantic import BaseModel


class ReachabilityData(BaseModel):
    aliasMapping: Dict[str, Any]  # noqa: CCE003


class ReachabilityRunConfig(BaseModel):
    packageNamesForMapping: Set[str]  # noqa: CCE003
