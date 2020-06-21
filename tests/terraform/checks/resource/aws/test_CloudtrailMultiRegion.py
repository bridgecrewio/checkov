import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.CloudtrailMultiRegion import check


class TestCloudtrailMultiRegion(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_cloudtrail" "foobar" {
                      name                          = "tf-trail-foobar"
                      s3_bucket_name                = "${aws_s3_bucket.foo.id}"
                      s3_key_prefix                 = "prefix"
                      include_global_service_events = false
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_cloudtrail']['foobar']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_negative_multi_region(self):
        hcl_res = hcl2.loads("""
                    resource "aws_cloudtrail" "foobar" {
                      name                          = "tf-trail-foobar"
                      s3_bucket_name                = "${aws_s3_bucket.foo.id}"
                      s3_key_prefix                 = "prefix"
                      include_global_service_events = false
                      is_multi_region_trail  = false
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_cloudtrail']['foobar']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_cloudtrail" "foobar" {
                      name                          = "tf-trail-foobar"
                      s3_bucket_name                = "${aws_s3_bucket.foo.id}"
                      s3_key_prefix                 = "prefix"
                      include_global_service_events = false
                      is_multi_region_trail  = true
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_cloudtrail']['foobar']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
