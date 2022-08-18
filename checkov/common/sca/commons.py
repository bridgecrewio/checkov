from __future__ import annotations
from checkov.common.output.common import ImageDetails

UNFIXABLE_VERSION = "N/A"

TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION = {
    "gem": "ruby"
}

def get_file_path_for_record(rootless_file_path: str) -> str:
    return f"/{rootless_file_path}"


def get_resource_for_record(rootless_file_path: str, package_name: str) -> str:
    return f"{rootless_file_path}.{package_name}"


def get_package_alias(package_name: str, package_version: str) -> str:
    return f"{package_name}@{package_version}"


def get_package_type(package_name: str, package_version: str, image_details: ImageDetails | None = None) -> str:
    if image_details:
        return str(image_details.package_types.get(f"{package_name}@{package_version}", ""))
    else:
        return ""


def normalize_twistcli_language(language: str) -> str:
    """
    part of the language names that are returned by twistcli may be a little differ from those we use in checkov.
    this function's goal is to normalize them
    """
    return TWISTCLI_TO_CHECKOV_LANG_NORMALIZATION.get(language, language)
