import unittest

from checkov.terraform.checks.resource.gcp.GoogleContainerClusterClientCertificateEnabled import check
from checkov.terraform.models.enums import CheckResult


class GoogleContainerClusterClientCertificateEnabled(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster'], 'master_auth': [{'client_certificate_config': [{'issue_client_certificate': [False]}]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'master_auth': [{'client_certificate_config': [{'issue_client_certificate': [True]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
