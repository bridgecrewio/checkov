import os
import unittest

from checkov.terraform.module_loading.loaders.local_path_loader import loader


class TestLocalPathLoader(unittest.TestCase):
    def test_child_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with loader.load(current_dir, "./resources", None, '', '') as content:
            assert content.loaded()
            assert content.path() == os.path.join(current_dir, "resources")

    def test_unhandled_source(self):
        with loader.load("current_dir", "hashicorp/consul/aws", None, '', '') as content:
            assert not content.loaded()

    def test_bad_source(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with self.assertRaises(FileNotFoundError):
            loader.load(current_dir, "./path_that_doesnt_exist", None, '', '')
