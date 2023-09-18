from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel

from checkov.sast.consts import SastLanguages


class Profiler(BaseModel):
    duration: str  # noqa: CCE003
    memory: int  # noqa: CCE003


class Point(BaseModel):
    row: int  # noqa: CCE003
    column: int  # noqa: CCE003


class Flow(BaseModel):
    path: str  # noqa: CCE003
    start: Point  # noqa: CCE003
    end: Point  # noqa: CCE003
    code_block: str  # noqa: CCE003


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


class DataFlow(BaseModel):
    data_flow: List[Flow]  # noqa: CCE003


class MatchMetadata(BaseModel):
    metavariables: Dict[str, MatchMetavariable]  # noqa: CCE003
    variables: Dict[str, Any]  # noqa: CCE003
    taint_mode: Optional[DataFlow]  # noqa: CCE003


class Match(BaseModel):
    location: MatchLocation  # noqa: CCE003
    metadata: MatchMetadata  # noqa: CCE003


class RuleMatch(BaseModel):
    check_id: str  # noqa: CCE003
    check_name: str  # noqa: CCE003
    check_cwe: Optional[Union[List[str], str]]  # noqa: CCE003
    check_owasp: Optional[Union[List[str], str]]  # noqa: CCE003
    severity: str  # noqa: CCE003
    matches: List[Match]  # noqa: CCE003


class PrismaReport(BaseModel):
    rule_match: Dict[SastLanguages, Dict[str, RuleMatch]]  # noqa: CCE003
    errors: Dict[str, List[str]]  # noqa: CCE003
    profiler: Dict[str, Profiler]  # noqa: CCE003
    run_metadata: Dict[str, Optional[Union[str, int, List[str]]]]  # noqa: CCE003
    imports: Dict[SastLanguages, Dict[str, Dict[str, List[str]]]]  # noqa: CCE003


def create_empty_report(languages: List[SastLanguages]) -> PrismaReport:
    matches: Dict[SastLanguages, Dict[str, RuleMatch]] = {}
    for lang in languages:
        matches[lang] = {}
    return PrismaReport(rule_match=matches, errors={}, profiler={}, run_metadata={}, imports={})
