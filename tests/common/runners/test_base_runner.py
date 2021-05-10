import os
import unittest

from checkov.common.runners.base_runner import filter_ignored_directories


class TestBaseRunner(unittest.TestCase):

    def test_filter_ignored_directories_regex(self):
        os.environ["CKV_EXCLUDED_PATHS_REGEXP"] = "tests"
        d_names = ['bin', 'integration_tests', 'tests', 'docs', '.github', 'checkov', 'venv', '.git', 'kubernetes', '.idea']
        expected = ['bin', 'docs', '.github', 'checkov', 'venv', '.git', 'kubernetes', '.idea']
        actual = filter_ignored_directories(d_names)
        self.assertEqual(expected, actual)
