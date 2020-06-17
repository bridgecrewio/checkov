import os

from abc import ABC, abstractmethod

from checkov.runner_filter import RunnerFilter

IGNORED_DIRECTORIES_ENV = os.getenv('IGNORED_DIRECTORIES',"node_modules,.terraform,.serverless")

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")

class BaseRunner(ABC):
    check_type = ""

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
        pass
