from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, TypeVar, Set, Union
from typing_extensions import TypeAlias, TypedDict

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.db_connectors.db_connector import DBConnector
    from checkov.common.models.enums import CheckResult
    from checkov.common.runners.base_runner import BaseRunner  # noqa
    from networkx import DiGraph
    from igraph import Graph


_BaseRunner = TypeVar("_BaseRunner", bound="BaseRunner[Any]")

_ScannerCallableAlias: TypeAlias = Callable[
    [str, "BaseCheck", "_SkippedCheck", "dict[str, Any]", str, str, "dict[str, Any]"], None
]

_Resource: TypeAlias = str
_Attributes: TypeAlias = Set[str]
ResourceAttributesToOmit: TypeAlias = Dict[_Resource, _Attributes]
LibraryGraph: TypeAlias = "Union[DiGraph, Graph]"
LibraryGraphConnector: TypeAlias = "Union[DBConnector[DiGraph], DBConnector[Graph]]"


class _CheckResult(TypedDict, total=False):
    result: "CheckResult" | tuple["CheckResult", dict[str, Any]]
    suppress_comment: str
    evaluated_keys: list[str]
    results_configuration: dict[str, Any] | None
    check: BaseCheck
    entity: dict[str, Any]  # only exists for graph results


class _SkippedCheck(TypedDict, total=False):
    bc_id: str | None
    id: str
    suppress_comment: str
    line_number: int | None


class _BaselineFinding(TypedDict):
    resource: str
    check_ids: list[str]


class _BaselineFailedChecks(TypedDict):
    file: str
    findings: list[_BaselineFinding]


class _ReducedScanReport(TypedDict):
    checks: _ReducedScanReportCheck
    image_cached_results: list[dict[str, Any]]


class _ReducedScanReportCheck(TypedDict):
    failed_checks: list[dict[str, Any]]
    passed_checks: list[dict[str, Any]]
    skipped_checks: list[dict[str, Any]]


class _CicdDetails(TypedDict, total=False):
    commit: str | None
    pr: str | None
    runId: str | None
    scaCliScanId: str | None


class _ExitCodeThresholds(TypedDict):
    soft_fail: bool
    soft_fail_checks: list[str]
    soft_fail_threshold: Severity | None
    hard_fail_checks: list[str]
    hard_fail_threshold: Severity | None


class _ScaExitCodeThresholds(TypedDict):
    LICENSES: _ExitCodeThresholds
    VULNERABILITIES: _ExitCodeThresholds


class _LicenseStatus(TypedDict):
    package_name: str
    package_version: str
    policy: str
    license: str
    status: str


class _EntityContext(TypedDict, total=False):
    start_line: int
    end_line: int
    policy: str
    code_lines: list[tuple[int, str]]
    skipped_checks: list[_SkippedCheck]
