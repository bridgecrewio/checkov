import logging

logger = logging.getLogger(__name__)


class RunnerDependencyHandler():
    """
    Scan runners for system dependencies, disable runners with failed deps via main.py/run()
    """
    checkov_frameworks_unmatched_deps = []
    checkov_runner_module_names = ""
    calledGlobals = {}

    def __init__(self, checkov_runner_module_names: list, calledGlobals: dict):
        """
        RunnerDependencyHandler
        :param checkov_runner_module_names: list of runner module names to check
        :param calledGlobals: The main-scoped dict output of globals(), so we can access the registered runners.
        """
        self.checkov_runner_module_names = checkov_runner_module_names
        self.calledGlobals = calledGlobals

    def validate_runner_deps(self):
        """
        Checks if each runner declares any system dependancies by calling each runner's system_deps() function.
        This function can safley not exist, but if returns true, call check_system_deps() on the same function.
        The function would impliment it's own dependancy checks (see helm/runner.py for example).
        Sucessful check_system_deps() should return None, otherwise self.check_type to indicate a runner has failed deps.
        Failed dep check runners are added to the checkov_frameworks_unmatched_deps list, to be filtered out in main.py/run()

        :param checkov_runner_module_names: A list of runners as module names to check for deps
        :return: A list of runners which have failed deps, listed as the runners self.check_type.
        """
        for runner in self.checkov_runner_module_names:
            try:
                self.calledGlobals[f"{runner}_runner"]().system_deps
            except:
                logging.debug(f"{runner}_runner declares no system dependency checks required.")
                continue

            if self.calledGlobals[f"{runner}_runner"]().system_deps:
                    result = self.calledGlobals[f"{runner}_runner"]().check_system_deps()
                    if result is not None:
                        self.checkov_frameworks_unmatched_deps.append(result)
        
        if self.checkov_frameworks_unmatched_deps:
            logging.info(f"The following frameworks will automatically be disabled due to missing system dependencies: {','.join(self.checkov_frameworks_unmatched_deps)}")


    def disable_incompatible_runners(self, skip_framework):
        """
        Modifies the skip_framework argument to ensure any runners failing dependency checks are excluded.

        :param skip_framrwork: from args.skip_framework checkov arguments
        :return: a replacement args.skip_frameworks
        """

        if self.checkov_frameworks_unmatched_deps:
            if skip_framework is None:
                skip_framework = ",".join(self.checkov_frameworks_unmatched_deps)
            else:
                skip_framework = f"{skip_framework},{','.join(self.checkov_frameworks_unmatched_deps)}"

        return skip_framework