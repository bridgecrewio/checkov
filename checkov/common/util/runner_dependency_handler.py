import logging

from checkov.common.runners.runner_registry import RunnerRegistry

logger = logging.getLogger(__name__)


class RunnerDependencyHandler():
    """
    Scan runners for system dependencies, disable runners with failed deps
    """
    def __init__(self, runner_registry: RunnerRegistry):
        """
        RunnerDependencyHandler
        :param runner_registry: a populated runner registry
        """
        self.runner_registry = runner_registry

    def validate_runner_deps(self):
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
            try:
                runner.system_deps
            except Exception:
                logging.debug(f"{runner.check_type}_runner declares no system dependency checks required.")
                continue

            if runner.system_deps:
                result = runner.check_system_deps()
                if result is not None:
                    runner_names.append(result)
                    runners_with_unmatched_deps.append(runner)
        
        if runners_with_unmatched_deps:
            logging.info(f"The following frameworks will automatically be disabled due to missing system dependencies: {','.join(runner_names)}")
            for runner in runners_with_unmatched_deps:
                self.runner_registry.remove_runner(runner)
