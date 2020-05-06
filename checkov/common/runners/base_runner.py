from abc import ABC, abstractmethod

from checkov.runner_filter import RunnerFilter


class BaseRunner(ABC):
    check_type = ""

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter()):
        pass
