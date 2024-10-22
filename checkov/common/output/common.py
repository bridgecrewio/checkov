from __future__ import annotations

from dataclasses import dataclass, field

from checkov.common.bridgecrew.severities import Severities
from checkov.common.output.record import DEFAULT_SEVERITY

UNKNOWN_LICENSE = 'Unknown'


@dataclass
class SCADetails:
    package_types: dict[str, str] = field(default_factory=dict)


@dataclass
class ImageDetails(SCADetails):
    distro: str = ''
    distro_release: str = ''
    image_id: str = ''
    name: str | None = ''
    related_resource_id: str | None = ''


def is_raw_formatted(licenses: str) -> bool:
    return '","' in licenses


def format_licenses_to_string(licenses_lst: list[str]) -> str:
    if isinstance(licenses_lst, list):
        if len(licenses_lst) > 1:
            joined_str = '","'.join(licenses_lst)
            return f'"{joined_str}"'
        elif licenses_lst:
            return licenses_lst[0]
    return UNKNOWN_LICENSE


def format_string_to_licenses(licenses_str: str) -> list[str]:
    if licenses_str == UNKNOWN_LICENSE:
        return [licenses_str]
    elif licenses_str:
        # remove first and last quotes
        licenses_str = licenses_str[1:-1] if licenses_str.startswith('"') and licenses_str.endswith(
            '"') else licenses_str
        license_lst = licenses_str.split('","')

        return license_lst
    else:
        return []


def compare_table_items_severity(table_item: dict[str, str]) -> int:
    severity = (table_item.get("severity") or DEFAULT_SEVERITY).upper()
    return Severities[severity].level


def validate_lines(lines: list[int] | None) -> list[int] | None:
    if lines and lines[0] > 0 and lines[1] > 0:
        return lines
    return None


def get_package_name_with_lines(package_name: str, lines: list[int] | None) -> str:
    if lines and validate_lines(lines):
        return f"{package_name} [{lines[0]}-{lines[1]}]"
    return package_name


def get_reachability_output_indication(cve_reachability_risk_factors: dict[str, bool]) -> str:
    if cve_reachability_risk_factors.get("ReachableFunction"):
        return "Reachable Function"
    if cve_reachability_risk_factors.get("IsUsed"):
        return "Package Used"
    return ""
