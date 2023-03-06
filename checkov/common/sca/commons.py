from __future__ import annotations

from typing import List, Optional

from checkov.common.output.common import SCADetails

UNFIXABLE_VERSION = "N/A"

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


def get_package_type(package_name: str, package_version: str, sca_details: SCADetails | None = None) -> str:
    if sca_details:
        return str(sca_details.package_types.get(f"{package_name}@{package_version}", ""))
    else:
        return ""


def normalize_twistcli_language(language: str) -> str:
    """
    part of the language names that are returned by twistcli may be a little differ from those we use in checkov.
    this function's goal is to normalize them
    """
    return TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION.get(language, language)


def should_run_scan(runner_filter_checks: Optional[List[str]]) -> bool:
    return not (runner_filter_checks and all(not (check.startswith("CKV_CVE") or check.startswith("BC_CVE") or check.startswith("BC_LIC")) for check in runner_filter_checks))
