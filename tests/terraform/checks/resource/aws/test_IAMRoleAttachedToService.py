import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.IAMRoleAllowsPublicAssume import check


class TestIAMRoleAllowsPublicAssume(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["${var.name}-default"],
            "assume_role_policy": [
                '{\n  "Version": "2012-10-17",\n  '
                '"Statement": [\n    '
                "{\n      "
                '"Action": "sts:AssumeRole",'
                '\n      "Principal": {\n        '
                '"AWS": '
                '"*"\n      },'
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


if __name__ == "__main__":
    unittest.main()
