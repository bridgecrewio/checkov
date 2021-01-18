import logging
import fnmatch
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR


class RunnerFilter(object):
    # NOTE: This needs to be static because different filters may be used at load time versus runtime
    #       (see note in BaseCheckRegistery.register). The concept of which checks are external is
    #       logically a "static" concept anyway, so this makes logical sense.
    __EXTERNAL_CHECK_IDS = set()

    def __init__(self, framework='all', checks=None, skip_checks=None, download_external_modules=False, external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR, evaluate_variables=True, runners=None, skip_framework=None):
        if checks is None:
            checks = []
        if isinstance(checks, str):
            self.checks = checks.split(",")
        else:
            self.checks = checks

        if skip_checks is None:
            skip_checks = []
        if isinstance(skip_checks, str):
            self.skip_checks = skip_checks.split(",")
        else:
            self.skip_checks = skip_checks

        if skip_framework is None:
            self.framework = framework
        else:
            if isinstance(skip_framework, str):
                if framework == "all":
                    selected_frameworks = list(set(runners) - set(skip_framework.split(",")))
                    self.framework = ','.join(selected_frameworks)
                else:
                    selected_frameworks = list(set(framework.split(",")) - set(skip_framework.split(",")))
                    self.framework = ','.join(selected_frameworks)
        logging.info(f'Resultant set of frameworks (removing skipped frameworks): {self.framework}')

        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.evaluate_variables = evaluate_variables

    def should_run_check(self, check_id):
        if RunnerFilter.is_external_check(check_id):
            pass        # enabled unless skipped
        elif self.checks:
            if check_id in self.checks:
                return True
            else:
                return False
        if self.skip_checks and any(fnmatch.fnmatch(check_id, pattern) for pattern in self.skip_checks):
            return False
        return True

    @staticmethod
    def notify_external_check(check_id):
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id):
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
