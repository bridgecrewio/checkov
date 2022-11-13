from __future__ import annotations

from dataclasses import dataclass, field


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

def fotmat_licenses_to_string(licenses_lst:list[str]) -> str:
    if licenses_lst and len(licenses_lst) > 0:
        # in case we have a quote inside the license, then we need to escape it,
        # in CSV the escape is 2 double quotes
        # for license in licenses_lst:
        #   license = license.replace(r'"', r'"""')

        joined_str = '","'.join(licenses_lst)
        return f'"{joined_str}"'
    else:
        return 'Unknown'

def format_string_to_licenses(licenses_str: str) -> list[str]:
    if licenses_str == 'Unknown':
        return [licenses_str]
    elif licenses_str and len(licenses_str) > 0:
        print('licenses_str to convert:', licenses_str)
        # remove first and last quotes
        licenses_str = licenses_str[1:-1]
        license_lst = licenses_str.split('","')

        print('licenses_str to convert res:', license_lst)
        return license_lst
    else:
        return []
