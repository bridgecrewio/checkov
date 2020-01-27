import unittest

from checkov.terraform.checks.resource.aws.IAMPolicyAttachedToGroupOrRoles import check
from checkov.terraform.models.enums import CheckResult


class TestIAMPolicyAttachedToGroupOrRoles(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'user': ['${aws_iam_user.user.name}'], 'policy_arn': ['${aws_iam_policy.policy.arn}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'], 'policy': [
            '{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Action": [\n        "ec2:Describe*"\n      ],\n      "Effect": "Allow",\n      "Resource": "*"\n    }\n  ]\n}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
