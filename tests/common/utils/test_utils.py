import os
import unittest

from checkov.common.models.consts import SCAN_HCL_FLAG
from checkov.common.util.config_utils import should_scan_hcl_files
from checkov.common.util.data_structures_utils import merge_dicts


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


    def test_should_scan_hcl_env_var(self):
        orig_value = os.getenv(SCAN_HCL_FLAG)

        os.unsetenv(SCAN_HCL_FLAG)
        self.assertFalse(should_scan_hcl_files())

        os.environ[SCAN_HCL_FLAG] = 'FALSE'
        self.assertFalse(should_scan_hcl_files())

        os.environ[SCAN_HCL_FLAG] = 'TrUe'
        self.assertTrue(should_scan_hcl_files())

        if orig_value:
            os.environ[SCAN_HCL_FLAG] = orig_value


if __name__ == '__main__':
    unittest.main()
