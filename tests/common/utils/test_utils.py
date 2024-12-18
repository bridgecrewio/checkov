import os
import re
import unittest

from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import normalize_prisma_url, normalize_bc_url


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

    def test_normalize_prisma_url(self):
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://app0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('http://api0.prismacloud.io'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url('https://api0.prismacloud.io/'))
        self.assertEqual('https://api0.prismacloud.io', normalize_prisma_url(' https://api0.prismacloud.io'))
        self.assertIsNone(normalize_prisma_url(''))
        self.assertIsNone(normalize_prisma_url(None))

    def test_normalize_bc_url(self):
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('https://www.bridgecrew.cloud'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('http://www.bridgecrew.cloud'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url('https://www.bridgecrew.cloud/'))
        self.assertEqual('https://www.bridgecrew.cloud', normalize_bc_url(' https://www.bridgecrew.cloud'))
        self.assertIsNone(normalize_bc_url(''))
        self.assertIsNone(normalize_bc_url(None))

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
