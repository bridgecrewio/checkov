import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.util.dict_utils import merge_dicts
from checkov.common.util.docs_generator import get_compare_key


class TestUtils(unittest.TestCase):
    def test_merge_dicts(self):
        dict1 = {"a": "1", "b": "2"}
        dict2 = {"a": "4", "c": "3"}
        dict3 = {"x": "x", "y": "y", "a": "q"}

        res = merge_dicts(dict1, dict2)
        self.assertEqual(len(res), 3)
        self.assertEqual(res["a"], "4")
        self.assertEqual(res["b"], "2")
        self.assertEqual(res["c"], "3")

        res = merge_dicts(dict1, dict2, dict3)
        self.assertEqual(len(res), 5)
        self.assertEqual(res["a"], "q")
        self.assertEqual(res["b"], "2")
        self.assertEqual(res["c"], "3")
        self.assertEqual(res["x"], "x")
        self.assertEqual(res["y"], "y")

        res = merge_dicts(dict1, None)
        self.assertEqual(len(res), 2)
        self.assertEqual(res["a"], "1")
        self.assertEqual(res["b"], "2")

        res = merge_dicts(dict1, 7)
        self.assertEqual(len(res), 2)
        self.assertEqual(res["a"], "1")
        self.assertEqual(res["b"], "2")


if __name__ == "__main__":
    unittest.main()
