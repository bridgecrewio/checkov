from __future__ import annotations

import logging
from typing import List, Optional, Any, cast

from checkov.common.output.common import SCADetails

UNFIXABLE_VERSION = "N/A"
OPEN_STATUS = "open"

TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION = {
    "gem": "ruby",
    "nuget": "dotNet"
}


def get_file_path_for_record(rootless_file_path: str) -> str:
    return f"/{rootless_file_path}"


def get_resource_for_record(rootless_file_path: str, package_name: str) -> str:
    return f"{rootless_file_path}.{package_name}"


def get_package_alias(package_name: str, package_version: str) -> str:
    return f"{package_name}@{package_version}"


def get_license_policy_and_package_alias(policy: str, package_name: str) -> str:
    return f'{policy}_{package_name}'


def get_package_type(package_name: str, package_version: str, sca_details: SCADetails | None = None) -> str:
    if sca_details:
        return str(sca_details.package_types.get(f"{package_name}@{package_version}", ""))
    else:
        return ""


def get_registry_url(package: dict[str, Any]) -> str:
    if "registry" in package:
        return cast("str", package.get("registry", ""))
    return cast("str", package.get("registryUrl", ""))


def normalize_twistcli_language(language: str) -> str:
    """
    part of the language names that are returned by twistcli may be a little differ from those we use in checkov.
    this function's goal is to normalize them
    """
    return TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION.get(language, language)


def get_package_lines(package: dict[str, Any]) -> list[int] | None:
    return cast("list[int] | None", package.get("linesNumbers", package.get("lines")))


def get_record_file_line_range(package: dict[str, Any], file_line_range: list[int] | None) -> list[int]:
    """
    Currently, there are 2 way for getting file_line_range for the sca-report:
    1. by the arg 'file_line_range' which comes from the runner - this is specific for entire file (e.g: image referencer)
    2. by a dedicated attribute in a package-object - (e.g: DT-cli V2)
    The purpose of this function is making sure there are no conflicts between those resources, and return a valid rage
    """
    package_line_range = get_package_lines(package)
    if package_line_range and file_line_range:
        logging.error(
            '[get_record_file_line_range] Both \'package_line_range\' and \'file_line_range\' are not None. Conflict.')
    return package_line_range or file_line_range or [0, 0]


def should_run_scan(runner_filter_checks: Optional[List[str]]) -> bool:
    return not (runner_filter_checks and all(
        not (check.startswith("CKV_CVE") or check.startswith("BC_CVE") or check.startswith("BC_LIC")) for check in
        runner_filter_checks))


def get_fix_version(vulnerability_details: dict[str, Any]) -> str:
    if "fix_version" in vulnerability_details:
        return str(vulnerability_details["fix_version"])

    if "lowest_fixed_version" in vulnerability_details:
        return str(vulnerability_details["lowest_fixed_version"])

    return UNFIXABLE_VERSION
