from checkov.sast.consts import SastLanguages
from checkov.sast.checks.base_registry import Registry
import pathlib
import os
import unittest


class TestRegistry(unittest.TestCase):
    def test_sast_registry_only_python(self):
        checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'checks')
        registry = Registry(checks_dir)

        registry.load_rules([SastLanguages.PYTHON])
        assert registry.rules == [os.path.join(checks_dir, 'python_rule.yaml')]


    def test_sast_registry_with_external_dir(self):
        checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'checks')
        external_checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'external_checks')
        registry = Registry(checks_dir)

        registry.load_rules([SastLanguages.PYTHON])
        registry.load_external_rules(external_checks_dir, [SastLanguages.JAVA])
        assert registry.rules == [ os.path.join(checks_dir, 'python_rule.yaml'), os.path.join(external_checks_dir, 'java_rule.yaml')]
