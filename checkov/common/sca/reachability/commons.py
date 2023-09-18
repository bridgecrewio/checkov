from typing import Dict, List, Any


def add_package_aliases(package_aliases_map: Dict[str, Any], language: str, repository_name: str,
                        file_relative_path: str, package_name: str, package_aliases: List[str]) -> None:
    package_aliases_for_file = package_aliases_map.setdefault(language, {"repositories": dict()})["repositories"]\
        .setdefault(repository_name, {"files": dict()})["files"].setdefault(file_relative_path, {"packageAliases": dict()})["packageAliases"]
    if package_name in package_aliases_for_file:
        raise Exception(f"aliases for \'{package_name}\' in the file \'{file_relative_path}\' in the repository "
                        f"\'{repository_name}\' already were set")
    package_aliases_for_file[package_name] = {"packageAliases": package_aliases}
