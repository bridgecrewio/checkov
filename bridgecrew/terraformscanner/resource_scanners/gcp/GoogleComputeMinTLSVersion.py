from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class GoogleComputeMinTLSVersion(ResourceScanner):
    def __init__(self):
        name = "Ensure Google SSL policy minimal TLS version is TLS_1_2"
        scan_id = "BC_GCP_SSL_1"
        supported_resources = ['google_compute_ssl_policy']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <ScanResult>
        """
        if 'min_tls_version' in conf.keys():
            if conf['min_tls_version'][0] == "TLS_1_2":
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = GoogleComputeMinTLSVersion()
