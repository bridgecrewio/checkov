import os
from typing import List
from checkov.common.runners.base_runner import strtobool

PATH_SEPARATOR = "->"


def unify_dependency_path(dependency_path: List[str]) -> str:
    if not dependency_path:
        return ''
    if strtobool(os.getenv('CHECKOV_ENABLE_NESTED_MODULES', 'False')):
        return dependency_path[-1]
    return PATH_SEPARATOR.join(dependency_path)
