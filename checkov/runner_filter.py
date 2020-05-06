class RunnerFilter(object):
    framework = 'all'
    checks = []

    def __init__(self, framework='all', checks=None):
        if checks is None:
            checks = []
        self.framework = framework
        self.checks = checks
