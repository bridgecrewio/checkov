class RunnerFilter(object):
    framework = 'all'
    checks = []
    skip_checks = []

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
