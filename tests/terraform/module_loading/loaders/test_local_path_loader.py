import os
import unittest

from checkov.terraform.module_loading.loaders.local_path_loader import loader


class TestLocalPathLoader(unittest.TestCase):
    def test_child_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        content = loader.load(current_dir, current_dir, "./resources", None, "", "")
        assert content.loaded()
        assert content.path() == os.path.join(current_dir, "resources")

    def test_unhandled_source(self):
        content = loader.load("current_dir", "current_dir", "hashicorp/consul/aws", None, "", "")
        assert not content.loaded()

    def test_bad_source(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with self.assertRaises(FileNotFoundError):
            loader.load(current_dir, current_dir, "./path_that_doesnt_exist", None, '', '')

    def test_absolute_path(self):
        # Generate absolute path dynamically so test is OS agnostic
        current_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = os.path.join(current_dir, "resources")
        content = loader.load(current_dir, current_dir, target_dir, None, '', '')
        assert content.loaded()
        assert content.path() == os.path.join(current_dir, "resources")
