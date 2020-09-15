
class RunnerFilter(object):
    # NOTE: This needs to be static because different filters may be used at load time versus runtime
    #       (see note in BaseCheckRegistery.register). The concept of which checks are external is
    #       logically a "static" concept anyway, so this makes logical sense.
    __EXTERNAL_CHECK_IDS = set()

    def __init__(self, framework='all', checks=None, skip_checks=None):
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
        self.framework = framework

    def should_run_check(self, check_id):
        if RunnerFilter.is_external_check(check_id):
            pass        # enabled unless skipped
        elif self.checks:
            if check_id in self.checks:
                return True
            else:
                return False
        if self.skip_checks and check_id in self.skip_checks:
            return False
        return True

    @staticmethod
    def notify_external_check(check_id):
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id):
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
