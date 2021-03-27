import os
import shutil
import unittest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry


class TestModuleLoaderRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "./tmp")
        )

    def tearDown(self) -> None:
        if os.path.exists(self.current_dir):
            shutil.rmtree(self.current_dir)

    def test_load_terraform_registry(self):
        registry = ModuleLoaderRegistry(True, DEFAULT_EXTERNAL_MODULES_DIR)
        source = "terraform-aws-modules/security-group/aws"
        with registry.load(
            current_dir=self.current_dir, source=source, source_version="~> 3.0"
        ) as content:
            assert content.loaded()
            expected_content_path = os.path.join(
                self.current_dir, DEFAULT_EXTERNAL_MODULES_DIR, source
            )
            self.assertEqual(
                expected_content_path,
                content.path(),
                f"expected content.path() to be {content.path()}, got {expected_content_path}",
            )

    def test_load_terraform_registry_check_cache(self):
        registry = ModuleLoaderRegistry(download_external_modules=True)
        source1 = "https://github.com/bridgecrewio/checkov_not_working1.git"
        registry.load(
            current_dir=self.current_dir, source=source1, source_version="latest"
        )
        self.assertTrue(source1 in registry.failed_urls_cache)
        source2 = "https://github.com/bridgecrewio/checkov_not_working2.git"
        registry.load(
            current_dir=self.current_dir, source=source2, source_version="latest"
        )
        self.assertTrue(
            source1 in registry.failed_urls_cache
            and source2 in registry.failed_urls_cache
        )

    def test_load_local_module_absolute_path(self):
        registry = ModuleLoaderRegistry(download_external_modules=True)
        source = "/some/module"
        try:
            registry.load(
                current_dir=self.current_dir, source=source, source_version="latest"
            )
            self.assertEqual(1, 2, "Module loading should have thrown an error")
        except FileNotFoundError as e:
            self.assertEqual(str(e), source)
