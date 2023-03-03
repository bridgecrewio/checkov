import os
import unittest

from checkov.common.checks_infra.registry import Registry
from checkov.common.checks_infra.checks_parser import GraphCheckParser


class TestRegistry(unittest.TestCase):
    def test_invalid_check_yaml_does_not_throw_exception(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/test-registry-data/invalid-yaml"
        r = Registry(checks_dir=test_files_dir)
        r.load_checks()

    def test_valid_yaml_but_invalid_check_does_not_throw_exception(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/test-registry-data/valid-yaml-invalid-check"
        r = Registry(checks_dir=test_files_dir, parser=GraphCheckParser())
        r.load_checks()
