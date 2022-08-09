def get_file_path_for_record(rootless_file_path: str) -> str:
    return f"/{rootless_file_path}"


def get_resource_for_record(rootless_file_path: str, package_name: str) -> str:
    return f"{rootless_file_path}.{package_name}"


def get_package_alias(package_name: str, package_version: str) -> str:
    return f'{package_name}@{package_version}'
