import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DAXEncryption import check


class TestDAXEncryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "cluster_name": "${var.cluster_name}",
            "iam_role_arn": "${var.iam_role_arn}",
            "parameter_group_name": "${aws_dax_parameter_group.example.name}",
            "subnet_group_name": "${aws_dax_subnet_group.example.name}",
            "tags": "${var.common_tags}",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "cluster_name": "${var.cluster_name}",
            "iam_role_arn": "${var.iam_role_arn}",
            "parameter_group_name": "${aws_dax_parameter_group.example.name}",
            "server_side_encryption": [{"enabled": [True]}],
            "subnet_group_name": "${aws_dax_subnet_group.example.name}",
            "tags": "${var.common_tags}",
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
