import os
import shutil
import unittest
import logging
from pathlib import Path
from unittest import mock

from checkov.common.util.env_vars_config import env_vars_config
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.module_finder import (
    ModuleDownload,
    _download_module,
    find_modules,
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

@mock.patch.object(env_vars_config, "CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES", True)
def test_tf_managed_and_comment_out_modules():
    src_path = Path(__file__).parent / 'data' / 'tf_managed_modules'
    modules = find_modules(str(src_path))

    assert len(modules) == 1
    assert modules[0].tf_managed is True
    assert modules[0].address == "registry.terraform.io/terraform-aws-modules/cloudwatch/aws//modules/log-group:4.1.0"
    assert modules[0].module_link == ".terraform/modules/log_group/modules/log-group"

@mock.patch.object(env_vars_config, "CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES", True)
def test_tf_managed_submodules():
    modules = find_modules(Path(__file__).parent / 'data' / 'tf_managed_submodules')
    assert len(modules) == 2
    assert modules[0].tf_managed is True
    assert modules[0].address == 'somewhere/a:0'
    assert modules[0].module_name == 'a'
    assert modules[0].module_link == '.terraform/modules/a'
    assert modules[1].tf_managed is True
    assert modules[1].address == 'somewhere/b:1'
    assert modules[1].module_name == 'a.b'
    assert modules[1].module_link == '.terraform/modules/a.b'

