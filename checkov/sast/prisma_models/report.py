from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from checkov.sast.consts import SastLanguages


class Profiler(BaseModel):
    policies_patterns_parse_time: float  # noqa: CCE003
    source_code_parse_time: float  # noqa: CCE003
    memory: float  # noqa: CCE003
    policy_match_time: Optional[Dict[str, float]]  # noqa: CCE003
    source_code_match_time: Optional[Dict[str, float]]  # noqa: CCE003


class Point(BaseModel):
    row: int  # noqa: CCE003
    column: int  # noqa: CCE003


class Flow(BaseModel):
    path: str  # noqa: CCE003
    start: Point  # noqa: CCE003
    end: Point  # noqa: CCE003


class MatchLocation(BaseModel):
    path: str  # noqa: CCE003
    start: Point  # noqa: CCE003
    end: Point  # noqa: CCE003
    code_block: str  # noqa: CCE003


class MatchMetavariable(BaseModel):
    path: Optional[str]  # noqa: CCE003
    start: Optional[Point]  # noqa: CCE003
    end: Optional[Point]  # noqa: CCE003
    data_flow: Optional[List[Flow]]  # noqa: CCE003
    code_block: Optional[str]  # noqa: CCE003


class MatchMetadata(BaseModel):
    metavariables: Dict[str, MatchMetavariable]  # noqa: CCE003
    variables: Dict[str, Any]  # noqa: CCE003


class Match(BaseModel):
    location: MatchLocation  # noqa: CCE003
    metadata: MatchMetadata  # noqa: CCE003


class RuleMatch(BaseModel):
    check_id: str  # noqa: CCE003
    check_name: str  # noqa: CCE003
    check_cwe: str  # noqa: CCE003
    check_owasp: str  # noqa: CCE003
    severity: str  # noqa: CCE003
    matches: List[Match]  # noqa: CCE003


class PrismaReport(BaseModel):
    rule_match: Dict[SastLanguages, Dict[str, RuleMatch]]  # noqa: CCE003
    errors: List[str]  # noqa: CCE003
    profiler: Profiler  # noqa: CCE003
