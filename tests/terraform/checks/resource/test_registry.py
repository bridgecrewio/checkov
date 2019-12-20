import os
import unittest
from unittest.mock import patch

from checkov.terraform.checks.resource.registry import Registry


class TestDirectoryHasInitPy(unittest.TestCase):

    def setUp(self):
        self.registry = Registry()

    @patch('os.path.exists')
    def test_with_init(self, mock_path_exists):
        mock_path_exists.return_value = True
        self.assertTrue(self.registry._directory_has_init_py("/foo/bar"))

    @patch('os.path.exists')
    def test_without_init(self, mock_path_exists):
        mock_path_exists.return_value = False
        self.assertFalse(self.registry._directory_has_init_py("/foo/bar"))



if __name__ == '__main__':
    unittest.main()
