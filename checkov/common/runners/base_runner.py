import os
from abc import ABC, abstractmethod

from checkov.runner_filter import RunnerFilter

IGNORED_DIRECTORIES_ENV = os.getenv('CKV_IGNORED_DIRECTORIES', "node_modules,.terraform,.serverless")

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")


class BaseRunner(ABC):
    check_type = ""

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
        pass


def filter_ignored_directories(d_names):
    [d_names.remove(d) for d in list(d_names) if d in ignored_directories]
