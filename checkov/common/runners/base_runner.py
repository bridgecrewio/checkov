import os
import re
from abc import ABC, abstractmethod
from typing import List

from checkov.runner_filter import RunnerFilter

IGNORED_DIRECTORIES_ENV = os.getenv('CKV_IGNORED_DIRECTORIES', "node_modules,.terraform,.serverless")

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")


class BaseRunner(ABC):
    check_type = ""

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        pass


def filter_ignored_directories(root_dir, d_names, excluded_paths: List[str]):
    # we need to handle legacy logic, where directories to skip could be specified using the env var (default value above)
    # or a directory starting with '.'; these look only at directory basenames, not relative paths.
    # But then any other excluded paths (specified via --skip-path or via the platform repo settings) should look at
    # the directory name relative to the root folder.
    # Example: take the following dir tree:
    # .
    #   ./dir1
    #      ./dir1/dir33
    #      ./dir1/.terraform
    #   ./dir2
    #      ./dir2/dir33
    #
    # if excluded_paths = ['dir1/dir33'], then we would scan dir1, but we would skip its subdirectories. We would scan
    # dir2 and its subdirectory.

    # first handle the legacy logic
    [d_names.remove(dir) for dir in list(d_names) if dir in ignored_directories or dir.startswith(".")]

    # now apply the new logic
    if excluded_paths:
        compiled = [re.compile(p) for p in excluded_paths]
        [d_names.remove(dir) for dir in list(d_names) if any(pattern.search(os.path.join(root_dir, dir)) for pattern in compiled)]

