from __future__ import annotations

from typing import List, Optional, Any

from checkov.common.output.common import SCADetails
from checkov.common.packaging import version as packaging_version

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


def get_registry_url(package: dict[str, Any]) -> str:
    if "registry" in package:
        return package.get("registry", "")
    return package.get("registryUrl", "")


def normalize_twistcli_language(language: str) -> str:
    """
    part of the language names that are returned by twistcli may be a little differ from those we use in checkov.
    this function's goal is to normalize them
    """
    return TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION.get(language, language)


def should_run_scan(runner_filter_checks: Optional[List[str]]) -> bool:
    return not (runner_filter_checks and all(not (check.startswith("CKV_CVE") or check.startswith("BC_CVE") or check.startswith("BC_LIC")) for check in runner_filter_checks))


def get_lowest_fix_version(vulnerability_details: dict[str, Any]) -> str:
    if "cveStatus" in vulnerability_details:
        return str(vulnerability_details["cveStatus"])

    lowest_fixed_version = UNFIXABLE_VERSION
    package_version = vulnerability_details["package_version"]
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

    return lowest_fixed_version
