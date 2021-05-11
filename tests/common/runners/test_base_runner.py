import os
import unittest

from checkov.common.runners.base_runner import filter_ignored_directories


class TestBaseRunner(unittest.TestCase):

    def test_filter_ignored_directories_regex(self):
        d_names = ['bin', 'integration_tests', 'tests', 'docs', '.github', 'checkov', 'venv', '.git', 'kubernetes', '.idea']
        expected = ['bin', 'docs', 'checkov', 'venv', 'kubernetes']
        filter_ignored_directories(d_names, ["tests"])
        self.assertEqual(expected, d_names)
