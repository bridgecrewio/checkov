from typing import List

PATH_SEPARATOR = "->"


def unify_dependency_path(dependency_path: List[str]) -> str:
    return PATH_SEPARATOR.join(dependency_path)
