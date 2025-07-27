from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional, Dict, List

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import (
    integration as metadata_integration,
)
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities, Severity
from checkov.common.models.enums import CheckResult, ScanDataFormat
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import Record, DEFAULT_SEVERITY, SCA_PACKAGE_SCAN_CHECK_NAME, SCA_LICENSE_CHECK_NAME
from checkov.common.packaging import version as packaging_version
from checkov.common.sca.commons import (
    get_file_path_for_record,
    get_resource_for_record,
    get_package_alias,
    UNFIXABLE_VERSION,
    get_package_type,
    normalize_twistcli_language,
    get_registry_url, get_package_lines,
    get_record_file_line_range, get_license_policy_and_package_alias
)
from checkov.common.util.http_utils import request_wrapper, aiohttp_client_session_wrapper
from checkov.runner_filter import RunnerFilter
from checkov.common.output.common import format_licenses_to_string

if TYPE_CHECKING:
    from checkov.common.output.common import SCADetails
    from checkov.common.output.report import Report
    from checkov.common.typing import (
        _LicenseStatus,
        _CheckResult,
        _ScaSuppressions,
        _ScaSuppressionsMaps,
        _SuppressedCves,
        _SuppressedLicenses,
        _ImageReferencerLicenseStatus,
    )


def create_report_license_record(
        rootless_file_path: str,
        file_abs_path: str,
        check_class: str,
        licenses_status: _LicenseStatus,
        package: dict[str, Any],
        sca_details: SCADetails | None = None,
        severity: Severity | None = None
) -> Record:
    package_name = licenses_status["package_name"]
    package_version = licenses_status["package_version"]
    policy = licenses_status["policy"]
    bc_status = licenses_status["status"]

    # renaming the status name from the one in platform's report to be convenient with checkov's-report
    status = "FAILED" if bc_status == "OPEN" else bc_status

    check_result: _CheckResult = {
        "result": CheckResult.FAILED,
    }
    if status == "COMPLIANT":
        check_result["result"] = CheckResult.PASSED

    code_block = get_code_block(package, package_name, package_version)

    details = {
        "package_name": package_name,
        "package_version": package_version,
        "package_registry": get_registry_url(package),
        "is_private_registry": package.get("isPrivateRegistry", False),
        "license": licenses_status["license"],
        "status": status,
        "policy": policy,
        "package_type": get_package_type(package_name, package_version, sca_details),
    }

    record = Record(
        check_id=policy,
        bc_check_id=policy,
        check_name=SCA_LICENSE_CHECK_NAME,
        check_result=check_result,
        code_block=code_block,
        file_path=get_file_path_for_record(rootless_file_path),
        file_line_range=get_package_lines(package) or [0, 0],
        resource=get_resource_for_record(rootless_file_path, package_name),
        check_class=check_class,
        evaluations=None,
        file_abs_path=file_abs_path,
        short_description=f"License {licenses_status['license']} - {package_name}: {package_version}",
        vulnerability_details=details,
        severity=severity
    )
    return record


def _update_details_by_scan_data_format(
        details: dict[str, Any],
        vulnerability_details: dict[str, Any],
        sca_details: SCADetails | None = None,
        scan_data_format: ScanDataFormat = ScanDataFormat.TWISTCLI
) -> None:
    if scan_data_format in {ScanDataFormat.TWISTCLI, ScanDataFormat.DEPENDENCY_TREE}:
        lowest_fixed_version = UNFIXABLE_VERSION
        package_version = vulnerability_details["packageVersion"]
        fixed_versions: list[packaging_version.Version | packaging_version.LegacyVersion] = []
        status = vulnerability_details.get("status") or "open"
        if status != "open":
            parsed_current_version = packaging_version.parse(package_version)
            for version in status.replace("fixed in", "").split(","):
                parsed_version = packaging_version.parse(version.strip())
                if parsed_version > parsed_current_version:
                    fixed_versions.append(parsed_version)

            if fixed_versions:
                lowest_fixed_version = str(min(fixed_versions))
        details.update({"status": status, "lowest_fixed_version": lowest_fixed_version,
                        "fixed_versions": fixed_versions, "image_details": sca_details})
    elif scan_data_format == ScanDataFormat.PLATFORM:
        status = vulnerability_details["status"]
        fix_version = vulnerability_details.get("cveStatus")
        details.update({"status": status, "fix_version": fix_version})


def get_code_block(package: dict[str, Any], package_name: str, package_version: str,
                   root_package: Optional[dict[str, Any]] = None) -> list[tuple[int, str]]:
    if root_package:
        root_lines_number = root_package.get("lines")
        root_code_block = root_package.get("code_block")
        if root_lines_number and root_code_block:
            return [(int(root_lines_number[0]), root_code_block)]

    lines_number = package.get("lines")
    code_block = package.get("code_block")

    if lines_number and code_block:
        return [(int(lines_number[0]), code_block)]

    return [(0, f"{package_name}: {package_version}")]


def get_fix_command_and_code(vulnerability_details: dict[str, Any], root_package: dict[str, Any] | None = None,
                             root_package_cve: dict[str, Any] | None = None
                             ) -> tuple[dict[str, Any] | None, str | None]:
    if root_package_cve:
        return root_package_cve.get('fixCommand'), root_package_cve.get('fixCode')

    if root_package and (
            root_package['name'] != vulnerability_details["packageName"] or root_package['version'] !=
            vulnerability_details["packageVersion"]):
        return None, None
    return vulnerability_details.get('fixCommand'), vulnerability_details.get('fixCode')


def get_package_lines_numbers(package: dict[str, Any], root_package: dict[str, Any] | None = None,
                              file_line_range: list[int] | None = None) -> list[int]:
    if root_package:
        return get_record_file_line_range(root_package, file_line_range)
    return get_record_file_line_range(package, file_line_range)


def create_report_cve_record(
        rootless_file_path: str,
        file_abs_path: str,
        check_class: str,
        vulnerability_details: dict[str, Any],
        licenses: str,
        package: dict[str, Any],
        used_private_registry: bool = False,
        root_package: dict[str, Any] | None = None,
        runner_filter: RunnerFilter | None = None,
        sca_details: SCADetails | None = None,
        scan_data_format: ScanDataFormat = ScanDataFormat.TWISTCLI,
        file_line_range: list[int] | None = None,
        root_package_cve: dict[str, Any] | None = None
) -> Record:
    runner_filter = runner_filter or RunnerFilter()
    package_name = vulnerability_details["packageName"]
    package_version = vulnerability_details["packageVersion"]
    package_type = get_package_type(package_name, package_version, sca_details)
    cve_id = vulnerability_details.get("id", vulnerability_details.get("cveId", '')).upper()
    severity = vulnerability_details.get("severity", DEFAULT_SEVERITY)

    # sanitize severity names
    if severity == "moderate":
        severity = "medium"
    if severity.upper() not in Severities:
        logging.warning(
            f"unknown severity - severity '{severity}' is unknown. using the DEFAULT_SEVERITY: '{DEFAULT_SEVERITY}' instead. "
            f"vulnerabilities-details: {vulnerability_details}")
        severity = DEFAULT_SEVERITY

    description = vulnerability_details.get("description")

    check_result: _CheckResult = {
        "result": CheckResult.FAILED,
    }

    if runner_filter.skip_cve_package and package_name in runner_filter.skip_cve_package:
        check_result = {
            "result": CheckResult.SKIPPED,
            "suppress_comment": f"Filtered by package '{package_name}'",
        }
    elif not runner_filter.within_threshold(Severities[severity.upper()]):
        check_result = {
            "result": CheckResult.SKIPPED,
            "suppress_comment": "Filtered by severity",
        }
    code_block = get_code_block(package, package_name, package_version, root_package)
    fix_command, fix_code = get_fix_command_and_code(vulnerability_details, root_package, root_package_cve)
    details = {
        "id": cve_id,
        "severity": severity,
        "package_name": package_name,
        "package_version": package_version,
        "package_registry": get_registry_url(package),
        "is_private_registry": package.get("isPrivateRegistry", False),
        "package_type": package_type,
        "link": vulnerability_details.get("link"),
        "cvss": vulnerability_details.get("cvss"),
        "vector": vulnerability_details.get("vector"),
        "description": description,
        "risk_factors": vulnerability_details.get("riskFactorsV2"),
        "published_date": vulnerability_details.get("publishedDate") or (datetime.now() - timedelta(
            days=vulnerability_details.get("publishedDays", 0))).isoformat(),
        "licenses": licenses,
        "root_package_name": root_package.get("name") if root_package else None,
        "root_package_version": root_package.get("version") if root_package else None,
        "root_package_file_line_range": get_package_lines(root_package) if root_package else None or [0, 0],
        "fix_command": fix_command
    }

    if used_private_registry:
        details["is_private_fix"] = vulnerability_details.get("isPrivateRegFix", False)

    if root_package_cve and root_package_cve.get('fixVersion'):
        details['root_package_fix_version'] = root_package_cve.get('fixVersion')

    _update_details_by_scan_data_format(details, vulnerability_details, sca_details, scan_data_format)
    record = Record(
        check_id=f"CKV_{cve_id.replace('-', '_')}",
        bc_check_id=f"BC_{cve_id.replace('-', '_')}",
        check_name=SCA_PACKAGE_SCAN_CHECK_NAME,
        check_result=check_result,
        code_block=code_block,
        file_path=get_file_path_for_record(rootless_file_path),
        file_line_range=get_package_lines_numbers(package, root_package, file_line_range),
        resource=get_resource_for_record(rootless_file_path, package_name),
        check_class=check_class,
        evaluations=None,
        file_abs_path=file_abs_path,
        severity=Severities[severity.upper()],
        description=description,
        short_description=f"{cve_id} - {package_name}: {package_version}",
        vulnerability_details=details,
    )

    record.fixed_definition = fix_code  # type: ignore
    return record


def _add_to_report_licenses_statuses(
        report: Report,
        check_class: str | None,
        scanned_file_path: str,
        rootless_file_path: str,
        runner_filter: RunnerFilter,
        packages_map: dict[str, dict[str, Any]],
        license_statuses: list[_LicenseStatus],
        sca_details: SCADetails | None = None,
        report_type: str | None = None,
        inline_suppressions_maps: _ScaSuppressionsMaps | None = None,
) -> dict[str, list[str]]:
    licenses_per_package_map: dict[str, list[str]] = defaultdict(list)

    for license_status in license_statuses:
        # filling 'licenses_per_package_map', will be used in the call to 'create_report_cve_record' for efficient
        # extracting of license per package
        package_name, package_version, license = (
            license_status["package_name"],
            license_status["package_version"],
            license_status["license"],
        )
        package_alias = get_package_alias(package_name, package_version)
        licenses_per_package_map[package_alias].append(license)

        policy = license_status["policy"]
        severity = metadata_integration.get_severity(policy)

        license_record = create_report_license_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=scanned_file_path,
            check_class=check_class or "",
            licenses_status=license_status,
            package=packages_map.get(package_alias, {}),
            sca_details=sca_details,
            severity=severity
        )

        vulnerability_details = license_record.vulnerability_details or {}

        # apply inline suppressions
        suppressed = apply_licenses_inline_suppressions(
            record=license_record, vulnerability_details=vulnerability_details,
            inline_suppressions_maps=inline_suppressions_maps
        )

        if not suppressed and not runner_filter.should_run_check(
                check_id=policy,
                bc_check_id=policy,
                severity=severity,
                report_type=report_type,
        ):
            if runner_filter.checks:
                continue
            else:
                license_record.check_result = {
                    "result": CheckResult.SKIPPED,
                    "suppress_comment": f"{policy} is skipped",
                }

        report.add_resource(license_record.resource)
        report.add_record(license_record)

    return licenses_per_package_map


def get_inline_suppressions_map(inline_suppressions: _ScaSuppressions | None = None) -> _ScaSuppressionsMaps | None:
    if not inline_suppressions:
        return None
    suppressions_map: _ScaSuppressionsMaps = {}

    # fill cves suppressions map
    cve_suppresion_by_cve_map: dict[str, _SuppressedCves] = {}
    inline_suppressions_by_cve: list[_SuppressedCves] = inline_suppressions.get("cves", {}).get("byCve", [])
    for cve_suppression in inline_suppressions_by_cve:
        cve_id = cve_suppression.get("cveId")
        if cve_id:
            cve_suppresion_by_cve_map[cve_id] = cve_suppression

    # fill licenses suppressions map
    licenses_suppressions_by_policy_and_package_map: dict[str, _SuppressedLicenses] = {}
    inline_suppressions_by_license: list[_SuppressedLicenses] = inline_suppressions.get("licenses", {}).get("byPackage",
                                                                                                            [])
    for license_suppression in inline_suppressions_by_license:
        if license_suppression.get("licensePolicy") and license_suppression.get("packageName"):
            key = get_license_policy_and_package_alias(license_suppression["licensePolicy"],
                                                       license_suppression["packageName"])
            licenses_suppressions_by_policy_and_package_map[key] = license_suppression

    suppressions_map['cve_suppresion_by_cve_map'] = cve_suppresion_by_cve_map
    suppressions_map[
        'licenses_suppressions_by_policy_and_package_map'] = licenses_suppressions_by_policy_and_package_map

    return suppressions_map


def add_to_reports_cves_and_packages(
        report: Report,
        check_class: str | None,
        scanned_file_path: str,
        rootless_file_path: str,
        runner_filter: RunnerFilter,
        vulnerabilities: list[dict[str, Any]],
        packages: list[dict[str, Any]],
        packages_map: dict[str, dict[str, Any]],
        licenses_per_package_map: dict[str, list[str]],
        used_private_registry: bool = False,
        dependencies: dict[str, List[int]] | None = None,
        sca_details: SCADetails | None = None,
        report_type: str | None = None,
        inline_suppressions_maps: _ScaSuppressionsMaps | None = None,
        scan_data_format: ScanDataFormat = ScanDataFormat.TWISTCLI,
        file_line_range: list[int] | None = None
) -> None:
    is_dependency_tree_flow = bool(dependencies)

    vulnerable_packages, root_packages_list = create_vulnerable_packages_dict(vulnerabilities, packages,
                                                                              is_dependency_tree_flow)

    for package in packages:
        package_name, package_version = package["name"], package["version"]
        package_alias = get_package_alias(package_name, package_version)

        if package_alias in vulnerable_packages:
            package["cves"] = vulnerable_packages[package_alias]
        else:
            # adding resources without cves for adding them also in the output-bom-repors
            add_extra_resources_to_report(report, scanned_file_path, rootless_file_path,
                                          package, package_alias, licenses_per_package_map, sca_details)

    if is_dependency_tree_flow:
        add_to_reports_dependency_tree_cves(check_class, packages_map, licenses_per_package_map, packages, report,
                                            root_packages_list, rootless_file_path, runner_filter,
                                            scanned_file_path, used_private_registry, scan_data_format, sca_details,
                                            report_type, inline_suppressions_maps)
    else:  # twistlock scan results.
        for vulnerability in vulnerabilities:
            package_name, package_version = vulnerability["packageName"], vulnerability["packageVersion"]
            add_cve_record_to_report(vulnerability_details=vulnerability,
                                     package_name=package_name,
                                     package_version=package_version,
                                     packages_map=packages_map,
                                     rootless_file_path=rootless_file_path,
                                     scanned_file_path=scanned_file_path,
                                     check_class=check_class or "",
                                     licenses_per_package_map=licenses_per_package_map,
                                     runner_filter=runner_filter,
                                     sca_details=sca_details,
                                     scan_data_format=scan_data_format,
                                     report_type=report_type,
                                     report=report,
                                     inline_suppressions_maps=inline_suppressions_maps,
                                     file_line_range=file_line_range,
                                     used_private_registry=used_private_registry)


def add_to_reports_dependency_tree_cves(check_class: str | None, packages_map: dict[str, dict[str, Any]],
                                        licenses_per_package_map: dict[str, list[str]], packages: list[dict[str, Any]],
                                        report: Report, root_packages_list: list[int],
                                        rootless_file_path: str, runner_filter: RunnerFilter, scanned_file_path: str,
                                        used_private_registry: bool = False,
                                        scan_data_format: ScanDataFormat = ScanDataFormat.TWISTCLI,
                                        sca_details: SCADetails | None = None, report_type: str | None = None,
                                        inline_suppressions_maps: _ScaSuppressionsMaps | None = None) -> None:
    for root_package_index in root_packages_list:
        vulnerable_dependencies = find_vulnerable_dependencies(root_package_index, packages)

        root_package = packages[root_package_index]
        if len(root_package.get("cves", [])) > 0 or len(vulnerable_dependencies) > 0:
            root_package["vulnerable_dependencies"] = vulnerable_dependencies

        indirect_packages: dict[str, Any] = dict()
        for cve in root_package.get("cves", []):
            if 'causePackageName' in cve:
                cve_alias = f'{cve["cveId"]}@{cve["causePackageName"]}@{cve["causePackageVersion"]}'
                indirect_packages[cve_alias] = cve
                continue

            add_cve_record_to_report(vulnerability_details=cve, package_name=root_package['name'],
                                     package_version=root_package['version'], packages_map=packages_map,
                                     rootless_file_path=rootless_file_path, scanned_file_path=scanned_file_path,
                                     check_class=check_class, licenses_per_package_map=licenses_per_package_map,
                                     runner_filter=runner_filter, sca_details=sca_details,
                                     scan_data_format=scan_data_format, report_type=report_type, report=report,
                                     root_package=root_package, inline_suppressions_maps=inline_suppressions_maps,
                                     used_private_registry=used_private_registry)

        for dep in root_package.get("vulnerable_dependencies", []):
            for dep_cve in dep.get("cves", []):
                cve_alias = f'{dep_cve["cveId"]}@{dep_cve["packageName"]}@{dep_cve["packageVersion"]}'
                root_package_cve = None
                if cve_alias in indirect_packages:
                    root_package_cve = indirect_packages[cve_alias]

                add_cve_record_to_report(vulnerability_details=dep_cve, package_name=dep['name'],
                                         package_version=dep['version'], packages_map=packages_map,
                                         rootless_file_path=rootless_file_path, scanned_file_path=scanned_file_path,
                                         check_class=check_class, licenses_per_package_map=licenses_per_package_map,
                                         runner_filter=runner_filter, sca_details=sca_details,
                                         scan_data_format=scan_data_format, report_type=report_type, report=report,
                                         root_package=root_package,
                                         inline_suppressions_maps=inline_suppressions_maps,
                                         used_private_registry=used_private_registry, root_package_cve=root_package_cve)


def add_cve_record_to_report(vulnerability_details: dict[str, Any], package_name: str, package_version: str,
                             packages_map: dict[str, dict[str, Any]], rootless_file_path: str,
                             scanned_file_path: str, check_class: Optional[str],
                             licenses_per_package_map: dict[str, list[str]], runner_filter: RunnerFilter,
                             sca_details: Optional[SCADetails], scan_data_format: ScanDataFormat,
                             report_type: Optional[str], report: Report, used_private_registry: bool = False,
                             root_package: dict[str, Any] | None = None,
                             inline_suppressions_maps: _ScaSuppressionsMaps | None = None,
                             file_line_range: list[int] | None = None,
                             root_package_cve: dict[str, Any] | None = None) -> None:
    package_alias = get_package_alias(package_name, package_version)
    cve_record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=scanned_file_path,
        check_class=check_class or "",
        vulnerability_details=vulnerability_details,
        licenses=format_licenses_to_string(licenses_per_package_map[package_alias]),
        package=packages_map.get(package_alias, {}),
        runner_filter=runner_filter,
        sca_details=sca_details,
        scan_data_format=scan_data_format,
        root_package=root_package,
        root_package_cve=root_package_cve,
        file_line_range=file_line_range,
        used_private_registry=used_private_registry
    )
    suppressed = apply_cves_inline_suppressions(
        record=cve_record, inline_suppressions_maps=inline_suppressions_maps
    )

    if not suppressed and not runner_filter.should_run_check(
            check_id=cve_record.check_id,
            bc_check_id=cve_record.bc_check_id,
            severity=cve_record.severity,
            report_type=report_type,
    ):
        if runner_filter.checks:
            return
        else:
            cve_record.check_result = {
                "result": CheckResult.SKIPPED,
                "suppress_comment": f"{vulnerability_details.get('cveId', vulnerability_details.get('id', ''))} is skipped"
            }

    report.add_resource(cve_record.resource)
    report.add_record(cve_record)


def apply_cves_inline_suppressions(
        record: Record, inline_suppressions_maps: _ScaSuppressionsMaps | None = None
) -> bool:
    """Applies the inline suppression and returns an accomplish status"""

    if inline_suppressions_maps and record.vulnerability_details and inline_suppressions_maps.get(
            "cve_suppresion_by_cve_map"):
        cve_id = record.vulnerability_details.get("id", "")
        cve_suppression = inline_suppressions_maps["cve_suppresion_by_cve_map"].get(cve_id)
        if cve_suppression:
            record.check_result = {
                "result": CheckResult.SKIPPED,
                "suppress_comment": cve_suppression.get('reason', ''),
            }
            return True

    return False


def apply_licenses_inline_suppressions(
        record: Record, vulnerability_details: dict[str, Any],
        inline_suppressions_maps: _ScaSuppressionsMaps | None = None
) -> bool:
    """Applies the inline suppression and returns an accomplish status"""

    if inline_suppressions_maps and inline_suppressions_maps.get("licenses_suppressions_by_policy_and_package_map"):
        key = get_license_policy_and_package_alias(vulnerability_details.get("policy", ""),
                                                   vulnerability_details.get("package_name", ""))
        license_suppression = inline_suppressions_maps["licenses_suppressions_by_policy_and_package_map"].get(key)
        if license_suppression:
            record.check_result = {
                "result": CheckResult.SKIPPED,
                "suppress_comment": license_suppression.get('reason', ''),
            }
            return True

    return False


def find_vulnerable_dependencies(root_package_index: int, packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vulnerable_dependencies: list[dict[str, Any]] = []
    for vulnerable_dependency_idx in packages[root_package_index].get('vulnerable_dependencies', []):
        vulnerable_dependencies.append(packages[vulnerable_dependency_idx])
    return vulnerable_dependencies


def create_root_packages_list(root_packages_list: list[int], packages: list[dict[str, Any]], package: dict[str, Any],
                              dependencies: Optional[Dict[str, List[int]]]) -> None:
    if dependencies:
        if package.get("root", ""):
            root_packages_list.append(packages.index(package))
    else:
        # if we don't have dependencies, all packages will be "roots"
        root_packages_list.append(packages.index(package))


def create_vulnerable_packages_dict(vulnerabilities: list[dict[str, Any]], packages: list[dict[str, Any]],
                                    is_dependency_tree_flow: bool) -> tuple[dict[str, list[dict[str, Any]]], list[int]]:
    vulnerable_packages: dict[str, list[dict[str, Any]]] = dict()
    root_packages_list: list[int] = []
    if is_dependency_tree_flow:
        for package_idx, package in enumerate(packages):
            if package.get("root", False):
                root_packages_list.append(package_idx)

            package_alias = get_package_alias(package["name"], package["version"])
            for cve_idx in package.get('cves_index', []):
                vulnerable_packages.setdefault(package_alias, []).append(vulnerabilities[cve_idx])
    else:
        for vulnerability in vulnerabilities:
            package_alias = get_package_alias(vulnerability["packageName"], vulnerability["packageVersion"])
            vulnerable_packages.setdefault(package_alias, []).append(vulnerability)

    return vulnerable_packages, root_packages_list


def add_extra_resources_to_report(report: Report, scanned_file_path: str, rootless_file_path: str,
                                  package: dict[str, Any], package_alias: str,
                                  licenses_per_package_map: dict[str, list[str]],
                                  sca_details: Optional[SCADetails]) -> None:
    package_name, package_version = package["name"], package["version"]
    report.extra_resources.add(
        ExtraResource(
            file_abs_path=scanned_file_path,
            file_path=get_file_path_for_record(rootless_file_path),
            resource=get_resource_for_record(rootless_file_path, package_name),
            file_line_range=get_package_lines(package),
            vulnerability_details={
                "package_name": package_name,
                "package_version": package_version,
                "package_registry": get_registry_url(package),
                "is_private_registry": package.get("isPrivateRegistry", False),
                "licenses": format_licenses_to_string(
                    licenses_per_package_map[package_alias]),
                "package_type": get_package_type(package_name, package_version, sca_details)
            },
        )
    )


def add_to_report_sca_data(
        report: Report,
        check_class: str | None,
        scanned_file_path: str,
        rootless_file_path: str,
        runner_filter: RunnerFilter,
        vulnerabilities: list[dict[str, Any]],
        packages: list[dict[str, Any]],
        license_statuses: list[_LicenseStatus],
        used_private_registry: bool = False,
        dependencies: dict[str, list[int]] | None = None,
        sca_details: SCADetails | None = None,
        report_type: str | None = None,
        inline_suppressions: _ScaSuppressions | None = None,
        file_line_range: list[int] | None = None
) -> None:
    inline_suppressions_maps: _ScaSuppressionsMaps | None = get_inline_suppressions_map(inline_suppressions)
    packages_map: dict[str, dict[str, Any]] = {get_package_alias(p["name"], p["version"]): p for p in packages}
    licenses_per_package_map: dict[str, list[str]] = \
        _add_to_report_licenses_statuses(report, check_class, scanned_file_path, rootless_file_path, runner_filter,
                                         packages_map, license_statuses, sca_details, report_type,
                                         inline_suppressions_maps)
    # if dependencies is empty list it means we got results via DependencyTree scan but no dependencies have found.
    add_to_reports_cves_and_packages(report=report, check_class=check_class,
                                     scanned_file_path=scanned_file_path,
                                     rootless_file_path=rootless_file_path,
                                     runner_filter=runner_filter,
                                     vulnerabilities=vulnerabilities,
                                     packages=packages,
                                     packages_map=packages_map,
                                     licenses_per_package_map=licenses_per_package_map,
                                     sca_details=sca_details,
                                     report_type=report_type,
                                     scan_data_format=ScanDataFormat.DEPENDENCY_TREE,
                                     dependencies=dependencies,
                                     inline_suppressions_maps=inline_suppressions_maps,
                                     file_line_range=file_line_range,
                                     used_private_registry=used_private_registry)


def _get_request_input(packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"name": package.get("name", ""), "version": package.get("version", ""),
         "lang": normalize_twistcli_language(package.get("type", ""))}
        for package in packages
    ]


def get_license_statuses(packages: list[dict[str, Any]]) -> list[_LicenseStatus]:
    requests_input = _get_request_input(packages)
    if not requests_input:
        return []
    try:
        response = request_wrapper(
            method="POST",
            url=f"{bc_integration.api_url}/api/v1/vulnerabilities/packages/get-licenses-violations",
            headers=bc_integration.get_default_headers("POST"),
            json={"packages": requests_input},
            should_call_raise_for_status=True
        )
        response_json = response.json()
        license_statuses: list[_LicenseStatus] = _extract_license_statuses(response_json)
        return license_statuses
    except Exception:
        error_message = (
            "failing when trying to get licenses-violations. it is apparently some unexpected "
            "connection issue. please try later. in case it keep happening. please report."
        )
        logging.info(error_message, exc_info=True)

    return []


async def get_license_statuses_async(packages: list[dict[str, Any]], image_name: str) -> _ImageReferencerLicenseStatus:
    """
    This is an async implementation of `get_license_statuses`. The only change is we're getting a session
    as an input, and the asyncio behavior is managed in the calling method.
    """
    requests_input = _get_request_input(packages)
    url = f"{bc_integration.api_url}/api/v1/vulnerabilities/packages/get-licenses-violations"
    if not requests_input:
        return {'image_name': image_name, 'licenses': []}
    try:
        response = await aiohttp_client_session_wrapper("POST", url,
                                                        headers=bc_integration.get_default_headers("POST"),
                                                        payload={"packages": requests_input})
        response_json = await response.json()

        license_statuses = _extract_license_statuses(response_json)
        return {'image_name': image_name, 'licenses': license_statuses}
    except Exception as e:
        error_message = (
            "failing when trying to get licenses-violations. it is apparently some unexpected "
            "connection issue. please try later. in case it keeps happening, please report."
            f"Error: {str(e)}"
        )
        logging.info(error_message, exc_info=True)

        return {'image_name': image_name, 'licenses': []}


def _extract_license_statuses(response_json: dict[str, list[dict[str, str]]]) -> list[_LicenseStatus]:
    license_statuses: list[_LicenseStatus] = [
        {
            "package_name": license_violation.get("name", ""),
            "package_version": license_violation.get("version", ""),
            "policy": license_violation.get("policy", "BC_LIC1"),
            "license": license_violation.get("license", ""),
            "status": license_violation.get("status", "COMPLIANT")
        }
        for license_violation in response_json.get("violations", [])
    ]
    return license_statuses
