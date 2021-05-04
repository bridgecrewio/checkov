import unittest
import hcl2

from checkov.terraform.checks.resource.aws.IAMRoleAllowsPublicAssume import check
from checkov.common.models.enums import CheckResult


class TestIAMRoleAllowsPublicAssume(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_iam_role" "lambdaRole" {
    name = "test-role"
    assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
{
"Action": "sts:AssumeRole",
"Principal" : {"Service": "lambda.amazonaws.com"},
"Effect": "Allow"
},
{
"Action": "sts:AssumeRole",
"Principal" : {"AWS": "*"},
"Effect": "Allow"
},
{
"Action": "sts:AssumeRole",
"Principal" : {"Service": "events.amazonaws.com"},
"Effect": "Allow"
}
]
}

EOF
}        
        """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_array(self):
        hcl_res = hcl2.loads("""
resource "aws_iam_role" "lambdaRole" {
    name = "test-role"
    assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
{
"Action": "sts:AssumeRole",
"Principal" : {"Service": "lambda.amazonaws.com"},
"Effect": "Allow"
},
{
"Action": "sts:AssumeRole",
"Principal" : {"AWS": ["*"]},
"Effect": "Allow"
},
{
"Action": "sts:AssumeRole",
"Principal" : {"Service": "events.amazonaws.com"},
"Effect": "Allow"
}
]
}

EOF
}        
        """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_iam_role" "lambdaRole" {
    name = "test-role"
    assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
{
"Action": "sts:AssumeRole",
"Principal" : {"Service": "lambda.amazonaws.com"},
"Effect": "Allow"
}
]
}

EOF
}        
        """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_deny(self):
        hcl_res = hcl2.loads("""
resource "aws_iam_role" "lambdaRole" {
    name = "test-role"
    assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
{
"Action": "sts:AssumeRole",
"Principal" : {"AWS": "*"},
"Effect": "Deny"
}
]
}

EOF
}        
        """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_empty_iam_policy(self):
        hcl_res = hcl2.loads("""
        resource "aws_iam_role" "lambdaRole" {
            name = "test-role"
            assume_role_policy = ""
        }        
                """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_empty_iam_policy_2(self):
        hcl_res = hcl2.loads("""
        resource "aws_iam_role" "lambdaRole" {
            name = "test-role"
        }        
                """)
        resource_conf = hcl_res['resource'][0]['aws_iam_role']['lambdaRole']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
