import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.scanners.AdminPolicyDocument import AdminPolicyDocument


class TestAdminPolicyDocument(unittest.TestCase):

    def test_success(self):
        scanner = AdminPolicyDocument()
        resource_conf = {
            "statement": {
                "actions": ["Describe*"],
                "resources": ["arn:aws:s3:::my_corporate_bucket/*"]
            }
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

    def test_failure(self):
        scanner = AdminPolicyDocument()
        resource_conf = {
            "statement": {
                "actions": ["*"],
                "resources": ["*"]
            }
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)



if __name__ == '__main__':
    unittest.main()
