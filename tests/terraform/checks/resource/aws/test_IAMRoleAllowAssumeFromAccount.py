import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.IAMRoleAllowAssumeFromAccount import check


class TestIAMRoleAllowAssumeFromAccount(unittest.TestCase):
    def test_failure_1(self):
        resource_conf = {
            "name": ["${var.name}-default"],
            "assume_role_policy": [
                '{\n  "Version": "2012-10-17",\n  '
                '"Statement": [\n    '
                "{\n      "
                '"Action": "sts:AssumeRole",'
                '\n      "Principal": {\n        '
                '"AWS": '
                '"123123123123"\n      },'
                '\n      "Effect": "Allow",'
                '\n      "Sid": ""\n    }\n  ]\n}'
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        resource_conf = {
            "name": ["${var.name}-default"],
            "assume_role_policy": [
                '{\n  "Version": "2012-10-17",\n  '
                '"Statement": [\n    '
                "{\n      "
                '"Action": "sts:AssumeRole",'
                '\n      "Principal": {\n        '
                '"AWS": '
                '"arn:aws:iam::123123123123:root"\n      },'
                '\n      "Effect": "Allow",'
                '\n      "Sid": ""\n    }\n  ]\n}'
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["${var.name}-default"],
            "assume_role_policy": [
                '{\n  "Version": "2012-10-17",\n  '
                '"Statement": [\n    '
                "{\n      "
                '"Action": "sts:AssumeRole",'
                '\n      "Principal": {\n        '
                '"Service": '
                '"ecs-tasks.amazonaws.com"\n      },'
                '\n      "Effect": "Allow",'
                '\n      "Sid": ""\n    }\n  ]\n}'
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_empty_iam_role(self):
        resource_conf = {"name": ["${var.name}-default"], "assume_role_policy": ""}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_empty_iam_role_2(self):
        resource_conf = {
            "name": ["${var.name}-default"],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
