import os
import shutil
import unittest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry


class TestModuleLoaderRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./tmp"))

    def tearDown(self) -> None:
        if os.path.exists(self.current_dir):
            shutil.rmtree(self.current_dir)

    def test_load_terraform_registry(self):
        registry = ModuleLoaderRegistry(True, DEFAULT_EXTERNAL_MODULES_DIR)
        source = "terraform-aws-modules/security-group/aws"
        with registry.load(current_dir=self.current_dir, source=source, source_version="~> 3.0") as content:
            assert content.loaded()
            expected_content_path = os.path.join(self.current_dir, DEFAULT_EXTERNAL_MODULES_DIR, source)
            self.assertEqual(expected_content_path, content.path(), f"expected content.path() to be {content.path()}, got {expected_content_path}")
