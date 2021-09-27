import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.IAMStarActionPolicyDocument import check


class TestIAMStarActionPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': ['{"Version": "2012-10-17", "Statement": [{"Action": ["ec2:Describe*"], "Effect": "Allow", "Resource": "abc*"}]}']}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_iam_policy')
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_service_star(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': [{'Version': '2012-10-17',
                                     'Statement': [{'Action': 'ec2:*', 'Effect': 'Allow', 'Resource': 'abc*'}]}]}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_iam_policy')
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': [{'Version': '2012-10-17',
                                     'Statement': [{'Action': ['*'], 'Effect': 'Allow', 'Resource': 'abc*'}]}]}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_iam_policy')
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_multiple_statements(self):
        resource_conf = {'name': ['test'], 'user': ['${aws_iam_user.lb.name}'],
                         'policy': [
                             {'Version': '2012-10-17', 'Statement': [{'Sid': 'SqsAllow', 'Effect': 'Allow',
                                                                      'Action': ['sqs:GetQueueAttributes',
                                                                                 'sqs:GetQueueUrl',
                                                                                 'sqs:ListDeadLetterSourceQueues',
                                                                                 'sqs:ListQueues', 'sqs:ReceiveMessage',
                                                                                 'sqs:SendMessage',
                                                                                 'sqs:SendMessageBatch'],
                                                                      'Resource': '*'},
                                                                     {'Sid': 'ALL', 'Effect': 'Allow', 'Action': ['*'],
                                                                      'Resource': ['${var.my_resource_arn}']}]}

                         ]}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_iam_policy')
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_sso_failure(self):

        resource_conf = {'instance_arn': '${aws_ssoadmin_permission_set.example.arn}', 'permission_set_arn': '${aws_iam_user.lb.name}',
                         'inline_policy': [{'Version': '2012-10-17',
                                     'Statement': [{'Action': ['*'], 'Effect': 'Allow', 'Resource': 'abc*'}]}]}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_ssoadmin_permission_set_inline_policy')
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_sso_success(self):
        resource_conf = {'instance_arn': '${aws_ssoadmin_permission_set.example.arn}', 'permission_set_arn': '${aws_iam_user.lb.name}',
                         'inline_policy': ['{"Version": "2012-10-17", "Statement": [{"Action": ["ec2:Describe*"], "Effect": "Allow", "Resource": "abc*"}]}']}
        scan_result = check.scan_entity_conf(conf=resource_conf, entity_type='aws_ssoadmin_permission_set_inline_policy')
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
