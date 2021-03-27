import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleBigQueryDatasetPublicACL import check


class TestBigQueryDatasetPublicACL(unittest.TestCase):
    def test_failure_special_group(self):
        resource_conf = {
            "dataset_id": ["example_dataset"],
            "friendly_name": ["test"],
            "description": ["This is a test description"],
            "location": ["EU"],
            "default_table_expiration_ms": [3600000],
            "access": [
                {"role": ["READER"], "special_group": ["allAuthenticatedUsers"]}
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_all_users(self):
        resource_conf = {
            "dataset_id": ["example_dataset"],
            "friendly_name": ["test"],
            "description": ["This is a test description"],
            "location": ["EU"],
            "default_table_expiration_ms": [3600000],
            "access": [
                {"role": ["VIEWER"], "special_group": ["projectReaders"]},
                {"role": ["READER"]},
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_special_group(self):
        resource_conf = {
            "dataset_id": ["example_dataset"],
            "friendly_name": ["test"],
            "description": ["This is a test description"],
            "location": ["EU"],
            "default_table_expiration_ms": [3600000],
            "access": [{"role": ["READER"], "special_group": ["projectReaders"]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        resource_conf = {
            "dataset_id": ["example_dataset"],
            "friendly_name": ["test"],
            "description": ["This is a test description"],
            "location": ["EU"],
            "default_table_expiration_ms": [3600000],
            "access": [{"role": ["EDITOR"], "user_by_email": ["foo@bar.com"]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
