class RunnerFilter(object):
    framework = 'all'
    checks = []
    skip_checks = []
    external_check_ids = set()

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

    def notify_external_check(self, check_id):
        self.external_check_ids.add(check_id)

    def should_run_check(self, check_id):
        if check_id in self.external_check_ids:
            pass        # enabled unless skipped
        elif self.checks:
            if check_id in self.checks:
                return True
            else:
                return False
        if self.skip_checks and check_id in self.skip_checks:
            return False
        return True
