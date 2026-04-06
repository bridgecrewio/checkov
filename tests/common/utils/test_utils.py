import os
import re
import unittest
from unittest.mock import patch

from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import normalize_prisma_url, normalize_bc_url, _validate_api_url_domain


class TestUtils(unittest.TestCase):

    def test_merge_dicts(self):
        dict1 = {'a': '1', 'b': '2'}
        dict2 = {'a': '4', 'c': '3'}
        dict3 = {'x': 'x', 'y': 'y', 'a': 'q'}

        res = merge_dicts(dict1, dict2)
        self.assertEqual(len(res), 3)
        self.assertEqual(res['a'], '4')
        self.assertEqual(res['b'], '2')
        self.assertEqual(res['c'], '3')

        res = merge_dicts(dict1, dict2, dict3)
        self.assertEqual(len(res), 5)
        self.assertEqual(res['a'], 'q')
        self.assertEqual(res['b'], '2')
        self.assertEqual(res['c'], '3')
        self.assertEqual(res['x'], 'x')
        self.assertEqual(res['y'], 'y')

        res = merge_dicts(dict1, None)
        self.assertEqual(len(res), 2)
        self.assertEqual(res['a'], '1')
        self.assertEqual(res['b'], '2')

        res = merge_dicts(dict1, 7)
        self.assertEqual(len(res), 2)
        self.assertEqual(res['a'], '1')
        self.assertEqual(res['b'], '2')

    # --- Prisma URL normalization + domain validation ---

    def test_normalize_prisma_url(self):
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://app0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('http://api0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io/'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url(' https://api0.prismacloud.io'))
        self.assertIsNone(normalize_prisma_url(''))
        self.assertIsNone(normalize_prisma_url(None))

    def test_normalize_prisma_url_valid_domains(self):
        """Verify all legitimate Prisma Cloud API URL patterns are accepted."""
        self.assertEqual('https://api.prismacloud.io', normalize_prisma_url('https://api.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io'))
        self.assertEqual('https://api2.eu.prismacloud.io', normalize_prisma_url('https://api2.eu.prismacloud.io'))
        self.assertEqual('https://api.gov.prismacloud.io', normalize_prisma_url('https://api.gov.prismacloud.io'))
        self.assertEqual('https://api.prismacloud.cn', normalize_prisma_url('https://api.prismacloud.cn'))

    def test_normalize_prisma_url_rejects_unknown_domain(self):
        """Verify that non-allowlisted domains are rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://example.com/api')
        self.assertEqual(ctx.exception.code, 2)

    def test_normalize_prisma_url_rejects_invalid_domains(self):
        """Verify that spoofed or look-alike domains are rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://not-prismacloud.com')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://api0.prismacloud.io.example.com')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://prismacloud.io.example.com')
        self.assertEqual(ctx.exception.code, 2)

    # --- Bridgecrew URL normalization + domain validation ---

    def test_normalize_bc_url(self):
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('https://www.bridgecrew.cloud'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('http://www.bridgecrew.cloud'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('https://www.bridgecrew.cloud/'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url(' https://www.bridgecrew.cloud'))
        self.assertIsNone(normalize_bc_url(''))
        self.assertIsNone(normalize_bc_url(None))

    def test_normalize_bc_url_valid_domains(self):
        """Verify legitimate Bridgecrew URLs are accepted."""
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('https://www.bridgecrew.cloud'))
        self.assertEqual('https://bridgecrew.cloud', normalize_bc_url('https://bridgecrew.cloud'))

    def test_normalize_bc_url_rejects_invalid_domains(self):
        """Verify that spoofed or look-alike Bridgecrew domains are rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_bc_url('https://not-bridgecrew.cloud')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_bc_url('https://bridgecrew.cloud.example.com')
        self.assertEqual(ctx.exception.code, 2)

    # --- _validate_api_url_domain direct tests ---

    def test_validate_api_url_domain_rejects_no_hostname(self):
        with self.assertRaises(SystemExit) as ctx:
            _validate_api_url_domain('not-a-url', 'test')
        self.assertEqual(ctx.exception.code, 2)

    # --- CHECKOV_ALLOW_API_DOMAINS env var override tests ---

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': '.execute-api.us-west-2.amazonaws.com'})
    def test_env_var_allows_custom_domain(self):
        """Verify CHECKOV_ALLOW_API_DOMAINS extends the allowlist for local dev."""
        result = normalize_prisma_url('https://zff3s5gfse.execute-api.us-west-2.amazonaws.com/v1')
        self.assertEqual('https://zff3s5gfse.execute-api.us-west-2.amazonaws.com/v1', result)

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': '.execute-api.us-west-2.amazonaws.com'})
    def test_env_var_still_allows_default_domains(self):
        """Verify default domains still work when env var is set."""
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io'))
        self.assertEqual('https://api.prismacloud.cn', normalize_prisma_url('https://api.prismacloud.cn'))

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': '.execute-api.us-west-2.amazonaws.com'})
    def test_env_var_does_not_allow_unlisted_domains(self):
        """Verify domains not in default or env var list are still rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://evil.com/api')
        self.assertEqual(ctx.exception.code, 2)

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': '.example.dev, .staging.internal'})
    def test_env_var_multiple_domains(self):
        """Verify comma-separated domains are all accepted."""
        result1 = normalize_prisma_url('https://api.example.dev')
        self.assertEqual('https://api.example.dev', result1)
        result2 = normalize_prisma_url('https://api.staging.internal')
        self.assertEqual('https://api.staging.internal', result2)

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': 'execute-api.us-west-2.amazonaws.com'})
    def test_env_var_auto_adds_leading_dot(self):
        """Verify leading dot is added automatically if missing."""
        result = normalize_prisma_url('https://abc123.execute-api.us-west-2.amazonaws.com/v1')
        self.assertEqual('https://abc123.execute-api.us-west-2.amazonaws.com/v1', result)

    @patch.dict(os.environ, {'CHECKOV_ALLOW_API_DOMAINS': ''})
    def test_env_var_empty_uses_defaults_only(self):
        """Verify empty env var doesn't change behavior."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://evil.com')
        self.assertEqual(ctx.exception.code, 2)
        # Default domains still work
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io'))

    def test_skip_comment_regex(self):
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'checkov:skip=CKV_AWS_145: ADD REASON'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'checkov:skip=CKV_AWS_145:ADD REASON'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'checkov:skip=CKV_AWS_145'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'bridgecrew:skip=CKV_AWS_145:ADD REASON'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'bridgecrew:skip=CKV_AWS_145'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'bridgecrew:skip=BC_AWS_GENERAL_123'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'bridgecrew:skip=bcorg_AWS_1234567'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'checkov:skip=bcorg_AWS_1234567'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'cortex:skip=CKV_AWS_145: ADD REASON'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'cortex:skip=CKV_AWS_145:ADD REASON'))
        self.assertIsNotNone(re.search(COMMENT_REGEX, 'cortex:skip=CKV_AWS_145'))



if __name__ == '__main__':
    unittest.main()
