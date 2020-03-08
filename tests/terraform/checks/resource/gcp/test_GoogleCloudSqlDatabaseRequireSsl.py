import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudSqlDatabaseRequireSsl import check
from checkov.common.models.enums import CheckResult


class GoogleCloudSqlDatabaseRequireSsl(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster'], 'monitoring_service': ['none']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'settings': [{'tier': ['1'], 'ip_configuration': [{'require_ssl': [True]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
