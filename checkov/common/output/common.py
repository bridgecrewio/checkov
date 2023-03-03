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
        licenses_str = licenses_str[1:-1] if licenses_str.startswith('"') and licenses_str.endswith('"') else licenses_str
        license_lst = licenses_str.split('","')

        return license_lst
    else:
        return []


def compare_table_items_severity(table_item: dict[str, str]) -> int:
    severity = (table_item.get("severity") or DEFAULT_SEVERITY).upper()
    return Severities[severity].level
