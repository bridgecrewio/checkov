import logging
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

    def test_definition_is_list_does_not_crash_and_warns(self):
        """A custom policy whose 'definition' is a list (instead of a dict) must be
        skipped with a logger.warning rather than raising an AttributeError and
        crashing the entire scan."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/test-registry-data/definition-is-list"
        r = Registry(checks_dir=test_files_dir, parser=GraphCheckParser())

        with self.assertLogs("checkov.common.checks_infra.registry", level=logging.WARNING) as cm:
            r.load_checks()

        # The registry must not have loaded the broken check
        self.assertEqual(r.checks, [])

        # A warning mentioning the offending file must have been emitted
        warning_messages = "\n".join(cm.output)
        self.assertIn("check.yaml", warning_messages)
