from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

if TYPE_CHECKING:
    from checkov.common.runners.runner_registry import RunnerRegistry

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


class RunnerDependencyHandler():
    """
    Scan runners for system dependencies, disable runners with failed deps
    """
    def __init__(self, runner_registry: RunnerRegistry) -> None:
        """
        RunnerDependencyHandler
        :param runner_registry: a populated runner registry
        """
        self.runner_registry = runner_registry

    def validate_runner_deps(self) -> None:
        """
        Checks if each runner declares any system dependancies by calling each runner's system_deps() function.
        This function can safley not exist, but if returns true, call check_system_deps() on the same function.
        The function would impliment it's own dependancy checks (see helm/runner.py for example).
        Sucessful check_system_deps() should return None, otherwise self.check_type to indicate a runner has failed deps.

        THen removes any runners with missing dependencies from runner_registry.
        """
        runners_with_unmatched_deps = []
        runner_names = []
        for runner in self.runner_registry.runners:
            system_deps = getattr(runner, 'system_deps', None)
            if system_deps:
                check_system_deps = getattr(runner, 'check_system_deps', None)
                if check_system_deps is not None:
                    result = check_system_deps()
                    if result is not None:
                        runner_names.append(result)
                        runners_with_unmatched_deps.append(runner)
            else:
                logging.debug(f"{runner.check_type}_runner declares no system dependency checks required.")
                continue

        if runners_with_unmatched_deps:
            logging.info(f"The following frameworks will automatically be disabled due to missing system dependencies: {','.join(runner_names)}")
            for runner in runners_with_unmatched_deps:
                self.runner_registry.remove_runner(runner)
