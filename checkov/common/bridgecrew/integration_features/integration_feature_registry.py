

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

    def run_post_scan(self, scan_reports):
        for integration in self.features:
            if integration.is_valid():
                integration.post_scan(scan_reports)


integration_feature_registry = IntegrationFeatureRegistry()
