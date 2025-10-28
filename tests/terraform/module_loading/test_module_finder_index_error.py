import logging

import pytest

from checkov.terraform.module_loading.module_finder import ModuleDownload, _download_module
from checkov.terraform.module_loading.registry import module_loader_registry


@pytest.mark.parametrize(
    "module_link",
    [
        "github.com/someorg/terraform-aws-mcaf-role?ref=v0.3.3",
        "terraform-aws-modules/kms/aws",
    ],
    ids=[
        "github_ref",
        "registry",
    ],
)
def test_download_module_logs_index_error(caplog, module_link):
    """
    Validate that ModuleFinder not logs a warning with the address and the IndexError
    ('list index out of range').
    """
    caplog.set_level(logging.WARNING)

    md = ModuleDownload(source_dir=".")
    md.module_link = module_link
    md.version = None  # version is embedded in module_link for github_ref cases
    md.address = module_link
    md.tf_managed = False

    success = _download_module(module_loader_registry, md)

    assert success is False
    assert "Unable to load module in module_finder" not in caplog.text
    assert "list index out of range" not in caplog.text
