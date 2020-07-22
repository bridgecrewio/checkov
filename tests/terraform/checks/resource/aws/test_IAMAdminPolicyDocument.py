import unittest

from checkov.terraform.checks.resource.aws.IAMAdminPolicyDocument import check
from checkov.common.models.enums import CheckResult


class TestAdminPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': ['{\n  "Version": "2012-10-17", \n  \
                         "Statement": [\n    {\n      \
                         "Action": [\n        "ec2:Describe*"\n      ],\n      \
                         "Effect": "Allow",\n     \
                          "Resource": "*"\n    }\n  ]\n}']}
        scan_result = check.scan_entity_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': ['{\n  "Version": "2012-10-17", \n  \
                         "Statement": [\n    {\n      \
                         "Action": [\n        "*"\n      ],\n      \
                         "Effect": "Allow",\n     \
                          "Resource": "*"\n    }\n  ]\n}']}
        scan_result = check.scan_entity_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_multiple_statements(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': [
                             '{"Version":"2012-10-17","Statement":[{"Sid":"SqsAllow","Effect":"Allow","Action":['
                             '"sqs:GetQueueAttributes","sqs:GetQueueUrl","sqs:ListDeadLetterSourceQueues",'
                             '"sqs:ListQueues","sqs:ReceiveMessage","sqs:SendMessage","sqs:SendMessageBatch"],'
                             '"Resource":"*"},{"Sid":"ALL","Effect":"Allow","Action":["*"],"Resource":["*"]}]} '
                             ]}
        scan_result = check.scan_entity_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()