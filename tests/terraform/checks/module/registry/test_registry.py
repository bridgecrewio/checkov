import os
import unittest
from unittest.mock import patch

from checkov.runner_filter import RunnerFilter


class TestRegistry(unittest.TestCase):

    def setUp(self):
        from checkov.terraform.checks.module.registry import module_registry
        self.registry = module_registry

    @patch('os.path.exists')
    def test_with_init(self, mock_path_exists):
        mock_path_exists.return_value = True
        self.assertTrue(self.registry._directory_has_init_py("/foo/bar"))

    @patch('os.path.exists')
    def test_without_init(self, mock_path_exists):
        mock_path_exists.return_value = False
        self.assertFalse(self.registry._directory_has_init_py("/foo/bar"))

    def test_registry_external_check_load(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        external_dir = current_dir + "/example_external_dir/extra_checks"
        self.registry.load_external_checks(external_dir, RunnerFilter())

        external_check_loaded = False
        external_check = None
        for check in self.registry.checks['module']:
            if check.__class__.__name__ == 'ModuleCheck':
                external_check_loaded = True
                external_check = check
        self.assertTrue(external_check_loaded)
        self.registry.checks['module'].remove(external_check)


if __name__ == '__main__':
    unittest.main()
