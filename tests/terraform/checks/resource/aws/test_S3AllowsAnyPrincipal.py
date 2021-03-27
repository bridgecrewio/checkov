import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3AllowsAnyPrincipal import check


class TestS3AllowsAnyPrincipal(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
resource "aws_s3_bucket" "s3" {
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            }
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_policyobj(self):
        hcl_res = hcl2.loads(
            """
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            }
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket_policy"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_array(self):
        hcl_res = hcl2.loads(
            """
resource "aws_s3_bucket" "s3" {
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": ["*"]
            }
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_anon(self):
        hcl_res = hcl2.loads(
            """
resource "aws_s3_bucket" "s3" {
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": "*"
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
resource "aws_s3_bucket" "s3" {
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "some_arn"
            }
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_deny(self):
        hcl_res = hcl2.loads(
            """
resource "aws_s3_bucket" "s3" {
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
            "Principal": "*"
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_policyobj(self):
        hcl_res = hcl2.loads(
            """
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
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "some_arn"
            }
        }
    ]
}
POLICY
}
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket_policy"]["s3"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
