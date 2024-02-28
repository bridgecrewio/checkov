from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, TypeVar, Set, Union, TypedDict, Tuple
from typing_extensions import TypeAlias  # noqa[TC002]

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.db_connectors.db_connector import DBConnector
    from checkov.common.models.enums import CheckResult
    from checkov.common.runners.base_runner import BaseRunner  # noqa
    from networkx import DiGraph
    from rustworkx import PyDiGraph
    from checkov.terraform.modules.module_objects import TFDefinitionKey

_BaseRunner = TypeVar("_BaseRunner", bound="BaseRunner[Any, Any, Any]")

_ScannerCallableAlias: TypeAlias = Callable[
    [str, "BaseCheck", "list[_SkippedCheck]", "dict[str, Any]", str, str, "dict[str, Any]"], None
]

_Resource: TypeAlias = str
_Attributes: TypeAlias = Set[str]
ResourceAttributesToOmit: TypeAlias = Dict[_Resource, _Attributes]
_RustworkxGraph: TypeAlias = "PyDiGraph[tuple[int, dict[str, Any]], dict[str, str | int]]"
LibraryGraph: TypeAlias = "Union[DiGraph, _RustworkxGraph]"
LibraryGraphConnector: TypeAlias = "Union[DBConnector[DiGraph], DBConnector[_RustworkxGraph]]"
# TODO Remove this type and only use TFDefinitionKey
TFDefinitionKeyType: TypeAlias = "Union[str, TFDefinitionKey]"


class _CheckResult(TypedDict, total=False):
    result: Union["CheckResult", Tuple["CheckResult", dict[str, Any]]]
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


class _ScaSuppressionsMaps(TypedDict, total=False):
    cve_suppresion_by_cve_map: dict[str, _SuppressedCves]
    licenses_suppressions_by_policy_and_package_map: dict[str, _SuppressedLicenses]


# _ScaSuppressions fields are in camel case because this is the output of the server report
class _ScaSuppressions(TypedDict, total=False):
    cves: _CvesSuppressions
    licenses: _LicensesSuppressions


class _CvesSuppressions(TypedDict):
    byCve: list[_SuppressedCves]


class _LicensesSuppressions(TypedDict):
    byPackage: list[_SuppressedLicenses]


class _SuppressedCves(TypedDict):
    reason: str
    cveId: str


class _SuppressedLicenses(TypedDict):
    reason: str
    packageName: str
    licensePolicy: str
    licenses: list[str]


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


class _LicenseStatusWithLines(_LicenseStatus):
    lines: list[int] | None  # noqa: CCE003  # a static attribute


class _ImageReferencerLicenseStatus(TypedDict):
    image_name: str
    licenses: list[_LicenseStatus]


class _EntityContext(TypedDict, total=False):
    start_line: int
    end_line: int
    policy: str
    code_lines: list[tuple[int, str]]
    skipped_checks: list[_SkippedCheck]
    origin_relative_path: str
