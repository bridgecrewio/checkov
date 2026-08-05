import os
import shutil
import unittest
import logging
import tempfile
from pathlib import Path
from unittest import mock

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.module_finder import (
    ModuleDownload,
    _download_module,
    find_modules,
    find_tf_managed_modules,
    should_download,
    load_tf_modules
)
from checkov.terraform.module_loading.registry import module_loader_registry


class TestModuleFinder(unittest.TestCase):
    @staticmethod
    def get_src_dir():
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(cur_dir, 'data', 'tf_module_downloader', 'public_modules')

    def test_module_finder(self):
        modules = find_modules(self.get_src_dir())
        self.assertEqual(2, len(modules), f"modules: {list(map(lambda mod: mod.module_link, modules))}")
        remote_modules = list(filter(lambda mod: should_download(mod.module_link), modules))
        self.assertEqual(1, len(remote_modules))
        for m in remote_modules:
            if 'terraform-aws-modules' in m.module_link:
                self.assertEqual('~> 2.1.0', m.version)
            else:
                self.assertIsNone(m.version)

    def test_module_finder_ignore_comments(self):
        modules = find_modules(self.get_src_dir())
        module_list = list(map(lambda mod: mod.module_link, modules))
        for m in module_list:
            self.assertIn(m, ["terraform-aws-modules/s3-bucket/aws",
                              "../../../../../../../platform/src/stacks/accountStack"])

    def test_module_finder_nested_blocks(self):
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(cur_dir, 'data', 'nested_modules')
        modules = find_modules(src_dir)
        self.assertEqual(1, len(modules))
        self.assertEqual("3.14.0", modules[0].version)

    def test_excluded_paths_regex_with_character_classes(self):
        """Test that excluded_paths with regex character classes work correctly (issue #7290)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directory structure
            charts_dir = os.path.join(temp_dir, "charts", "app-123", "charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            # Create terraform files
            with open(os.path.join(charts_dir, "main.tf"), 'w') as f:
                f.write('module "test" { source = "terraform-aws-modules/vpc/aws" }')
            with open(os.path.join(temp_dir, "main.tf"), 'w') as f:
                f.write('module "included" { source = "terraform-aws-modules/s3-bucket/aws" }')
            
            # Test with character class regex pattern that caused the original issue
            excluded_paths = [r"charts/[a-z0-9-]+/charts/.*"]
            
            # This should not raise a regex compilation error
            modules = find_modules(temp_dir, excluded_paths=excluded_paths)
            
            # Should find only the included module, not the excluded one
            self.assertEqual(1, len(modules))
            
    def test_excluded_paths_invalid_regex_handling(self):
        """Test that invalid regex patterns in excluded_paths are handled gracefully (issue #7290)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create terraform file
            with open(os.path.join(temp_dir, "main.tf"), 'w') as f:
                f.write('module "test" { source = "terraform-aws-modules/vpc/aws" }')
            
            # Test with invalid regex pattern (backslash escapes that don't work)
            excluded_paths = [r"charts\[a-z0-9-]+\charts\.*"]
            
            # This should not raise a regex compilation error, just skip the invalid pattern
            modules = find_modules(temp_dir, excluded_paths=excluded_paths)
            
            # Should still find the module since the invalid pattern is ignored
            self.assertEqual(1, len(modules))

    def test_downloader(self):
        modules = find_modules(self.get_src_dir())

        remote_modules = [m for m in modules if should_download(m.module_link)]
        module_loader_registry.download_external_modules = True
        load_tf_modules(os.path.join(self.get_src_dir()), run_parallel=True)
        downloaded_modules = os.listdir(os.path.join(self.get_src_dir(), DEFAULT_EXTERNAL_MODULES_DIR))
        distinct_roots = {md.module_link.split('/')[0] for md in remote_modules}
        shutil.rmtree(os.path.join(self.get_src_dir(), DEFAULT_EXTERNAL_MODULES_DIR))
        self.assertEqual(len(downloaded_modules), 1)
        self.assertEqual(len(distinct_roots), 1)


def test_dem_warning(caplog):
    """
    Test that the --download-external-modules flag warning message is only
    logged if the flag is not specified on the command line, and that
    module download warnings are not logged if the flag is set to False.
    """
    caplog.set_level(logging.WARNING)
    module_loader_registry.download_external_modules = None
    _download_module(module_loader_registry, ModuleDownload('xxx'))
    assert 'Failed to download module' in caplog.text
    assert '--download-external-modules flag' in caplog.text
    caplog.clear()

    module_loader_registry.download_external_modules = True
    _download_module(module_loader_registry, ModuleDownload('xxx'))
    assert 'Failed to download module' in caplog.text
    assert '--download-external-modules flag' not in caplog.text
    caplog.clear()

    module_loader_registry.download_external_modules = False
    _download_module(module_loader_registry, ModuleDownload('xxx'))
    assert 'Failed to download module' not in caplog.text
    assert '--download-external-modules flag' not in caplog.text

def test_tf_managed_and_comment_out_modules():
    src_path = Path(__file__).parent / 'data' / 'tf_managed_modules'
    modules = find_tf_managed_modules(str(src_path))

    assert len(modules) == 1
    assert modules[0].tf_managed is True
    assert modules[0].address == "registry.terraform.io/terraform-aws-modules/cloudwatch/aws//modules/log-group:4.1.0"
    assert modules[0].module_link == ".terraform/modules/log_group/modules/log-group"

def test_tf_managed_submodules():
    modules = find_tf_managed_modules(Path(__file__).parent / 'data' / 'tf_managed_submodules')
    assert len(modules) == 2
    assert modules[0].tf_managed is True
    assert modules[0].address == 'somewhere/a:0'
    assert modules[0].module_name == 'a'
    assert modules[0].module_link == '.terraform/modules/a'
    assert modules[1].tf_managed is True
    assert modules[1].address == 'somewhere/b:1'
    assert modules[1].module_name == 'a.b'
    assert modules[1].module_link == '.terraform/modules/a.b'
