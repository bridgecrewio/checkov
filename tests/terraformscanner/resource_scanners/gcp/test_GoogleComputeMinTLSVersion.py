import unittest

from checkov.terraform.models.enums import ScanResult
from checkov.terraform.checks.resource.gcp.GoogleComputeMinTLSVersion import scanner


class TestGoogleComputeMinTLSVersion(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'name': ['nonprod-ssl-policy'], 'profile': ['MODERN']
                          }

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf = {'name': ['nonprod-ssl-policy'], 'profile': ['MODERN'], 'min_tls_version': ['TLS_1_2']}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
