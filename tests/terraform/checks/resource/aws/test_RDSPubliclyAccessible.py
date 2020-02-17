

import unittest

from checkov.terraform.checks.resource.aws.RDSPubliclyAccessible import check
from checkov.common.models.enums import CheckResult


class TestRDSPubliclyAccessible(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'engine': ['postgres'], 'engine_version': ['9.6.3'], 'multi_az': [False], 'backup_retention_period': [10], 'auto_minor_version_upgrade': [True], 'storage_encrypted': [False],'publicly_accessible':[True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf =  {'engine': ['postgres'], 'engine_version': ['9.6.3'], 'multi_az': [False], 'backup_retention_period': [10], 'auto_minor_version_upgrade': [True], 'storage_encrypted': [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
