import unittest

from checkov.terraform.checks.resource.aws.CloudfrontDistributionEncryption import check
from checkov.common.models.enums import CheckResult


class TestCloudfrontDistributionEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'origin': [
            {'domain_name': ['${aws_s3_bucket.b.bucket_regional_domain_name}'], 'origin_id': ['${local.s3_origin_id}'],
             's3_origin_config': [{'origin_access_identity': ['origin-access-identity/cloudfront/ABCDEFG1234567']}]}],  # checkov:skip=CKV_SECRET_6 false positive
            'enabled': [True], 'is_ipv6_enabled': [True], 'comment': ['Some comment'],
            'default_root_object': ['index.html'], 'logging_config': [
                {'include_cookies': [False], 'bucket': ['mylogs.s3.amazonaws.com'], 'prefix': ['myprefix']}],
            'aliases': [['mysite.example.com', 'yoursite.example.com']], 'ordered_cache_behavior': [
                {'path_pattern': ['/content/immutable/*'], 'allowed_methods': [['GET', 'HEAD', 'OPTIONS']],
                 'cached_methods': [['GET', 'HEAD', 'OPTIONS']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [
                     {'query_string': [False], 'headers': [['Origin']], 'cookies': [{'forward': ['none']}]}],
                 'min_ttl': [0], 'default_ttl': [86400], 'max_ttl': [31536000], 'compress': [True],
                 'viewer_protocol_policy': ['redirect-to-https']},
                {'path_pattern': ['/content/*'], 'allowed_methods': [['GET', 'HEAD', 'OPTIONS']],
                 'cached_methods': [['GET', 'HEAD']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [{'query_string': [False], 'cookies': [{'forward': ['none']}]}], 'min_ttl': [0],
                 'default_ttl': [3600], 'max_ttl': [86400], 'compress': [True],
                 'viewer_protocol_policy': ['redirect-to-https']}], 'price_class': ['PriceClass_200'], 'restrictions': [
                {'geo_restriction': [{'restriction_type': ['whitelist'], 'locations': [['US', 'CA', 'GB', 'DE']]}]}],
            'viewer_certificate': [{'cloudfront_default_certificate': [True]}], 'default_cache_behavior': [
                {'allowed_methods': [['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT']],
                 'cached_methods': [['GET', 'HEAD']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [{'query_string': [False], 'cookies': [{'forward': ['none']}]}],
                 'viewer_protocol_policy': ['allow-all'], 'min_ttl': [0], 'default_ttl': [3600], 'max_ttl': [86400]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'origin': [
            {'domain_name': ['${aws_s3_bucket.b.bucket_regional_domain_name}'], 'origin_id': ['${local.s3_origin_id}'],
             's3_origin_config': [{'origin_access_identity': ['origin-access-identity/cloudfront/ABCDEFG1234567']}]}],
            'enabled': [True], 'is_ipv6_enabled': [True], 'comment': ['Some comment'],
            'default_root_object': ['index.html'], 'logging_config': [
                {'include_cookies': [False], 'bucket': ['mylogs.s3.amazonaws.com'], 'prefix': ['myprefix']}],
            'aliases': [['mysite.example.com', 'yoursite.example.com']], 'ordered_cache_behavior': [
                {'path_pattern': ['/content/immutable/*'], 'allowed_methods': [['GET', 'HEAD', 'OPTIONS']],
                 'cached_methods': [['GET', 'HEAD', 'OPTIONS']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [
                     {'query_string': [False], 'headers': [['Origin']], 'cookies': [{'forward': ['none']}]}],
                 'min_ttl': [0], 'default_ttl': [86400], 'max_ttl': [31536000], 'compress': [True],
                 'viewer_protocol_policy': ['redirect-to-https']},
                {'path_pattern': ['/content/*'], 'allowed_methods': [['GET', 'HEAD', 'OPTIONS']],
                 'cached_methods': [['GET', 'HEAD']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [{'query_string': [False], 'cookies': [{'forward': ['none']}]}], 'min_ttl': [0],
                 'default_ttl': [3600], 'max_ttl': [86400], 'compress': [True],
                 'viewer_protocol_policy': ['redirect-to-https']}], 'price_class': ['PriceClass_200'], 'restrictions': [
                {'geo_restriction': [{'restriction_type': ['whitelist'], 'locations': [['US', 'CA', 'GB', 'DE']]}]}],
            'viewer_certificate': [{'cloudfront_default_certificate': [True]}], 'default_cache_behavior': [
                {'allowed_methods': [['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT']],
                 'cached_methods': [['GET', 'HEAD']], 'target_origin_id': ['${local.s3_origin_id}'],
                 'forwarded_values': [{'query_string': [False], 'cookies': [{'forward': ['none']}]}],
                 'viewer_protocol_policy': ['redirect-to-https'], 'min_ttl': [0], 'default_ttl': [3600],
                 'max_ttl': [86400]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
