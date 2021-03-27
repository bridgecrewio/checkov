import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SQSPolicy import check


class TestSQSPolicy(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
                    resource "aws_sqs_queue_policy" "test" {
                    queue_url = aws_sqs_queue.q.id

                    policy = <<POLICY
                    {
                    "Version": "2012-10-17",
                    "Id": "sqspolicy",
                    "Statement": [
                        {
                        "Sid": "First",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "*",
                        "Resource": "${aws_sqs_queue.q.arn}",
                        "Condition": {
                            "ArnEquals": {
                            "aws:SourceArn": "${aws_sns_topic.example.arn}"
                            }
                        }
                        }
                    ]
                    }
                    POLICY
                    }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_sqs_queue_policy"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
                    resource "aws_sqs_queue_policy" "test" {
                    queue_url = aws_sqs_queue.q.id

                    policy = <<POLICY
                    {
                    "Version": "2012-10-17",
                    "Id": "sqspolicy",
                    "Statement": [
                        {
                        "Sid": "First",
                        "Effect": "Allow",
                        "Principal": "ARN:01010101010:TEST:SAMPLE",
                        "Action": "sqs:SendMessage",
                        "Resource": "${aws_sqs_queue.q.arn}",
                        "Condition": {
                            "ArnEquals": {
                            "aws:SourceArn": "${aws_sns_topic.example.arn}"
                            }
                        }
                        }
                    ]
                    }
                    POLICY
                    }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_sqs_queue_policy"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
