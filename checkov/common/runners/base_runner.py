import os
import re
from abc import ABC, abstractmethod

from checkov.runner_filter import RunnerFilter

IGNORED_DIRECTORIES_ENV = os.getenv('CKV_IGNORED_DIRECTORIES', "node_modules,.terraform,.serverless")
EXCLUDED_PATHS_REGEXP = os.getenv('CKV_EXCLUDED_PATHS_REGEXP', "") + ","

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")
excluded_paths_regex = [re.compile(e) for e in EXCLUDED_PATHS_REGEXP.split(",")]


class BaseRunner(ABC):
    check_type = ""

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        pass


def filter_ignored_directories(d_names):
    [d_names.remove(d) for d in list(d_names) if d in ignored_directories or d.startswith(".")
     or any(re.match(exp, d) for exp in excluded_paths_regex)]
