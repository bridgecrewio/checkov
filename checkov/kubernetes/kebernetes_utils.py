import logging
import os
from typing import Tuple, Dict, Optional, List

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.parsers.node import DictNode
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.kubernetes.parser.parser import parse

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


def get_folder_definitions(
        root_folder: str, excluded_paths: Optional[List[str]]
) -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    files_list = []
    filepath_fn = lambda f: f'/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}'
    for root, d_names, f_names in os.walk(root_folder):
        filter_ignored_paths(root, d_names, excluded_paths)
        filter_ignored_paths(root, f_names, excluded_paths)

        for file in f_names:
            file_ending = os.path.splitext(file)[1]
            if file_ending in K8_POSSIBLE_ENDINGS:
                full_path = os.path.join(root, file)
                if "/." not in full_path and file not in ['package.json', 'package-lock.json']:
                    # skip temp directories
                    files_list.append(full_path)
    return get_files_definitions(files_list, filepath_fn)


def get_files_definitions(files: List[str], filepath_fn=None) \
        -> Tuple[Dict[str, DictNode], Dict[str, List[Tuple[int, str]]]]:
    def _parse_file(filename):
        try:
            return filename, parse(filename)
        except (TypeError, ValueError) as e:
            logging.warning(f"Kubernetes skipping {filename} as it is not a valid Kubernetes template\n{e}")

    definitions = {}
    definitions_raw = {}
    results = parallel_runner.run_function(_parse_file, files)
    for result in results:
        if result:
            (file, parse_result) = result
            if parse_result:
                path = filepath_fn(file) if filepath_fn else file
                (definitions[path], definitions_raw[path]) = parse_result
    return definitions, definitions_raw
