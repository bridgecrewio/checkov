class RunnerFilter(object):
    framework = 'all'
    checks = []

    def __init__(self, framework='all', checks=None):
        if checks is None:
            checks = []
        if isinstance(checks,str):
            self.checks = checks.split(",")
        else:
            self.checks = checks
        self.framework = framework
