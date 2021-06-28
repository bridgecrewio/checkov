import os
import re
from typing import Tuple, List

MODULE_DEPENDENCY_PATTERN_IN_PATH = r"\[.+\#.+\]"


def is_local_path(root_dir: str, source: str) -> bool:
    # https://www.terraform.io/docs/modules/sources.html#local-paths
    return (
        source.startswith("./")
        or source.startswith("/./")
        or source.startswith("../")
        or source in os.listdir(root_dir)
    )


def remove_module_dependency_in_path(path: str) -> Tuple[str, str, str]:
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: separated path from module dependency: dir/main.tf, other_dir/x.tf
    """
    module_dependency = re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path)
    if re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path):
        path = re.sub(MODULE_DEPENDENCY_PATTERN_IN_PATH, "", path)
    module_and_num = extract_module_dependency_path(module_dependency)
    return path, module_and_num[0], module_and_num[1]


def extract_module_dependency_path(module_dependency: List[str]) -> List[str]:
    """
    :param module_dependency: a list looking like ['[path_to_module.tf#0]']
    :return: the path without enclosing array and index: 'path_to_module.tf'
    """
    if not module_dependency:
        return ["", ""]
    if isinstance(module_dependency, list) and len(module_dependency) > 0:
        module_dependency = module_dependency[0]
    return module_dependency[1:-1].split("#")
