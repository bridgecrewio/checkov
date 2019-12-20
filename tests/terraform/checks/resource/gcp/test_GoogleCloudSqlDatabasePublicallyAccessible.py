import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudSqlDatabasePublicallyAccessible import check
from checkov.terraform.models.enums import CheckResult


class GoogleCloudSqlDatabasePublicallyAccessible(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'settings': [{'tier': ['db-f1-micro'], 'ip_configuration': [{'ipv4_enabled': True, 'authorized_networks': [ [ {'name': 'net1', 'value': '10.0.0.0/16'}, {'name': 'net1', 'value': '0.0.0.0/0'} ] ]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'settings': [{'tier': ['db-f1-micro'], 'ip_configuration': [{'ipv4_enabled': True, 'authorized_networks': [ [ {'name': 'net1', 'value': '10.0.0.0/16'}, {'name': 'net1', 'value': '10.10.0.0/16'} ] ]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
