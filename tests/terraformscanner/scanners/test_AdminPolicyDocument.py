import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.AdminPolicyDocument import scanner


class TestAdminPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {
            "statement": {
                "actions": ["Describe*"],
                "resources": ["arn:aws:s3:::my_corporate_bucket/*"]
            }
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

    def test_failure(self):
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
