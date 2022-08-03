import os
import unittest

from checkov.terraform.module_loading.loaders.local_path_loader import loader
from checkov.terraform.module_loading.module_params import ModuleParams


class TestLocalPathLoader(unittest.TestCase):
    def test_child_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        module_params = ModuleParams(current_dir, current_dir, "./resources", None, "", "")
        content = loader.load(module_params)
        assert content.loaded()
        assert content.path() == os.path.join(current_dir, "resources")

    def test_unhandled_source(self):
        module_params = ModuleParams("current_dir", "current_dir", "hashicorp/consul/aws", None, "", "")
        content = loader.load(module_params)
        assert not content.loaded()

    def test_bad_source(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with self.assertRaises(FileNotFoundError):
            module_params = ModuleParams(current_dir, current_dir, "./path_that_doesnt_exist", None, '', '')
            loader.load(module_params)

    def test_absolute_path(self):
        # Generate absolute path dynamically so test is OS agnostic
        current_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = os.path.join(current_dir, "resources")
        module_params = ModuleParams(current_dir, current_dir, target_dir, None, '', '')
        content = loader.load(module_params)
        assert content.loaded()
        assert content.path() == os.path.join(current_dir, "resources")
