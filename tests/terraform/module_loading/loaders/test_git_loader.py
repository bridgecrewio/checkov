import pytest

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.module_params import ModuleParams


@pytest.mark.parametrize("source, expected_root_module, expected_inner_module", [
    ("git::git@github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("git::ssh://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-with-inner-module-no-git-prefix/out-module//in-module",
     "github.com:test-with-inner-module-no-git-prefix/out-module", "in-module")
]
                         )
def test__parse_module_source(source: str, expected_root_module: str, expected_inner_module: str) -> None:
    git_loader = GenericGitLoader()
    module_params = ModuleParams(
        root_dir="test",
        current_dir="test",
        source=source,
        source_version="source_version",
        dest_dir="test",
        external_modules_folder_name="test",
        inner_module="",
        tf_managed=False
    )
    module_source = git_loader._parse_module_source(module_params)
    assert module_source.root_module == expected_root_module
    assert module_source.inner_module == expected_inner_module
