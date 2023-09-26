from typing import List

PATH_SEPARATOR = "->"


def unify_dependency_path(dependency_path: List[str]) -> str:
    if not dependency_path:
        return ''
    return dependency_path[-1]
