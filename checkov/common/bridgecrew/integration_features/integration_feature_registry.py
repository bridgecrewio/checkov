

class IntegrationFeatureRegistry:

    def __init__(self) -> None:
        self.features = []

    def register(self, integration_feature) -> None:
        self.features.append(integration_feature)
        self.features.sort(key=lambda f: f.order)

    def run_pre_scan(self) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_scan()

    def run_pre_runner(self) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_runner()

    def run_post_runner(self, scan_reports) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.post_runner(scan_reports)


integration_feature_registry = IntegrationFeatureRegistry()
