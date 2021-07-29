

class IntegrationFeatureRegistry:

    def __init__(self):
        self.features = []

    def register(self, integration_feature):
        self.features.append(integration_feature)
        self.features.sort(key=lambda f: f.order)

    def run_pre_scan(self):
        for integration in self.features:
            if integration.is_valid():
                integration.pre_scan()

    def run_pre_runner(self):
        for integration in self.features:
            if integration.is_valid():
                integration.pre_runner()

    def run_post_runner(self, scan_reports):
        for integration in self.features:
            if integration.is_valid():
                integration.post_runner(scan_reports)


integration_feature_registry = IntegrationFeatureRegistry()
