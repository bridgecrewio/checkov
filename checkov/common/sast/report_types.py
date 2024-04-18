from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, model_serializer

from checkov.common.sast.consts import SastLanguages


class Profiler(BaseModel):
    duration: Union[str, int]  # noqa: CCE003
    memory: int  # noqa: CCE003


class Point(BaseModel):
    row: int  # noqa: CCE003
    column: int  # noqa: CCE003

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return self.__dict__


class MatchLocation(BaseModel):
    path: str  # noqa: CCE003
    start: Point  # noqa: CCE003
    end: Point  # noqa: CCE003
    code_block: str  # noqa: CCE003
    extended_code_block: Optional[Dict[str, Any]] = None   # noqa: CCE003

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return self.__dict__


class DataFlow(BaseModel):
    data_flow: List[MatchLocation]  # noqa: CCE003

    @model_serializer
    def serialize_model(self) -> Dict[str, List[MatchLocation]]:
        return {'data_flow': self.data_flow}


class MatchMetadata(BaseModel):
    taint_mode: Optional[DataFlow] = None  # noqa: CCE003
    code_locations: Optional[List[MatchLocation]] = None  # noqa: CCE003

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        metadata = {}
        if hasattr(self, 'taint_mode') and self.taint_mode:
            metadata['taint_mode'] = self.taint_mode
        if hasattr(self, 'code_locations') and self.code_locations:
            metadata['code_locations'] = self.code_locations  # type: ignore

        return metadata


class Match(BaseModel):
    exact_hash: str  # noqa: CCE003
    structure_hash: str  # noqa: CCE003
    location: MatchLocation  # noqa: CCE003
    metadata: MatchMetadata  # noqa: CCE003
    minimized_ast: str  # noqa: CCE003


class RuleMatchMetadata(BaseModel):
    framework: Optional[str] = ''  # noqa: CCE003


class RuleMatch(BaseModel):
    check_id: str  # noqa: CCE003
    check_name: str  # noqa: CCE003
    check_cwe: Optional[Union[List[str], str]]  # noqa: CCE003
    check_owasp: Optional[Union[List[str], str]]  # noqa: CCE003
    severity: str  # noqa: CCE003
    matches: List[Match]  # noqa: CCE003
    metadata: Optional[RuleMatchMetadata] = None  # noqa: CCE003


class Function(BaseModel):
    name: str  # noqa: CCE003
    alias: str  # noqa: CCE003
    line_number: int  # noqa: CCE003
    code_block: str  # noqa: CCE003
    cve_id: Optional[str]  # noqa: CCE003

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class Package(BaseModel):
    alias: str  # noqa: CCE003
    functions: List[Function]   # noqa: CCE003


class File(BaseModel):
    packages: Dict[str, Package]  # noqa: CCE003


class Repositories(BaseModel):
    files: Dict[str, File]  # noqa: CCE003


class SkippedCheck(BaseModel):
    check_id: str   # noqa: CCE003
    suppress_comment: str   # noqa: CCE003


class PrismaReport(BaseModel):
    rule_match: Dict[SastLanguages, Dict[str, RuleMatch]]  # noqa: CCE003
    errors: Dict[str, List[str]]  # noqa: CCE003
    profiler: Dict[str, Profiler]  # noqa: CCE003
    run_metadata: Dict[str, Optional[Union[str, int, List[str]]]]  # noqa: CCE003
    imports: Dict[SastLanguages, Dict[str, Dict[str, Union[List[str], Dict[str, str]]]]]  # noqa: CCE003
    reachability_report: Dict[SastLanguages, Dict[str, Repositories]]   # noqa: CCE003
    skipped_checks_by_file: Dict[str, List[SkippedCheck]]   # noqa: CCE003


def create_empty_report(languages: List[SastLanguages]) -> PrismaReport:
    matches: Dict[SastLanguages, Dict[str, RuleMatch]] = {}
    for lang in languages:
        matches[lang] = {}
    return PrismaReport(rule_match=matches, errors={}, profiler={}, run_metadata={}, imports={}, reachability_report={},
                        skipped_checks_by_file={})


def serialize_reachability_report(report: Dict[str, Repositories]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for repo_path, files in report.items():
        result[repo_path] = {"files": {}}
        for file_name, packages in files.files.items():
            result[repo_path]["files"][file_name] = {"packages": {}}
            for package_name, package in packages.packages.items():
                result[repo_path]["files"][file_name]["packages"][package_name] = {"alias": package.alias, "functions": []}
                for function in package.functions:
                    result[repo_path]["files"][file_name]["packages"][package_name]["functions"].append(function.to_dict())
    return result
