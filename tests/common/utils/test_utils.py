import os
import re
import unittest

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

    def test_normalize_prisma_url_rejects_attacker_domain(self):
        """PoC rejection: the exact payload from the reproduction steps must be rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://attacker.example/capture')
        self.assertEqual(ctx.exception.code, 2)

    def test_normalize_prisma_url_rejects_invalid_domains(self):
        """Verify various attacker-controlled or spoofed domains are rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://evil.com')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://api0.prismacloud.io.evil.com')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_prisma_url('https://prismacloud.io.evil.com')
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
        """Verify attacker-controlled or spoofed Bridgecrew domains are rejected."""
        with self.assertRaises(SystemExit) as ctx:
            normalize_bc_url('https://evil-bridgecrew.cloud')
        self.assertEqual(ctx.exception.code, 2)
        with self.assertRaises(SystemExit) as ctx:
            normalize_bc_url('https://bridgecrew.cloud.evil.com')
        self.assertEqual(ctx.exception.code, 2)

    # --- _validate_api_url_domain direct tests ---

    def test_validate_api_url_domain_rejects_no_hostname(self):
        with self.assertRaises(SystemExit) as ctx:
            _validate_api_url_domain('not-a-url', 'test')
        self.assertEqual(ctx.exception.code, 2)

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
