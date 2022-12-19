import unittest

from checkov.terraform.checks.resource.gcp.GoogleBigQueryDatasetPublicACL import check
from checkov.common.models.enums import CheckResult


class TestBigQueryDatasetPublicACL(unittest.TestCase):

    def test_failure_special_group(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["READER"], "special_group": ["allAuthenticatedUsers"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_all_users(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["VIEWER"], "special_group": ["projectReaders"]},
                                    {"role": ["READER"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_special_group(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["READER"], "special_group": ["projectReaders"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_user_by_email(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["EDITOR"], "user_by_email": ["foo@bar.com"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_group_by_email(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["EDITOR"], "group_by_email": ["foo-team@bar.com"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_domain(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["EDITOR"], "domain": ["example.com"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_view(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["EDITOR"], "view": ["example-view-id"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_routine(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["EDITOR"], "routine": ["example-routine-id"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_dataset(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"dataset": {"dataset": {"datasetId": "foo","projectId": "bar"},"targetTypes": ["VIEWS"]}}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_iam_member(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["READER"], "iam_member": ["deleted:serviceAccount:foo@bar.iam.gserviceaccount.com?uid=1234567890"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_unknown_key_to_be_added_in_the_future(self):
        resource_conf = {"dataset_id": ["example_dataset"],
                         "friendly_name": ["test"],
                         "description": ["This is a test description"],
                         "location": ["EU"],
                         "default_table_expiration_ms": [3600000],
                         "access": [{"role": ["READER"], "unknown_key": ["unknown_value"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
