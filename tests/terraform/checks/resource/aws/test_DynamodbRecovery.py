import unittest

from checkov.terraform.checks.resource.aws.DynamodbRecovery import check
from checkov.common.models.enums import CheckResult


class TestDynamodbRecovery(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["violations_for_resources${var.unique_tag}"],
            "billing_mode": ["PAY_PER_REQUEST"],
            "hash_key": ["id"],
            "range_key": ["violation_id"],
            "local_secondary_index": [
                {"name": ["violation_id_index"], "projection_type": ["ALL"], "range_key": ["violation_id"]}
            ],
            "global_secondary_index": [
                {
                    "hash_key": ["violation_id"],
                    "name": ["violation_id-aws_account_id-index"],
                    "range_key": ["aws_account_id"],
                    "projection_type": ["ALL"],
                }
            ],
            "attribute": [
                {"name": ["id"], "type": ["S"]},
                {"name": ["violation_id"], "type": ["S"]},
                {"name": ["aws_account_id"], "type": ["S"]},
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["violations_for_resources${var.unique_tag}"],
            "billing_mode": ["PAY_PER_REQUEST"],
            "hash_key": ["id"],
            "range_key": ["violation_id"],
            "local_secondary_index": [
                {"name": ["violation_id_index"], "projection_type": ["ALL"], "range_key": ["violation_id"]}
            ],
            "global_secondary_index": [
                {
                    "hash_key": ["violation_id"],
                    "name": ["violation_id-aws_account_id-index"],
                    "range_key": ["aws_account_id"],
                    "projection_type": ["ALL"],
                }
            ],
            "attribute": [
                {"name": ["id"], "type": ["S"]},
                {"name": ["violation_id"], "type": ["S"]},
                {"name": ["aws_account_id"], "type": ["S"]},
            ],
            "point_in_time_recovery": [{"enabled": [True]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
