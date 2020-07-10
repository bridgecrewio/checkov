import unittest

import hcl2
from checkov.terraform.checks.resource.aws.WAFEnabled import check
from checkov.common.models.enums import CheckResult


class TestS3MFADelete(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "aws_cloudfront_distribution" "example" {
            origin {
                domain_name = aws_s3_bucket.website.bucket_regional_domain_name
				origin_id   = "${aws_s3_bucket.website.id}-origin"
                s3_origin_config {
                    origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
					}
		   		}
                enabled         = true
                is_ipv6_enabled = true
                default_root_object = "index.html"
                price_class = var.price_class
                tags = var.common_tags
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_cloudfront_distribution']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_cloudfront_distribution" "example" {
            web_acl_id = "IsSetToAValue"
            origin {
                domain_name = aws_s3_bucket.website.bucket_regional_domain_name
				origin_id   = "${aws_s3_bucket.website.id}-origin"
                
                s3_origin_config {
                    origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
				}
            }
						
  			enabled         = true
  			is_ipv6_enabled = true
 			default_root_object = "index.html"
            price_class = var.price_class
            tags = var.common_tags
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_cloudfront_distribution']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
