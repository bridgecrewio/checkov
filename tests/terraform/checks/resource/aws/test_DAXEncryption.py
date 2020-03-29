import unittest

from checkov.terraform.checks.resource.aws.DAXEncryption import check
from checkov.common.models.enums import CheckResult


class TestDAXEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {
		'cluster_name': ['myDAXcluster']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf =  {	'cluster_name': ['myDAXcluster'],
		'server_side_encryption':{'enabled': [True]}}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
