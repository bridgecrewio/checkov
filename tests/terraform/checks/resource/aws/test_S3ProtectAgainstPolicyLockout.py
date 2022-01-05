import unittest
import hcl2

from checkov.terraform.checks.resource.aws.S3ProtectAgainstPolicyLockout import check
from checkov.common.models.enums import CheckResult


class TestS3ProtectAgainstPolicyLockout(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Principal": {
                "AWS": [
                "*"
                ]
            },
            "Effect": "Deny",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "*"
            ]
            }
        ]
        }
        POLICY
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket_policy" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
            "Version": "2012-10-17",
            "Statement": [{
                "Principal": {
                    "AWS": [
                        "*"
                    ]
                },
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [
                    "*"
                ]
            }]
        }
        POLICY
        }
                """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket_policy']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_3(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Principal": "*",
            "Effect": "Deny",
            "Action": "s3:*"
            }
        ]
        }
        POLICY
        }
                """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_skip_noeffect(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket_policy" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
            ]
        }
        POLICY
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket_policy']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_skip_notaction(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket_policy" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "NotAction": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
            ]
        }
        POLICY
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket_policy']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_policyobj(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket_policy" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
            ]
        }
        POLICY
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket_policy']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_statementnotlist(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket_policy" "s3" {
        bucket = "bucket"

        policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
        }
        POLICY
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket_policy']['s3']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
